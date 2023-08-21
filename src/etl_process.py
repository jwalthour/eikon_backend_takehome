import logging
from multiprocessing import Process
import os
import pandas as pd
import sqlalchemy
import sys

logger = logging.getLogger(__name__)

DB_NAME = "postgres"
DB_SCHEMA = "public"
DB_TABLE_NAME = "user_experiment_stats"


class EtlProcess(Process):
    def __init__(
        self,
        data_folder: str,
        experiments_filename: str,
        compounds_filename: str,
        users_filename: str,
        db_hostname: str = "user-experiment-stats",
        db_port_num: int = 5432,
        db_username: str = "postgres",
        db_password: str = "password",
    ) -> None:
        """Initialize this procees. Call start() to start it.

        Args:
            data_folder (str): Path to directory in which to find the following CSV files.
            experiments_filename (str): Name of CSV file in data_folder following the example schema for user_experiments.csv
            compounds_filename (str): Name of CSV file in data_folder following the example schema for compounds.csv
            users_filename (str): Name of CSV file in data_folder following the example schema for users.csv
            db_hostname (str, optional): Hostname (or IP address) of postgres host. Defaults to "user-experiment-stats".
            db_port_num (int, optional): postgres port numner. Defaults to 5432.
            db_username (str, optional): postgres username. Defaults to "postgres".
            db_password (str, optional): postgres password. Defaults to "password".
        """
        # Set daemon=True so that the parent process will terminate this process when it exits,
        # rather than waiting for this process to finish
        super().__init__(daemon=True)
        self._data_folder = data_folder
        logger.info(f"Initialized with data folder: {data_folder}")
        self._experiments_file = open(
            os.path.join(self._data_folder, experiments_filename), "r"
        )
        self._compounds_file = open(
            os.path.join(self._data_folder, compounds_filename), "r"
        )
        self._users_file = open(os.path.join(self._data_folder, users_filename), "r")

        self._sql_engine = sqlalchemy.create_engine(
            f"postgresql+psycopg2://{db_username}:{db_password}@{db_hostname}:{db_port_num}/{DB_NAME}",
        )

    def run(self) -> None:
        """
        Overrides Process.run().  Runs the ETL steps.
        """
        self._extract_from_files()  # Extract
        self._compute_statistics()  # Transform
        self._load_into_database()  # Load

    def _extract_from_files(self) -> None:
        """
        Load all CSV files into pandas dataframes.
        """

        # Note: I implemented a full load of each file into RAM prior to processing.
        # This was easier to implement, but will not extend well to very large data files.
        # To support very large files, we'd want to do a couple things differently:
        # - Load and process the files in chunks, so that input files can be larger than the RAM of the current machine.
        # - Update the statistics as each line is processed.  Every statistic required by the assignment can be updated
        #    with each new row - none of them need the entire table to be in RAM to compute them.
        # - Some kind of job status table with progress and possibly cancellation would be nice.  The API could
        #    return some kind of job ID when it kicks off this process, then the frontend could poll for status.
        #    Perhaps the job could be cancelled by another API call by its ID.

        # In a production setting, we would want to validate at least the following:
        # - Make sure the column labels are what we expect
        # - Make sure that the data is valid, or at least of a valid type
        # - Gracefully handle gaps in the data, such as by skipping lines without all fields valid, or by providing some default values.

        logger.info(f"Loading user experiments data file ...")
        self._experiments = pd.read_csv(
            self._experiments_file,
            sep=",[\t ]*",
            engine="python",
            # index_col="experiment_id", # Keep this a normal column so we can select it after the explode
        )
        logger.info(f"Done, loaded {len(self._experiments)} rows.")
        # Parse semicolon-delimited column into a list format
        self._experiments["experiment_compound_ids"] = self._experiments[
            "experiment_compound_ids"
        ].apply(lambda cell: cell.split(";"))

        logger.info(f"Loading compounds data file...")
        self._compounds = pd.read_csv(
            self._compounds_file,
            sep=",[\t ]*",
            engine="python",
            index_col="compound_id",
        )
        logger.info(f"Done, loaded {len(self._compounds)} rows.")
        logger.info(f"Loading users data file...")
        self._users = pd.read_csv(
            self._users_file,
            sep=",[\t ]*",
            engine="python",
            index_col="user_id",
        )
        logger.info(f"Done, loaded {len(self._users)} rows.")

    def _compute_statistics(self) -> None:
        """
        Compute statistics on loaded pandas dataframes.
        """
        logger.info("Computing statistics")
        experiment_stats_per_user_id = self._experiments.groupby("user_id").agg(
            total_experiment_count=("experiment_run_time", "count"),
            mean_experiment_duration=("experiment_run_time", "mean"),
        )
        logger.info(
            f"Have experiment stats for {len(experiment_stats_per_user_id)} users"
        )
        logger.debug(experiment_stats_per_user_id)

        # Split each list of compounds into multiple rows
        experiment_compounds = self._experiments.explode(
            "experiment_compound_ids"
        ).rename(columns={"experiment_compound_ids": "experiment_compound_id"})[
            ["experiment_id", "experiment_compound_id", "user_id"]
        ]
        compounds_used = experiment_compounds.groupby(
            ["user_id", "experiment_compound_id"]
        ).agg(experiments_using_compound=("experiment_id", "count"))
        users_most_experimented_compound = compounds_used.groupby("user_id").agg(
            favorite_compound=("experiments_using_compound", "max")
        )
        logger.info(
            f"Have compound stats for {len(users_most_experimented_compound)} users"
        )
        logger.debug(users_most_experimented_compound)
        self._user_stats = (
            experiment_stats_per_user_id.join(
                users_most_experimented_compound, how="inner"
            )
            .join(self._users)
            .join(self._compounds, on="favorite_compound")
        )
        logger.info(f"Collated stats for {len(self._user_stats)} users")
        logger.debug(self._user_stats)

    def _load_into_database(self) -> None:
        """
        Load computed statistics into the indicated postgres database.
        """
        logger.info(f"Writing {len(self._user_stats)} rows to DB.")
        # I've chosen to drop all extant data prior to adding the new data.
        # In a real system, this behavior might want to be different, based on requirements - maybe we'd want
        # to update historically-kept statistics with new information.
        self._user_stats.to_sql(
            DB_TABLE_NAME, self._sql_engine, schema=DB_SCHEMA, if_exists="replace"
        )
        logger.info(f"Succeeded.")


if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(module)s:  %(message)s",
    )

    etl_proc = EtlProcess(
        "./data/", "user_experiments.csv", "compounds.csv", "users.csv"
    )
    etl_proc.start()
    logger.info("Started")
    etl_proc.join()  # Ignore the daemon behavior and wait for it to be done
    logger.info("Exiting main")

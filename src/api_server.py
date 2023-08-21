from etl_process import EtlProcess
from flask import Flask, request
import logging
import os
import sys

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variable names
ROOT_DATA_PATH_ENV = "ROOT_DATA_PATH"
DB_HOSTNAME_ENV = "DB_HOSTNAME"
DB_PORT_NUM_ENV = "DB_PORT_NUM"
DB_USERNAME_ENV = "DB_USERNAME"
DB_PASSWORD_ENV = "DB_PASSWORD"

# Keys for submitted form values
USER_EXP_FN_KEY = "userExperiments"
USERS_FN_KEY = "users"
COMPOUNDS_FN_KEY = "compounds"


@app.route("/start_etl", methods=["POST"])
def start_etl():
    """
    Start an ETL process.

    Returns:
        dict: Response to serialize to JSON, of the form {"success":bool, "message": str}
    """
    # Supply no defaults so that the exception will explain the required variables
    db_hostname = os.environ[DB_HOSTNAME_ENV]
    db_port_num = int(os.environ[DB_PORT_NUM_ENV])
    db_user_name = os.environ[DB_USERNAME_ENV]
    db_password = os.environ[DB_PASSWORD_ENV]
    root_data_path = os.environ[ROOT_DATA_PATH_ENV]

    if request.method == "POST":
        if (
            USER_EXP_FN_KEY in request.form
            and USERS_FN_KEY in request.form
            and COMPOUNDS_FN_KEY in request.form
        ):
            try:
                EtlProcess(
                    root_data_path,
                    request.form[USER_EXP_FN_KEY],
                    request.form[COMPOUNDS_FN_KEY],
                    request.form[USERS_FN_KEY],
                    db_hostname,
                    db_port_num,
                    db_user_name,
                    db_password,
                ).start()
                return {"success": True, "message": "Started ETL job"}
            except FileNotFoundError as err:
                # In a production context it could be poor security practice to reveal a file path by returning the error directly
                return {"success": True, "message": f"Failed to open a file: {err}"}
            except Exception as err:
                # In a production context returning the error directly may reveal too much information
                return {"success": True, "message": f"Failure: {err}"}
        else:
            return {
                "success": False,
                "message": f"Need string values for the all following keys in the submitted POST form data: {','.join([USER_EXP_FN_KEY,USERS_FN_KEY, COMPOUNDS_FN_KEY])}",
            }
    else:
        return {"success": False, "message": "Use POST"}


if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(module)s:  %(message)s",
    )
    # Note: a production environment should use:
    # - a WSGI server
    # - HTTPS
    # - authentication
    app.run(host="0.0.0.0")

# Eikon backend takehome assignment

I'm John Walthour, and this is my submission for the backend developer position.  Please don't hesitate to reach out with any questions at john.walthour at gmail.com.

## Building
To build:
* Install all the following prerequisites.  I've listed the CLI commands as they will be called; their package names will vary depending on your package manager.
    * `git`
    * `docker`
    * `docker-compose`
    * `psql`
    * `curl`
* If you are using Amazon Linux 2, this is the sequence of commands to install these prerequisites:
```
sudo amazon-linux-extras enable postgresql14
sudo yum clean metadata
sudo yum install -y git docker postgresql
sudo systemctl start docker
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /bin/docker-compose
```
* Clone this repository and `cd` into it.
```
git clone https://github.com/jwalthour/eikon_backend_takehome.git
cd eikon_backend_takehome/
```
* Run `sudo ./build.sh` (`sudo` may or may not be required depending on your docker permissions)

## Running
To start the service, run `sudo ./run_etl_service.sh` (`sudo` may or may not be required depending on your docker permissions).  This will start both the ETL service, and a postgreSQL database to support it.

If you wish to run just the ETL service, and connect it to your own postgres instance, please either edit `compose.yaml` or consult `./run_etl_service.sh` for an example command that
configures the ETL service appropriately.

## Using
To start an ETL job, either run `./start_etl_process.sh`.  This file is just one `curl` command, so you can also run it in another client if you prefer.

To see the results of theh ETL job, run `./query_db_for_results.sh`.  Alternatively, connect to the postgreSQL instance and run `select * from user_experiment_stats;`.


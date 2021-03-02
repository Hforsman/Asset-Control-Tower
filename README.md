# Asset Control Tower
This project is my attempt at creating a viable solution for the CarNext case. 

## What does it do?
It is a data pipeline that downloads files from a pre-specified location and unzips these files.
The unzipped files are stored on disk. The second step is to load in these csv files, 
perform preprocessing to fit the data into the database.
After the data is stored, a series of data manipulation queries sanitize the cars' build year and
perform feature normalization on the amount damage column. The normalized damage is stored in a
separate column.

All data manipulation queries are implemented in sqlalchemy to make the python code as database agnostic as possible.

The database is a MySQL database running in a Docker container. The python script can be run both locally
and in its own Docker.

## Tech used
- Make
- Docker
- Python3.8

## How to use
### How to start
After you cloned the repo, you can just call 

    make first_run

This will (in order) 
- create a Python3 virtualenv
- pull the latest MySQL docker from dockerhub
- create a custom Docker network
- launch a MySQL container attached to the custom network
- build a Python3.8 image with all python files, requirements file and Makefile
- run a Python3.8 container that executes main.py

Creating the virtualenv is not really necessary in this step, but it allows you to more easily run the code locally.
If you rather run the python file locally, just edit the make command and remove `python_docker_run` from the end.

### Removing the mysql container to start fresh
Run 

    make remove_container_db

This will stop and remove the database container. To start a fresh one simply run:

    make create_database

## Next steps
This project can obviously use more work to make it better. Here is just some stuff from the top of my head:
- More streamlined data flow: The implemented data flow just loads everything at once. Handling one file at a time 
would be nice, then more files might be added, or even one entry at a time to prepare for streaming.
- Deduplication in the database itself: This is now performed in-memory using pandas. It works. The reason for this 
approach was the really slow performance of `session.merge()` where the deduplication is handled by the database on insert.
- More checks on the downloaded files to make sure they are compatible both for file type and content.
- A data dictionary to sanitize both the _make_ and _model_ fields. These can contain the same data; just have the model;
or have the model including subtypes like engine and wheel size. Between countries there are also a lot of differences for
  the same type (i.e. Series 3 / 3 series / 320i).
- A nice, general way to fix data where the csv reader decided to split it up into more fields than the standard 36.
- For production purposes the username and password need to stored and accessed securely.
- More subtlety in checking if the database is initialized.
- Add a different database docker as back-end to test if the data wrangling is actually database agnostic.
# Bitbucket Deployment Environment Copier

Script to copy one Deployment Environment to an empty one.
Both Source and Destination environments must exist before running this script.
There does not seem to be a way to create environemts from the api.
Any secured variable will be created as secured in the destination, with the value of "none", and must be changed before use.

## Requirements

-   Python 3.8 or higher
-   atlassian-python-api

## Installation

Clone the repository to your desired location. Then, make the directory a Python vm

`python3 -m venv bitbucket_copy_env`

Change directory into the repo directory, and enable the vm

`cd bitbucket_copy_env
 source bin/activate`

Then install python requirements with:

`pip install -r requirements.txt`

## Usage

```
usage: BitbucketCopyEnv.py [-h] -u USERNAME -p PASSWORD --workspace WORKSPACE -r REPOSITORY -s SOURCE -d DEST

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Bitbucket Username
  -p PASSWORD, --password PASSWORD
                        Bitbucket Password
  --workspace WORKSPACE
                        Bitbucket workspace containing the Repository
  -r REPOSITORY, --repository REPOSITORY
                        Name of Repository
  -s SOURCE, --source SOURCE
                        Source Deployment Environment
  -d DEST, --dest DEST  Destination Deployment Environment
```

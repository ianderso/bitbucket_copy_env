# Bitbucket Repository Cloner

This script has several functions

1. Create a new repository in a given workspace.
2. Enable pipelines on the new repository
3. Copy Deployment environments from one repo to another
4. Copy Repository Variables from one repository to another
5. Clone a specific Deployment Environment withing the same repository

When setting up a new repository, this script can be used to grab all of the deployment environments, and repository variables
from one repo and create them in another. In this use, specify the source and dest repositories, and NOT the environments.

If a source environment is specified, The script will clone a single Deployment Environment, potentially from one repository to another.

When adding a new environment in an existing repo, this script can be used to clone a Deployment Environment, saving
time to do it manually. In this use, specify source repository, and source and destination environments.

It is possible to use this script to clone from one workspace to another as well if needed.

## Requirements

-   Python 3.8 or higher
-   atlassian-python-api
-   requests

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
usage: BitbucketDuplicateRepoConfig.py [-h] -u USERNAME -p PASSWORD --source_workspace SOURCE_WORKSPACE [--dest_workspace DEST_WORKSPACE] --source_repository
                                       SOURCE_REPOSITORY [--dest_repository DEST_REPOSITORY] [--source_env SOURCE_ENV] [--dest_env DEST_ENV]

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Bitbucket Username
  -p PASSWORD, --password PASSWORD
                        Bitbucket Password
  --source_workspace SOURCE_WORKSPACE
                        Bitbucket workspace containing the Source Repository
  --dest_workspace DEST_WORKSPACE
                        Optionally specify a Bitbucket workspace containing the Destination Repository, if none is given, the Source Workspace will be used
  --source_repository SOURCE_REPOSITORY
                        Name of Source Repository
  --dest_repository DEST_REPOSITORY
                        Name of Destination Repository
  --source_env SOURCE_ENV
                        Source Deployment Environment. leave off is copying all
  --dest_env DEST_ENV   Destination Deployment Environment. leave off is copying all
```

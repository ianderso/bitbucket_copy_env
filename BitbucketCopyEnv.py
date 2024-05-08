"""
Script to copy one Deployment Environment to an empty one.
Both Source and Destination environments must exist before running this script.
There does not seem to be a way to create environemts from the api.
Any secured variable will be created as secured in the destination, with the value of "none", and must be changed before use.

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
"""

from argparse import ArgumentParser
from atlassian.bitbucket import Cloud


def get_clone_url(repository, clone_type="https"):
    links = repository.get_data("links")
    for link in links["clone"]:
        if clone_type == link["name"]:
            return link["href"]


def get_repository(cloud, workspace, repository_slug):
    return cloud.workspaces.get(workspace).repositories.get(repository_slug)


def get_deployment_environment(repository, deploy_name):
    for deploy in repository.deployment_environments.each():
        if deploy.name == deploy_name:
            return deploy


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--username", help="Bitbucket Username", required=True)
    parser.add_argument("-p", "--password", help="Bitbucket Password", required=True)
    parser.add_argument(
        "--workspace",
        help="Bitbucket workspace containing the Repository",
        required=True,
    )
    parser.add_argument("-r", "--repository", help="Name of Repository", required=True)
    parser.add_argument(
        "-s", "--source", help="Source Deployment Environment", required=True
    )
    parser.add_argument(
        "-d", "--dest", help="Destination Deployment Environment", required=True
    )
    args = parser.parse_args()

    cloud = Cloud(username=args.username, password=args.password)

    repository = get_repository(cloud, args.workspace, args.repository)

    source_deploy = get_deployment_environment(repository, args.source)
    dest_deploy = get_deployment_environment(repository, args.dest)

    for var in source_deploy.deployment_environment_variables.each():
        if var.value:
            dest_deploy.deployment_environment_variables.create(
                var.key, var.value, False
            )
        else:
            dest_deploy.deployment_environment_variables.create(var.key, "none", True)

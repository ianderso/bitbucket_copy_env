"""
Script to copy one Deployment Environment to an empty one.
If either source or destination are missing, they will be created
Any secured variable will be created as secured in the destination, with the value of "none", and must be changed before use.

usage: BitbucketCopyEnv.py [-h] -u USERNAME -p PASSWORD --workspace WORKSPACE -r REPOSITORY -s SOURCE -d DEST [--env_type {Test,Staging,Production}]

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
  --env_type {Test,Staging,Production}
                        Type of any created deploy environments
"""

from argparse import ArgumentParser
from atlassian.bitbucket import Cloud
from json import dumps, loads
from requests.auth import HTTPBasicAuth
from requests import post


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


def create_deployment_environment(repository, username, password, env_name, env_type):
    basic = HTTPBasicAuth(username, password)
    base_url = repository.get_link("self")
    url = f"{base_url}/environments"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {username}:{password}",
    }

    payload_dict = {
        "type": "deployment_environment",
        "name": env_name,
        "rank": 0,
        "environment_type": {
            "name": env_type,
            "rank": 0,
            "type": "deployment_environment_type",
        },
    }

    response = post(url, data=dumps(payload_dict), headers=headers, auth=basic)
    uuid = loads(response.text)["uuid"]

    return repository.deployment_environments.get(uuid)


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
    parser.add_argument(
        "--env_type",
        help="Type of any created deploy environments",
        choices=["Test", "Staging", "Production"],
        default="Test",
    )
    args = parser.parse_args()

    cloud = Cloud(username=args.username, password=args.password)
    repository = get_repository(cloud, args.workspace, args.repository)

    source_deploy = get_deployment_environment(repository, args.source)
    if not source_deploy:
        source_deploy = create_deployment_environment(
            repository, args.username, args.password, args.source, args.env_type
        )

    dest_deploy = get_deployment_environment(repository, args.dest)
    if not dest_deploy:
        dest_deploy = create_deployment_environment(
            repository, args.username, args.password, args.dest, args.env_type
        )

    dest_vars = dest_deploy.deployment_environment_variables.each()

    for var in source_deploy.deployment_environment_variables.each():
        dvar = False
        for dest_var in dest_vars:
            if var.key == dest_var.key:
                dvar = dest_var

        if dvar:
            dvar.update(value=var.value)
        else:
            if var.value:
                dest_deploy.deployment_environment_variables.create(
                    var.key, var.value, False
                )
            else:
                dest_deploy.deployment_environment_variables.create(
                    var.key, "none", True
                )

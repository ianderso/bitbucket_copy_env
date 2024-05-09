"""
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
"""

from argparse import ArgumentParser
from atlassian.bitbucket import Cloud
from json import dumps, loads
from requests.auth import HTTPBasicAuth
from requests import post, put
from requests import exceptions


def get_clone_url(repository, clone_type="https"):
    links = repository.get_data("links")
    for link in links["clone"]:
        if clone_type == link["name"]:
            return link["href"]


def get_repository(cloud, workspace, repository_slug):
    try:
        return cloud.workspaces.get(workspace).repositories.get(repository_slug)
    except exceptions.HTTPError as e:
        if "You may not have access to this repository" in str(e):
            return False


def create_repository(
    cloud,
    workspace,
    repository_slug,
    project_key=None,
    is_private=True,
    fork_policy=None,
):
    return cloud.workspaces.get(workspace).repositories.create(
        repository_slug, project_key, is_private, fork_policy
    )


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


def enable_pipelines(repository, username, password):
    basic = HTTPBasicAuth(username, password)
    base_url = repository.get_link("self")
    url = f"{base_url}/pipelines_config"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {username}:{password}",
    }

    payload_dict = {
        "enabled": True,
    }

    response = put(url, data=dumps(payload_dict), headers=headers, auth=basic)

    return response


def copy_deployment_environment(
    username,
    password,
    source_repository,
    dest_repository,
    source_env_slug,
    dest_env_slug,
):
    source_deploy = get_deployment_environment(source_repository, source_env_slug)
    if not source_deploy:
        source_deploy = create_deployment_environment(
            source_repository,
            username,
            password,
            source_env_slug,
            "Test",
        )

    dest_deploy = get_deployment_environment(dest_repository, dest_env_slug)
    if not dest_deploy:
        dest_deploy = create_deployment_environment(
            dest_repository,
            username,
            password,
            dest_env_slug,
            source_deploy.environment_type["name"],
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


def copy_repository_variables(
    source_repository,
    dest_repository,
):

    dest_vars = dest_repository.repository_variables.each()

    for var in source_repository.repository_variables.each():
        dvar = False
        for dest_var in dest_vars:
            if var.key == dest_var.key:
                dvar = dest_var

        if dvar:
            dvar.update(value=var.value)
        else:
            if var.value:
                dest_repository.repository_variables.create(var.key, var.value, False)
            else:
                dest_repository.repository_variables.create(var.key, "none", True)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--username", help="Bitbucket Username", required=True)
    parser.add_argument("-p", "--password", help="Bitbucket Password", required=True)
    parser.add_argument(
        "--source_workspace",
        help="Bitbucket workspace containing the Source Repository",
        required=True,
    )
    parser.add_argument(
        "--dest_workspace",
        help="Optionally specify a Bitbucket workspace containing the Destination Repository, if none is given, the Source Workspace will be used",
        default=False,
    )
    parser.add_argument(
        "--source_repository", help="Name of Source Repository", required=True
    )
    parser.add_argument(
        "--dest_repository", help="Name of Destination Repository", default=False
    )
    parser.add_argument(
        "--source_env",
        help="Source Deployment Environment. leave off is copying all",
        default=False,
    )
    parser.add_argument(
        "--dest_env",
        help="Destination Deployment Environment. leave off is copying all",
    )

    args = parser.parse_args()

    if not args.dest_workspace:
        args.dest_workspace = args.source_workspace

    if not args.dest_repository:
        args.dest_repository = args.source_repository

    cloud = Cloud(username=args.username, password=args.password)

    source_repository = get_repository(
        cloud, args.source_workspace, args.source_repository
    )
    if not source_repository:
        source_repository = create_repository(
            cloud, args.source_workspace, args.source_repository
        )
    dest_repository = get_repository(cloud, args.dest_workspace, args.dest_repository)
    if not dest_repository:
        dest_repository = create_repository(
            cloud, args.dest_workspace, args.dest_repository
        )

    if args.source_env:
        copy_deployment_environment(
            args.username,
            args.password,
            source_repository,
            dest_repository,
            args.source_env,
            args.dest_env,
        )
    else:
        for deploy in source_repository.deployment_environments.each():
            copy_deployment_environment(
                args.username,
                args.password,
                source_repository,
                dest_repository,
                deploy.name,
                deploy.name,
            )

    if args.source_repository != args.dest_repository:
        enable_pipelines(dest_repository, args.username, args.password)
        copy_repository_variables(
            source_repository,
            dest_repository,
        )

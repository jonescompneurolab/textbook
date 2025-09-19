import sys

from scripts.logger_setup import setup_logger


def check_version(enable_debug=True):
    """
    Return True if all notebooks are run on the same version of hnn_core,
    else False

    This function performs the following steps:
    1. Get notebooks to skip from 'notebooks_to_skip.json'.
    2. Get the json output files for notebooks and extract the version used
       to run the notebook
    3. Get the latest version of hnn-core from pypi
    4. Check if all notebooks are run on the same version of hnn-core
        - If not, warn user
    5. If yes, compare the version used for execution with the latest version from pypi
        - If not, warn user
    7. Print all notebooks and versions used for execution in the format:
        {
            'plot_simulate_evoked.json': {'hnn_version': '0.4.2'},
            'plot_simulate_gamma.json': {'hnn_version': '0.4.1'},
            ...
        }

    Inputs
    ------
    debug : bool
        If True, enables debug logging to print verbose information about
        the process

    Returns
    -------
    bool
        True if all executed notebooks were run with the latest
        version of hnn-core, else False
    """

    logger = setup_logger(__name__, enable_debug=enable_debug)

    logger.debug(
        'DEV',
    )
    import json
    import os

    import requests

    with open(
        os.path.join(
            "scripts",
            "notebook_hashes.json",
        ),
        "r",
    ) as f:
        notebook_hashes = json.load(f)

    with open(
        os.path.join(
            "scripts",
            "notebooks_to_skip.json",
        ),
        "r",
    ) as f:
        notebooks_to_skip = json.load(f)

    # get names of notebooks to skip
    notebooks_to_skip = notebooks_to_skip["skip_execution"]
    logger.debug(
        '\n',
        'Notebooks to skip:\n',
        notebooks_to_skip,
    )

    # get json filenames for executed notebooks only
    json_fnames = [
        notebook.replace(".ipynb", ".json")
        for notebook in notebook_hashes.keys()
        if notebook not in notebooks_to_skip
    ]
    logger.debug(
        '\n',
        'Notebooks to run:\n',
        json_fnames,
    )

    # get filepaths for each filename in json_fnames
    json_fpaths = []
    for root, dirs, files in os.walk(
        os.path.join(
            os.getcwd(),
            "content",
        )
    ):
        for file in files:
            if file in json_fnames:
                json_fpaths.append(os.path.join(root, file))

    # get the value of the "hnn_version" key from each json
    notebook_versions = []
    execution_statuses = dict()
    for file in json_fpaths:
        file_key = file.split(os.sep)[-1]
        if file_key not in execution_statuses.keys():
            execution_statuses[file_key] = dict()
        with open(file, "r") as f:
            contents = json.load(f)
            if "hnn_version" in contents:
                notebook_versions.append(contents["hnn_version"])
                execution_statuses[file_key]['hnn_version'] = contents["hnn_version"]
            else:
                print(f"Version key not found in {file}")
            # if "master_commit" in contents:
                # execution_statuses[file]['master_commit'] =

    # unique versions for executed notebooks
    notebook_versions = list(set(notebook_versions))

    resp = requests.get("https://pypi.org/pypi/hnn-core/json")
    latest = resp.json()["info"]["version"]

    if len(notebook_versions) != 1:
        latest_version_check = False

    else:
        latest_version_check = notebook_versions[0] == latest

    if latest_version_check:
        print(
            f"All notebooks were executed with the latest hnn-core=={latest}",
        )
    else:
        print(
            f"\nLatest version of hnn-core: {latest}",
            f"\nVersions of hnn-core used in executed notebooks: {notebook_versions}",
            "Notebooks should be re-executed using the latest version",
        )

    logger.debug(
        '\nExecution statuses:',
        '\n',
        execution_statuses
    )

    print(
        '\nReturn:'
    )
    return latest_version_check


if __name__ == "__main__":
    # return 0 to indicate success if True
    # return 1 to indicate failure if False
    sys.exit(
        0 if check_version() else 1,
    )

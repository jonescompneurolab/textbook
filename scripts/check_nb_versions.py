import json
from pathlib import Path
import requests
import sys

sys.path.insert(
    0,
    str(Path(__file__).parent),
)

from logger_setup import setup_logger

textbook_root_path = Path(__file__).parents[1]


# AES TODO: This output probably shouldn't be set to "debug" specifically as opposed to
# expected output, but that should be fixed only after logging in general is better
# integrated with the code.


def check_version(enable_debug=False, root_path=None):
    """
    Return True if all notebooks are run on the same version of hnn_core,
    else False

    This function performs the following steps:
    1. Get notebooks to skip from 'nbs_to_skip.json'.
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
    enable_debug : bool
        If True, enables debug logging to print verbose information about
        the process
    root_path : pathlib.Path, optional
        Path of the "root" directory of the textbook (i.e. the directory containing
        "content", "scripts", etc.), if you want to use a different root.

    Returns
    -------
    bool
        True if all executed notebooks were run with the latest
        version of hnn-core, else False
    """

    if not root_path:
        root_path = textbook_root_path

    logger = setup_logger(
        __name__,
        enable_debug=enable_debug,
    )

    logger.debug(
        "Debugging check_nb_versions.check_version",
    )
    nb_hashes_path = root_path / "scripts" / "nb_hashes.json"
    with open(
        nb_hashes_path,
        "r",
    ) as f:
        nb_hashes = json.load(f)

    nb_skips_path = root_path / "scripts" / "nbs_to_skip.json"
    with open(
        nb_skips_path,
        "r",
    ) as f:
        nbs_to_skip = json.load(f)

    # get names of nbs to skip
    # Since this script is only run in the stable build, we only need to skip the
    # appopriate notebooks.
    nbs_to_skip = nbs_to_skip["skip_if_stable"]
    logger.debug(
        "\n",
        "Notebooks to skip:\n",
        nbs_to_skip,
    )

    # get json filenames for executed nbs only
    # Using JSON outputs since IPYNBs are harder to navigate
    json_fnames = [
        nb.replace(".ipynb", ".json")
        for nb in nb_hashes.keys()
        if nb not in nbs_to_skip
    ]
    logger.debug(
        "\n",
        "Notebooks to run:\n",
        json_fnames,
    )

    # get filepaths for each filename in json_fnames
    json_fpaths = []
    for root, dirs, files in (root_path / "content").walk():
        for file in files:
            if file in json_fnames:
                json_fpaths.append(root / file)

    # get the value of the "hnn_version" key from each json
    nb_versions = []
    execution_statuses = dict()
    for json_fpath in json_fpaths:
        filename = json_fpath.name
        if filename not in execution_statuses.keys():
            execution_statuses[filename] = dict()
        with open(json_fpath, "r") as f:
            contents = json.load(f)
            if "hnn_version" in contents:
                nb_versions.append(contents["hnn_version"])
                execution_statuses[filename]["hnn_version"] = contents["hnn_version"]
            else:
                print(f"Version key not found in {json_fpath}")
            # if "master_commit" in contents:
            # execution_statuses[json_fpath]['master_commit'] =

    # unique versions for executed nbs
    nb_versions = list(set(nb_versions))

    resp = requests.get("https://pypi.org/pypi/hnn-core/json")
    latest = resp.json()["info"]["version"]

    if len(nb_versions) != 1:
        latest_version_check_success = False

    else:
        latest_version_check_success = nb_versions[0] == latest

    if latest_version_check_success:
        print(f"All notebooks were executed with the latest hnn-core=={latest}")
    else:
        print(
            f"\nLatest version of hnn-core: {latest}",
            f"\nVersions of hnn-core used in executed notebooks: {nb_versions}",
            "\nERROR: Notebooks should be re-executed using the latest version",
            f"\n\nfExecution statuses:\n{execution_statuses}",
        )

    logger.debug(
        "\nExecution statuses:",
        "\n",
        execution_statuses,
    )

    return latest_version_check_success


if __name__ == "__main__":
    version_check_success = check_version()

    # Need to convert version check to int to use as exit code. In Python, True = 1 and
    # False = 0, so we need to reverse the boolean value to get the correct exit code (0
    # for success, 1 for failure).
    print("\nReturn:")
    if version_check_success:
        print("Success!")
        status = 0  #  exit code 0 for success
    else:
        print("ERROR: 'check_nb_versions.py' Failed, please investigate")
        status = 1  # exit code 1 for failure

    sys.exit(status)

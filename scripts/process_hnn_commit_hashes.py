import subprocess
import requests

from hnn_core import __version__ as installed_version


def get_hnn_commit_hash():
    """Retrieve the installed hnn-core version and commit hash.

    Returns
    -------
    str
        The commit hash of hnn-core is installed, if hnn-core is installed from
        source. Otherwise, the current version of hnn-core that is installed
    """
    try:
        installed_commit = subprocess.check_output(["pip", "freeze"], text=True)
        for line in installed_commit.splitlines():
            if "hnn" in line:
                if "@" in line:
                    installed_commit = line.split("@")[2].split("#")[0]
                else:
                    installed_commit = line.split("hnn-core==")[-1]
        print(
            "Configuration: The installed version of hnn-core is:\n"
            f"    {installed_version}"
            "\nConfiguration: The installed commit (or version if not installed from "
            "source) of hnn-core is:\n"
            f"    {installed_commit}\n"
        )
    except Exception as e:
        raise RuntimeError(
            f"Could not import hnn_core and retrieve the installed commit:\n{e}"
        )
    return installed_commit


def validate_hnn_versions(
    installed_commit,
    code_version,
    custom_owner_commit=None,
):
    """Validate the installed hnn-core version/hash against 'code-version' options.

    This function verifies that the installed hnn-core version/commit matches the
    requested version/commit for building the textbook (unless `code_version` is set to
    'no-check'), then returns the appropriate commit hash to use for documentation
    links. The function requires internet access to query PyPI and/or GitHub APIs
    (unless `code_version` is set to 'no-check').

    Parameters
    ----------
    installed_commit : str
        The commit hash of hnn-core is installed, if hnn-core is installed from
        source. Otherwise, the current version of hnn-core that is installed
    code_version : str
        The desired hnn-core version to use and validate against. See 'python build.py
        --help' with the '--code-version' CLI argument for more details. Must be one of:
        - 'stable': Latest stable release from PyPI
        - 'master': Latest commit from the master branch
        - 'custom': Custom repository owner and commit hash
    custom_owner_commit : str, optional
        Required when code_version='custom'. Format: '<owner>:<commit-hash>'
        Example: 'asoplata:92b000c' to retrieve the commit for
        https://github.com/asoplata/hnn-core/commit/92b000c597052a661d9e177b8754695446336b96

    Returns
    -------
    str or None
        The commit hash of the hnn_core code version to use for either new execution or
        comparison with the old execution history. None if doing a 'stable' build (since
        stable releases don't require commit hashes), otherwise (i.e. 'dev' build) is
        the full commit SHA.
    """
    # 'stable' version checks
    # ----------------------------------------------------------------------------------
    if code_version == "stable":
        # We don't need the commit hash if simply using the latest stable. Any executed notebook
        # output will not show a commit hash version for what was last used for execution. The hash
        # being None indicates a stable build.
        hnn_commit_hash = None

        # Lookup online the latest stable version
        latest_stable_version = requests.get(
            "https://pypi.org/pypi/hnn-core/json"
        ).json()["info"]["version"]

        # "stable" case version validation
        if installed_version > latest_stable_version:
            raise RuntimeError(
                "Your installed version of hnn-core is ahead of the "
                "latest stable version:"
                f"\n   Latest stable version: {latest_stable_version}"
                f"\n   Installed version:     {installed_version}"
                "\nIf you want to generate the textbook website using a version of "
                "hnn-core that is newer than the latest stable version, you must "
                "provide a different argument to '--code-version'. "
                "See 'build.py --help' for more details."
            )
        elif installed_version != latest_stable_version:
            raise RuntimeError(
                "Your installed version of hnn-core does not match the latest stable "
                "version, and is probably out of date: "
                f"\n   Latest stable version: {latest_stable_version}"
                f"\n   Installed version:     {installed_version}"
                "\nIf your installed version is behind the latest stable "
                "version, you can update your local install using: "
                "\n   $ pip install --upgrade 'hnn-core[dev]'"
                "\n\nIf your installed version references a particular commit or "
                "branch (e.g.: hnn-core @ git+https://github.com/jonescompneurolab"
                "/hnn-core.git@1413550b2c610b700b7bb12ce7e1ae408ef8d4d3), "
                "then you need to either change your environment or provide a different "
                "value to the '--code-version' argument of 'build.py'. "
                "See 'build.py --help' for more details."
            )
        elif installed_version == latest_stable_version:
            print(
                "Configuration: Success: Your installed version and the latest stable "
                "version of hnn-core appear to be equivalent: "
                f"\n   Latest stable version: {latest_stable_version}"
                f"\n   Installed version:     {installed_version}"
            )

    # 'master' version checks and commit setting
    # ----------------------------------------------------------------------------------
    elif code_version == "master":
        # Lookup online the latest commit hash from upstream/master
        url = "https://api.github.com/repos/jonescompneurolab/hnn-core/commits/master"
        response = requests.get(url)
        response.raise_for_status()
        latest_master_commit = response.json()["sha"]
        hnn_commit_hash = latest_master_commit

        # "master" case version/commit validation
        if installed_commit != latest_master_commit:
            raise RuntimeError(
                "Your installed commit hash of hnn-core does not match the latest "
                "'master' branch commit hash:"
                f"\n   Latest master commit hash: {latest_master_commit}"
                f"\n   Installed commit hash:     {installed_commit}"
                "To build the textbook website against the latest 'master', you can "
                "create a valid environment by running the following commands in a "
                "terminal:"
                "\n   $ make create-textbook-dev-env"
                "\n   $ conda activate textbook-dev-env"
                "\n   $ pip install --upgrade --force-reinstall --no-cache-dir "
                f'"hnn-core[dev] @ git+https://github.com/jonescompneurolab/hnn-core.git@{latest_master_commit}"'
                "\nSee 'build.py --help' for more details."
            )
        elif installed_commit == latest_master_commit:
            print(
                "Configuration: Success: Your installed commit and the latest master "
                "commit of hnn-core appear to be equivalent: "
                f"\n   Latest master commit hash: {latest_master_commit}"
                f"\n   Installed commit hash:     {installed_commit}"
            )

    # 'custom' version checks and commit setting
    # ----------------------------------------------------------------------------------
    elif code_version == "custom":
        if not custom_owner_commit:
            raise RuntimeError(
                "If you specify '--code-version=custom', you are also required to "
                "specify the combination of repo-owner and commit using the following "
                "format: "
                "\n--custom-owner-commit=<repository-owner>:<commit-hash>"
                "\nFor example, a valid input would be: "
                "\n--custom-owner-commit=asoplata:92b000c "
                "\nwhich would correspond to the commit at "
                "\nhttps://github.com/asoplata/hnn-core/commit/92b000c597052a661d9e177b8754695446336b96 "
                "\nSee 'build.py --help' for more details."
            )

        # "custom" case "<owner>:<commit>" input processing and validation
        owner_hash = custom_owner_commit.strip()
        try:
            owner, provided_commit = owner_hash.split(":")

            url = f"https://api.github.com/repos/{owner}/hnn-core/commits/{provided_commit}"
            response = requests.get(url)
            response.raise_for_status()
            full_provided_commit = response.json()["sha"]
            hnn_commit_hash = full_provided_commit

        except Exception as e:
            raise RuntimeError(
                "You must"
                "specify the combination of repo-owner and commit using the following "
                "format: "
                "\n--custom-owner-commit=<repository-owner>:<commit-hash> "
                "\nFor example, a valid input would be: "
                "\n--custom-owner-commit=asoplata:92b000c "
                "\nwhich would correspond to the commit at "
                "\nhttps://github.com/asoplata/hnn-core/commit/92b000c597052a661d9e177b8754695446336b96 "
                "\nSee 'build.py --help' for more details."
                f"\n\nError message: {e}"
            )

        # "custom" case version/commit validation
        if installed_commit != full_provided_commit:
            raise RuntimeError(
                "Your installed version/commit of hnn-core does not match the custom "
                "repository-owner and commit you specified: "
                f"\n   Provided repository owner: {owner}"
                f"\n   Provided commit hash (full):      {full_provided_commit} "
                f"\n   Installed version or commit hash: {installed_commit}"
                "\nTo build the textbook website against the owner and commit you "
                "provided, you can create a valid environment by running the following "
                "commands in a terminal:"
                "\n   $ make create-textbook-dev-env"
                "\n   $ conda activate textbook-dev-env"
                "\n   $ pip install --upgrade --force-reinstall --no-cache-dir "
                f'"hnn-core[dev] @ git+https://github.com/{owner}/hnn-core.git@{full_provided_commit}"'
                "\nSee 'build.py --help' for more details."
            )
        elif installed_commit == full_provided_commit:
            print(
                "Configuration: Success: Your installed commit and the provided commit "
                "of hnn-core appear to be equivalent: "
                f"\n   Provided commit hash (full):      {full_provided_commit} "
                f"\n   Installed version or commit hash: {installed_commit}"
            )

    # 'no-check' ignore everything and just do whatever
    # ----------------------------------------------------------------------------------
    elif code_version == "no-check":
        hnn_commit_hash = installed_commit
        print(
            "\nConfiguration: Checking of hnn-core version/commit has been disabled for "
            "this build."
        )

    return hnn_commit_hash

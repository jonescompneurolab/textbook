import sys


def check_version():
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

    # get json filenames for executed notebooks only
    json_fnames = [
        notebook.replace(".ipynb", ".json")
        for notebook in notebook_hashes.keys()
        if notebook not in notebooks_to_skip
    ]

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
    for file in json_fpaths:
        with open(file, "r") as f:
            contents = json.load(f)
            if "hnn_version" in contents:
                notebook_versions.append(contents["hnn_version"])
            else:
                print(f"Version key not found in {file}")

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
            f"Latest version of hnn-core: {latest}",
            f"Versions of hnn-core used in executed notebooks: {notebook_versions}",
            "Notebooks should be re-executed using the latest version",
        )

    return latest_version_check


if __name__ == "__main__":
    # return 0 to indicate success if True
    # return 1 to indicate failure if False
    sys.exit(
        0 if check_version() else 1,
    )

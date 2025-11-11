# %%
import base64
import hashlib
import html
import json
import os
from pathlib import Path
import re
import textwrap
import warnings

import nbformat
import pypandoc
from hnn_core import __version__ as hnn_version
from nbconvert.preprocessors import (
    ClearOutputPreprocessor,
    ExecutePreprocessor,
)
from packaging.version import Version


def _convert_html_to_json(
    html: str,
    filename: str,
):
    """
    Convert html into hierarchical json
    """
    # variable for processed json output
    contents = {filename: {}}

    # variable to track section content and metadata
    current_html = list()
    current_title = None
    current_level = None

    # split html into lines while replacing tabs with spaces
    lines = [
        line.replace(
            "\t",
            "    ",
        )
        for line in html.splitlines()
        # if line.strip()
    ]

    for i, line in enumerate(lines):
        # identify lines with header tag
        # note: the match is performed on the line stripped of any
        # spaces or newlines
        line_match = re.match(
            r"(<h[1-6]>)(.*?)(</h[1-6]>)",
            line.strip(),
        )

        if line_match:
            # when a new header is found, save the previous section
            if current_title:
                contents[filename][current_title] = {}
                contents[filename][current_title]["level"] = current_level
                contents[filename][current_title]["html"] = "\n".join(current_html)

            # get the title, level of the new section
            current_level = line_match.group(1).strip()
            current_level = int(current_level.lstrip("<h").rstrip(">"))
            current_title = line_match.group(2).strip()

            # start a new section with the previous line
            current_html = [lines[i - 1]]

        elif current_html is not None:
            # add new html lines
            current_html.append(lines[i - 1])

    # save the last section
    if current_title:
        # append the last line
        current_html.append(line)

        # update contants
        contents[filename][current_title] = {}
        contents[filename][current_title]["level"] = current_level
        contents[filename][current_title]["html"] = "\n".join(current_html)

    return contents


def _extract_html_from_nb(
    nb,
    nb_path,
    nb_json_output_dir,
    dev_build=False,
    use_base64=False,
):
    """
    Extract and convert notebook cells to HTML, including code, outputs, and markdown.

    This function processes all cells in a Jupyter notebook and converts them to
    formatted HTML. Code cells are rendered with their source and outputs (text,
    images, errors). Markdown cells are converted to HTML using PyPandoc. Images from
    notebook outputs are either embedded as Base64 strings or saved as PNG files.

    The function handles:
    - Code cell source formatting
    - Multiple output types (text/plain, stdout, images, errors)
    - Image output processing (Base64 embedding or file saving)
    - Markdown cell conversion with MathML support
    - Proper HTML structure with CSS classes for styling

    Parameters
    ----------
    nb : nbformat.notebooknode.NotebookNode
        The notebook object containing cells to convert
    nb_path : pathlib.Path
        Path to the Jupyter notebook file (.ipynb). Used to determine output file naming
        and location
    nb_json_output_dir : pathlib.Path
        Directory where the notebook's JSON output file is located. This will become the
        parent of the new directory where any images will be stored.
    dev_build : str or bool
        False if not running a dev build. Otherwise, a string containing the repo and
        commit hash to be used for the build.
    use_base64 : bool, optional
        If True, embed images as Base64-encoded strings in the HTML.
        If False, save images as separate PNG files and link to them.
        Default is False

    Returns
    -------
    str
        Complete HTML string containing all converted notebook cells with
        appropriate formatting and styling divs
    """

    html_output = []
    fig_id = 0
    aggregated_output = ""

    img_output_dir = nb_json_output_dir / f"output_nb_{nb_path.stem}"
    img_output_dir.mkdir(parents=True, exist_ok=True)

    # helper for aggregating outputs
    # -----------------------------
    def _aggregate_outputs(
        html_output,
        accumulated_outputs,
    ):
        """
        If there are accumulated outputs, append them to html_output and reset.
        """
        if accumulated_outputs:
            cell_output_html = textwrap.dedent(f"""
                <!-- code cell output -->
                <div class='output-cell'>
                    <div class='output-label'>
                        Out:
                    </div>
                    <div class='output-code'>
                        {accumulated_outputs}
                    </div>
                </div>
            """)
            html_output.append(cell_output_html)
        return ""

    for cell in nb["cells"]:
        # ------------------------------
        # process code cells
        # ------------------------------
        if cell["cell_type"] == "code":
            # ==============================
            # add code cell contents
            # ==============================
            code_cell_html = textwrap.dedent(f"""
                <!-- code cell -->
                <div class='code-cell'>
                    <code class='language-python'>
                        {cell["source"]}
                    </code>
                </div>
            """)
            html_output.append(code_cell_html)

            # ==============================
            # add code cell outputs
            # ==============================
            for output in cell.get("outputs", []):
                # handle plain text outputs
                # ------------------------------
                if "text/plain" in output.get("data", {}):
                    text_output = output["data"]["text/plain"]
                    # escape '<' and '>' characters which can be
                    # incorrectly interpreted as HTML tags
                    escaped_text_output = html.escape(text_output)

                    # aggregate outputs
                    aggregated_output += f"\n\t\t{escaped_text_output}"

                # handle stdout (exclude stderr)
                # ------------------------------
                # e.g., this includes outputs from print statements
                if (
                    output.get("output_type") == "stream"
                    and output.get("name") == "stdout"
                ):
                    stream_output = output.get("text", "")
                    # escape '<' and '>' characters
                    escaped_stream_output = html.escape(stream_output)

                    # aggregate outputs
                    aggregated_output += f"\n\t\t{escaped_stream_output}"

                # handle image outputs (e.g., plots)
                # ------------------------------
                if "image/png" in output.get("data", {}):
                    # before processing the image, append any already-accumulated
                    # outputs to html_output and re-set aggregated_output to ""
                    aggregated_output = _aggregate_outputs(
                        html_output,
                        aggregated_output,
                    )

                    img_data = output["data"]["image/png"]

                    # optional Base64 encoding for image embedding
                    # ------------------------------
                    if use_base64:
                        output_base64_html = textwrap.dedent(f"""
                            <!-- code cell image -->
                            <div class='output-cell'>
                                <img src='data:image/png;base64,{img_data}'/>
                            </div>
                        """)
                        html_output.append(output_base64_html)

                    # standard image processing using saved .png file
                    # ------------------------------
                    else:
                        fig_id += 1
                        img_path = img_output_dir / f"fig_{fig_id:02d}.png"
                        with open(img_path, "wb") as img_file:
                            img_file.write(base64.b64decode(img_data))

                        relative_img_path = img_path.relative_to(img_path.parents[1])
                        output_img_html = textwrap.dedent(f"""
                            <!-- code cell image -->
                            <div class='output-cell'>
                                <img src='{relative_img_path}'/>
                            </div>
                        """)
                        html_output.append(output_img_html)

                # handle errors
                # ------------------------------
                if output.get("output_type") == "error":
                    error_message = "\n".join(
                        output.get(
                            "traceback",
                            [],
                        ),
                    )
                    output_error_html = textwrap.dedent(f"""
                        <!-- code cell error -->
                        <div class='output-cell error'>
                            <pre>
                                {error_message}
                            </pre>
                        </div>
                    """)
                    html_output.append(output_error_html)

            # ==============================
            # accumulate remaining cell outputs
            # ==============================
            # If there are accumulated outputs for the cell that have not
            # yet been added to the html, append the outputs to html_output
            aggregated_output = _aggregate_outputs(
                html_output,
                aggregated_output,
            )

        # ------------------------------
        # process "markdown" cells
        # ------------------------------
        elif cell["cell_type"] == "markdown":
            # escape < and > characters
            markdown_content = html.escape(cell["source"])

            html_content = pypandoc.convert_text(
                markdown_content,
                format="md",
                to="html",
                extra_args=[
                    "--mathml",
                    # the "-f", "markdown-auto_identifiers" arguments below
                    # disable the automatic ids added to header tags
                    "-f",
                    "markdown-auto_identifiers",
                ],
            )
            markdown_html_output = textwrap.dedent(f"""
                <!-- markdown cell -->
                <div class='markdown-cell'>
                    {html_content}
                </div>
            """)
            html_output.append(markdown_html_output)

    html_output = "\n".join(html_output)

    return html_output


def _hash_nb(nb_path):
    """
    Generate a content-based SHA256 hash of a notebook.

    This function creates a deterministic hash of the notebook's source code
    by removing execution outputs, metadata, and execution counts before hashing.
    This ensures that the hash only changes when the actual notebook content
    (code and markdown) changes, not when it is simply re-executed with the
    same code.

    The cleaning process includes:
    - Clearing all cell outputs
    - Removing execution counts from code cells
    - Removing all cell-level metadata
    - Removing all notebook-level metadata

    Parameters
    ----------
    nb_path : str or pathlib.Path
        Path to the Jupyter notebook file (.ipynb) to hash

    Returns
    -------
    str
        A 64-character hexadecimal string representing the SHA256 hash
        of the cleaned notebook content
    """

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # clear all cell outputs
    preprocessor = ClearOutputPreprocessor()
    preprocessor.preprocess(nb, {})

    # remove execution counts and cell metadata
    for cell in nb.cells:
        if "execution_count" in cell:
            cell["execution_count"] = None
        if "metadata" in cell:
            cell["metadata"] = {}

    # remove nb metadata
    nb.metadata = {}

    # serialize cleaned nb
    nb_json = nbformat.writes(nb, version=4).encode("utf-8")

    # generate hash
    hasher = hashlib.sha256()
    hasher.update(nb_json)

    return hasher.hexdigest()


def _load_nb_hashes(nb_hash_path):
    """
    Load previously-recorded notebook content hashes from JSON file.

    This function retrieves the hash dictionary that tracks notebook content changes
    across builds. The hashes are used by the build system to determine which notebooks
    have been modified and need re-execution. Each hash represents the content-only
    state of a notebook (code and markdown cells), excluding execution outputs and
    metadata, as generated by _hash_nb().

    If the hash file does not exist (e.g., first build or after cleaning), an empty
    dictionary is returned, which will cause all notebooks to be treated as new and
    trigger execution according to the execution filter settings.

    Parameters
    ----------
    nb_hash_path : str or pathlib.Path
        Path to the JSON file containing notebook hashes, typically
        'scripts/nb_hashes.json' in the repository root

    Returns
    -------
    dict
        Mapping of notebook filenames (str) to their SHA256 hash values (str).
        Keys are notebook filenames (e.g., "example.ipynb"), values are 64-character
        hexadecimal hash strings. Returns an empty dictionary if the hash file
        does not exist
    """
    # AES if we want to support optional or fresh hash building, we should do it at the
    # CLI in main, not here, but leaving this as-is for now.
    if os.path.exists(nb_hash_path):
        with open(nb_hash_path, "r") as f:
            return json.load(f)
    return {}


def _save_nb_hashes(
    new_hashes,
    nb_hash_path,
):
    """
    Persist updated notebook content hashes to JSON file for tracking changes.

    This function saves a dictionary mapping notebook filenames to their SHA256 content
    hashes. These hashes are used by the build system to determine which notebooks need
    re-execution after their content has changed. The hashes are generated by _hash_nb()
    and track only the code/markdown content (not execution outputs or metadata).

    Parameters
    ----------
    new_hashes : dict
        Mapping of notebook filenames (str) to their SHA256 hash values (str).
        Keys are notebook filenames (e.g., "example.ipynb"), values are 64-character
        hexadecimal hash strings
    nb_hash_path : str or pathlib.Path
        Path to the JSON file where hashes will be saved, typically
        'scripts/nb_hashes.json' in the repository root

    Returns
    -------
    None
        Writes the hash dictionary to disk as formatted JSON with 4-space indentation
    """
    with open(nb_hash_path, "w") as f:
        json.dump(new_hashes, f, indent=4)


def _load_nb(nb_path):
    """
    Load a Jupyter notebook object from a path to a file.

    Parameters
    ----------
    nb_path : str or pathlib.Path
        Path to the Jupyter notebook file (.ipynb) to load

    Returns
    -------
    nbformat.notebooknode.NotebookNode
        The loaded notebook object
    """
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    return nb


def _is_nb_fully_executed(nb):
    """
    Check if a notebook object has been fully executed.

    Parameters
    ----------
    nb : nbformat.notebooknode.NotebookNode
        The notebook object to check for complete execution

    Returns
    -------
    bool
        True if all *non-empty* code cells have been executed (have an execution_count),
        False otherwise.
    """
    for cell in nb.get("cells", []):
        if (
            (cell.get("cell_type") == "code")
            and (cell.get("execution_count") is None)
            and (cell.get("source") != "")
        ):
            return False

    return True


def _read_nb_json_output_metadata(
    nb_path,
    nb_json_output_dir,
):
    """
    Retrieve prior execution metadata from a notebook's JSON output file.

    This function checks for the existence of a notebook's corresponding JSON
    output file and extracts metadata about its previous execution, including
    the commit hash used (for dev builds), execution status, and hnn-core version.

    Parameters
    ----------
    nb_path : pathlib.Path
        Path to the Jupyter notebook file (.ipynb)
    nb_json_output_dir : pathlib.Path
        Directory where the notebook's JSON output file is located

    Returns
    -------
    commit_check : str or bool
        The commit hash from the previous execution if available and the notebook
        was executed. False if the JSON file doesn't exist or doesn't contain
        commit information
    execution_check : bool
        True if the notebook was fully executed in a prior run (all non-empty
        code cells completed execution). False if the JSON file doesn't exist
        or if the prior execution was incomplete
    version_check : str or bool
        The version string of hnn-core used in the previous execution (e.g., "0.4.2").
        False if the JSON file doesn't exist or doesn't contain version
        information. "NA" if the metadata exists, but the notebook has not been run
        successfully since recording versions of last successful execution.
    """

    json_path = nb_json_output_dir / f"{nb_path.stem}.json"

    execution_check = False
    version_check = False
    commit_check = False

    # if the json output exists, get the execution status, base version,
    # and latest commit used to execute the nb
    if json_path.exists():
        with open(json_path, "r") as file:
            nb_outputs = json.load(file)
            execution_check = nb_outputs.get(
                "full_executed",
                False,
            )
            version_check = nb_outputs.get(
                "hnn_version",
                False,
            )
            commit_check = nb_outputs.get(
                "commit",
                False,
            )

    return commit_check, execution_check, version_check


def _load_nbs_to_skip(nb_skip_path, dev_build):
    """
    Load list of notebooks to skip during execution based on build type.

    This function reads a JSON configuration file that specifies which notebooks should
    be skipped during execution. The configuration file contains two separate lists:
    "skip_if_dev" for development builds and "skip_if_stable" for production builds.
    This allows different notebooks to be skipped depending on the build context.

    Skipped notebooks will not be executed even if they have changed content, unless
    the execution filter is set to "execute-absolutely-all-notebooks". Notebooks in the
    skip list should have been successfully executed previously, otherwise warnings will
    be issued about potentially incomplete outputs.

    The JSON file structure should be:
    {
        "skip_if_dev": ["notebook1.ipynb", "notebook2.ipynb", ...],
        "skip_if_stable": ["notebook3.ipynb", ...]
    }

    Parameters
    ----------
    nb_skip_path : str or pathlib.Path
        Path to the JSON file containing skip lists, typically
        'scripts/nbs_to_skip.json' in the repository root
    dev_build : str or bool
        False if running a production/stable build, in which case the "skip_if_stable"
        list is used. Otherwise, a string containing the repo and commit hash for a dev
        build, in which case the "skip_if_dev" list is used

    Returns
    -------
    list
        List of notebook filenames (str) that should be skipped during execution.
        Filenames should match the actual .ipynb file names (e.g., "example.ipynb")
    """
    with open(nb_skip_path, "r") as f:
        nbs_to_skip = json.load(f)

    if dev_build:
        # AES maybe most are in the "skip if dev" for debugging? not sure why
        nbs_to_skip = nbs_to_skip["skip_if_dev"]
    else:
        nbs_to_skip = nbs_to_skip["skip_if_stable"]

    return nbs_to_skip


def _execute_nb(nb_path, timeout=600):
    """
    Execute a Jupyter notebook using nbconvert's ExecutePreprocessor.

    Parameters
    ----------
    nb_path : str or pathlib.Path
        Path to the Jupyter notebook file (.ipynb) to execute
    timeout : int, optional
        Maximum time in seconds to wait for each cell to execute.
        Default is 600 seconds (10 minutes)

    Returns
    -------
    loaded_nb : nbformat.notebooknode.NotebookNode
        The executed notebook object with outputs
    execution_initiated : bool
        Always True, indicating that execution was initiated
    execution_successful : bool
        True if all non-empty code cells were successfully executed,
        False otherwise
    """
    execution_initiated = True
    print(f"Execution: Notebook {nb_path.name} execution has been initiated.")
    loaded_nb = _load_nb(nb_path)

    ep = ExecutePreprocessor(
        timeout=timeout,
        kernel_name="python3",
    )
    ep.preprocess(
        loaded_nb,
        {"metadata": {"path": nb_path.parents[0]}},
    )

    execution_successful = _is_nb_fully_executed(
        loaded_nb,
    )
    if execution_successful:
        print(f"Execution: Notebook {nb_path.name} execution has been successful.")

    return loaded_nb, execution_initiated, execution_successful


def _process_nb(
    nb_path,
    nb_hashes,
    nbs_to_skip,
    nb_json_output_dir,
    dev_build,
    execution_filter,
):
    """
    Process a notebook by determining if execution is needed and executing if appropriate.

    This function orchestrates the notebook processing workflow by:
    1. Computing the current hash of the notebook
    2. Loading the notebook without executing it
    3. Checking prior execution status from JSON output files
    4. Determining if the notebook should be executed based on various criteria
    5. Executing the notebook if needed
    6. Issuing warnings for execution failures

    Parameters
    ----------
    nb_path : pathlib.Path
        Path to the Jupyter notebook file (.ipynb) to process
    nb_hashes : dict
        Mapping of notebook filenames (str) to their SHA256 hash values (str).
        Keys are notebook filenames (e.g., "example.ipynb"), values are 64-character
        hexadecimal hash strings
    nbs_to_skip : list
        List of notebook filenames that should be skipped during execution
    nb_json_output_dir : pathlib.Path
        Directory where the notebook's JSON output file is located
    dev_build : str or bool
        False if not running a dev build. Otherwise, a string containing
        the repo and commit hash to be used for the build
    execution_filter : str
        Execution mode that determines which notebooks to execute. See the 'help'
        description of 'build.py's CLI for what these different values mean. Valid
        values:
        - 'no-execution'
        - 'execute-only-updated-or-new-notebooks'
        - 'execute-all-unskipped-notebooks'
        - 'execute-absolutely-all-notebooks'

    Returns
    -------
    current_hash : str
        The SHA256 hash of the notebook in its current state
    loaded_nb : nbformat.notebooknode.NotebookNode
        The notebook object, either freshly loaded or executed with outputs
    current_execution_initiated : bool
        True if execution was attempted for this notebook, False otherwise
    execution_successful : bool
        True if the notebook was fully executed successfully (all non-empty
        code cells have execution_count), False otherwise. For non-executed
        notebooks, this reflects the prior execution status
    """
    # Don't need to show the whole path in logging and warning messages
    filename = nb_path.name

    # hash the nb in its current state
    current_hash = _hash_nb(nb_path)

    # get the nb without executing it
    loaded_nb = _load_nb(nb_path)

    # flag for whether the nb was run, initialized as false
    current_execution_initiated = False

    # Check if the nb has been fully executed, and get the nb_version as well as the
    # commit hash. We will use this in a warning in the skipped case, or actually use
    # this data in other cases.
    prior_commit_if_any, prior_execution_if_any, prior_version_if_any = (
        _read_nb_json_output_metadata(
            nb_path=nb_path,
            nb_json_output_dir=nb_json_output_dir,
        )
    )

    # determine if nb should be executed
    print(f"Configuration: Checking whether '{filename}' should be newly re-executed.")
    should_execute = _determine_should_execute_nb(
        filename,
        nb_hashes,
        current_hash,
        nbs_to_skip,
        dev_build,
        execution_filter,
        prior_commit_if_any,
        prior_execution_if_any,
        prior_version_if_any,
    )
    # execute nb as needed
    if should_execute:
        loaded_nb, current_execution_initiated, current_execution_successful = (
            _execute_nb(nb_path)
        )
        execution_successful = current_execution_successful

        # AES: I've tried to reorganize the warnings. The warnings here are now only for
        # issues with a current execution attempt. All warnings related to prior
        # execution attempts or skipping are inside
        # _determine_should_execute_nb. Original comment follows:
        # --------------------------------
        # warning for the case when nb execution was attempted
        # but the nb was not fully executed for some reason
        if not current_execution_initiated:
            # AES This is a new warning.
            warnings.warn(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # ERROR: Execution of notebook
                # '{filename}'
                # could not be initiated successfully. Please investigate the notebook
                # to determine why execution was not successfully initiated. The html
                # and json outputs may be incomplete.
                # ----------------------------------------------------------------------
            """)
            )
        elif (current_execution_initiated) and (not current_execution_successful):
            warnings.warn(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # ERROR: Execution of notebook
                # '{filename}'
                # was initiated but did not complete successfully. Please investigate
                # the notebook to determine why execution was not successfully
                # completed. The html and json outputs may be incomplete.
                # ----------------------------------------------------------------------
            """)
            )
    else:
        execution_successful = prior_execution_if_any

    return current_hash, loaded_nb, current_execution_initiated, execution_successful


def _determine_should_execute_nb(
    filename,
    nb_hashes,
    current_hash,
    nbs_to_skip,
    dev_build,
    execution_filter,
    prior_commit_if_any,
    prior_execution_if_any,
    prior_version_if_any,
):
    """
    Determine whether a notebook should be executed based on various factors.

    This function evaluates multiple conditions including:
    - Whether the notebook has been executed previously
    - Whether the notebook is flagged for skipping
    - Whether the notebook is "new" (not associated with a json output)
    - Whether the user is performing a 'dev' build
    - Whether the notebook hash has changed since last execution
    - The execution filter mode specified by the user

    Warnings are printed if the notebook appears outdated or if execution
    is needed but skipped based on the execution filter.

    Parameters
    ----------
    filename : str
        The filename of the notebook (e.g., "example.ipynb")
    nb_hashes : dict
        Mapping of notebook filenames (str) to their SHA256 hash values (str).
        Keys are notebook filenames (e.g., "example.ipynb"), values are 64-character
        hexadecimal hash strings
    current_hash : str
        Newly-determined SHA256 hash of the notebook based on its current state
    nbs_to_skip : list
        List of notebook filenames that should be skipped during execution
    dev_build : str or bool
        False if not running a dev build. Otherwise, a string containing
        the repo and commit hash to be used for the build
    execution_filter : str
        Execution mode that determines which notebooks to execute. See the 'help'
        description of 'build.py's CLI for what these different values mean. Valid
        values:
        - 'no-execution'
        - 'execute-only-updated-or-new-notebooks'
        - 'execute-all-unskipped-notebooks'
        - 'execute-absolutely-all-notebooks'
    prior_commit_if_any : str or bool
        Commit hash from the previous execution, loaded from the notebook's
        corresponding json output file. False if not found. Used for
        checking/validating versions when doing a 'dev' build
    prior_execution_if_any : bool
        True if the notebook was fully executed previously (per the
        notebook's corresponding json output file), False otherwise
    prior_version_if_any : str or bool
        The version of hnn-core that was last used to execute the notebook.
        False if not found, "NA" if never executed

    Returns
    -------
    bool
        True if the notebook should be executed, False otherwise
    """
    # 1) handle super omega execute all notebooks, including skipped
    #     - This is a brand-new option.
    if execution_filter == "execute-absolutely-all-notebooks":
        print(
            "Execution set to all notebooks, including skipped! CHARGE PROTON TORPEDOS!"
        )
        return True

    # 2) handle no execution of any notebooks
    #     - This was formerly the "silent default" behavior of "python build.py" with no
    #     args.
    if execution_filter == "no-execution":
        # 2.1) if nb new
        if filename not in nb_hashes:
            print(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # Notebook
                # '{filename}'
                # appears to be new and needs to be executed. Not performing execution
                # since execution_filter is set to '{execution_filter}'.
                # ----------------------------------------------------------------------
            """)
            )
        # 2.2) if nb hash has changed
        elif nb_hashes[filename] != current_hash:
            print(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # Notebook
                # '{filename}'
                # appears to have been updated and needs to be executed. Not performing
                # execution since execution_filter is set to '{execution_filter}'.
                # ----------------------------------------------------------------------
            """)
            )
        # 2.3) warning if version out of date
        # This one's a little complicated: read both the code of _write_nb_html_to_json
        # and docstring of _read_nb_json_output_metadata for guidance on its (currently
        # three) values. May need more refactoring.
        elif prior_version_if_any != "NA":
            if prior_version_if_any is not False:
                if Version(hnn_version) > Version(prior_version_if_any):
                    warnings.warn(
                        textwrap.dedent(f"""
                        # --------------------------------------------------------------
                        # WARNING: Notebook
                        # '{filename}'
                        # may have been executed on an older version of hnn-core, as
                        # your installed version is greater than version used to run the
                        # notebook previously. Please consider re-executing this
                        # notebook.
                        #
                        # Last version used to run notebook:
                        #    {prior_version_if_any}
                        # Installed version:
                        #    {hnn_version}
                        #
                        # Not performing execution since execution_filter is set to
                        # '{execution_filter}'.
                        # --------------------------------------------------------------
                    """)
                    )
        # 2.4) warning if prior execution not successful
        elif not prior_execution_if_any:
            warnings.warn(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # WARNING: Notebook
                # '{filename}'
                # does not appear to have been successfully executed the last time it
                # was run. The html and json output may be incomplete. Please consider
                # re-executing this notebook.
                #
                # Not performing execution since execution_filter is set to
                # '{execution_filter}'.
                # ----------------------------------------------------------------------
            """)
            )

        return False

    # 3) In all other cases (see below), skip first if possible
    skip_nb = filename in nbs_to_skip
    if skip_nb:
        print(
            textwrap.dedent(f"""
            Notebook '{filename}' has been flagged to be skipped. Execution will not be
            attempted for this notebook.
        """)
        )
        if not prior_execution_if_any:
            warnings.warn(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # WARNING: Notebook
                # '{filename}'
                # is flagged to be skipped, but does not appear to have been
                # successfully executed the last time it was run. The html and json
                # output may be incomplete.
                #
                # Please either remove the notebook from the skipped list JSON file, or
                # re-run the script with
                # '--execution-filter=execute-absolutely-all-notebooks'
                # to ensure that the notebook outputs are correct.
                # ----------------------------------------------------------------------
            """)
            )
        elif prior_version_if_any == "NA":
            warnings.warn(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # WARNING: Notebook
                # '{filename}'
                # is flagged to be skipped, but does not appear to have been previously
                # executed ever.
                #
                # Please either remove the notebook from the skipped list JSON file, or
                # re-run the script with
                # '--execution-filter=execute-absolutely-all-notebooks'
                # to ensure that the notebook outputs are correct.
                # ----------------------------------------------------------------------
            """)
            )

        return False

    # 4) Handle executing everything except skipped, since skippable nbs have already
    # been skipped above.
    #     - This was formerly called via the "--force-execute-all" CLI arg.
    if execution_filter == "execute-all-unskipped-notebooks":
        print(f"Executing '{filename}'")
        return True

    # 5) handle "regular" execute
    #     - This was formerly called via the "--execute-notebooks" CLI arg.
    if execution_filter == "execute-updated-unskipped-notebooks":
        # 5.1) if the hash has not changed
        if (filename in nb_hashes) and (nb_hashes[filename] == current_hash):
            if dev_build:
                # check if the commit specified to use by the dev build
                # matches the commit last used to run the nb per the
                # prior_commit_if_any (returned by _read_nb_json_output_metadata)
                #
                # if the versions do not match, the nb is flagged to
                # be re-executed by setting "prior_execution_if_any=False"
                if dev_build != prior_commit_if_any:
                    prior_execution_if_any = False
                    print(f"Executing '{filename}' due to dev build commit mismatch.")
                    return True
            elif not prior_execution_if_any:
                print(f"Executing '{filename}' due to previous failure of execution.")
                return True
            else:
                print(
                    f"Not executing: Notebook '{filename}' is unchanged and already fully executed."
                )
                return False
        else:
            print(
                f"Executing '{filename}' due to notebook being either new or changed."
            )
            return True


def _write_nb_html_to_json(
    html_content,
    nb_path,
    nb_json_output_dir,
    execution_initiated,
    execution_successful,
    dev_build=False,
):
    """
    Generate and save structured JSON output file containing notebook HTML and metadata.

    This function converts the notebook HTML content into a hierarchical JSON structure
    organized by section headers and saves it to a JSON file. The output includes
    execution metadata (execution status, hnn-core version, and optional commit hash
    for dev builds) along with the structured HTML content.

    (In the future, the JSON structure will enable selective insertion of notebook
    sections into markdown pages by specifying header ranges (a planned enhancement
    feature).)

    Parameters
    ----------
    html_content : str
        The complete HTML string containing all converted notebook cells, as returned
        by _extract_html_from_nb
    nb_path : pathlib.Path
        Path to the Jupyter notebook file (.ipynb). Used to determine the output
        JSON filename (stem of the notebook filename)
    nb_json_output_dir : pathlib.Path
        Directory where the JSON output file will be saved. The file will be named
        {nb_path.stem}.json
    execution_initiated : bool
        True if notebook execution was attempted in this run, False otherwise.
        Determines whether to use current or previously-saved hnn-core version
    execution_successful : bool
        True if the notebook was fully executed successfully (all non-empty code
        cells completed execution), False otherwise
    dev_build : str or bool, optional
        False if not running a dev build. Otherwise, a string containing the repo
        and commit hash to be used for the build. Default is False

    Returns
    -------
    pathlib.Path
        Path to the generated JSON output file
    """

    # ----------------------------------------
    # generate structured json output
    # ----------------------------------------
    # Note: this section pertains to a planned enhancement
    # to enable inserting sections of a nb into an
    # html file by specifing the headers to include; e.g.,
    # including [[notebook][start header][end header]] in your
    # .md file would inject only the .html for those header
    # sections into your html output file

    nb_html_json = _convert_html_to_json(
        html_content,
        str(nb_path.name),
    )

    output_json_path = nb_json_output_dir / f"{nb_path.stem}.json"

    # Set or load the last version that the nb was executed with
    if execution_initiated:
        # Add execution status directly to json output
        # Track version used in nb execution
        nb_html_json = {
            "full_executed": execution_successful,
            "hnn_version": hnn_version,
            **nb_html_json,
        }
        if dev_build:
            print("Dev version to use:", dev_build)
            nb_html_json["commit"] = dev_build
    else:
        # get previously-used hnn version from json file
        previous_version = "NA"
        if output_json_path.exists():
            with open(output_json_path, "r") as f:
                nb_html_json = json.load(f)
            # check for hnn_version key
            if "hnn_version" in nb_html_json:
                previous_version = nb_html_json["hnn_version"]
        nb_html_json = {
            "full_executed": execution_successful,
            "hnn_version": previous_version,
            **nb_html_json,
        }
        if dev_build:
            nb_html_json["commit"] = dev_build

    with open(output_json_path, "w") as f:
        json.dump(nb_html_json, f, indent=4)

    return output_json_path


def _write_standalone_html(
    html_content,
    nb_path,
    nb_json_output_dir,
):
    """
    Write notebook HTML content to a standalone HTML file for preview purposes.

    This function creates a minimal standalone HTML file containing the notebook's
    rendered content. These files are NOT part of the published textbook website
    but provide a quick "snapshot" for previewing how notebooks will appear when
    integrated into the site. This is particularly useful for reviewing unpublished
    or in-development notebooks before they are officially added to the textbook.

    The generated HTML file includes only basic <html> and <body> tags wrapping
    the notebook content, without the full site styling, navigation, or template
    structure. For complete styling preview, view the notebook through the full
    build system instead.

    Parameters
    ----------
    html_content : str
        The complete HTML string containing all converted notebook cells, as returned
        by _extract_html_from_nb. This includes code cells, outputs, markdown cells,
        and embedded images
    nb_path : pathlib.Path
        Path to the Jupyter notebook file (.ipynb). The stem of this path (filename
        without extension) determines the output HTML filename
    nb_json_output_dir : pathlib.Path
        Directory where the standalone HTML file will be saved. The file will be named
        {nb_path.stem}.html
    """
    standalone_html_path = nb_json_output_dir / f"{nb_path.stem}.html"
    with open(standalone_html_path, "w", encoding="utf-8") as f:
        f.write("<html><body>\n")
        f.write(html_content)
        f.write("\n</body></html>")


def execute_and_convert_nbs_to_json(
    content_path,
    nb_hash_path,
    nb_skip_path,
    execution_filter,
    dev_build=False,
    use_base64=False,
    write_standalone_html=False,
):
    """
    Main orchestration function for processing all Jupyter notebooks in the textbook.

    This function coordinates the complete notebook processing pipeline for the HNN
    textbook build system. It discovers all .ipynb files in the content directory,
    determines which notebooks need execution based on content changes and
    configuration, executes notebooks as needed, generates structured JSON output files,
    optionally converts them to HTML, and updates the hash tracking system.

    The workflow for each notebook:
    1. Load previous content hashes and skip lists
    2. For each notebook found:
       a. Compute current content hash
       b. Determine if execution is needed (based on several criteria)
       c. Execute notebook if needed (via nbconvert)
       d. Convert notebook cells to HTML (code, outputs, markdown)
       e. Save images from notebook outputs to disk (if use_base64=False)
       f. Generate structured JSON file with HTML content and execution metadata
       g. Optionally write standalone HTML preview file
       h. Update hash tracking
    3. Save updated hashes for next build

    Parameters
    ----------
    content_path : pathlib.Path
        Path to the directory containing all directories which contain markdown files,
        notebook files, and possibly their outputs. This is ALWAYS
        "<textbook_root>/content" and never "<textbook_root>/dev", since "dev" versions
        of required directories will be created as needed.
    nb_hash_path : pathlib.Path
        Path to the JSON file for loading/saving notebook content hashes, typically
        'scripts/nb_hashes.json'
    nb_skip_path : pathlib.Path
        Path to the JSON file containing skip configuration lists, typically
        'scripts/nbs_to_skip.json'
    execution_filter : str
        Execution mode controlling which notebooks get executed. Valid values:
        - 'no-execution': Skip all notebook execution
        - 'execute-updated-unskipped-notebooks': Execute only changed/new unskipped notebooks
        - 'execute-all-unskipped-notebooks': Execute all notebooks except those in skip list
        - 'execute-absolutely-all-notebooks': Execute all notebooks including skipped ones
    dev_build : str or bool, optional
        False for production/stable builds (default). For development builds, provide
        a string containing the repo and commit hash. Affects skip list selection and
        commit tracking in JSON metadata. Default is False
    use_base64 : bool, optional
        If True, embed notebook output images as Base64 strings in HTML. If False,
        save images as separate PNG files. Default is False
    write_standalone_html : bool, optional
        If True, generate standalone HTML preview files for each notebook in addition
        to the JSON outputs. These are useful for development but not used in the
        published site. Default is False

    Returns
    -------
    None
        Processes all notebooks and writes output files (JSON, HTML, images, hashes)
        to appropriate locations. No return value

    Notes
    -----
    - Notebook content hashes track only code/markdown content (not outputs or metadata)
    - JSON output files contain HTML, execution metadata, and hnn-core version info
    - Images from notebook outputs are saved to output_nb_{notebook_name}/ directories
    - For dev builds, JSON output is written to a parallel 'dev/' directory structure
    """
    # ==================== #
    #        SETUP
    # ==================== #
    # Get all notebook file paths
    all_nb_paths = sorted(content_path.glob("**/*.ipynb"))

    # get nb hashes from json
    nb_hashes = _load_nb_hashes(nb_hash_path)
    updated_hashes = nb_hashes.copy()

    # get list of nbs to skip
    nbs_to_skip = _load_nbs_to_skip(nb_skip_path, dev_build)

    # ==================== #
    # Loop through notebooks
    # ==================== #
    for nb_path in all_nb_paths:
        print(f"\nProcessing notebook: '{nb_path.name}'")

        nb_path = Path(nb_path)
        if dev_build:
            # This needs to be done separately in both the notebook-execution code and
            # here in the page-generation code, since there is not necessarily a 1-to-1
            # correspondence between every markdown file and every notebook.
            #
            # Replace "content" parent directory with "dev" one, and safely make it
            nb_json_output_dir = Path(str(nb_path).replace("content", "dev"))
            nb_json_output_dir = nb_json_output_dir.parents[0]
            nb_json_output_dir.mkdir(parents=True, exist_ok=True)
        else:
            nb_json_output_dir = nb_path.parents[0]

        # process nb and update hash
        processed_hash, loaded_nb, execution_initiated, execution_successful = (
            _process_nb(
                nb_path,
                nb_hashes,
                nbs_to_skip,
                nb_json_output_dir,
                dev_build,
                execution_filter,
            )
        )

        # extract the html from the nb, including saving any images if needed
        html_content = _extract_html_from_nb(
            loaded_nb,
            nb_path,
            nb_json_output_dir,
            dev_build=dev_build,
            use_base64=use_base64,
        )

        # generate complete json output file
        _write_nb_html_to_json(
            html_content,
            nb_path,
            nb_json_output_dir,
            execution_initiated,
            execution_successful,
            dev_build=dev_build,
        )

        # optionally write standalone nb to an html file
        if write_standalone_html:
            _write_standalone_html(
                html_content,
                nb_path,
                nb_json_output_dir,
            )

        print(f"Successfully converted '{nb_path.name}' to html, then json")

        updated_hashes[nb_path.name] = processed_hash

    # save updated hashes
    _save_nb_hashes(
        updated_hashes,
        nb_hash_path,
    )


# # AES TODO
# # %%

# run_test = False


# def test_nb_conversion(input_folder=None):
#     execute_and_convert_nbs_to_json(
#         input_folder=input_folder,
#         use_base64=False,
#         write_standalone_html=True,
#         execute_nbs=True,
#     )


# if run_test:
#     test_nb_conversion("tests")

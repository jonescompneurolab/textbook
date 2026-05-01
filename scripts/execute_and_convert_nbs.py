# %%
from copy import deepcopy
import base64
import hashlib
import html
import json
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


def load_nb_json_output(
    nb_path,
    nb_json_output_dir,
):
    """
    Load the JSON output for a notebook file, depending on "content"/"dev" build.

    Important: If doing a "content" build, then ONLY the '<textbook-root>/content/**'
    version of the JSON output file will attempt to be loaded. However, if doing a "dev"
    build, then ONLY the '<textbook-root>/dev/**' version of the JSON output file will
    attempt to be loaded. In other words, in the "dev" case, we are reading the notebook
    *itself* from the "content" path, but only interested in pre-existing JSON output
    from the "dev" path.

    Parameters
    ----------
    nb_path : pathlib.Path
        Path to the Jupyter notebook file (.ipynb)
    nb_json_output_dir : pathlib.Path
        Directory where the notebook's JSON output file will be located (and, if it
        exists, is present currently from a prior execution)

    Returns
    -------
    nb_outputs_if_any
    """
    json_path = nb_json_output_dir / f"{nb_path.stem}.json"

    if json_path.exists():
        with open(json_path, "r") as file:
            nb_outputs_if_any = json.load(file)
    else:
        nb_outputs_if_any = None

    return nb_outputs_if_any


def _convert_nb_html_to_json(
    html_input: str,
    nb_path: Path,
):
    """
    Convert a notebook's HTML content into a custom structured JSON format.

    The structured JSON structure are organized by section headers. TODO More
    description will be added in the future...

    Parameters
    ----------
    html_input : str
        The complete HTML content of the notebook, as obtained from
        `_extract_html_from_nb`
    nb_path : pathlib.Path
        Path to the Jupyter notebook file currently being converted

    Returns
    -------
    dict
        The complete structured JSON content containing all converted notebook cells

    Notes
    -----
    TODO In the future, this section pertains to a planned enhancement to enable inserting
    sections of a nb into an HTML file by specifing the headers to include. E.g.,
    including '[[notebook][start header][end header]]' in your .md file would inject
    only the .html for those header sections into your HTML output file.
    """
    filename = str(nb_path.name)

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
        for line in html_input.splitlines()
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


def _structure_json(contents):
    """
    (Unused) Determine the hierarchy of sections based on levels without adding content.

    Returns a list of sections in order of their hierarchy.

    TODO This is currently unused and will be expanded in future updates.
    """
    hierarchy = {}

    for filename, sections in contents.items():
        hierarchy[filename] = {}

        # list to track parent sections for potential nesting
        parent_stack = []

        for section_title, section_data in sections.items():
            level = section_data["level"]
            html_contents = section_data["html"]

            # Create a section dict with 'title', 'level', and 'sub-sections'
            section_info = {
                "title": section_title,
                "level": level,
                "html": html_contents,
                "sub-sections": [],
            }

            # Ensure only sections with a level greater than the current
            # section remain in the stack as potential parents
            while parent_stack and parent_stack[-1]["level"] >= level:
                parent_stack.pop()

            if parent_stack:
                # Add the section as a child of the last parent
                parent_stack[-1]["sub-sections"].append(section_info)
            else:
                # Add the section as a top-level section
                hierarchy[filename][section_title] = section_info

            # Add the current section to the parent stack for future nesting
            parent_stack.append(section_info)

    def remove_blank_subsections(sections):
        seek = "sub-sections"

        for k, v in list(sections.items()):
            if isinstance(v, dict):
                # check for 'sub-sections' key in dict
                if seek in v:
                    # delete empty sub-sections
                    if v[seek] == []:
                        del v[seek]

                    # Recursively check all sub-sections
                    else:
                        for sub_section in v[seek]:
                            remove_blank_subsections(sub_section)

            elif isinstance(v, list):
                # if v is an empty list, delete it
                if v == []:
                    del sections[k]
                # if v is a list of dicts, iterate through the dicts
                else:
                    for dictionary in v:
                        remove_blank_subsections(dictionary)

        return sections

    hierarchy[filename] = remove_blank_subsections(hierarchy[filename])

    return hierarchy


def _extract_html_from_nb(
    nb,
    nb_path,
    nb_json_output_dir,
    use_base64=False,
):
    """
    Extract and convert notebook cells to HTML, including code, outputs, and markdown.

    This function processes all cells in a Jupyter notebook and converts them to
    formatted HTML. Code cells are rendered with their source and outputs (text,
    images, errors). Markdown cells are converted to HTML using Pandoc. Images from
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
        Directory where the notebook's JSON output file will be located. This will
        become the parent of the new directory where any images will be stored.
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

    # Helper for aggregating outputs
    # -----------------------------------------------------------------------
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
            # yet been added to the HTML, append the outputs to html_output
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


def _calculate_nb_hash(loaded_nb):
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
    loaded_nb : nbformat.notebooknode.NotebookNode
        The notebook object, either freshly loaded or executed with outputs

    Returns
    -------
    str
        A 64-character hexadecimal string representing the SHA256 hash of the cleaned
        notebook content
    """
    nb = deepcopy(loaded_nb)

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


def _load_nb_hashes(nb_hashes_path):
    """
    Load previously-recorded notebook content hashes from JSON file.

    This function retrieves the hash dictionary that tracks notebook content changes
    across builds. The hashes are used by the build system to determine which notebooks
    have been modified and possibly need re-execution. Each hash represents the
    content-only state of a notebook (code and markdown cells), excluding execution
    outputs and metadata, as generated by `_calculate_hash_nb`.

    If the hash file does not exist (e.g., first build), an empty dictionary is
    returned, which will cause all notebooks to be treated as new. Later in the code,
    this will trigger execution according to the '--execution-type' settings.

    Parameters
    ----------
    nb_hashes_path : pathlib.Path
        Path to the JSON file containing notebook hashes, typically
        'scripts/nb_hashes.json' in the textbook-root directory

    Returns
    -------
    dict
        Mapping of notebook filenames (str) to their SHA256 hash values (str). Keys are
        local notebook filenames (e.g., "example.ipynb"), values are 64-character
        hexadecimal hash strings. Returns an empty dictionary if the hash file does not
        exist
    """
    # AES if we want to support optional or fresh hash building, we should do it at the
    # CLI in main, not here, but leaving this as-is for now.
    if nb_hashes_path.exists():
        with open(nb_hashes_path, "r") as f:
            return json.load(f)
    return {}


def _save_nb_hashes(
    new_hashes,
    nb_hashes_path,
):
    """
    Persist updated notebook content hashes to a JSON file for tracking changes.

    This function saves a dictionary mapping notebook filenames to their SHA256 content
    hashes. These hashes are used by the build system to determine which notebooks need
    re-execution after their content has changed. The hashes are generated by
    `_calculate_hash_nb` and track only the code/markdown content (not execution outputs
    or metadata, see that function for details).

    Parameters
    ----------
    new_hashes : dict
        Mapping of notebook filenames (str) to their SHA256 hash values (str).
        Keys are local notebook filenames (e.g., "example.ipynb"), values are 64-character
        hexadecimal hash strings
    nb_hashes_path : pathlib.Path
        Path to the JSON file where hashes will be saved, typically
        'scripts/nb_hashes.json' in the textbook-root directory

    Returns
    -------
    None
        Writes the hash dictionary to disk as formatted JSON with 4-space indentation
    """
    with open(nb_hashes_path, "w") as f:
        json.dump(new_hashes, f, indent=4)


def _load_nb(nb_path):
    """
    Load a Jupyter notebook object from a file path.

    Parameters
    ----------
    nb_path : pathlib.Path
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
        Directory where the notebook's JSON output file will be located (and, if it
        exists, is present currently from a prior execution)

    Returns
    -------
    prior_commit_if_any : str or bool
        The commit hash from the previous execution if available. False if the JSON file
        doesn't exist or doesn't contain commit information
    prior_execution_if_any : bool
        True if the notebook was fully executed in a prior run (all non-empty
        code cells completed execution). False if the JSON file doesn't exist
        or if the prior execution was incomplete
    prior_version_if_any : str or bool
        The version string of hnn-core used in the previous execution (e.g., "0.4.2").
        False if the JSON file doesn't exist or doesn't contain version
        information. "NA" if the metadata exists, but the notebook has not been run
        successfully since recording versions of last successful execution.
    """

    prior_commit_if_any = False
    prior_execution_if_any = False
    prior_version_if_any = False

    # Has content if the file is found, otherwise returns None
    nb_outputs_if_any = load_nb_json_output(nb_path, nb_json_output_dir)

    # if the json output exists, get the execution status, base version,
    # and latest commit used to execute the nb
    if nb_outputs_if_any:
        prior_commit_if_any = nb_outputs_if_any.get(
            "last_hnn_dev_commit_used",
            False,
        )
        prior_execution_if_any = nb_outputs_if_any.get(
            "last_execution_successful",
            False,
        )
        prior_version_if_any = nb_outputs_if_any.get(
            "last_hnn_version_used",
            False,
        )

    return prior_commit_if_any, prior_execution_if_any, prior_version_if_any


def _load_nbs_to_skip(nb_skips_path, is_dev_build):
    """
    Load list of notebooks to skip during execution based on build type.

    This function reads a JSON configuration file that specifies which notebooks should
    be skipped during execution. The configuration file contains two separate lists:
    "skip_if_dev" for development builds and "skip_if_stable" for production builds.
    This allows different notebooks to be skipped depending on the build context.

    Skipped notebooks will not be executed even if they have changed content, unless
    '--execution-type' was set to "absolutely-all-notebooks" when calling
    'build.py'. Notebooks in the skip list should have been successfully executed
    previously, otherwise warnings will be issued about potentially incomplete outputs.

    The JSON file structure should resemble:
    {
        "skip_if_dev": ["notebook1.ipynb", "notebook2.ipynb", ...],
        "skip_if_stable": ["notebook3.ipynb", ...]
    }

    Parameters
    ----------
    nb_skips_path : pathlib.Path
        Path to the JSON file containing skip lists, typically
        'scripts/nbs_to_skip.json' in the textbook-root directory
    is_dev_build : bool
        Flag for if we are doing a "dev" build, requiring use of the "dev" version of
        which notebooks should be skipped.

    Returns
    -------
    list
        List of notebook filenames (str) that should be skipped during execution.
        Filenames should match the actual .ipynb file names (e.g., "example.ipynb")
    """
    with open(nb_skips_path, "r") as f:
        nbs_to_skip = json.load(f)

    if is_dev_build:
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
    nb_path : pathlib.Path
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
    execution_type,
    is_dev_build,
    hnn_commit_hash,
):
    """
    Process a notebook by determining if execution is needed and executing if appropriate.

    This function orchestrates the notebook processing workflow by:
    1. Loading the notebook without executing it
    2. Computing the current hash of the notebook
    3. Checking prior execution status from pre-existing JSON output files
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
    execution_type : str
        Execution mode that determines which notebooks to execute. See the 'help'
        description of 'build.py's CLI for what these different values mean. Valid
        values:
        - 'no-execution'
        - 'execute-only-updated-or-new-notebooks'
        - 'all-unskipped-notebooks'
        - 'absolutely-all-notebooks'
    is_dev_build : bool
        Flag for if we are doing a "dev" build and should use the 'hnn_commit_hash' as
        part of our algorithm to determine whether or not a notebook should be
        re-executed.
    hnn_commit_hash : str or None
        The commit hash of the hnn_core code version to use for either new execution or
        comparison with the old execution history. None if doing a 'stable' build,
        otherwise (i.e. 'dev' build) is the full commit SHA.

    Returns
    -------
    current_nb_hash : str
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

    # get the nb without executing it
    loaded_nb = _load_nb(nb_path)

    # hash the nb in its current state
    current_nb_hash = _calculate_nb_hash(loaded_nb)

    # flag for whether the nb was run, initialized as false
    current_execution_initiated = False

    # If the data exists, obtain the prior commit used (in the "dev" cases), whether the
    # last nb execution was successful, and/or what was the last HNN version used to run
    # the nb. We will use this in a warning in the skipped case, or actually use this
    # data in other cases.
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
        current_nb_hash,
        nbs_to_skip,
        execution_type,
        prior_commit_if_any,
        prior_execution_if_any,
        prior_version_if_any,
        is_dev_build,
        hnn_commit_hash,
    )
    # execute nb as needed
    if should_execute:
        loaded_nb, current_execution_initiated, current_execution_successful = (
            _execute_nb(nb_path)
        )
        execution_successful = current_execution_successful

        # AES: I've tried to reorganize the warnings. The warnings here are now only for
        # issues with a current execution attempt. All warnings related to prior
        # execution attempts or skipping are inside _determine_should_execute_nb.
        # Original comment follows:
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
                # to determine why execution was not successfully initiated. The HTML
                # and JSON outputs may be incomplete.
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
                # completed. The HTML and JSON outputs may be incomplete.
                # ----------------------------------------------------------------------
            """)
            )
    else:
        execution_successful = prior_execution_if_any

    return current_nb_hash, loaded_nb, current_execution_initiated, execution_successful


def _determine_should_execute_nb(
    filename,
    nb_hashes,
    current_nb_hash,
    nbs_to_skip,
    execution_type,
    prior_commit_if_any,
    prior_execution_if_any,
    prior_version_if_any,
    is_dev_build,
    hnn_commit_hash,
):
    """
    Determine whether a notebook should be executed based on various factors.

    This function evaluates multiple conditions including:
    - Whether the notebook has been executed previously
    - Whether the notebook is flagged for skipping
    - Whether the notebook is "new" (not associated with a JSON output)
    - Whether the user is performing a 'dev' build
    - Whether the notebook hash has changed since last execution
    - The execution type specified by the user

    Warnings are printed if the notebook appears outdated or if execution
    is needed but skipped based on the execution type.

    Parameters
    ----------
    filename : str
        The local filename of the notebook (e.g., "example.ipynb")
    nb_hashes : dict
        Mapping of notebook filenames (str) to their SHA256 hash values (str).
        Keys are notebook filenames (e.g., "example.ipynb"), values are 64-character
        hexadecimal hash strings
    current_nb_hash : str
        Newly-determined SHA256 hash of the notebook based on its current state
    nbs_to_skip : list
        List of notebook filenames that should be skipped during execution
    execution_type : str
        Execution mode that determines which notebooks to execute. See the 'help'
        description of 'build.py's CLI for what these different values mean. Valid
        values:
        - 'no-execution'
        - 'execute-only-updated-or-new-notebooks'
        - 'all-unskipped-notebooks'
        - 'absolutely-all-notebooks'
    prior_commit_if_any : str or bool
        Commit hash from the previous execution, loaded from the notebook's
        corresponding JSON output file. False if not found
    prior_execution_if_any : bool
        True if the notebook was fully executed previously (per the
        notebook's corresponding JSON output file), False otherwise
    prior_version_if_any : str or bool
        The version of hnn-core that was last used to execute the notebook.
        False if not found, "NA" if never executed
    is_dev_build : bool
        Flag for if we are doing a "dev" build and should use the 'hnn_commit_hash' as
        part of our algorithm to determine whether or not a notebook should be
        re-executed.
    hnn_commit_hash : str or None
        The commit hash of the hnn_core code version to use for either new execution or
        comparison with the old execution history. None if doing a 'stable' build,
        otherwise (i.e. 'dev' build) is the full commit SHA.

    Returns
    -------
    bool
        True if the notebook should be executed, False otherwise
    """
    # 1. Handle SUPER-OMEGA-execute-all-notebooks, including skipped
    # ----------------------------------------------------------------------------------
    # AES: This is a brand-new option.
    if execution_type == "absolutely-all-notebooks":
        print(
            "Execution set to all notebooks, including skipped! CHARGE PROTON TORPEDOS!"
        )
        return True

    # 2. Handle "no-execution" of any notebooks
    # ----------------------------------------------------------------------------------
    # - AES: This was formerly the "silent default" behavior of "python build.py" with
    # no args.
    if execution_type == "no-execution":
        # 2.1) if nb new
        if filename not in nb_hashes:
            print(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # WARNING: Notebook
                # '{filename}'
                # appears to be new and needs to be executed. Not performing execution
                # since execution_type is set to '{execution_type}'.
                # ----------------------------------------------------------------------
            """)
            )
        # 2.2) if nb hash has changed
        elif nb_hashes[filename] != current_nb_hash:
            print(
                textwrap.dedent(f"""
                # ----------------------------------------------------------------------
                # WARNING: Notebook
                # '{filename}'
                # appears to have been updated and needs to be executed. Not performing
                # execution since execution_type is set to '{execution_type}'.
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
                        # Not performing execution since execution_type is set to
                        # '{execution_type}'.
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
                # was run, or has never been executed. The HTML and JSON output may be
                # incomplete. Please consider re-executing this notebook.
                #
                # Not performing execution since execution_type is set to
                # '{execution_type}'.
                # ----------------------------------------------------------------------
            """)
            )

        return False

    # 3. Apply notebook SKIPPING check before any further options
    # ----------------------------------------------------------------------------------
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
                # successfully executed the last time it was run, or has never been
                # executed. The HTML and JSON output may be incomplete.
                #
                # Please either remove the notebook from the skipped list JSON file, or
                # re-run the script with
                # '--execution-type=absolutely-all-notebooks'
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
                # '--execution-type=absolutely-all-notebooks'
                # to ensure that the notebook outputs are correct.
                # ----------------------------------------------------------------------
            """)
            )

        return False

    # 4. Handle executing "everything except skipped", since skippable nbs have already
    # been skipped above.
    # ----------------------------------------------------------------------------------
    # AES: This was formerly called via the "--force-execute-all" CLI arg.
    if execution_type == "all-unskipped-notebooks":
        print(f"Executing '{filename}'")
        return True

    # 5. Finally, handle "regular" execute
    # ----------------------------------------------------------------------------------
    # AES: This was formerly called via the "--execute-notebooks" CLI arg.
    if execution_type == "updated-unskipped-notebooks":
        # 5.1) if the hash has not changed
        if (filename in nb_hashes) and (nb_hashes[filename] == current_nb_hash):
            if is_dev_build:
                # check if the commit specified to use by the dev build
                # matches the commit last used to run the nb per the
                # prior_commit_if_any (returned by _read_nb_json_output_metadata)
                #
                # if the versions do not match, the nb is flagged to
                # be re-executed by setting "prior_execution_if_any=False"
                if hnn_commit_hash != prior_commit_if_any:
                    prior_execution_if_any = False
                    print(f"Executing '{filename}' due to prior HNN commit mismatch.")
                    return True
            elif not prior_execution_if_any:
                print(f"Executing '{filename}' due to previous failure of execution.")
                return True
            else:
                print(
                    f"Not executing: Notebook '{filename}' is unchanged and already fully executed."
                )
                return False
        # 5.2) if the hash has changed or it's a new notebook
        else:
            print(
                f"Executing '{filename}' due to notebook being either new or changed."
            )
            return True


def _write_nb_json_output(
    nb_json_content,
    nb_path,
    nb_json_output_dir,
    execution_initiated,
    execution_successful,
    is_dev_build,
    hnn_commit_hash,
):
    """
    Save structured JSON output file containing notebook HTML and metadata.

    The processed structured JSON output from the notebook is combined with execution
    metadata (execution status, hnn-core version, and optional commit hash for dev
    builds), and then saved to file.

    Parameters
    ----------
    nb_json_content : dict
        The complete structured JSON content containing all converted notebook cells,
        as returned by `_convert_nb_html_to_json`
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
    is_dev_build : bool
        Flag for if we are doing a "dev" build and should record the 'hnn_commit_hash'
        in the notebook's JSON output, for history tracking of the last version that was
        used to execute
    hnn_commit_hash : str or None
        The commit hash of the hnn_core code version to use for either new execution or
        comparison with the old execution history. None if doing a 'stable' build,
        otherwise (i.e. 'dev' build) is the full commit SHA.

    Returns
    -------
    pathlib.Path
        Path to the generated JSON output file
    """
    output_json_path = nb_json_output_dir / f"{nb_path.stem}.json"

    # Set or load the last version that the nb was executed with
    if execution_initiated:
        # Add execution status directly to json output
        # Track version used in nb execution
        nb_json_content = {
            "last_execution_successful": execution_successful,
            "last_hnn_version_used": hnn_version,
            **nb_json_content,
        }
        if is_dev_build:
            print("Commit to use:", hnn_commit_hash)
            nb_json_content["last_hnn_dev_commit_used"] = hnn_commit_hash
    else:
        # get previously-used hnn version from json file
        previous_version = "NA"
        if output_json_path.exists():
            with open(output_json_path, "r") as f:
                nb_json_content = json.load(f)
            # check for hnn_version key
            if "last_hnn_version_used" in nb_json_content:
                previous_version = nb_json_content["last_hnn_version_used"]
        nb_json_content = {
            "last_execution_successful": execution_successful,
            "last_hnn_version_used": previous_version,
            **nb_json_content,
        }
        # # AES: Potential mistake to write the hash here
        # if is_dev_build:
        #     nb_json_content["last_hnn_dev_commit_used"] = hnn_commit_hash

    with open(output_json_path, "w") as f:
        json.dump(nb_json_content, f, indent=4)

    return output_json_path


def _save_standalone_nb_html(
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
        without extension) determines the output HTML filename, which will be
        `{nb_path.stem}.html`
    nb_json_output_dir : pathlib.Path
        Directory where the standalone HTML file will be saved
    """
    standalone_html_path = nb_json_output_dir / f"{nb_path.stem}.html"
    with open(standalone_html_path, "w", encoding="utf-8") as f:
        f.write("<html><body>\n")
        f.write(html_content)
        f.write("\n</body></html>")


def execute_and_convert_nbs_to_json(
    content_path,
    nb_hashes_path,
    nb_skips_path,
    execution_type,
    is_dev_build,
    hnn_commit_hash,
    save_standalone_nb_html,
    use_base64=False,
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
       e. Save images from notebook outputs to disk (if use_base64=False, the default)
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
    nb_hashes_path : pathlib.Path
        Path to the JSON file for loading/saving notebook content hashes, typically
        'scripts/nb_hashes.json'
    nb_skips_path : pathlib.Path
        Path to the JSON file containing skip configuration lists, typically
        'scripts/nbs_to_skip.json'
    execution_type : str
        Execution mode controlling which notebooks get executed. This is the same as
        value passed to the '--execution-type' argument of the CLI in `build.py`. See
        'python build.py --help' for more details. Valid values:
        - 'no-execution': Skip all notebook execution
        - 'updated-unskipped-notebooks': Execute only changed/new unskipped notebooks
        - 'all-unskipped-notebooks': Execute all notebooks except those in skip list
        - 'absolutely-all-notebooks': Execute all notebooks including skipped ones
    is_dev_build : bool
        Flag for if we are doing a "dev" build and should place all processed outputs in
        a "<textbook-root>/dev/**" directory, including creating all necessary
        directories as needed, redirecting the relevant links in the dev HTML output,
        and using the "dev" version of which notebooks should be skipped. This is
        determined by a prior step in the overall code process, based on the
        user-provided option to the '--code-version' argument of 'build.py.
    hnn_commit_hash : str or None
        The commit hash of the hnn_core code version to use for either new execution or
        comparison with the old execution history. None if doing a 'stable' build,
        otherwise (i.e. 'dev' build) is the full commit SHA.
    save_standalone_nb_html : bool, optional
        If True, generate standalone HTML preview files for each notebook in addition
        to the JSON outputs. These are useful for development but not used in the
        published site. Default is False
    use_base64 : bool, optional
        If True, embed notebook output images as Base64 strings in HTML. If False,
        save images as separate PNG files. Default is False

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
    # Setup
    # ----------------------------------------------------------------------------------
    # Get all notebook file paths
    all_nb_paths = sorted(content_path.glob("**/*.ipynb"))

    # get nb hashes from json
    nb_hashes = _load_nb_hashes(nb_hashes_path)
    updated_hashes = nb_hashes.copy()

    # get list of nbs to skip
    nbs_to_skip = _load_nbs_to_skip(nb_skips_path, is_dev_build)

    # Loop through all notebooks
    # ----------------------------------------------------------------------------------
    for nb_path in all_nb_paths:
        print(f"\nProcessing notebook: '{nb_path.name}'")

        nb_path = Path(nb_path)
        if is_dev_build:
            # This needs to be done separately in both the notebook-execution code here
            # and later in the page-generation code, since there is not necessarily a
            # 1-to-1 correspondence between every markdown file and every notebook.
            #
            # Replace "content" parent directory with "dev" one:
            nb_json_output_dir = Path(str(nb_path).replace("content", "dev"))
            nb_json_output_dir = nb_json_output_dir.parents[0]
            # Importantly, create parent directories if they don't exist:
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
                execution_type,
                is_dev_build,
                hnn_commit_hash,
            )
        )

        # extract the html from the nb, including saving any images if needed
        nb_html_content = _extract_html_from_nb(
            loaded_nb,
            nb_path,
            nb_json_output_dir,
            use_base64=use_base64,
        )

        # optionally write standalone nb to an html file
        if save_standalone_nb_html:
            _save_standalone_nb_html(
                nb_html_content,
                nb_path,
                nb_json_output_dir,
            )

        # Generate structured json output
        nb_json_content = _convert_nb_html_to_json(
            nb_html_content,
            nb_path,
        )

        # Save the final json output file
        _write_nb_json_output(
            nb_json_content,
            nb_path,
            nb_json_output_dir,
            execution_initiated,
            execution_successful,
            is_dev_build,
            hnn_commit_hash,
        )

        print(
            f"\nExecution: Success: Converted '{nb_path.name}' "
            "to HTML, then structured JSON."
        )

        updated_hashes[nb_path.name] = processed_hash

    # Finally, save updated hashes
    _save_nb_hashes(
        updated_hashes,
        nb_hashes_path,
    )


# # AES TODO
# # %%

# run_test = False


# def test_nb_conversion(input_folder=None):
#     execute_and_convert_nbs_to_json(
#         input_folder=input_folder,
#         use_base64=False,
#         save_standalone_nb_html=True,
#         execute_nbs=True,
#     )


# if run_test:
#     test_nb_conversion("tests")

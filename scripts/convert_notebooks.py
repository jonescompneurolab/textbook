# %%
import base64
import hashlib
import html
import json
import os
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


def save_plot_as_image(
    img_data,
    img_filename,
    output_dir,
):
    """Saves the plot image to the specified directory."""
    img_path = os.path.join(
        output_dir,
        img_filename,
    )
    with open(img_path, "wb") as img_file:
        img_file.write(base64.b64decode(img_data))
    return


def html_to_json(
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


def structure_json(contents):
    """
    Determine the hierarchy of sections based on levels without adding content.
    Returns a list of sections in order of their hierarchy.
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


def extract_html_from_notebook(
    notebook,
    input_dir,
    filename,
    dev_build=False,
    use_base64=False,
):
    """Extracts HTML for cell contents and outputs,
    including code and markdown."""

    html_output = []
    fig_id = 0
    delim = os.path.sep
    aggregated_output = ""

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

    for cell in notebook["cells"]:
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

                # handle stdout
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
                        img_filename = f"fig_{fig_id:02d}.png"

                        output_folder = "output_nb_" + f"{filename.split('.ipynb')[0]}"
                        output_dir = f"{input_dir}{delim}{output_folder}"

                        # if doing a dev build, switch the output directory
                        if dev_build:
                            output_dir = output_dir.replace(
                                "content",
                                "dev",
                            )

                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)

                        save_plot_as_image(
                            img_data,
                            img_filename,
                            output_dir,
                        )

                        output_img_html = textwrap.dedent(f"""
                            <!-- code cell image -->
                            <div class='output-cell'>
                                <img src='{output_folder}{delim}{img_filename}'/>
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


def hash_notebook(notebook_path):
    """Generate a SHA256 hash of the notebook, ignoring outputs/metadata."""

    with open(notebook_path, "r", encoding="utf-8") as f:
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

    # remove notebook metadata
    nb.metadata = {}

    # serialize cleaned notebook
    notebook_json = nbformat.writes(nb, version=4).encode("utf-8")

    # generate hash
    hasher = hashlib.sha256()
    hasher.update(notebook_json)

    return hasher.hexdigest()


def load_notebook_hashes(hash_path):
    """Load previously-recorded hashes notebook hashes"""
    if os.path.exists(hash_path):
        with open(hash_path, "r") as f:
            return json.load(f)
    return {}


def save_notebook_hashes(
    new_hashes,
    hash_path,
):
    """Save updated notebook hashes"""

    # print(f'Saving hashes to {hash_path}')
    with open(hash_path, "w") as f:
        json.dump(new_hashes, f, indent=4)


def get_notebook(
    notebook_path,
    execute,
    timeout=600,
):
    """Get a jupyter notebook object and optionally execute it"""
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    if execute:
        ep = ExecutePreprocessor(
            timeout=timeout,
            kernel_name="python3",
        )
        ep.preprocess(
            notebook,
            {"metadata": {"path": os.path.dirname(notebook_path)}},
        )

    return notebook


def is_notebook_fully_executed(notebook):
    """
    Check if a notebook object has been fully executed.
    Returns True if all code cells have an associated execution_count.
    """
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code" and cell.get("execution_count") is None:
            return False
    return True


def notebook_has_json_output(
    root,
    cwd,
    filename,
    dev_build=False,
):
    """
    Check if the notebook has been fully executed by checking against the
    json output file.
    """
    if dev_build:
        wd = cwd.split("content")[-1].lstrip(os.sep)
        json_path = os.path.join(
            root,
            "dev",
            wd,
            f"{os.path.splitext(filename)[0]}.json",
        )

    else:
        json_path = os.path.join(
            cwd,
            f"{os.path.splitext(filename)[0]}.json",
        )

    execution_check = False
    version_check = False
    commit_check = False

    if os.path.exists(json_path):
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

    return execution_check, version_check, commit_check


def convert_notebooks_to_html(
    input_folder=None,
    use_base64=False,
    write_html=False,
    execute_notebooks=False,
    force_execute_all=False,
    dev_build=False,
    hash_path="notebook_hashes.json",
):
    """
    Executes and converts .ipynb files in the input folder to HTML.
    """

    # ==================== #
    #        SETUP
    # ==================== #

    # if wd doesn't end in 'textbook', look for 'textbook' in the path
    root = os.getcwd()
    while os.path.basename(root) != "textbook":
        root = os.path.dirname(root)

    # default input folder is the 'content' folder, which is
    # the directory from which our site is published
    if not input_folder:
        input_folder = os.path.join(
            root,
            "content",
        )

    notebook_hashes = load_notebook_hashes(hash_path)
    updated_hashes = notebook_hashes.copy()

    # get list of notebooks to skip
    # -----------------------------
    with open(
        os.path.join(
            os.getcwd(),
            "scripts",
            "notebooks_to_skip.json",
        ),
        "r",
    ) as f:
        notebooks_to_skip = json.load(f)

    if dev_build:
        notebooks_to_skip = notebooks_to_skip["dev"]
    else:
        notebooks_to_skip = notebooks_to_skip["skip_execution"]

    # notify user of forced notebook re execution
    if force_execute_all:
        print(
            "The force_execute_all argument has been set to True. All "
            "notebooks will be re-executed unless flagged to be skipped "
            "in the notebooks_to_skip.json file."
        )

    # ==================== #
    # Loop through notebooks
    # ==================== #

    # iterate through input directory and process notebooks
    for current_directory, list_folders, list_files in os.walk(input_folder):
        for filename in list_files:
            if filename.endswith(".ipynb"):
                print(f"\nProcessing notebook: {filename}")

                # get the path to the notebook
                nb_path = os.path.join(
                    current_directory,
                    filename,
                )

                # get the notebook without executing it
                loaded_notebook = get_notebook(
                    nb_path,
                    execute=False,
                )

                # check if the notebook has been fully executed
                notebook_executed, nb_version, commit_check = notebook_has_json_output(
                    root=root,
                    cwd=current_directory,
                    filename=filename,
                    dev_build=dev_build,
                )

                # get current hash of the notebook
                current_hash = hash_notebook(nb_path)

                # default value for skip_notebook, to be updated based
                # on notebooks_to_skip.json per the main loop below
                skip_notebook = False

                # flag for whether the notebook was run
                notebook_was_run = False

                # when force_execute_all is True, all notebooks
                # should be executed unless flagged to be skipped
                # --------------------------------------------------
                if force_execute_all:
                    # update the skip_notebook flag
                    if filename in notebooks_to_skip:
                        skip_notebook = True

                    # check if notebook should be skipped
                    # --------------------------------------------------
                    if skip_notebook:
                        print(
                            f"Notebook '{filename}' has been flagged to be"
                            " skipped. Execution will not be attempted for"
                            " this notebook."
                        )
                    # run all notebooks not flagged to be skipped
                    # --------------------------------------------------
                    else:
                        print(f"Executing {filename}")

                        loaded_notebook = get_notebook(
                            nb_path,
                            execute=True,
                        )
                        notebook_was_run = True
                        print("Notebook has been executed")
                        notebook_executed = is_notebook_fully_executed(loaded_notebook)

                # when force_execute_all is False, notebooks are
                # conditionally executed based on the hash and
                # the skip condition
                # --------------------------------------------------
                else:
                    # check if notebook should be skipped
                    if filename in notebooks_to_skip:
                        skip_notebook = True

                    # 1) skip notebook if indicated in json
                    # --------------------------------------------------
                    if skip_notebook:
                        print(
                            f"Notebook '{filename}' has been flagged to be"
                            " skipped. Execution will not be attempted for"
                            " this notebook."
                        )
                    # 2) if the hash has not changed
                    # --------------------------------------------------
                    elif (filename in notebook_hashes) and (
                        notebook_hashes[filename] == current_hash
                    ):
                        if dev_build:
                            # check if the commit specified to use by the dev build
                            # matches the commit last used to run the notebook per the
                            # commit_check (returned by notebook_has_json_output)
                            #
                            # if the versions do not match, the notebook is flagged to
                            # be re-executed by setting "notebook_executed=False"
                            if dev_build != commit_check:
                                notebook_executed = False
                        if not execute_notebooks:
                            if nb_version == "NA":
                                warnings.warn(
                                    "We were not able to find a previous execution "
                                    "attempt for this notebook. Please consider re-"
                                    "executing the notebook so that we can log the "
                                    "execution metadata."
                                )
                            elif Version(hnn_version) > Version(nb_version):
                                warnings.warn(
                                    "The notebook may have been executed on an "
                                    "older version of hnn-core, as your installed "
                                    f"version ({hnn_version}) is greater than the "
                                    "version used to run the notebook previously "
                                    f"({nb_version}) Please consider re-executing "
                                    "this notebook."
                                )

                        # case when notebook is *not* fully executed
                        if not notebook_executed:
                            print(
                                f"Warning: Notebook {filename} has not been"
                                " fully executed on the specified version"
                                " of hnn-core."
                            )
                            # execute the notebook if execute_notebooks is True
                            if execute_notebooks:
                                loaded_notebook = get_notebook(
                                    nb_path,
                                    execute=True,
                                )
                                notebook_was_run = True
                                print("Notebook has been executed")
                                notebook_executed = is_notebook_fully_executed(
                                    loaded_notebook,
                                )
                            # skip notebook if execute_notebooks is False
                            else:
                                print(
                                    "Notebook execution skipped since"
                                    " execute_notebooks is False."
                                )
                        # case when notebook *is* fully executed
                        else:
                            print(
                                f"Notebook {filename} is unchanged and already"
                                " fully executed"
                            )

                    # 3) if the file is new (un-hashed) or has been changed,
                    # conditionally execute the notebook and update the hash dict
                    # --------------------------------------------------
                    else:
                        print(
                            f"Notebook {filename} is new or has been updated and"
                            " needs to be executed"
                        )
                        # execute the notebook if execute_notebooks is True
                        if execute_notebooks:
                            loaded_notebook = get_notebook(
                                nb_path,
                                execute=True,
                            )
                            notebook_was_run = True
                            print("Notebook has been executed")
                            notebook_executed = is_notebook_fully_executed(
                                loaded_notebook,
                            )
                        # skip notebook if execute_notebooks is False
                        else:
                            print(
                                "Skipping notebook execution since"
                                " execute_notebook is False"
                            )

                # update the hash dictionary
                updated_hashes[filename] = current_hash

                # extract and process the html from the notebook
                html_content = extract_html_from_notebook(
                    loaded_notebook,
                    current_directory,
                    filename,
                    dev_build=dev_build,
                    use_base64=use_base64,
                )

                # optionally write the converted notebook to a
                # standalone html file
                if write_html:
                    if dev_build:
                        dev_dir = current_directory.replace(
                            "content",
                            "dev",
                        )
                        output_file = os.path.join(
                            dev_dir,
                            f"{os.path.splitext(filename)[0]}.html",
                        )
                        if not os.path.exists(dev_dir):
                            os.makedirs(dev_dir)
                    else:
                        output_file = os.path.join(
                            current_directory,
                            f"{os.path.splitext(filename)[0]}.html",
                        )

                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write("<html><body>\n")
                        f.write(html_content)
                        f.write("\n</body></html>")

                # ----------------------------------------
                # generated structured json output
                # ----------------------------------------
                # Note: this section pertains to a planned enhancement
                # to enable inserting sections of a notebook into an
                # html file by specifing the headers to include; e.g.,
                # including [[notebook][start header][end header]] in your
                # .md file would inject only the .html for those header
                # sections into your html output file

                nb_html_json = html_to_json(
                    html_content,
                    filename,
                )

                if dev_build:
                    output_json = os.path.join(
                        current_directory.replace("content", "dev"),
                        f"{os.path.splitext(filename)[0]}.json",
                    )
                else:
                    output_json = os.path.join(
                        current_directory,
                        f"{os.path.splitext(filename)[0]}.json",
                    )

                if notebook_was_run:
                    # Add execution status directly to json output
                    # Track version used in notebook execution
                    nb_html_json = {
                        "full_executed": notebook_executed,
                        "hnn_version": hnn_version,
                        **nb_html_json,
                    }
                    if dev_build:
                        print("Dev version to use:", dev_build)
                        nb_html_json["commit"] = dev_build
                else:
                    # get previously-used hnn version from json file
                    previous_version = "NA"
                    if os.path.exists(output_json):
                        with open(output_json, "r") as f:
                            nb_html_json = json.load(f)
                        # check for hnn_version key
                        if "hnn_version" in nb_html_json:
                            previous_version = nb_html_json["hnn_version"]
                    nb_html_json = {
                        "full_executed": notebook_executed,
                        "hnn_version": previous_version,
                        **nb_html_json,
                    }
                    if dev_build:
                        nb_html_json["commit"] = dev_build

                with open(output_json, "w") as f:
                    json.dump(nb_html_json, f, indent=4)
                # ----------------------------------------

                print(f"Successfully converted '{filename}' to html")

                if not skip_notebook and not notebook_executed:
                    print(
                        f"Warning: the html and json outputs for '{filename}'"
                        " may be incomplete."
                        "\nPlease re-run the script with"
                        " 'execute_notebooks=True' to ensure that the"
                        " notebook outputs are correct."
                    )

    # save updated hashes
    save_notebook_hashes(
        updated_hashes,
        hash_path,
    )

    return


# %%

run_test = False


def test_nb_conversion(input_folder=None):
    convert_notebooks_to_html(
        input_folder=input_folder,
        use_base64=False,
        write_html=True,
        execute_notebooks=True,
    )


if run_test:
    test_nb_conversion("tests")

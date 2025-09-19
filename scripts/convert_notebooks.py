# %%
import base64
import hashlib
import html
import json
import os
import re

import nbformat
import pypandoc
from hnn_core import __version__ as hnn_version
from nbconvert.preprocessors import (
    ClearOutputPreprocessor,
    ExecutePreprocessor,
)


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
    current_html = None
    current_title = None
    current_level = None

    # split html into lines while replacing tabs with spaces
    lines = [
        line.replace("\t", "    ")
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
    use_base64=False,
):
    """Extracts HTML for cell contents and outputs,
    including code and markdown."""

    html_output = []
    fig_id = 0
    delim = os.path.sep
    aggregated_output = ""

    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            # add code cell contents
            html_output.append(
                "<div class='code-cell'>"
                "\n\t<code class='language-python'>"
                f"\n\t\t{cell['source']}"
                "\n\t</code>"
                "\n</div>"
            )

            # add code cell outputs
            for output in cell.get("outputs", []):
                # handle plain outputs (e.g., function returns)
                if "text/plain" in output.get("data", {}):
                    text_output = output["data"]["text/plain"]
                    # escape the '<' and '>' characters which can be
                    # incorrectly interpreted as HTML tags
                    escaped_text_output = html.escape(text_output)

                    # Aggregate plain text outputs
                    aggregated_output += f"\n\t\t{escaped_text_output}"

                # handle stdout (e.g., outputs from print statements)
                if (
                    output.get("output_type") == "stream"
                    and output.get("name") == "stdout"
                ):
                    stream_output = output.get("text", "")
                    # escape < and > characters
                    escaped_stream_output = html.escape(stream_output)

                    aggregated_output += f"\n\t\t{escaped_stream_output}"

                # handle image outputs (e.g., plots) using either Base64
                # encoding or .png files
                if "image/png" in output.get("data", {}):
                    # If there are accumulated outputs, output them first
                    if aggregated_output:
                        html_output.append(
                            "<div class='output-cell'>"
                            "<div class='output-label'>"
                            "\n\tOut:"
                            "\n</div>"
                            "\n\t<div class='output-code'>"
                            f"{aggregated_output}"
                            "\n\t</div>"
                            "\n</div>"
                        )
                        aggregated_output = ""

                    img_data = output["data"]["image/png"]

                    if use_base64:
                        # optional Base64 encoding for image embedding
                        html_output.append(
                            "<div class='output-cell'>"
                            "\n\t<img src='data:image/png;base64,"
                            f"{img_data}'/>"
                            "\n</div>"
                        )
                    else:
                        # save the image as a file and reference it in HTML
                        fig_id += 1
                        if fig_id <= 10:
                            img_filename = f"fig_0{fig_id}.png"
                        else:
                            img_filename = f"fig_{fig_id}.png"

                        output_folder = "output_nb_" + f"{filename.split('.ipynb')[0]}"

                        output_dir = f"{input_dir}{delim}{output_folder}"

                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)

                        save_plot_as_image(
                            img_data,
                            img_filename,
                            output_dir,
                        )
                        html_output.append(
                            "<div class='output-cell'>"
                            f"\n\t<img src='{output_folder}{delim}"
                            f"{img_filename}'/>"
                            "\n</div>"
                        )

                # handle errors
                if output.get("output_type") == "error":
                    error_message = "\n".join(output.get("traceback", []))
                    html_output.append(
                        "<div class='output-cell error'>"
                        "\n\t<pre>"
                        f"\n\t\t{error_message}"
                        "\n\t</pre>"
                        "\n</div>"
                    )

            # If there are any accumulated outputs after processing all
            # outputs for the cell
            if aggregated_output:
                html_output.append(
                    "<div class='output-cell'>"
                    "<div class='output-label'>"
                    "\n\tOut:"
                    "\n</div>"
                    "\n\t<div class='output-code'>"
                    f"{aggregated_output}"
                    "\n\t</div>"
                    "\n</div>"
                )
                aggregated_output = ""

        elif cell["cell_type"] == "markdown":
            # escape < and > characters
            markdown_content = html.escape(cell["source"])

            # html_content = markdown.markdown(markdown_content)

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

            # print(
            #     "Markdown:", type(html_content), html_content[0:50],
            #     '\n',
            #     "Pandoc:", type(test), test[0:50]
            # )

            html_output.append(f"<div class='markdown-cell'>\n\t{html_content}\n</div>")

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
    filename,
):
    """
    Check if the notebook has been fully executed by checking against the
    json output file.
    """
    json_path = os.path.join(root, f"{os.path.splitext(filename)[0]}.json")
    execution_check = False

    if os.path.exists(json_path):
        with open(json_path, "r") as file:
            nb_outputs = json.load(file)
            execution_check = nb_outputs.get("full_executed", False)

    return execution_check


def convert_notebooks_to_html(
    input_folder=None,
    use_base64=False,
    write_html=False,
    execute_notebooks=False,
    force_execute_all=False,
    hash_path="notebook_hashes.json",
):
    """
    Executes and converts .ipynb files in the input folder to HTML.
    """

    if not input_folder:
        input_folder = os.getcwd().split("scripts")[0]
        input_folder += "content"

    # load saved notebook hashes
    notebook_hashes = load_notebook_hashes(hash_path)
    # create a copy of the hashes to update and save
    updated_hashes = notebook_hashes.copy()

    # get list of notebooks to skip
    with open(
        os.path.join(os.getcwd(), "scripts", "notebooks_to_skip.json"),
        "r",
    ) as f:
        notebooks_to_skip = json.load(f)
    notebooks_to_skip = notebooks_to_skip["skip_execution"]

    if force_execute_all:
        print(
            "The force_execute_all argument has been set to True. All "
            "notebooks will be re-executed unless flagged to be skipped "
            "in the notebooks_to_skip.json file."
        )

    # iterate through input directory and process notebooks
    for root, list_folders, list_files in os.walk(input_folder):
        for filename in list_files:
            if filename.endswith(".ipynb"):
                print(f"\nProcessing notebook: {filename}")

                # get current hash of the notebook
                nb_path = os.path.join(root, filename)
                current_hash = hash_notebook(nb_path)

                # get the notebook without executing it
                loaded_notebook = get_notebook(
                    nb_path,
                    execute=False,
                )

                # check if the notebook has been fully executed
                notebook_executed = notebook_has_json_output(
                    root,
                    filename,
                )

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
                        # case when notebook is *not* fully executed
                        if not notebook_executed:
                            print(
                                f"Warning: Notebook {filename} has not been"
                                " fully executed."
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
                                    loaded_notebook
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
                                loaded_notebook
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
                    root,
                    filename,
                    use_base64,
                )

                # optionally write the converted notebook to a
                # standalone html file
                if write_html:
                    output_file = os.path.join(
                        root, f"{os.path.splitext(filename)[0]}.html"
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

                output_json = os.path.join(
                    root,
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

                with open(output_json, "w") as f:
                    json.dump(nb_html_json, f, indent=4)
                # ----------------------------------------

                print(f"Successfully converted '{filename}'to html")

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
def test_nb_conversion(input_folder=None):
    convert_notebooks_to_html(
        input_folder=input_folder,
        use_base64=False,
        write_html=True,
    )


# _ = test_nb_conversion()

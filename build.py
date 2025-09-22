import argparse
import json
import os
import re
import subprocess
import textwrap

import pypandoc
import requests
from hnn_core import __version__ as installed_hnn_version

from scripts.convert_notebooks import convert_notebooks_to_html
from scripts.create_navbar import generate_navbar_html
from scripts.create_page_index import update_page_index


def compile_page_components(dev_build=False):
    """Compile base html components for building webpage"""

    templates_folder = os.path.join(
        os.getcwd(),
        "templates",
    )
    templates = [
        "header",
        "topbar",
        "footer",
        "script",
    ]
    html_parts = {}

    for template in templates:
        templates_path = os.path.join(
            templates_folder,
            f"{template}.html",
        )
        with open(templates_path, "r") as f:
            html_parts[template] = f.read()

    update_page_index()
    navbar_html, ordered_links = generate_navbar_html(dev_build=dev_build)
    html_parts["navbar"] = navbar_html

    return html_parts, ordered_links


def get_page_paths(path=None):
    """
    Recursively get paths to all markdown files in a directory

    Parameters
    ----------
    path : (str | None)
        The root directory to search. If None, defaults to the "content" folder in the
        working directory. This parameter is used internally for recursion and should
        initially be called with None or excluded.

    Returns
    -------
    dict
        A dictionary mapping markdown page paths relative to the "content" directory
        to their absolute paths in the form of: { relative_path: absolute_path, ...}

        This may seem redundant at a first glance, but having the absolute paths as
        well aids greatly in producing the correct path links for local/dev builds
        where the absolute URL is not known

    Notes
    -----
    - README.md files are excluded.
    - Keys in the returned dictionary are paths relative to the "content" directory
    """

    md_pages = {}
    if path is None:
        path = os.path.join(
            os.getcwd(),
            "content",
        )
    directories = os.listdir(path)
    for item in directories:
        item_path = os.path.join(
            path,
            item,
        )
        if os.path.isdir(item_path):
            # add items from new dict into md_pages
            md_pages.update(
                get_page_paths(item_path),
            )
        else:
            if not item == "README.md" and item.endswith(".md"):
                rel_path = os.path.relpath(
                    item_path,
                    start=os.path.join(
                        os.getcwd(),
                        "content",
                    ),
                )
                md_pages[rel_path] = item_path

    return md_pages


def get_html_from_json(
    nb_name,
    nb_path,
):
    """Get the structured .json output for a specified
    .ipynb notebook, extract the relevent html components,
    and return the aggregated html as a string.

    Arguments
    ---------
    nb_name : str
        Jupyter notebook file name
        E.g., 'simulate_erps.ipynb'
    nb_path : str
        Path to notebook
        E.g.: 'website/content/erps/simulate_erps.ipynb'

    Returns
    -------
    agg_html : str
    """
    json_path = nb_path.split(".ipynb")[0] + ".json"
    with open(json_path, "r") as file:
        nb_outputs = json.load(file)
        nb_outputs = nb_outputs.get(nb_name, {})
        agg_html = ""
        for section, content in nb_outputs.items():
            if isinstance(content, dict) and "html" in content:
                agg_html += content["html"]
    return agg_html


def add_notebook_to_html(
    converted_html,
    path,
    md_page,
):
    """
    Function to insert Jupyter notebook html outputs into html
    pages converted from markdown files

    Arguments
    ---------
    converted_html : str

    Returns
    -------
    combined_html : str
    """
    # regex pattern match for "[[notebook_name.ipynb]" with only
    # a single closing bracket, as additional parameters may be
    # included in the notebook specification line
    nb_match_pattern = re.compile(r"\[\[(.+?\.ipynb)\]")
    # notebook specifications with additional arguments will
    # match the exact pattern ".ipynb][" as defined below
    nb_arguments_pattern = ".ipynb]["

    nb_button_indent = "\t\t"

    nb_button = textwrap.dedent("""
        <div class="notebook-download-wrapper">
            <a href='notebook_name' download>
                <button class="notebook-download">
                    <svg xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    <span style="width: 8px"></span>
                    <span>Download Notebook</span>
                </button>
            </a>
        </div>

    """)

    nb_button = textwrap.indent(
        nb_button,
        nb_button_indent,
    )

    output_lines = []
    for line in converted_html.splitlines():
        match = nb_match_pattern.search(line)
        args = nb_arguments_pattern in line

        if match and args:
            notebook_name = match.group(1)
            nb_path = path.split(md_page)[0] + notebook_name
            print(f"nb with args found: {line}")
            print("Argument handling will be added in a future update")
            output_lines.append(line)
        elif match:
            notebook_name = match.group(1)
            nb_path = path.split(md_page)[0] + notebook_name

            # specify notebook button with correct file reference
            nb_button = nb_button.replace(
                "notebook_name",
                notebook_name,
            )
            output_lines.append(
                nb_button,
            )

            # generate and append the notebook html output
            notebook_html = get_html_from_json(notebook_name, nb_path)
            output_lines.append(notebook_html)
        else:
            output_lines.append(line)

    combined_html = "\n".join(output_lines)
    return combined_html


def generate_page_html(
    page_paths,
    dev_build=False,
):
    """
    Converts markdown pages into HTML pages and saves them in the same directory.

    This function handles all processing steps involved in page conversion by calling
    various helper functions (which, in turn, call on imported scripts)

    Parameters
    ----------
    page_paths : dict
        A dictionary mapping markdown page paths relative to the "content" directory
        to their absolute paths in the form: { relative_path: absolute_path, ...}

    dev_build  : bool
        An indicator for doing a "development" build of the website

    Returns
    -------
    None
    """

    # get the .html templates for building pages
    html_parts, ordered_links = compile_page_components(dev_build=dev_build)

    # specify the order of components for assembling pages
    order = [
        "header",
        "navbar",
        "topbar",
        "body",
        "footer",
        "script",
    ]

    # iterate over all markdown pages found in the "content" directory (excluding ...
    # README.md files)
    for md_page, path in page_paths.items():
        page_components = html_parts.copy()

        # get the filename from the realtive path
        md_page = os.path.basename(md_page)
        # get the directory containing the markdown file
        out_directory = path.split(md_page)[0]

        if dev_build:
            out_directory = out_directory.replace(
                "content",
                "dev",
            )

        # remove leading `##_` from page and change extension to .html
        html_page = md_page.split("_", 1)[1]
        html_page = html_page.split(".md")[0] + ".html"

        # set the output path
        out_path = out_directory + html_page

        # update header imports with the relative paths
        # ------------------------------------------------------------
        # get path from root to styles.css
        css_path = os.path.join(
            os.getcwd(),
            "content",
            "assets",
            "styles.css",
        )
        # get the relative path for the styles.css
        relative_css_path = os.path.relpath(
            css_path,
            start=out_directory,
        )
        # update the 'header' import for styles.css
        page_components["header"] = page_components["header"].replace(
            '<link rel="stylesheet" href="styles.css">',
            f'<link rel="stylesheet" href="{relative_css_path}">',
        )

        # get path from root to scripts.js
        js_path = os.path.join(
            os.getcwd(),
            "templates",
            "scripts.js",
        )
        # get relative path for scripts.js
        relative_js_path = os.path.relpath(
            js_path,
            start=out_directory,
        )
        # update the 'header' import for scripts.js
        page_components["header"] = page_components["header"].replace(
            '<script src="scripts.js" defer></script>',
            f'<script src="{relative_js_path}" defer></script>',
        )

        # update 'footer' page_component with the correct links
        # ------------------------------------------------------------
        footer_path = os.path.join(
            os.getcwd(),
            "templates",
            "ordered_page_links.json",
        )

        with open(footer_path, "r") as f:
            ordered_page_links = json.load(f)

        ordered_links = ordered_page_links["links"]
        ordered_titles = ordered_page_links["titles"]

        if dev_build:
            ordered_links = [
                link.replace("content", "dev") for link in ordered_page_links["links"]
            ]
            out_path = out_path.replace("content", "dev")

        location = None
        last_page = len(ordered_links) - 1
        for i, link in enumerate(ordered_links):
            # print(f'{link} | {out_path}')
            if link in out_path:
                location = i

        if location is None:
            prev_page = ""
            prev_title = ""
            next_page = ""
            next_title = ""
        elif location == 0:
            prev_page = "None"
            prev_title = ""
            next_page = ordered_links[location + 1]
            next_title = ordered_titles[location + 1]
        elif location == last_page:
            prev_page = ordered_links[location - 1]
            prev_title = ordered_titles[location - 1]
            next_page = "None"
            next_title = "None"
        else:
            prev_page = ordered_links[location - 1]
            prev_title = ordered_titles[location - 1]
            next_page = ordered_links[location + 1]
            next_title = ordered_titles[location + 1]

        page_components["footer"] = page_components["footer"].replace(
            '<div class="previous-area" data-link="None">',
            f'<div class="previous-area" data-link="{prev_page}">',
        )
        page_components["footer"] = page_components["footer"].replace(
            '<div class="next-area" data-link="None">',
            f'<div class="next-area" data-link="{next_page}">',
        )

        page_components["footer"] = page_components["footer"].replace(
            "<a>PreviousTitle</a>",
            f"<a>{prev_title}</a>",
        )
        page_components["footer"] = page_components["footer"].replace(
            "<a>NextTitle</a>",
            f"<a>{next_title}</a>",
        )

        # load markdown and add yaml metadata
        # ------------------------------------------------------------
        # read markdown file into a string
        with open(path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        path_md_yaml_metadata = os.path.join(
            os.getcwd(),
            "templates",
            "md_yaml_metadata.txt",
        )
        with open(path_md_yaml_metadata) as f:
            md_yaml_metadata = f.read()

        # add check for title section in markdown file

        markdown_text = markdown_text.replace("-->", "-->\n\n" + md_yaml_metadata, 1)

        # convert markdown to html with pypandoc
        # ------------------------------------------------------------
        converted_html = pypandoc.convert_text(
            markdown_text,
            format="md",
            to="html",
            extra_args=[
                "--bibliography=textbook-bibliography.bib",
                "--citeproc",
                "--mathml",
                "-f",
                "markdown-auto_identifiers",
            ],
        )

        # set relative image paths when doing a dev build
        # ------------------------------------------------------------
        # images stored locally in "content" are not automatically propagated to the
        # new dev build folder "dev".
        #
        # html filepaths therefore need to be adjusted for images local to the repo
        #
        # to handle this, we match on the `img src="images` pattern, which
        # indicates a local image. This necessitates that any images are in an
        # "images" folder in "content". We could expand this later to find all images,
        # but for now, all images in "content" should be contained in an "images"
        # sub directory
        if dev_build:
            textbook_root = out_directory.split("textbook")[0] + "textbook"
            dev_path = out_directory.split("textbook")[-1]

            rel_path = os.path.relpath(
                textbook_root,
                out_directory,
            )

            rel_path = rel_path + dev_path.replace("dev", "content")

            converted_html = converted_html.replace(
                'img src="images', f'img src="{rel_path}images'
            )

        combined_html = add_notebook_to_html(
            converted_html,
            path,
            md_page,
        )

        # Aggregate all page components and write output
        # ------------------------------------------------------------
        page_components["body"] = combined_html

        file_contents = ""
        for section in order:
            file_contents += page_components[section]
        file_contents += "\n</body>\n</html>"

        if dev_build:
            # check that folder exists else create it
            os.makedirs(out_directory, exist_ok=True)

        with open(out_path, "w") as out:
            out.write(file_contents)

    return


def main():
    """
    Main function to generate html pages for deployment
    """

    # accept command line arguments
    parser = argparse.ArgumentParser(description="Generate html pages for deployment")
    parser.add_argument(
        "--execute-notebooks",
        action="store_true",
        help="Execute notebooks as needed based on their status "
        "before converting them to HTML.",
    )
    parser.add_argument(
        "--force-execute-all",
        action="store_true",
        help="Force execute all notebooks regardless of their status",
    )


    parser.add_argument(
        "--build-on-dev",
        type=str,
        help="Optionally provide the commit from upstream/master",
    )

    # add all above arguments to the parser
    args = parser.parse_args()

    content_path = os.path.join(
        os.getcwd(),
        "content",
    )
    hash_path = os.path.join(
        os.getcwd(),
        "scripts",
        "notebook_hashes.json",
    )

    # get the version of hnn installed in the environment
    # this is needed for the checks below
    try:
        installed_hnn_commit = subprocess.check_output(["pip", "freeze"], text=True)
        for line in installed_hnn_commit.splitlines():
            if "hnn" in line:
                if "@" in line:
                    installed_hnn_commit = line.split("@")[2].split("#")[0]
                else:
                    installed_hnn_commit = line.split("hnn-core==")[-1]
        print(
            "\nThe installed version of hnn-core being used for this "
            f"build is:\n   {installed_hnn_commit}"
        )

    except Exception as e:
        raise RuntimeError(
            f"Could not import hnn_core and retrieve the latest commit:\n{e}"
        )

    if args.build_on_dev is not None:
        if args.build_on_dev == "master":
            # get the latest commit from upstream/master
            url = (
                "https://api.github.com/repos/jonescompneurolab/hnn-core/commits/master"
            )
            response = requests.get(url)
            response.raise_for_status()
            commit_hash = response.json()["sha"]
            if commit_hash != installed_hnn_commit:
                raise RuntimeError(
                    f"The latest commit on master ({commit_hash}) "
                    "does not match the latest commit on the installed "
                    f"version of hnn-core ({installed_hnn_commit})."
                    "\n"
                    "Try creating an environment by running the following commands "
                    "in a terminal:"
                    "\nmake create-textbook-dev-build"
                    "\nconda activate textbook-dev-build"
                )
        else:
            repo_hash = args.build_on_dev.strip()
            try:
                repo, commit = repo_hash.split(":")

                url = f"https://api.github.com/repos/{repo}/hnn-core/commits/{commit}"
                response = requests.get(url)
                response.raise_for_status()
                commit_hash = response.json()["sha"]

            except Exception as e:
                raise RuntimeError(
                    "the --dev-version argument must be specified in the "
                    'format: --dev-version "your-repository:your-commit-hash" '
                    "\nE.g., a valid input would be: jonescompneurolab:9e14b99"
                    f"\n\nError message: {e}"
                )

            if commit_hash != installed_hnn_commit:
                raise RuntimeError(
                    "The repository and commit you specified: "
                    f"\n   Repository: {repo}"
                    f"\n   Commit: {commit_hash} "
                    "\nDo not match the latest commit on the installed "
                    "version of hnn-core: "
                    f"\n   Installed version / commit: {installed_hnn_commit}"
                    "\nPlease ensure you have installed the proper version of "
                    "hnn-core in your local environment."
                    "\nTry creating an environment by running the following "
                    "commands in a terminal:"
                    "\n   $ make create-textbook-dev-build"
                    "\n   $ conda activate textbook-dev-build"
                    "\n   $ pip install --upgrade --force-reinstall --no-cache-dir "
                    f'"hnn-core[dev] @ git+https://github.com/{repo}/hnn-core.git@{commit}"'
                )
    else:
        commit_hash = False

        latest_stable = requests.get("https://pypi.org/pypi/hnn-core/json").json()[
            "info"
        ]["version"]

        if installed_hnn_version > latest_stable:
            print(
                "Warning: your installed version of hnn-core is ahead of the "
                "current stable version, but you did not use the --build-on-dev "
                "flag:"
                f"\n   Stable version: {latest_stable}"
                f"\n   Installed version: {installed_hnn_version}"
                "\nIt is generally advisable to use the --build-on-dev flag "
                "when generating the textbook on versions of hnn-core that are "
                "ahead of the current stable version."
            )
        elif installed_hnn_version != latest_stable:
            print(
                "\nWarning: you are attempting to build the textbook on a "
                "version of hnn-core that does not match the latest stable version."
                f"\n   Stable version: {latest_stable}"
                f"\n   Installed version: {installed_hnn_version}"
                "\n\nIf your installed version is behind the latest stable "
                "version, pase consider updating your local install before "
                "pushing any changes."
                "\n\nIf your installed version references a particular commit or "
                "branch (e.g.: hnn-core @ git+https://github.com/jonescompneurolab"
                "/hnn-core.git@1413550b2c610b700b7bb12ce7e1ae408ef8d4d3),"
                " we recommend that you use the --build-on-dev flag to specify "
                "the version of hnn-core that should be used."
            )

    convert_notebooks_to_html(
        input_folder=content_path,
        hash_path=hash_path,
        write_html=True,
        execute_notebooks=args.execute_notebooks,
        force_execute_all=args.force_execute_all,
        dev_build=commit_hash,
    )

    page_paths = get_page_paths()

    generate_page_html(
        page_paths,
        dev_build=args.build_on_dev,
    )


if __name__ == "__main__":
    main()

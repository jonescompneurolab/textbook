import json
import re
import os
from pathlib import Path

import pypandoc
import textwrap

from .create_navbar import generate_sidebar_html
from .update_page_index import update_page_index


def _get_markdown_paths(content_path: Path):
    """Recursively get paths to all markdown files in a directory (except READMEs)

    Parameters
    ----------
    content_path : pathlib.Path
        Path to the directory containing all directories which contain markdown files,
        notebook files, and possibly their outputs. This is ALWAYS
        "<textbook_root>/content" and never "<textbook_root>/dev", since we do not
        support "dev"-only versions of markdown files.

    Returns
    -------
    dict
        A dictionary mapping markdown page paths relative to the "content" directory
        to their absolute paths in the form of:

        {
            relative_path: absolute_path,
            ...
        }

        This may seem redundant at a first glance, but having the absolute paths as
        well aids greatly in producing the correct path links for local/dev builds
        where the absolute URL is not known

    Notes
    -----
    - README.md files are excluded.
    """
    # This glob is recursive, see
    # https://docs.python.org/3/library/pathlib.html#pathlib-pattern-language
    paths_all = sorted(content_path.glob("**/*.md"))
    paths_excluding_readme = [p for p in paths_all if ("README" not in str(p))]
    md_paths = {
        str(p.relative_to(content_path)): str(p.absolute())
        for p in paths_excluding_readme
    }
    return md_paths


def _load_simple_templates(templates_path):
    """
    TODO
    """
    templates = [
        "header",
        "topbar",
        "footer",
        "script",
    ]
    html_parts = {}

    for template in templates:
        with open((templates_path / f"{template}.html"), "r") as f:
            html_parts[template] = f.read()

    return html_parts


def _get_html_from_json(
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


def add_nb_to_html(
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
            nb_name = match.group(1)
            nb_path = path.split(md_page)[0] + nb_name
            print(f"nb with args found: {line}")
            print("Argument handling will be added in a future update")
            output_lines.append(line)
        elif match:
            nb_name = match.group(1)
            nb_path = path.split(md_page)[0] + nb_name

            # specify nb button with correct file reference
            nb_button = nb_button.replace(
                "notebook_name",
                nb_name,
            )
            output_lines.append(
                nb_button,
            )

            # generate and append the nb html output
            nb_html = _get_html_from_json(nb_name, nb_path)
            output_lines.append(nb_html)
        else:
            output_lines.append(line)

    combined_html = "\n".join(output_lines)
    return combined_html


def generate_page_html(
    content_path,
    index_path,
    templates_path,
    dev_build=False,
):
    """
    Converts markdown pages into HTML pages and saves them in the same directory.

    This function handles all processing steps involved in page conversion by calling
    various helper functions (which, in turn, call on imported scripts)

    Parameters
    ----------
    content_path : pathlib.Path
        Path to the directory containing all directories which contain markdown files,
        notebook files, and possibly their outputs. This is ALWAYS
        "<textbook_root>/content" and never "<textbook_root>/dev", since "dev" versions
        of required directories will be created as needed. Also, we do not
        support "dev"-only versions of markdown files.
    templates_path : pathlib.Path
        Path to the directory containing various template files. Typically the
        "templates" subdirectory of the textbook root directory
    dev_build : str or bool
        False if not running a dev build. Otherwise, this variable will be
        a string containing the repo and commit hash to be used for the build
    """

    # This loads the generic templates for the header, topbar, footer, and script, but
    # not others.
    html_parts = _load_simple_templates(templates_path)

    # update/load the dynamically-generated
    # page index from the index.json file
    # ----------------------------------
    update_page_index(
        content_path,
        index_path,
    )

    # Create the template for the sidebar/navbar, and the ordering of the pages
    html_parts["navbar"], ordered_links = generate_sidebar_html(index_path)

    # specify the order of components for assembling pages
    order = [
        "header",
        "navbar",
        "topbar",
        "body",
        "footer",
        "script",
    ]

    # Don't need to reload all these things every time on the main loop
    with open((templates_path / "ordered_page_links.json"), "r") as f:
        ordered_page_links = json.load(f)

        ordered_links = ordered_page_links["links"]
        ordered_titles = ordered_page_links["titles"]

        if dev_build:
            ordered_links = [
                link.replace("content", "dev") for link in ordered_page_links["links"]
            ]

    with open((templates_path / "md_yaml_metadata.txt"), "r") as f:
        md_yaml_metadata = f.read()

    # iterate over all markdown pages found in the "content" directory (excluding ...
    # README.md files)
    md_paths = _get_markdown_paths(content_path)
    for md_page, path_old in md_paths.items():
        # Le new pathlib stuff
        md_path = Path(path_old)
        if dev_build:
            # This needs to be done separately in both the notebook-execution code and
            # here in the page-generation code, since there is not necessarily a 1-to-1
            # correspondence between every markdown file and every notebook.
            #
            # Replace "content" parent directory with "dev" one, and safely make it
            new_output_dir_path = Path(str(md_path).replace("content", "dev"))
            new_output_dir_path = new_output_dir_path.parents[0]
            new_output_dir_path.mkdir(parents=True, exist_ok=True)
        else:
            new_output_dir_path = md_path.parents[0]

        page_components = html_parts.copy()

        # get the filename from the realtive path
        md_page = os.path.basename(md_page)
        # get the directory containing the markdown file
        out_directory = path_old.split(md_page)[0]

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
        if dev_build:
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
        with open(path_old, "r", encoding="utf-8") as f:
            markdown_text = f.read()

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

            rel_path = rel_path + dev_path.replace(
                "dev",
                "content",
            )

            converted_html = converted_html.replace(
                'img src="images',
                f'img src="{rel_path}images',
            )

        combined_html = add_nb_to_html(
            converted_html,
            path_old,
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

from copy import deepcopy
from pathlib import Path
import re
import textwrap

import pypandoc

from .create_sidebar_html import create_sidebar_html
from .create_indices import create_hier_index, create_flat_index
from .execute_and_convert_nbs import load_nb_json_output


def _read_nb_json_output_html_contents(
    nb_path,
    nb_json_output_dir,
):
    """
    Get the HTML output from the JSON output file of a notebook.

    Arguments
    ---------
    nb_path : pathlib.Path
        Path to the Jupyter notebook file (.ipynb)
    nb_json_output_dir : pathlib.Path
        Directory where the notebook's JSON output file will be located (and, if it
        exists, is present currently from a prior execution)

    Returns
    -------
    agg_html : str
        The aggregated HTML output inside the JSON output file, corresponding to the
        notebook at `nb_path`.
    """
    # Has content if the file is found, otherwise returns None
    nb_outputs_if_any = load_nb_json_output(nb_path, nb_json_output_dir)
    if nb_outputs_if_any:
        nb_outputs = nb_outputs_if_any.get(nb_path.name, {})
        agg_html = ""
        for section, content in nb_outputs.items():
            if isinstance(content, dict) and "html" in content:
                agg_html += content["html"]
        return agg_html
    else:
        raise FileNotFoundError(
            f"The notebook at '{nb_path}' does not appear to have a corresponding "
            "JSON output file. Please restart the build process with one of the "
            "execution types enabled, in order to execute the notebook. Exiting build "
            "process."
        )


def _add_ordering_to_footer(input_footer, page_idx, flat_index):
    """
    Inject previous/next page navigation links into the footer HTML template.

    This function takes a footer HTML template with placeholder elements and populates
    them with navigation links to the previous and next pages in the website's linear
    page order, as determined from `flat_index`.

    Parameters
    ----------
    input_footer : str
        The footer HTML template string containing placeholder elements that will be
        replaced with actual navigation data. Expected placeholders:
        - '<div class="previous-area" data-link="None">' : Previous page link container
        - '<div class="next-area" data-link="None">' : Next page link container
        - '<a>PreviousTitle</a>' : Previous page title placeholder
        - '<a>NextTitle</a>' : Next page title placeholder
    page_idx : int or None
        The index of the current page in the flat_index list. Use None for pages that
        should not have navigation (e.g., standalone pages not in the main sequence).
    flat_index : list of dict
        A flat (non-hierarchical) list of all pages in sequential navigation order.
        Each dict must contain at least:
        - 'relative_output_html_path' : str, the relative path to the HTML file
        - 'title' : str, the page title to display in navigation links

    Returns
    -------
    str
        A copy of the input footer HTML with navigation placeholders replaced by:
        - Actual page paths in data-link attributes (or "None" for missing pages)
        - Actual page titles in anchor tags (or empty string for missing pages)
    """
    output_footer = deepcopy(input_footer)

    # AES TODO If we want to support "orphan" pages that are not tracked in the main
    # ordering of pages across the website, then the best place to do that is to
    # probably read in some metadata from the orphan markdown page that uses something
    # like "orphan: true". This is getting complicated. As such, after the current
    # refactors, the first IF statement will never succeed.
    if page_idx is None:
        prev_page = ""
        prev_title = ""
        next_page = ""
        next_title = ""
    elif page_idx == 0:
        prev_page = "None"
        prev_title = ""
        next_page = flat_index[page_idx + 1]["relative_output_html_path"]
        next_title = flat_index[page_idx + 1]["title"]
    elif page_idx == (len(flat_index) - 1):
        prev_page = flat_index[page_idx - 1]["relative_output_html_path"]
        prev_title = flat_index[page_idx - 1]["title"]
        next_page = "None"
        next_title = "None"
    else:
        prev_page = flat_index[page_idx - 1]["relative_output_html_path"]
        prev_title = flat_index[page_idx - 1]["title"]
        next_page = flat_index[page_idx + 1]["relative_output_html_path"]
        next_title = flat_index[page_idx + 1]["title"]

    output_footer = output_footer.replace(
        '<div class="previous-area" data-link="None">',
        f'<div class="previous-area" data-link="{prev_page}">',
    )
    output_footer = output_footer.replace(
        '<div class="next-area" data-link="None">',
        f'<div class="next-area" data-link="{next_page}">',
    )
    if prev_title:
        output_footer = output_footer.replace(
            "<a>PreviousTitle</a>",
            f"<a>{prev_title}</a>",
        )
    else:
        output_footer = output_footer.replace(
            "<a>PreviousTitle</a>",
            "",
        )
    if next_title and next_title != "None":
        output_footer = output_footer.replace(
            "<a>NextTitle</a>",
            f"<a>{next_title}</a>",
        )
    else:
        output_footer = output_footer.replace(
            "<a>NextTitle</a>",
            "",
        )

    return output_footer


def _add_nb_to_html(
    converted_html,
    input_dir_path,
    is_dev_build,
):
    """
    Insert Jupyter notebook HTML outputs into HTML converted from markdown page files.

    This function searches for notebook references in the markdown-converted HTML using
    the syntax '[[<notebook_name>.ipynb]]' and replaces them with both the notebook's
    executed output HTML content and a download button. The function processes the HTML
    line-by-line to locate and replace notebook placeholders.

    Arguments
    ---------
    converted_html : str
        HTML content converted from a markdown page file, which may contain notebook
        reference placeholders in the format '[[<notebook_name>.ipynb]]'.
    input_dir_path : pathlib.Path
        Path to the directory containing the markdown page file and referenced
        notebooks. This is used to locate the notebook files (.ipynb). However, the JSON
        output file location for the notebook depends on if we are doing a "dev" build
        or not, and the output location will be inferred based on `is_dev_build`.
    is_dev_build : bool
        Whether this is a development build. If True, notebook JSON outputs are read
        from their '<textbook-root>/dev/**' directory instead of their source
        '<textbook-root>/content/**' directory.

    Returns
    -------
    combined_html : str
        The modified HTML with notebook placeholders replaced by:
        - A download button linking to the .ipynb file
        - The notebook's executed output HTML content (from the JSON output file)
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
            nb_path = input_dir_path / nb_name
            print(f"nb with args found: {line}")
            print("Argument handling will be added in a future update")
            output_lines.append(line)
        elif match:
            nb_name = match.group(1)
            nb_path = input_dir_path / nb_name

            # specify nb button with correct file reference
            nb_button = nb_button.replace(
                "notebook_name",
                nb_name,
            )
            output_lines.append(
                nb_button,
            )
            # generate and append the nb html output
            # --------------------------------------
            # Ugh, if we're doing a "dev" build, then we need to load the "dev" version
            # of the notebook's JSON output file. For this, we need to reconstruct that
            # location:
            if is_dev_build:
                nb_json_output_dir = Path(str(nb_path).replace("content", "dev"))
                nb_json_output_dir = nb_json_output_dir.parents[0]
            else:
                nb_json_output_dir = nb_path.parents[0]

            nb_html = _read_nb_json_output_html_contents(nb_path, nb_json_output_dir)
            output_lines.append(nb_html)
        else:
            # This line is very important! This is where most of the md-page content
            # passes through.
            output_lines.append(line)

    combined_html = "\n".join(output_lines)
    return combined_html


def generate_page_html(
    content_path,
    templates_path,
    is_dev_build,
    save_indices=False,
    hier_index_path=None,
    flat_index_path=None,
):
    """
    Convert markdown page files (and embedded notebooks) into HTML pages and save them.

    This function creates page navigation indices, loads HTML templates, converts
    markdown to HTML using Pandoc, embeds Jupyter notebook outputs, and assembles the
    final HTML pages with navigation and styling.

    Arguments
    ---------
    content_path : pathlib.Path
        Path to the '<textbook-root>/content' directory containing all markdown page
        files, notebook files, and their outputs. This is ALWAYS
        '<textbook-root>/content' and never '<textbook-root>/dev', since "dev" versions
        of output files and directories will be created automatically as needed based on
        `is_dev_build`. Note that we do not support "dev"-only versions of markdown page
        files or notebooks themselves.
    templates_path : pathlib.Path
        Path to the directory containing HTML template files. Typically the
        '<textbook-root>/templates/' subdirectory.
    is_dev_build : bool
        Whether this is a development build. If True, output HTML files are written to
        '<textbook-root>/dev/**' directories instead of '<textbook-root>/content/**'
        directories.
    save_indices : bool, optional
        Whether to save the hierarchical and flat page indices as JSON files for
        debugging purposes. Default is False. This descends from the '--save-indices'
        argument passed to the CLI of 'build.py'.
    hier_index_path : pathlib.Path, optional
        Path where the hierarchical index JSON file should be saved if `save_indices` is
        True. The hierarchical index is used for the sidebar navigation and contains page
        names, nested sections, and titles.
    flat_index_path : pathlib.Path, optional
        Path where the flat index JSON file should be saved if `save_indices` is True.
        The flat index contains a sequential list of all pages with their input/output
        paths and titles, determining the linear page navigation order.

    Returns
    -------
    None
        This function writes HTML files to disk but does not return any value.
    """
    print("Building: Beginning build of website HTML pages.")
    css_path = content_path / "assets" / "styles.css"
    js_path = templates_path / "scripts.js"

    # Create and possibly save the dynamically-generated hierarchical-index
    # ----------------------------------------------------------------------------------
    # The "hierarchical index" is only used for the sidebar. It contains only simple
    # page names, their nested sections if any, and the titles of each section and/or
    # page. It does NOT contain output filenames or anything like it. It is unchanged
    # from before the Great Refactors.
    hier_index = create_hier_index(
        content_path,
        save_indices,
        hier_index_path,
    )

    # Create and possibly save the dynamically-generated flat-index
    # ----------------------------------------------------------------------------------
    # The "flat index" is used for the sidebar and everything else in the website. Its
    # order is the true order of all pages (but NO sections!). Each element contains a
    # dictionary with the following keys, along with the appropriate values for each:
    #
    # - "absolute_input_md_path": Absolute filesystem path to the existing 'input'
    #     markdown file with actual page contents.
    # - "absolute_output_html_path": Absolute filesystem path to the not-yet-existing
    #     'output' HTML file corresponding to this markdown page.
    # - "relative_output_html_path": Relative path to the not-yet-existing 'output' HTML
    #     file corresponding to this markdown page. This is the path that is relative to
    #     what the website itself will consider the "root directory", where "/textbook"
    #     is the highest-order directory. As an example, this will be something like
    #     "/textbook/content/05_erps/erps_in_gui.html".
    # - "title": The title string extracted from the markdown file, meant for display on
    #     the webpage. This is identical to the page's title as in the
    #     hierarchical-index.
    #
    # Importantly, this is what determines the appropriate output paths and filenames
    # for every markdown page file. This does NOT create those directories, but instead
    # only figures out the paths.
    flat_index = create_flat_index(
        content_path,
        is_dev_build,
        save_indices,
        flat_index_path,
    )

    # Begin building each of the separate HTML components:
    # ----------------------------------------------------------------------------------
    # Specify the order of components for assembling pages
    order = [
        "header",
        "sidebar",
        "topbar",
        "body",
        "footer",
        "script",
    ]
    # Each of these components is handled with different complexity:
    # - header: We simply load a generic template for this.
    # - sidebar: This is created using its own module at `create_sidebar_html.py`.
    # - topbar: We simply load a generic template for this.
    # - body: This is where the magic happens; the main loop gradually constructs this
    #     from a combination of processed markdown content and (if necessary) processed
    #     notebook output content.
    # - footer: First, we load a generic template for this, but then page-specific
    #     navigation links are added to it for every page, inside the main loop.
    # - script: We simply load a generic template for this.

    html_parts = {}
    generic_templates = [
        "header",
        "topbar",
        "footer",
        "script",
    ]
    for template in generic_templates:
        with open((templates_path / f"{template}.html"), "r") as f:
            html_parts[template] = f.read()

    # Create the template for the sidebar based on both indices:
    html_parts["sidebar"] = create_sidebar_html(hier_index, flat_index)

    # Load some "MD+YAML" metadata to go at the top of every markdown page, but before
    # it is sent to PyPandoc:
    with open((templates_path / "md_yaml_metadata.txt"), "r") as f:
        md_yaml_metadata = f.read()

    # Main loop
    # ----------------------------------------------------------------------------------
    for page_idx, page in enumerate(flat_index):
        # Unique-ify our components for this page
        page_components = html_parts.copy()

        # Set some convenience variables for our many different paths
        input_md_path = page["absolute_input_md_path"]
        input_dir_path = page["absolute_input_md_path"].parents[0]
        abs_out_html_path = page["absolute_output_html_path"]
        abs_out_dir_path = page["absolute_output_html_path"].parents[0]

        # Create the output directory for the final HTML page (if necessary)
        # ------------------------------------------------------------------------------
        # This needs to be done separately in both the notebook-execution code before
        # and here in the page-generation code, since there is not necessarily a 1-to-1
        # correspondence between every markdown file and every notebook.
        abs_out_dir_path.mkdir(parents=True, exist_ok=True)

        # Update header imports with the relative paths
        # ------------------------------------------------------------------------------
        relative_css_path = css_path.relative_to(abs_out_dir_path, walk_up=True)
        page_components["header"] = page_components["header"].replace(
            '<link rel="stylesheet" href="styles.css">',
            f'<link rel="stylesheet" href="{relative_css_path}">',
        )

        relative_js_path = js_path.relative_to(abs_out_dir_path, walk_up=True)
        page_components["header"] = page_components["header"].replace(
            '<script src="scripts.js" defer></script>',
            f'<script src="{relative_js_path}" defer></script>',
        )

        # Update 'footer' page_component with navigation to prev/next page
        # ------------------------------------------------------------------------------
        page_components["footer"] = _add_ordering_to_footer(
            page_components["footer"],
            page_idx,
            flat_index,
        )

        # Load the actual markdown content, add yaml metadata, and preprocess it
        # ------------------------------------------------------------------------------
        with open(input_md_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        # add check for title section in markdown file
        markdown_text = markdown_text.replace("-->", "-->\n\n" + md_yaml_metadata, 1)

        # Convert markdown to html with pypandoc
        # ------------------------------------------------------------------------------
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

        # Set relative image paths when doing a dev build
        # ------------------------------------------------------------------------------
        # Images stored locally in "content", and which are not generated by notebooks,
        # are not automatically propagated to the new "dev" build directories.
        # Therefore, links to local images in HTML files need to be adjusted for the
        # "content"/"dev" switch.
        #
        # To handle this, we match on the `img src="images` pattern, which
        # indicates a local image. This necessitates that any images are in an
        # "images" folder in "content".
        #
        # TODO: We could expand this later to find all images, but for now, all images
        # in "content" should be contained in an "images" sub directory.
        if is_dev_build:
            # Input paths including `input_dir_path` always under "contents", never
            # "dev"
            relative_local_content_image_path = abs_out_dir_path.relative_to(
                input_dir_path,
                walk_up=True,
            )
            # Recreate a "content" version of the path to "images"
            relative_local_content_image_path = (
                relative_local_content_image_path / "images"
            )
            relative_local_content_image_path = str(
                relative_local_content_image_path
            ).replace("dev", "content")
            # Insert the link
            converted_html = converted_html.replace(
                'img src="images',
                f'img src="{relative_local_content_image_path}',
            )

        # Add any notebook content
        # ------------------------------------------------------------------------------
        # This line is very important, since all markdown-page content is replaced by it.
        combined_html = _add_nb_to_html(
            converted_html,
            input_dir_path,
            is_dev_build,
        )

        # Aggregate all page components and write output
        # ------------------------------------------------------------------------------
        page_components["body"] = combined_html

        file_contents = ""
        for section in order:
            file_contents += page_components[section]
        file_contents += "\n</body>\n</html>"

        with open(abs_out_html_path, "w") as out:
            out.write(file_contents)

    print("Building: Finished building of website HTML pages.")

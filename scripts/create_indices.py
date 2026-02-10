from copy import deepcopy
import json
from pathlib import Path


def _get_title(file_path):
    """
    Extract the title from a markdown file by searching for the '# Title: ' string.

    This function reads through a markdown file line-by-line looking for a special
    comment tag in the format '# Title: <title text>'. This tag is used to specify the
    display title for pages and sections in the website navigation.

    Arguments
    ---------
    file_path : pathlib.Path or str
        Path to the markdown file (either a markdown page file or 'README.md' for
        sections) from which to extract the title.

    Returns
    -------
    str
        The title text extracted from the '# Title: ' tag, with the trailing newline
        removed if present. Returns "NA" if no title tag is found in the file.
    """
    match_string = "# Title: "
    with open(file_path, "r") as file:
        title = "NA"
        for line in file:
            if match_string in line:
                title = line[9:]
                if title.endswith("\n"):
                    title = title[0:-1]
    return title


def create_hier_index(content_path, save_indices=False, hier_index_path=None):
    """
    Create a hierarchical index of all markdown pages and sections for sidebar navigation.

    This function recursively scans the '<textbook-root>/content' directory to build a
    nested dictionary structure representing the website's page hierarchy. The index
    includes page titles and section names, preserving the directory structure for use
    in the navigation sidebar. Unlike the "flat index", this includes section
    information from README.md files.

    Arguments
    ---------
    content_path : pathlib.Path
        Path to the '<textbook-root>/content' directory containing markdown page files and
        section subdirectories.
    save_indices : bool, optional
        Whether to save the hierarchical index as a JSON file for debugging purposes.
        Default is False. This descends from the '--save-indices' argument passed to the
        CLI of 'build.py'.
    hier_index_path : pathlib.Path, optional
        Path where the hierarchical index JSON file should be saved if `save_indices` is
        True.

    Returns
    -------
    dict
        A nested dictionary representing the hierarchical structure of pages and sections.
        Structure:
        - For sections (directories with README.md): {<dir_name>: [<section_title>,
          <nested_dict>]}
        - For pages (markdown files): {<file_name>: <page_title>}
        - Keys are file/directory names, values are either titles (for pages) or
          [title, nested_dict] pairs (for sections)

    Notes
    -----
    This function differs from create_flat_index() in that it:
    - Preserves the nested directory structure
    - Includes section information from README.md files
    - Uses recursive traversal to build the hierarchy
    - Does NOT compute output file paths
    """

    def _recur_create_hier_index(input_path):
        """
        Recursively build the hierarchical index structure.

        This is done independently of the "flat index" due to recursion and because we
        DO care about the section-defining "README.md" files for the "hierarchical
        index", unlike in the case of the "flat index".
        """
        page_index = {}
        directory_contents = sorted(Path(input_path).glob("*"))
        for item_path in directory_contents:
            readme_path = item_path / "README.md"
            if item_path.is_dir() and readme_path.exists():
                # Check for README inside any directories, which indicate a directory to be
                # indexed
                section_title = _get_title(readme_path)
                # Recursively search directories for files to index
                page_index[item_path.name] = [
                    section_title,
                    _recur_create_hier_index(item_path),
                ]
            elif (item_path.suffix == ".md") and (item_path.name != "README.md"):
                # Check for non-README markdown files
                page_index[item_path.name] = _get_title(item_path)
        return page_index

    hier_index = _recur_create_hier_index(content_path)

    # Save our hierarchical index, if desired:
    if save_indices and hier_index_path:
        with open(hier_index_path, "w", encoding="utf-8") as f:
            json.dump(hier_index, f, ensure_ascii=False, indent=4)

    return hier_index


def create_flat_index(
    content_path, is_dev_build, save_indices=False, flat_index_path=None
):
    """
    Create a flat index of all markdown pages with their paths and titles.

    This function scans the "<textbook-root>/content" directory for markdown page files
    (excluding README.md files) and creates a sequential list. Each element contains a
    dictionary with the following keys, along with the appropriate values for each:
    - "absolute_input_md_path": Absolute filesystem path to the existing 'input'
        markdown file with actual page contents.
    - "absolute_output_html_path": Absolute filesystem path to the not-yet-existing
        'output' HTML file corresponding to this markdown page.
    - "relative_output_html_path": Relative path to the not-yet-existing 'output' HTML
        file corresponding to this markdown page. This is the path that is relative to
        what the website itself will consider the "root directory", where "/textbook"
        is the highest-order directory. As an example, this will be something like
        "/textbook/content/05_erps/erps_in_gui.html".
    - "title": The title string extracted from the markdown file, meant for display on
        the webpage. This is identical to the page's title as in the
        hierarchical-index.

    Importantly, this is what determines the appropriate output paths and filenames for
    every markdown page file. This does NOT create the necessary directories however, it
    only figures out what they *should* be.

    Arguments
    ---------
    content_path : pathlib.Path
        Path to the '<textbook-root>/content' directory containing markdown page files.
    is_dev_build : bool
        Whether this is a development build. If True, output paths point to
        '<textbook-root>/dev/**' directories instead of '<textbook-root>/content/**'
        directories.
    save_indices : bool, optional
        Whether to save the flat index as a JSON file for debugging purposes. Default is
        False. This descends from the '--save-indices' argument passed to the CLI of
        'build.py'.
    flat_index_path : pathlib.Path, optional
        Path where the flat index JSON file should be saved if `save_indices` is True.

    Returns
    -------
    list of dict
        A sequential list of all pages in navigation order. Each dict element contains:
        - 'absolute_input_md_path' : pathlib.Path, input markdown file path
        - 'absolute_output_html_path' : pathlib.Path, output HTML file path
        - 'relative_output_html_path' : str, website-relative HTML path (e.g.,
          '/textbook/content/page.html')
        - 'title' : str, page title extracted from markdown file
    """
    # Get all markdown files, but excluding 'README.md' files. We don't care about the
    # sections.
    # ----------------------------------------------------------------------------------
    # This glob is recursive, see
    # https://docs.python.org/3/library/pathlib.html#pathlib-pattern-language
    paths_all = sorted(content_path.glob("**/*.md"))
    paths_excluding_readme = [p for p in paths_all if ("README" not in str(p))]

    # Create the initial flat index, containing only input files:
    # ----------------------------------------------------------------------------------
    flat_index = [
        {
            "absolute_input_md_path": input_path,
            "title": _get_title(input_path),
        }
        for input_path in paths_excluding_readme
    ]

    # Update the flat index to include output files:
    # ----------------------------------------------------------------------------------
    for page in flat_index:
        abs_inp_md_path = page["absolute_input_md_path"]
        # First, let's make the new filename, independent of any parent directories:
        new_filename = abs_inp_md_path.stem.split("_", 1)[1] + ".html"

        # Let's determine the new absolute output directory path, which will contain the
        # new output file. If we're usind a "dev" version, let's also change it to be a
        # "dev" version of the directory path:
        abs_out_dir_path = abs_inp_md_path.parents[0]
        if is_dev_build:
            # In this page-generation case, we do NOT necessarily know how many levels
            # are between the `dev` directory and the `abs_out_dir_path`, since not all
            # markdown pages are inside sections.
            #
            # Replace "content" parent directory with "dev" one
            abs_out_dir_path = Path(str(abs_out_dir_path).replace("content", "dev"))
        abs_out_html_path = abs_out_dir_path / new_filename

        # Let's determine the new "relative" output path, which will be used to insert
        # the proper links in the website HTML for pages relative to the website root:
        #
        # Since "content" is always a child of the textbook root, parents[1] can be used
        # to give us the textbook root.
        rel_out_html_path = abs_out_html_path.relative_to(content_path.parents[1])
        # Finally, change our path to treat the website root as root:
        rel_out_html_path = "/" + str(rel_out_html_path)

        # Add our new paths to the dictionary of the individual markdown page:
        page.update(
            {
                "absolute_output_html_path": abs_out_html_path,
                "relative_output_html_path": rel_out_html_path,
            }
        )

    # Save our flat index, if desired:
    if save_indices and flat_index_path:
        flat_index_serializable = deepcopy(flat_index)
        for idx, page in enumerate(flat_index):
            for key, val in page.items():
                flat_index_serializable[idx][key] = str(val)
        with open(flat_index_path, "w", encoding="utf-8") as f:
            json.dump(flat_index_serializable, f, ensure_ascii=False, indent=4)

    return flat_index

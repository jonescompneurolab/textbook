import textwrap


def _create_toggle_section(toggle_label):
    """
    Create HTML for a collapsible section header in the sidebar navigation.

    This function generates the opening HTML structure for a collapsible/expandable
    section in the sidebar. The section includes a toggle icon (+/-) and a label, and
    is designed to contain nested page links that can be shown or hidden by the user.

    Arguments
    ---------
    toggle_label : str
        The display text for the collapsible section header (e.g., "Getting Started",
        "Using HNN API"). This is the section title extracted from the 'README.md'
        file that should be in the subdirectory for that section.

    Returns
    -------
    str
        HTML string for the collapsible section with its title
    """
    section = textwrap.dedent(f"""
        <div class="sidebar-list">
            <a id="sidebar-section" onclick="toggleSubmenu(event)">
                <span class="toggle-icon">+</span>
                {toggle_label}
            </a>
            <div class="submenu">
    """)
    section = textwrap.indent(
        section,
        "\t\t",
    )
    return section


def _build_dynamic_sidebar(hier_index, flat_index):
    """
    Build the dynamic navigation component of the sidebar from page indices.

    This function processes the hierarchical index to generate HTML links for all pages
    and sections in the sidebar. It handles both top-level pages (non-collapsible links)
    and nested sections (collapsible groups of links). The flat index is used to lookup
    the relative file paths for each page based on matching titles.

    Arguments
    ---------
    hier_index : dict
        Hierarchical index containing the nested structure of pages and sections, as
        created by `scripts/create_indices.py::create_hier_index()`. Structure:
        - For sections (directories with README.md): {<dir_name>: [<section_title>,
          <nested_dict>]}
        - For pages (markdown files): {<file_name>: <page_title>}
        - Keys are file/directory names, values are either titles (for pages) or
          [title, nested_dict] pairs (for sections)
    flat_index : list of dict
        A sequential list of all pages in navigation order, as created by
        `scripts/create_indices.py::create_flat_index()`. Each dict element contains:
        - 'absolute_input_md_path' : pathlib.Path, input markdown file path
        - 'absolute_output_html_path' : pathlib.Path, output HTML file path
        - 'relative_output_html_path' : str, website-relative HTML path (e.g.,
          '/textbook/content/page.html')
        - 'title' : str, page title extracted from markdown file

    Returns
    -------
    str
        HTML string containing all navigation links for the sidebar
    """
    dynamic_links_html = ""
    indent = "\t\t"
    for section, contents in hier_index.items():
        # For pages that are not nested in a toggle
        if isinstance(contents, str):
            label = contents  # The title of this non-dropdown Markdown page
            for page in flat_index:
                if page["title"] == contents:
                    link = page["relative_output_html_path"]

            dynamic_links_html += f'\n{indent}<a href="{link}">{label}</a>'
        # For pages that are nested in a toggle
        elif isinstance(contents, list):
            toggle_label = contents[0]
            toggle_contents = contents[1]
            # Add toggle <div> sections and link
            dynamic_links_html += _create_toggle_section(toggle_label)
            # Add pages under toggle
            for sub_filename, sub_title in toggle_contents.items():
                label = sub_title
                for page in flat_index:
                    if page["title"] == sub_title:
                        link = page["relative_output_html_path"]
                dynamic_links_html += f'\n{indent + indent}<a href="{link}">{label}</a>'

            # Close toggle <div> sections
            dynamic_links_html += f"\n{indent}\t</div>"
            dynamic_links_html += f"\n{indent}</div>"

    return dynamic_links_html


def create_sidebar_html(
    hier_index,
    flat_index,
    add_workshop_link=False,
):
    """
    Generate complete sidebar HTML with static header and dynamic navigation links.

    This function assembles the full sidebar HTML by combining static elements with
    dynamic navigation links generated from the page indices. The sidebar includes the
    site title, installation link, optional workshop link, and a hierarchical navigation
    structure with collapsible sections.

    Arguments
    ---------
    hier_index : dict
        Hierarchical index containing the nested structure of pages and sections, as
        created by `scripts/create_indices.py::create_hier_index()`. Structure:
        - For sections (directories with README.md): {<dir_name>: [<section_title>,
          <nested_dict>]}
        - For pages (markdown files): {<file_name>: <page_title>}
        - Keys are file/directory names, values are either titles (for pages) or
          [title, nested_dict] pairs (for sections)
    flat_index : list of dict
        A sequential list of all pages in navigation order, as created by
        `scripts/create_indices.py::create_flat_index()`. Each dict element contains:
        - 'absolute_input_md_path' : pathlib.Path, input markdown file path
        - 'absolute_output_html_path' : pathlib.Path, output HTML file path
        - 'relative_output_html_path' : str, website-relative HTML path (e.g.,
          '/textbook/content/page.html')
        - 'title' : str, page title extracted from markdown file
    add_workshop_link : bool, optional
        TODO: Experimental. Whether to include a workshop page link in the sidebar
        header. Default is False. When True, adds a styled button linking to the
        workshop page. Note: formatting may need updates for current styling.

    Returns
    -------
    str
        Complete sidebar HTML string
    """

    base_indent = "\t"

    # create mySidebar
    # create the "sidebar header"
    # ---------------------------------
    # notes:
    #   the "sidebar header" contains the HNN name and the installation page link,
    #   which are not generated dynamically from the directory/file structure
    sidebar_html = textwrap.dedent("""
        <div id="mySidebar" class="sidebar">
            <div class="sidebar-close">
                <svg class="popup-symbol" viewBox="0 0 24 24">
                    <use href="#popup-symbol" />
                </svg>
            </div>
            <div class="sidebar-header">
                <div class="title-row">
                    <a>
                        Human Neocortical Neurosolver
                    </a>
                    <br>
                        <svg class="collapse-icon" viewBox="0 0 16 16"
                            xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 9H4v1h5V9z"/>
                            <path fill-rule="evenodd" clip-rule="evenodd"
                                d="M5 3l1-1h7l1 1v7l-1 1h-2v2l-1 1H3l-1-1V6l1-1h2V3zm1
                                    2h4l1 1v4h2V3H6v2zm4 1H3v7h7V6z"/>
                        </svg>
                </div>
                <div class="install-row">
                    <a class="download-icon-link" aria-label="Installation">
                        <svg class="download-icon" viewBox="0 0 24 24" fill="none"
                            xmlns="http://www.w3.org/2000/svg">
                        <path d="M7 19L5.78311 18.9954C3.12231 18.8818 1 16.6888 1
                            14C1 11.3501 3.06139 9.18169 5.66806 9.01084C6.78942
                            6.64027 9.20316 5 12 5C15.5268 5 18.4445 7.60822 18.9293
                            11.001L19 11C21.2091 11 23 12.7909 23 15C23 17.1422 21.316
                            18.8911 19.1996 18.9951L17 19M12 10V18M12 18L15 15M12 18L9
                            15"
                           stroke-width="2" stroke-linecap="round"
                           stroke-linejoin="round"/>
                        </svg>
                    </a>
                    <a>
                        Installation
                    </a>
                </div>
            </div>
    """)

    sidebar_html = textwrap.indent(
        sidebar_html,
        base_indent,
    )

    # optionally add a workshop link after the header
    # -----------------------------------------------
    # notes:
    #   the formatting likely needs to be updated to accommodate this addition
    #   as the styling has changed since the last workshop (April 2025)
    if add_workshop_link:
        page_link = "https://jonescompneurolab.github.io/textbook/tests/workshop.html"
        workshop_link = textwrap.dedent(f"""
            <a href="{page_link}">
                <div>
                    <code class="workshop-button">
                        Workshop Page
                    </code>
                </div>
            </a>
        """)
        workshop_link = textwrap.indent(
            workshop_link,
            base_indent,
        )

        sidebar_html += workshop_link

    # build the page navigation elements
    # from the updated page index
    # ----------------------------------
    dynamic_links_html = _build_dynamic_sidebar(hier_index, flat_index)

    close_sidebar = textwrap.dedent("""
            <div style='height: 30px;'></div>
        </div>
    """)
    close_sidebar = textwrap.indent(close_sidebar, "\t")

    # add page navigation to sidebar html
    # ----------------------------------
    sidebar_html += dynamic_links_html
    sidebar_html += close_sidebar

    return sidebar_html

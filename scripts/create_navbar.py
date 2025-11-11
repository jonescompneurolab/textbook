# %% ######################################################################
import json
import os
import textwrap

# %% #####################################
# functions to generate html for the
# dynamic components of the sidebar
# ########################################


def get_absolute_paths(path=None):
    """
    Get paths to all .md pages to be converted to html
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
            md_pages.update(get_absolute_paths(item_path))
        else:
            if not item == "README.md" and item.endswith(".md"):
                # get the relative path for the web content only
                location = item_path.split(os.getcwd() + os.sep)[1]
                location = location.split(item)[0]

                page = item.split("_", 1)[1]
                page = page.split(".md")[0] + ".html"

                md_pages[item] = "/textbook/" + location + page
    return md_pages


def create_page_link(
    file,
    label,
    page_paths,
    indent,
    dev_build=False,
):
    file_path = page_paths[file]
    if dev_build:
        file_path = file_path.replace(
            "content",
            "dev",
        )
    return f'\n{indent}<a href="{file_path}">{label}</a>'


def create_toggle_section(toggle_label):
    section = textwrap.dedent(f"""
        <div class="sidebar-list">
            <a id="sidebar-header" onclick="toggleSubmenu(event)">
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


def build_navbar(json_page_index):
    dynamic_links_html = ""
    indent = "\t\t"
    page_paths = get_absolute_paths()
    ordered_links = []
    ordered_pages = []
    for section, contents in json_page_index.items():
        # For pages that are not nested in a toggle
        if isinstance(contents, str):
            dynamic_links_html += create_page_link(
                section,
                contents,
                page_paths,
                indent,
            )
            ordered_links.append(page_paths[section])
            ordered_pages.append(contents)
        # For pages that are nested in a toggle
        elif isinstance(contents, list):
            toggle_label = contents[0]
            toggle_contents = contents[1]
            # Add toggle <div> sections and link
            dynamic_links_html += create_toggle_section(toggle_label)
            # Add pages under toggle
            for sub_page, sub_name in toggle_contents.items():
                dynamic_links_html += create_page_link(
                    sub_page,
                    sub_name,
                    page_paths,
                    indent + indent,
                )
                ordered_links.append(page_paths[sub_page])
                ordered_pages.append(sub_name)
            # Close toggle <div> sections
            dynamic_links_html += f"\n{indent}\t</div>"
            dynamic_links_html += f"\n{indent}</div>"

        # save ordered page links
        out_path = os.getcwd() + "/templates/ordered_page_links.json"
        ordered_page_links = {}
        ordered_page_links["links"] = ordered_links
        ordered_page_links["titles"] = ordered_pages

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                ordered_page_links,
                f,
                ensure_ascii=False,
                indent=4,
            )

    return dynamic_links_html, ordered_links


# %% #####################################
# build the complete sidebar html
# ########################################


def generate_sidebar_html(
    index_path,
    add_workshop_link=False,
):
    """
    Function to generate the sidebar ("mySidebar"), including both the static elements
    and the dynamic elements. The dynamic elements are built from the structure
    specified in the index.json file, which is updated when this function runs

    Inputs
    ------
    dev_build : str or bool
        False if not running a dev build. Otherwise, this variable will be
        a string containing the repo and commit hash to be used for the build

    Returns
    -------
    html : str
        The complete sidebar html contained in a string
    ordered_links :
    """

    base_indent = "\t"

    # create mySidebar
    # create the "navbar header"
    # ---------------------------------
    # notes:
    #   the "navbar header" contains the HNN name and the installation page link,
    #   which are not generated dynamically from the directory/file structure
    sidebar_html = textwrap.dedent("""
        <div id="mySidebar" class="sidebar">
            <div class="sidebar-close">
                <svg class="popup-symbol" viewBox="0 0 24 24">
                    <use href="#popup-symbol" />
                </svg>
            </div>
            <div class="navbar-header">
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
                    <a class="download-icon-link">
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

    # AES updating of the index has been moved upwards into generate_page_html
    with open(index_path, "r",) as f:
        json_page_index = json.load(f)

    # build the page navigation elements
    # from the updated page index
    # ----------------------------------
    dynamic_links_html, ordered_links = build_navbar(json_page_index)

    close_sidebar = textwrap.dedent("""
            <div style='height: 30px;'></div>
        </div>
    """)
    close_sidebar = textwrap.indent(close_sidebar, "\t")

    # add page navigation to sidebar html
    # ----------------------------------
    sidebar_html += dynamic_links_html
    sidebar_html += close_sidebar

    return sidebar_html, ordered_links


# print(generate_sidebar_html())

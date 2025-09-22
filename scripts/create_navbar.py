# %% ######################################################################
import json
import os
import textwrap

# %% ######################################################################


def generate_navbar_html(dev_build=False):
    """Function to generate the navbar from the structure specified
    in the index.json file"""

    base_indent = "\t"
    indent = "\t\t"  # need to deprecate this but it's currently used later

    # create mySidebar
    # create the header "navbar header"
    # using textwrap.dedent() to make is easier to use html style in python
    # without introducing extra indentation in the final html
    html = textwrap.dedent("""
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
                            xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
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

    html = textwrap.indent(
        html,
        base_indent,
    )

    # workshop_link = (
    #     f'\n{indent}<a href="https://jonescompneurolab.github.io/textbook/tests/workshop.html">'
    #     + f"\n{indent}<div>"
    #     + f'\n{indent}\t<code class="workshop-button">Workshop Page</code>'
    #     + f"\n{indent}</div>"
    #     + f"\n{indent}</a>"
    # )

    # html += workshop_link

    # load page index .json file
    index_path = os.getcwd() + "/index.json"

    with open(index_path, "r") as f:
        json_page_index = json.load(f)

    def get_absolute_paths(path=None):
        """Get paths to all .md pages to be converted to html"""
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
        dev_build=dev_build,
    ):
        file_path = page_paths[file]
        if dev_build:
            file_path = file_path.replace(
                "content",
                "dev",
            )
        return f'\n{indent}<a href="{file_path}">{label}</a>'

    def create_toggle_section(toggle_label):
        section = (
            f'\n{indent}<div class="sidebar-list">'
            + f'\n{indent}\t<a id="sidebar-header"'
            + ' onclick="toggleSubmenu(event)">'
            + f'\n{indent}<span class="toggle-icon">+</span>'
            + f"\n{indent}{indent}{toggle_label}"
            + f"\n{indent}\t</a>"
            + f'\n{indent}\t<div class="submenu">'
        )
        return section

    def build_navbar(json_page_index):
        navbar_html = ""
        page_paths = get_absolute_paths()
        ordered_links = []
        ordered_pages = []
        for section, contents in json_page_index.items():
            # For pages that are not nested in a toggle
            if isinstance(contents, str):
                navbar_html += create_page_link(
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
                navbar_html += create_toggle_section(toggle_label)
                # Add pages under toggle
                for sub_page, sub_name in toggle_contents.items():
                    navbar_html += create_page_link(
                        sub_page,
                        sub_name,
                        page_paths,
                        indent + indent,
                    )
                    ordered_links.append(page_paths[sub_page])
                    ordered_pages.append(sub_name)
                # Close toggle <div> sections
                navbar_html += f"\n{indent}\t</div>"
                navbar_html += f"\n{indent}</div>"

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

        return navbar_html, ordered_links

    navbar_html, ordered_links = build_navbar(json_page_index)
    html += navbar_html
    html += "\n\t<div style='height: 30px;'></div>"
    html += "\n\t</div>"
    return html, ordered_links


# print(generate_navbar_html())

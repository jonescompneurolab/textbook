import os
import argparse
import re
import pypandoc
import json
from scripts.create_page_index import update_page_index
from scripts.create_navbar import generate_navbar_html
from scripts.convert_notebooks import convert_notebooks_to_html


def compile_page_components():
    """Compile base html components for building webpage"""

    templates_folder = os.path.join(os.getcwd(), 'templates')
    templates = ['header', 'topbar', 'footer', 'script']
    html_parts = {}

    for template in templates:
        templates_path = os.path.join(templates_folder, f'{template}.html')
        with open(templates_path, 'r') as f:
            html_parts[template] = f.read()

    update_page_index()
    navbar_html, ordered_links = generate_navbar_html()
    html_parts['navbar'] = navbar_html

    return html_parts, ordered_links


def get_page_paths(path=None):
    """Get paths to all .md pages to be converted to html"""

    md_pages = {}
    if path is None:
        path = os.path.join(os.getcwd(), "content")
    directories = os.listdir(path)
    for item in directories:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            # add items from new dict into md_pages
            md_pages.update(get_page_paths(item_path))
        else:
            if not item == "README.md" and item.endswith(".md"):
                md_pages[item] = item_path

    return md_pages


def generate_page_html(page_paths):
    """
    """

    # get the .html templates for building pages
    html_parts, ordered_links = compile_page_components()

    # specify the order of components for assembling pages
    order = [
        'header',
        'navbar',
        'topbar',
        'body',
        'footer',
        'script',
    ]

    # print(ordered_links)

    for md_page, path in page_paths.items():
        page_components = html_parts.copy()

        # get the directory containing the markdown file
        out_directory = path.split(md_page)[0]

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
        page_components['header'] = page_components['header'].replace(
            '<link rel="stylesheet" href="styles.css">',
            f'<link rel="stylesheet" href="{relative_css_path}">'
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
        page_components['header'] = page_components['header'].replace(
            '<script src="scripts.js" defer></script>',
            f'<script src="{relative_js_path}" defer></script>'
        )

        # update 'footer' page_component with the correct links
        # ------------------------------------------------------------
        footer_path = os.path.join(
            os.getcwd(),
            'templates',
            'ordered_page_links.json'
        )

        with open(footer_path, 'r') as f:
            ordered_page_links = json.load(f)

        ordered_links = ordered_page_links['links']
        ordered_titles = ordered_page_links['titles']

        location = None
        last_page = len(ordered_links)-1
        for i, link in enumerate(ordered_links):
            # print(f'{link} | {out_path}')
            if link in out_path:
                location = i
        if location == 0:
            prev_page = "None"
            prev_title = ""
            next_page = ordered_links[location+1]
            next_title = ordered_titles[location+1]
        elif location == last_page:
            prev_page = ordered_links[location-1]
            prev_title = ordered_titles[location-1]
            next_page = "None"
            next_title = "None"
        else:
            prev_page = ordered_links[location-1]
            prev_title = ordered_titles[location-1]
            next_page = ordered_links[location+1]
            next_title = ordered_titles[location+1]

        page_components['footer'] = page_components['footer'].replace(
            '<div class="previous-area" data-link="None">',
            f'<div class="previous-area" data-link="{prev_page}">'
        )
        page_components['footer'] = page_components['footer'].replace(
            '<div class="next-area" data-link="None">',
            f'<div class="next-area" data-link="{next_page}">'
        )

        page_components['footer'] = page_components['footer'].replace(
            '<a>PreviousTitle</a>',
            f'<a>{prev_title}</a>'
        )
        page_components['footer'] = page_components['footer'].replace(
            '<a>NextTitle</a>',
            f'<a>{next_title}</a>'
        )

        # load markdown and add yaml metadata
        # ------------------------------------------------------------
        # read markdown file into a string
        with open(path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        path_md_yaml_metadata = os.path.join(
            os.getcwd(),
            'templates',
            'md_yaml_metadata.txt',
        )
        with open(path_md_yaml_metadata) as f:
            md_yaml_metadata = f.read()

        # add check for title section in markdown file

        markdown_text = markdown_text.replace(
            '-->',
            '-->\n\n'+md_yaml_metadata,
            1
        )

        # convert markdown to html with pypandoc
        # ------------------------------------------------------------
        converted_html = pypandoc.convert_text(
            markdown_text,
            format='md',
            to='html',
            extra_args=[
                "--bibliography=textbook-bibliography.bib",
                "--citeproc",
                "--mathml",
                "-f",
                "markdown-auto_identifiers",
            ],
        )

        # optionally add Jupyter notebook ouptuts to converted html
        # ------------------------------------------------------------

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
            json_path = nb_path.split('.ipynb')[0] + '.json'
            with open(json_path, 'r') as file:
                nb_outputs = json.load(file)
                nb_outputs = nb_outputs.get(nb_name, {})
                agg_html = ''
                for section, content in nb_outputs.items():
                    if isinstance(content, dict) and 'html' in content:
                        agg_html += content['html']
            return agg_html

        def add_notebook_to_html(converted_html):
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

            nb_button="""
        <div class="notebook-download-wrapper">
            <a href='notebook_name' download>
                <button class="notebook-download">
                    <svg xmlns="http://www.w3.org/2000/svg" 
                        width="20" height="20" viewBox="0 0 24 24" fill="none" 
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    <span style="width: 8px"></span>
                    <span>Download Notebook</span>
                </button>
            </a>
        </div>

    """

            output_lines = []
            for line in converted_html.splitlines():
                match = nb_match_pattern.search(line)
                args = nb_arguments_pattern in line

                if match and args:
                    notebook_name = match.group(1)
                    nb_path = path.split(md_page)[0] + notebook_name
                    print(f'nb with args found: {line}')
                    print(
                        'Argument handling will be added in a '
                        'future update'
                    )
                    output_lines.append(line)
                elif match:
                    notebook_name = match.group(1)
                    nb_path = path.split(md_page)[0] + notebook_name

                    # specify notebook button with correct file
                    nb_button = nb_button.replace(
                        'notebook_name',
                        notebook_name,
                    )
                    output_lines.append(nb_button,)

                    # generate and append the notebook html output
                    notebook_html = get_html_from_json(notebook_name, nb_path)
                    output_lines.append(notebook_html)
                else:
                    output_lines.append(line)

            combined_html = "\n".join(output_lines)
            return combined_html

        combined_html = add_notebook_to_html(converted_html)

        # Aggregate all page components and write output
        # ------------------------------------------------------------
        page_components['body'] = combined_html

        file_contents = ""
        for section in order:
            file_contents += page_components[section]
        file_contents += '\n</body>\n</html>'

        with open(out_path, 'w') as out:
            out.write(file_contents)

    return


def main():
    """
    Main function to generate html pages for deployment
    """

    # accept command line arguments
    parser = argparse.ArgumentParser(
        description="Generate html pages for deployment"
    )
    parser.add_argument(
        "--execute-notebooks",
        action="store_true",
        help="Execute notebooks as needed based on their status "
             "before converting them to HTML."
    )
    parser.add_argument(
        "--force-execute-all",
        action="store_true",
        help="Force execute all notebooks regardless of their status"
    )
    args = parser.parse_args()

    content_path = os.path.join(os.getcwd(), "content")
    hash_path = os.path.join(os.getcwd(), "scripts", "notebook_hashes.json")

    convert_notebooks_to_html(
        input_folder=content_path,
        hash_path=hash_path,
        write_html=True,
        execute_notebooks=args.execute_notebooks,
        force_execute_all=args.force_execute_all,
    )

    page_paths = get_page_paths()
    generate_page_html(page_paths)


if __name__ == "__main__":
    main()

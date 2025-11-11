import json
from pathlib import Path


# AES TODO: "Index" and "ordered_page_links" should probably be greatly expanded to
# prevent frequent re-searching of Markdown and other files in
# generate_page_html.py. For example, "Index" could have titles removed and consist only
# of the hierarchical mapping, while "ordered_page_links" could be changed to something
# like "page_metadata", where each Section (dir containing md files) and markdown
# filenames each contain child data like "title", "relative root path" (to textbook
# root), "output path" (where their output html goes, if necessary), etc.

def _get_title(file_path):
    file = open(file_path, "r")
    title = "NA"
    for line in file:
        if "# Title: " in line:
            title = line[9:]
            if title.endswith("\n"):
                title = title[0:-1]
    return title


def _index_md_pages(input_path):
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
                _index_md_pages(item_path),
            ]
        elif (item_path.suffix == ".md") and (item_path.name != "README.md"):
            # Check for non-README markdown files
            page_index[item_path.name] = _get_title(item_path)
    return page_index


def update_page_index(content_path, index_path):
    index_dict = _index_md_pages(content_path)

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_dict, f, ensure_ascii=False, indent=4)

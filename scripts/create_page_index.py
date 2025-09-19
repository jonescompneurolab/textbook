# %% ######################################################################
import json
import os

# %% ######################################################################


def get_title(file_path):
    file = open(file_path, "r")
    title = "NA"
    for line in file:
        if "# Title: " in line:
            title = line[9:]
            if title.endswith("\n"):
                title = title[0:-1]
    return title


def index_md_pages(path):
    page_index = {}
    directory_contents = os.listdir(path)
    directory_contents.sort()
    # print('dc: ', directory_contents)
    for item in directory_contents:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            # Check for README, which indicated a directory to be indexed
            readme_path = os.path.join(item_path, "README.md")
            if os.path.isfile(readme_path):
                # Recursively search directories for files to index
                section_title = get_title(readme_path)
                page_index[item] = [
                    section_title,
                    index_md_pages(item_path),
                ]
        else:
            # Add entry for .md file
            if item.endswith(".md"):
                if not item == "README.md":
                    page_index[item] = get_title(item_path)
    return page_index


def update_page_index():
    home = os.getcwd() + "/content"
    indexed_pages = index_md_pages(home)

    with open("index.json", "w", encoding="utf-8") as f:
        json.dump(indexed_pages, f, ensure_ascii=False, indent=4)


# update_page_index()

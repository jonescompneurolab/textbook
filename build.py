import argparse
from pathlib import Path

from scripts.execute_and_convert_nbs import execute_and_convert_nbs_to_json
from scripts.generate_page_html import generate_page_html
from scripts.get_commit_hash import get_commit_hash

textbook_root_path = Path(__file__).parents[0]


def main():
    """
    Main function to generate html pages for deployment

    AES TODO: describe required file structure
    """

    # accept command line arguments
    parser = argparse.ArgumentParser(
        description="Generate html pages for deployment",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--execution-filter",
        action="store",
        default="no-execution",
        choices=[
            "no-execution",
            "execute-updated-unskipped-notebooks",
            "execute-all-unskipped-notebooks",
            "execute-absolutely-all-notebooks",
        ],
        help="""Specify different criteria for which notebooks you want to execute before converting
them to HTML. The default is 'no-execution'. The four options are below, in order of
more execution:\n
- 'no-execution': This will not execute any notebooks. You may receive warnings if
  specific notebooks should be executed.\n
- 'execute-updated-unskipped-notebooks': Execute only notebooks which have been
  updated/changed or are new, excluding notebooks flagged for skipping.\n
- 'execute-all-unskipped-notebooks': Execute all notebooks except those flagged for
  skipping.\n
- 'execute-absolutely-all-notebooks': Execute all notebooks.
""",
    )
    parser.add_argument(
        "--build-on-dev",
        type=str,
        help="Optionally provide the commit from upstream/master",
    )
    # AES Not sure we want to support this, but leaving it as an option since I assume
    # this case was the reason why `os.getcwd()` is used so much in the scripts instead
    # of absolute paths.
    parser.add_argument(
        "--custom-root-path",
        type=str,
        help="Optionally provide a different 'root' location for your textbook files",
    )

    # add all above arguments to the parser
    args = parser.parse_args()

    if args.custom_root_path:
        root_path = args.custom_root_path
    else:
        root_path = textbook_root_path

    content_path = Path(root_path / "content")
    index_path = Path(root_path / "index.json")
    nb_hash_path = Path(root_path / "scripts" / "nb_hashes.json")
    nb_skip_path = Path(root_path / "scripts" / "nbs_to_skip.json")
    templates_path = Path(root_path / "templates")

    print(
        f"Configuration: Choosing notebooks based on '--execution-filter={args.execution_filter}'"
    )

    commit_hash = get_commit_hash(build_on_dev_arg=args.build_on_dev)

    execute_and_convert_nbs_to_json(
        content_path,
        nb_hash_path,
        nb_skip_path,
        args.execution_filter,
        dev_build=commit_hash,
        write_standalone_html=True,
    )

    generate_page_html(
        content_path,
        index_path,
        templates_path,
        dev_build=args.build_on_dev,
    )


if __name__ == "__main__":
    main()

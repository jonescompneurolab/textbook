# %%

import pytest  # noqa
import sys

from pathlib import Path

# Add project root to sys.path to allow importing from scripts folder
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(project_root),
)

import scripts.convert_notebooks as convert_notebooks  # noqa

############################################################
# Fixtures
# --------------------


@pytest.fixture
def _create_notebook():
    def _create(
        code=True,
        markdown=True,
        executed=False,
    ):
        cells = []
        if code:
            outputs = []
            if executed:
                outputs = [
                    {
                        "output_type": "stream",
                        "name": "stdout",
                        "text": "hello\n",
                    }
                ]
            cells.append(
                {
                    "cell_type": "code",
                    "source": "print('hello')",
                    "execution_count": 1 if executed else None,
                    "outputs": outputs,
                    "metadata": {},
                }
            )
        if markdown:
            cells.append(
                {
                    "cell_type": "markdown",
                    "source": "# Title",
                    "metadata": {},
                }
            )
        nb_content = {
            "cells": cells,
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 2,
        }
        return nb_content

    return _create


############################################################
# Helper Functions
# --------------------


def _create_skip_json(
    skip_list=None,
    dev_list=None,
):
    skip_json = {
        "dev": dev_list if dev_list is not None else [],
        "skip_execution": skip_list if skip_list is not None else [],
    }
    return skip_json


############################################################
# Integration tests
# --------------------


# def test_convert_notebooks_to_html(tmp_path):
    # add test


############################################################
# Unit Tests
# ----------------------


@pytest.mark.parametrize(
    "initial_execution_status, final_execution_status, notebook_was_run",
    [
        # nb unexecuted before run, nb remains unexecuted, nb execution skipped
        (False, False, False),
        # nb executed before run, nb remains executed, nb execution skipped
        (True, True, False),
    ],
)
def test_notebook_is_skipped(
    monkeypatch,  # used to create "mock" (faked) outputs for functions
    _create_notebook,  # helper function to create an executed/unexecuted notebook
    initial_execution_status,  # sets the execution state of the mock notebook
    final_execution_status,  # the expected execution status of the notebook
    notebook_was_run,  # the expected notebook_was_run return from _process_notebook
):
    """
    If the notebook filename is in notebooks_to_skip, the function
    should exit early.
    This function is parameterized for executed and unexecuted notebooks

    This tests the case where:
        - Versions/commits are in agreement
        - The hash does not change
        - The current notebook is in the "notebooks_to_skip" list
        - _should_execute_notebook is not invoked as execution is skipped

    notebooks_to_skip is currently the *first* check and has the highest priority,
    regardless of the values of execute_notebooks and force_execute_all passed
    to the _process_notebook function
    """
    notebook = _create_notebook(
        executed=initial_execution_status,
    )

    nb_name = "skipme.ipynb"
    skip_json = _create_skip_json(skip_list=[nb_name])

    fake_hash = "1793996"
    old_version = "0.4.1"
    old_commit = "a2f98d30def56b3789c1b72cf827191508398b70"

    # Use monkeypatch to set outputs for the following
    # helper functions called inside _convert_notebooks
    # --------------------------------------------------

    # set _notebook_has_json_output to return the execution
    # status as specified in the parameterization
    monkeypatch.setattr(
        convert_notebooks,
        "_notebook_has_json_output",
        lambda *a, **kw: (
            initial_execution_status,  # set execution status of mock notebook
            old_version,  # version_check (not relevant to the test)
            old_commit,  # commit_check (not relevant to the test)
        ),
    )
    # set _hash_notebook to return a fake hash
    monkeypatch.setattr(
        convert_notebooks,
        "_hash_notebook",
        lambda *a, **kw: fake_hash,
    )
    # set notebooks to skip
    monkeypatch.setattr(
        convert_notebooks,
        "_load_notebooks_to_skip",
        lambda *a, **kw: skip_json,
    )

    # _get_notebook is only needed for the returned notebook object,
    # not for validating the logic/returns of _get_notebook itself
    monkeypatch.setattr(
        convert_notebooks,
        "_get_notebook",
        lambda *a, **kw: notebook,
    )

    # Check that returns for _process_notebook match what we expect.
    # Returns: (current_hash, loaded_notebook, notebook_executed, notebook_was_run)
    #
    # Notes:
    #   - Since _get_notebook is "mocked," valid values for root, nb_path, and
    #     current_directory are not needed, hence the passing of "not_needed"
    #
    #   - Skipping should always override execution even when execute_notebooks
    #     is set to True
    result = convert_notebooks._process_notebook(
        root="not_needed",
        nb_path="not_needed",
        filename=nb_name,
        current_directory="not_needed",
        notebook_hashes={},
        notebooks_to_skip=[nb_name],
        execute_notebooks=True,  # set to True but should not trigger
        force_execute_all=True,  # set to True but should not trigger
        dev_build=False,
    )

    expected = (
        fake_hash,  # hash not changed
        notebook,  # notebook not changed
        final_execution_status,  # execution status of notebook should not change
        notebook_was_run,  # in this test, notebook_was_run should always return False
    )
    assert result == expected


@pytest.mark.parametrize(
    "force_execute_flag, initial_execution_status, "
    "fake_old_hash, fake_new_hash, should_execute",
    [
        # case where force_execute_all is False
        # -------------------------------------
        # unexecuted nb, hash changed, should be executed
        (False, False, "1793996", "2793996", True),
        # unexecuted nb, hash unchanged, should be executed
        (False, False, "1793996", "1793996", True),
        # executed nb, hash unchanged, should not be execute
        (False, True, "1793996", "1793996", False),
        # executed nb, hash changed, should be executed
        (False, True, "1793996", "2793996", True),
        # case where force_execute_all is True
        # -------------------------------------
        (True, False, "1793996", "2793996", True),
        (True, False, "1793996", "1793996", True),
        # the case below is the only one that should yield a different result
        # from the tests above
        (True, True, "1793996", "1793996", True),
        (True, True, "1793996", "2793996", True),
    ],
)
def test_notebook_executed_on_hash_change(
    monkeypatch,  # used to create "mock" (faked) outputs for functions
    _create_notebook,  # helper function to create an executed/unexecuted notebook
    force_execute_flag,
    initial_execution_status,  # sets the execution state of the mock notebook,
    fake_old_hash,
    fake_new_hash,
    should_execute,
):
    """
    The test logic presumes the notebook is *not* flagged ot be skipped and that
    execute_notebooks = True

    If the notebook hash has changed, _process_notebook should always execute the
    notebook regardless of the execution status in the notebook json.

    If the hash has not changed but the notebook is also not fully executed, the
    notebook should be executed; otherwise, if the notebook is already fully
    executed, then it should not be executed again

    This tests the case where:
        - Versions/commits are in agreement
        - The hash has changed since the last run
        - The current notebook is not in the "notebooks_to_skip" list
    """
    notebook = _create_notebook(
        executed=initial_execution_status,
    )

    nb_name = "changed_notebook.ipynb"
    skip_json = _create_skip_json(
        skip_list=[],
    )

    old_version = "0.4.1"
    old_commit = "a2f98d30def56b3789c1b72cf827191508398b70"

    # Use monkeypatch to set outputs for the following
    # helper functions called inside _convert_notebooks
    # --------------------------------------------------

    # set _notebook_has_json_output to return the execution
    # status as specified in the parameterization
    monkeypatch.setattr(
        convert_notebooks,
        "_notebook_has_json_output",
        lambda *a, **kw: (
            initial_execution_status,  # set execution status of mock notebook
            old_version,  # version_check (not relevant to the test)
            old_commit,  # commit_check (not relevant to the test)
        ),
    )

    # set _hash_notebook to return a fake, *new* hash, simulating a changed nb
    monkeypatch.setattr(
        convert_notebooks,
        "_hash_notebook",
        lambda *a, **kw: fake_new_hash,
    )

    # set notebooks to skip (none in this case)
    monkeypatch.setattr(
        convert_notebooks,
        "_load_notebooks_to_skip",
        lambda *a, **kw: skip_json,
    )

    # Track whether _execute_notebook is actually called
    executed_flag = {}
    executed_notebook = _create_notebook(executed=True)

    def fake_execute(nb_path):
        executed_flag["called"] = True
        return executed_notebook, True, True

    monkeypatch.setattr(
        convert_notebooks,
        "_execute_notebook",
        # fake notebook execution per function above
        # returns: executed_notebook, notebook_was_run, notebook_executed
        fake_execute,
    )

    # _get_notebook is only needed for the returned notebook object,
    # not for validating the logic/returns of _get_notebook itself
    monkeypatch.setattr(
        convert_notebooks,
        "_get_notebook",
        lambda *a, **kw: notebook,
    )

    # execute_notebooks = False if force_execute_all = True, else True
    # this is to test that force_execute_all supersedes the execute_notebooks flag
    standard_execute_flag = True
    if force_execute_flag:
        standard_execute_flag = False


    # --------------------------------------------------
    # Call _process_notebook
    # --------------------------------------------------
    result = convert_notebooks._process_notebook(
        root="not_needed",
        nb_path="not_needed",
        filename=nb_name,
        current_directory="not_needed",
        notebook_hashes={
            nb_name: fake_old_hash  # mock outdated hash loaded from json
        },
        notebooks_to_skip=skip_json,  # passing an empty dictionary
        execute_notebooks=standard_execute_flag,
        force_execute_all=force_execute_flag,
        dev_build=False,
    )

    # --------------------------------------------------
    # Check expected return values
    # Returns: (current_hash, loaded_notebook, notebook_executed, notebook_was_run)
    # --------------------------------------------------
    expected_notebook = executed_notebook if executed_flag.get("called") else notebook
    confirm_notebook_executed = (
        True if executed_flag.get("called") else initial_execution_status
    )
    confirm_notebook_run = executed_flag.get("called", False)

    expected = (
        fake_new_hash,  # new hash returned
        expected_notebook,  # return notebook after execution
        confirm_notebook_executed,  # notebook_executed after execution
        confirm_notebook_run,  # notebook_was_run = executed
    )
    assert result == expected

    # first, look for the "called" key; if not found, return False
    # result should match "should_execute", confirming that _execute_notebook
    # is run when we determine that it should be run
    assert executed_flag.get("called", False) is should_execute


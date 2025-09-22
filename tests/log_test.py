# %%
import importlib
import logging

import scripts.check_nb_versions as check_nb_versions

importlib.reload(logging)
logging.basicConfig(level=logging.DEBUG)

# %%
importlib.reload(check_nb_versions)
check_nb_versions.check_version()

# %%

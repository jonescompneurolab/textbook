
.PHONY: all build clean create-conda-env create-conda-env-mpi

HNN_VERSION := 0.4.2
OS := $(shell uname -s)

all: build

build:
	python build.py

execute-notebooks:
	python build.py --execute-notebooks

clean:
	rm -rf content/*.html
	rm -rf content/*/*.html

create-conda-env-mpi:
	conda env create --yes --file environment.yml --name textbook-env-mpi
	conda install -y -n textbook-env-mpi conda-forge::openmpi conda-forge::mpi4py
	@CONDA_ENV_PATH=$$(conda run -n textbook-env-mpi python -c "import os; print(os.environ['CONDA_PREFIX'])"); \
	mkdir -p $$CONDA_ENV_PATH/etc/conda/activate.d ; \
	mkdir -p $$CONDA_ENV_PATH/etc/conda/deactivate.d ; \
	if [ "$(OS)" = "Darwin" ]; then \
		echo "export OLD_DYLD_FALLBACK_LIBRARY_PATH=\$$DYLD_FALLBACK_LIBRARY_PATH" >> "$$CONDA_ENV_PATH/etc/conda/activate.d/env_vars.sh"; \
		echo "export DYLD_FALLBACK_LIBRARY_PATH=\$$DYLD_FALLBACK_LIBRARY_PATH:$$CONDA_ENV_PATH/lib" >> "$$CONDA_ENV_PATH/etc/conda/activate.d/env_vars.sh"; \
		echo "export DYLD_FALLBACK_LIBRARY_PATH=\$$OLD_DYLD_FALLBACK_LIBRARY_PATH" >> "$$CONDA_ENV_PATH/etc/conda/deactivate.d/env_vars.sh"; \
		echo "unset OLD_DYLD_FALLBACK_LIBRARY_PATH" >> "$$CONDA_ENV_PATH/etc/conda/deactivate.d/env_vars.sh"; \
	elif [ "$(OS)" = "Linux" ]; then \
		echo "export OLD_LD_LIBRARY_PATH=\$$LD_LIBRARY_PATH" >> "$$CONDA_ENV_PATH/etc/conda/activate.d/env_vars.sh"; \
		echo "export LD_LIBRARY_PATH=\$$LD_LIBRARY_PATH:$$CONDA_ENV_PATH/lib" >> "$$CONDA_ENV_PATH/etc/conda/activate.d/env_vars.sh"; \
		echo "export LD_LIBRARY_PATH=\$$OLD_LD_LIBRARY_PATH" >> "$$CONDA_ENV_PATH/etc/conda/deactivate.d/env_vars.sh"; \
		echo "unset OLD_LD_LIBRARY_PATH" >> "$$CONDA_ENV_PATH/etc/conda/deactivate.d/env_vars.sh"; \
	fi; \
	conda run -n textbook-env-mpi pip install 'hnn_core[dev]==$(HNN_VERSION)'; \
	echo "Conda environment 'textbook-env-mpi' successfully created."

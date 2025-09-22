
.PHONY: all build clean create-conda-env create-conda-env-mpi

HNN_VERSION := 0.4.2
OS := $(shell uname -s)

all: build

build:
	python build.py

force-execute-all-notebooks:
	python build.py --force-execute-all

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

create-textbook-dev-build:
	@# Check if textbook-dev-build is active and, if so, deactivate it
	-@if [ "$$CONDA_DEFAULT_ENV" = "textbook-dev-build" ]; then \
		echo "Deactivating environment 'textbook-dev-build' ..."; \
		conda deactivate; \
	fi

	@# Check if the environment already exists
	@# If it does, remove it and notify the user
	-@conda env list | grep -q "^textbook-dev-build\s" && \
	{ \
		echo "Attempting to remove 'textbook-dev-build' environment"; \
		conda env remove -y --name textbook-dev-build && \
		echo "Environment 'textbook-dev-build' successfully removed."; \
	} || true

	@# Create the new conda environment from environment.yml
	conda env create --yes --file environment.yml --name textbook-dev-build

	@# Install additional packages into the environment
	conda install -y -n textbook-dev-build conda-forge::openmpi conda-forge::mpi4py

	@# Get the path to the newly created conda environment and
	@# create directories for environment activation/deactivation scripts
	@# Then, configure library paths depending on the operating system
	@CONDA_ENV_PATH=$$(conda run -n textbook-dev-build python -c "import os; print(os.environ['CONDA_PREFIX'])"); \
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

	@# Get the latest commit hash of hnn-core master branch
	LATEST_HASH=$$(git ls-remote https://github.com/jonescompneurolab/hnn-core.git master | cut -f1);
	
	@# Install hnn-core in developer mode, forcing reinstall without cache
	conda run -n textbook-dev-build pip install --upgrade --force-reinstall --no-cache-dir "hnn-core[dev] @ git+https://github.com/jonescompneurolab/hnn-core.git@master"; \

	echo "Conda environment 'textbook-dev-build' successfully created."
	echo -e "\n\nActivate your environment with 'conda activate textbook-dev-build'"
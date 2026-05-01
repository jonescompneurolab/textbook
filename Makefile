
.PHONY: all build clean create-textbook-stable-env create-textbook-dev-env

HNN_VERSION := 0.5.0
OS := $(shell uname -s)

# Function to create and configure a conda environment with library paths
# Usage: $(call create-and-configure-env,env-name,force-recreate)
# - env-name: name of the conda environment
# - force-recreate: if "true", deactivate and remove existing environment before creating
define create-and-configure-env
	@# If the second flag is true, then deactivate the env if it is present,
        @# then remove it if it exists.
	$(if $(filter true,$(2)),\
		-@if [ "$$CONDA_DEFAULT_ENV" = "$(1)" ]; then \
			echo "Deactivating environment '$(1)' ..."; \
			conda deactivate; \
		fi
		-@conda env list | grep -q "^$(1)\s" && \
		{ \
			echo "Attempting to remove '$(1)' environment"; \
			conda env remove -y -q --name $(1) && \
			echo "Environment '$(1)' successfully removed."; \
		} || true
	)
	@# Create the new conda environment from environment.yml
	conda env create --quiet --yes --file environment.yml --name $(1)
	@# Configure library paths for the environment
	@CONDA_ENV_PATH=$$(conda run -n $(1) python -c "import os; print(os.environ['CONDA_PREFIX'])"); \
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
	fi;
endef

all: build

build:
	@#"This option is now equivalent to running build with '--execution-type no-execution'."
	python build.py

force-execute-all-notebooks:
	@echo "This option has been replaced with '--execution-type all-unskipped-notebooks'"
	@echo "You can run 'make all-unskipped-notebooks' for the same command."

execute-notebooks:
	@echo "This option has been replaced with '--execution-type updated-unskipped-notebooks'"
	@echo "You can run 'make updated-unskipped-notebooks' for the same command."

absolutely-all-notebooks:
	python build.py --execution-type absolutely-all-notebooks

all-unskipped-notebooks:
	python build.py --execution-type all-unskipped-notebooks

updated-unskipped-notebooks:
	python build.py --execution-type updated-unskipped-notebooks

clean:
	rm -rf content/*.html
	rm -rf content/*/*.html
	rm -rf dev/*.html
	rm -rf dev/*/*.html

create-textbook-stable-env:
	$(call create-and-configure-env,textbook-stable-env,false)
	conda run -n textbook-stable-env pip install 'hnn_core[dev]==$(HNN_VERSION)'
	conda run -n textbook-stable-env pip install --force-reinstall 'pooch==1.8.2'
	@echo "Conda environment 'textbook-stable-env' successfully created."
	@echo -e "\n\nActivate your environment with 'conda activate textbook-stable-env'"

create-textbook-dev-env:
	$(call create-and-configure-env,textbook-dev-env,true)

	@# Get the latest commit hash of hnn-core master branch
	LATEST_HASH=$$(git ls-remote https://github.com/jonescompneurolab/hnn-core.git master | cut -f1);
	@# Install hnn-core in developer mode, forcing reinstall without cache
	conda run -n textbook-dev-env pip install --upgrade --force-reinstall --no-cache-dir "hnn-core[dev] @ git+https://github.com/jonescompneurolab/hnn-core.git@master"
	conda run -n textbook-dev-env pip install --force-reinstall 'pooch==1.8.2'

	@echo "Conda environment 'textbook-dev-env' successfully created."
	@echo -e "\n\nActivate your environment with 'conda activate textbook-dev-env'"


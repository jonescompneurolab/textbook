<!--
# Title: 1.3 Installation
# Updated: 2025-03-06
#
# Contributors:
    # Austin Soplata
    # Joyce Gao
    # Dylan Daniels
-->

# 1.3 Installation

## Running HNN in the cloud

### Google CoLab

As an alternative to installing HNN locally, we provide Google CoLab notebooks that allow you to run HNN out of your browser, with access to your local filesystem.

- [GUI Colab Notebook](https://colab.research.google.com/drive/1yyjuEBimIu_f7_0Nf3YLwUiVOO7ZrKK3?usp=sharing)
- [API Colab Notebook](https://colab.research.google.com/drive/1FcNhHatsuxl-pACIFn7V6H5J4GPfZ1t8)

This is the quickest way to get up and running with HNN, though it does require a Google account. If you do not have a Google account, you can create one for free to run the notebooks. There is no charge associated with using Google CoLab.

### Neuroscience Gateway Portal

HNN is available for free, public use on the [Neuroscience Gateway Portal (NSG)](https://www.nsgportal.org/). You can find instructions for using HNN on NSG [at this page here](https://users.sdsc.edu/~kenneth/hnn/index.html).

## Using the Textbook

To follow along with the examples in the textbook, you'll need to clone or download the [hnn-data repository](https://github.com/jonescompneurolab/hnn-data). The hnn-data repository includes both source-localized data used in our lab's published research as well as network configurations that have been tuned for simulating different types of signals. Note that this is *not* the same as installing HNN -- these are only files that you will use as you go through our textbook examples.

You can directly [download the hnn-data folder by clicking here](https://github.com/jonescompneurolab/hnn-data/archive/refs/heads/main.zip). Alternatively, you can clone the repository using the following command:

```bash
git clone https://github.com/jonescompneurolab/hnn-data.git
```

## Local Installation

We **strongly** recommend that you install HNN from our **`conda` package** instead of from `pip`. This `conda` package is "batteries included" and contains ALL features of HNN: the HNN API, the HNN GUI, Optimization, Joblib Parallelism, and MPI Parallelism. This is *significantly* easier to install than using `pip`.

However, there are some cases where you should **not** use the `conda` installation:

- **If you want to co-install HNN alongside MNE:** In this case, we strongly recommend that you install MNE *first* [(MNE install guides here)](https://mne.tools/stable/install/index.html). If you installed MNE using its `pip` or `conda` methods, then afterwards, you should install HNN using our **`pip` Package Installation** method below, but *in the same Python environment* that you installed MNE into.
- **If you are using your institution's High-Performance Computing (HPC) environment** (also called a "computing cluster" or supercomputer): The `conda` installation may work on your HPC, but if you want to use your HPC's custom MPI libraries, you should try using our **`pip` Package Installation** below. Your HPC usually has documentation on how they want you to load OpenMPI (which is not a Python package) and possibly `mpi4py` (which is a Python package). You can always ask us for help at [our Github Discussions page][].
- **If you are at Brown University and want to use HNN on the OSCAR system:** We have made custom instructions for you, which [can be found here at this other page](https://github.com/jonescompneurolab/oscar-install).
- **If you want to use a "custom" version of HNN's source code:** This includes if you need to use your own "Github fork", someone else's fork, or **if you want to contribute to HNN's development**. In this case you should follow our **`pip` Source Installation** guide below.

The terms HNN, `hnn-core`, and `hnn_core` are effectively equivalent, as they are all different names for the same codebase. `hnn-core` or `hnn_core` are often used during the installation process or when you are using the API.

After you have installed HNN, we recommend you follow the **Testing Your Installation** section below to make sure it is installed correctly.

**If you have any questions or problems** while installing HNN, feel free to ask for help on [our GitHub Discussions page][]!

<div class="collapsible-section">
<h5 class="collapsible-header"> `conda` Package Installation </h5>
<div class="collapsible-content">

<a id="conda-package-installation"></a>

Note: If you want a minimal install of only the API using `conda`, then follow the instructions below, but replace the package name `hnn-core-all` with `hnn-core`.

## `conda` on MacOS or Linux

1. Install the [Anaconda Python Distribution](https://www.anaconda.com/download/success). If you are unfamiliar with using Anaconda/Conda virtual environments, [you can find resources here](https://www.anaconda.com/docs/getting-started/getting-started).

2. Open a Terminal, then create and activate a new Python 3.12 Conda environment by running the following commands:

```
conda create -y -q -n hnn-core-env python=3.12
conda activate hnn-core-env
```

Feel free to change the environment name `hnn-core-env`. **You must use Python 3.12 for our `conda` packages.**

3. Install our package using the following command:

```
conda install hnn-core-all -c jonescompneurolab -c conda-forge
```

4. (Optional) Run the following command, and write down the number that is output. You can use this number as the number of CPU "Cores", which will *greatly* speed up your simulations.

```
python -c "import psutil ; print(psutil.cpu_count(logical=False)-1)"
```

5. That's it! HNN should now be installed. Proceed to the rest of [our HNN Textbook][] to get started.
6. Note: The next time you need to re-enter the Conda Environment, all you need to do is run `conda activate hnn-core-env`.

## `conda` on Windows

For Windows users, there are some extra steps since you need to install HNN through "Windows Subsystem for Linux" (WSL).

1. Install WSL: Open the "PowerShell" or "Windows Command Prompt" programs in administrator mode by right-clicking the program icon and selecting "Run as administrator". Then, in the window, run the following command:

```
wsl --install
```

Follow the default options for your install. For more information, see <https://learn.microsoft.com/en-us/windows/wsl/install>.

2. Close the PowerShell or Command Prompt window.
3. You will now have a new App available from the Start Menu called `Ubuntu`. Run that app.
4. The first time you start Ubuntu, it will prompt you to `Create a default Unix user account` and ask for a password. If you provide a password, write it down.
5. You should now see a prompt and a blinking cursor similar to PowerShell/Command Prompt. Copy and paste the following commands. If you entered a password in Step 4, enter that when it prompts you for your password.

```bash
sudo apt-get update
sudo apt-get install build-essential
sudo apt-get install wget
```

6. In the same window, copy and paste the following commands, then follow the prompts. We strongly recommend that when you are asked  `Do you wish to update your shell profile to automatically initialize conda?` you enter `yes`. If you do not, then you will have to manually activate Conda whenever you open your Ubuntu app using the command this program provides at the end.

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

If you see output similar to `WARNING: Your machine hardware does not appear to be x86_64`, then please contact us via [our Github Discussions page][]. You may be able to install by using <https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh> instead.

7. Close the Ubuntu window, then open a new one. Your prompt should now show `(base)` at the beginning.
8. Inside this window, follow all the steps above in the [`conda` MacOS or Linux](#conda-macos-or-linux) section, then return here.
9. HNN should now be installed!
10. Note: On Windows, every time you start the GUI, you will need to navigate to <http://localhost:8866> in your browser (or refresh if you are already on the page).

</div>
</div>

<span style="height: 30px;" />

<div class="collapsible-section">
<h5 class="collapsible-header"> `pip` Package Installation </h5>
<div class="collapsible-content">

<a id="pip-package-installation"></a>

Please follow the instructions in Steps 1, 2, and 3, in that order. If installing through `pip`, HNN currently supports Python 3.9 through 3.13, inclusively.

Note that the `pip` installation methods do *not* include all features by default, only the API. If you want to install a specific set of features, you must include all of them in your `pip` install command. For example, if you want HNN GUI support and Optimization support, but not Parallel support, then you would replace the final command in Step 3 with

```
pip install "hnn_core[gui,opt]"
```

## Step 1. `pip` Python Environment

We strongly recommend that you install HNN inside a "virtual environment" using software like the [Anaconda Python Distribution](https://www.anaconda.com/download/success) or Python's builtin [`venv` module](https://docs.python.org/3/library/venv.html). If you are new to Python or data science in Python, we recommend you review the resources here: <https://docs.anaconda.com/getting-started/>.

If you use a virtual environment, you must first create the environment, and then separately *activate* the environment (see [Conda guidance here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment) and [`venv` guidance here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)) before running any of the commands below. **All of the installation commands below assume you have already activated your environment**. You may need to re-activate your environment every time you restart your computer or open a new terminal, depending on how you installed your virtual environment software.

## Step 2. `pip` Platform-specific requirements

### `pip` on MacOS

- If you already installed the [NEURON][] software system-wide using its
  traditional installer package, you must **remove it** first. We
  will be installing NEURON using its `pip` package.
- Before you install HNN, you must install "Xcode Command-Line
  Tools". This can be done easily by opening a Terminal, running the following command,
  and then clicking through the prompts in the window that will pop up. Note that you
  **must restart your computer** after Xcode Command-Line Tools has finished installing!

    ```
    xcode-select --install
    ```

If you run the above command and see output that resembles `xcode-select: note: Command
line tools are already installed.`, then you already have it installed, do not need to
restart your computer, and can proceed to the next step. Finally, note that you do *not* need to install Xcode in its entirety; only the above is required.

### `pip` on Linux

- If you already installed the [NEURON][] software system-wide using its
  traditional installer package, you must **remove it** first. We
  will be installing NEURON using its `pip` package.

### `pip` on Windows (native, not WSL)

- Before you install HNN, it is important that you **install** the [NEURON][]
  software system-wide using its [Windows-specific
  binaries](https://nrn.readthedocs.io/en/latest/install/install_instructions.html#windows). You
  can test that NEURON was installed correctly by opening a Command Prompt (or
  similar) via your Anaconda install (or virtual environment), and running the
  following command:

```
python -c "import neuron"
```
- Note that MPI use is **not** supported on native Windows, but is supported on Windows using WSL (see below).

### `pip` on Windows (WSL)

The following include instructions on how to install both "Windows Subsystem for Linux" (WSL) and the [Anaconda Python Distribution](https://www.anaconda.com/download/success) inside WSL.

1. Install WSL: Open the "PowerShell" or "Windows Command Prompt" programs in administrator mode by right-clicking the program icon and selecting "Run as administrator". Then, in the window, run the following command:

```
wsl --install
```

Follow the default options for your install. For more information, see <https://learn.microsoft.com/en-us/windows/wsl/install>.

2. Close the PowerShell or Command Prompt window.
3. You will now have a new App available from the Start Menu called `Ubuntu`. Run that app.
4. The first time you start Ubuntu, it will prompt you to `Create a default Unix user account` and ask for a password. If you provide a password, write it down.
5. You should now see a prompt and a blinking cursor similar to PowerShell/Command Prompt. Copy and paste the following commands. If you entered a password in Step 4, enter that when it prompts you for your password.

```bash
sudo apt-get update
sudo apt-get install build-essential
sudo apt-get install wget
```

6. In the same window, copy and paste the following commands, then follow the prompts. We strongly recommend that when you are asked  `Do you wish to update your shell profile to automatically initialize conda?` you enter `yes`. If you do not, then you will have to manually activate Conda whenever you open your Ubuntu app using the command this program provides at the end.

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

If you see output similar to `WARNING: Your machine hardware does not appear to be x86_64`, then please contact us via [our Github Discussions page][]. You may be able to install by using <https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh> instead.

7. Close the Ubuntu window, then open a new one. Your prompt should now show `(base)` at the beginning.
8. Inside this window, follow all the steps below for your preferred `pip` package installation type **as if you are installing for Linux**, then return here.
9. HNN should now be installed!
10. Note: On Windows, if you installed the GUI, then every time you start the GUI, you will need to navigate to <http://localhost:8866> in your browser (or refresh if you are already on the page).

## Step 3. `pip` installation types

The instructions shown below are for installing each set of HNN features **separately**, meaning you need to follow the instructions for the features you want. The HNN API is the only feature included in **all install types**. You can easily install multiple sets of HNN features below by combining them like the following:
```
pip install "hnn_core[gui,parallel]"
```

### `pip` Basic (API-only) Installation

To install only the HNN API, open a Terminal or Command Prompt using a fresh virtual
environment, and enter:

```
pip install hnn_core
```

This will install only the HNN API along with its required dependencies, which include: [NumPy](https://numpy.org/), [SciPy](https://scipy.org/), [Matplotlib](https://matplotlib.org/), [NEURON][] (>=7.7), and [h5io](https://github.com/h5io/h5io).

For guidance on using the API, see our "Using the HNN API" notebooks in the sidebar such as [here](../08_using_hnn_api/plot_firing_pattern.html), or in-depth examples like our [API tutorial of ERPs](../05_erps/hnn_core.html).

### `pip` Graphical User Interface (GUI) Installation

To install HNN with both its API and GUI support, run the following command (make sure to include the "quotes"):

```
pip install "hnn_core[gui]"
```

This automatically installs the following dependencies:
[ipykernel](https://ipykernel.readthedocs.io/en/stable/), [ipympl](https://matplotlib.org/ipympl/), [ipywidgets](https://github.com/jupyter-widgets/ipywidgets) >=8.0.0, and [voila](https://github.com/voila-dashboards/voila).

For guidance on using the GUI, see [our quickstart guide here](../04_using_hnn_gui/gui_quickstart.html), or in-depth examples like our [GUI tutorial of ERPs](../05_erps/erps_in_gui.html).

### `pip` Optimization Installation

To install HNN with both its API and Optimization support, run the following command (make sure to include the "quotes"):

```
pip install "hnn_core[opt]"
```

This automatically installs the following dependencies: [`scikit-learn`](https://scikit-learn.org/stable/index.html).

If you are using Optimization, it is recommended to also install Joblib support (see below).

For guidance on using Optimization, see our "Using the HNN API" notebooks in the sidebar such as [here](../08_using_hnn_api/optimize_simulated_evoked_response_parameters.html) and [here](../08_using_hnn_api/optimize_simulated_rhythmic_response_parameters.html).

### `pip` Joblib Installation

To install HNN with both its API and Joblib support, run the following command (make sure to include the "quotes"):

```
pip install "hnn_core[parallel]"
```

This automatically installs the following dependencies: [Joblib](https://joblib.readthedocs.io/en/stable/) and [psutil](https://github.com/giampaolo/psutil).

Many of the examples in our Textbook make use of Joblib support, and we provide an explicit [tutorial for it here](../08_using_hnn_api/parallelism_joblib.html).

### `pip` MPI Installation

MPI installation is the most difficult installation type. If you want to use [MPI](https://www.open-mpi.org/), we recommend you first try to install our `conda` package detailed above. Otherwise, we **strongly** recommend you use a virtual environment created using the [Anaconda Python Distribution](https://www.anaconda.com/download/success) specifically, since Anaconda is the easiest way to download [OpenMPI binaries](https://anaconda.org/conda-forge/openmpi), which are *not* Python code.

To install HNN with its MPI dependencies using the `pip` method, follow the below instructions for your operating system.

#### `pip` MPI: Windows (native)

Unfortunately, we do not officially support MPI usage on native Windows due to the complexity required. However, we do support MPI through "Windows Subsystem for Linux" (WSL); see below.

#### `pip` MPI: MacOS, Linux, or Windows (WSL)

1. Install the [Anaconda Python Distribution](https://www.anaconda.com/download/success). (If you have followed instructions in Step 2 for Windows WSL above, you can skip this.)

2. Create and activate a new `conda` environment using commands like the following:

```
conda create -y -q -n hnn-core-env python=3.12
conda activate hnn-core-env
```

You can change the environment name `hnn-core-env` to whatever you wish. Compatible Python versions currently include 3.9 to 3.13, inclusively.

3. (MacOS only) Copy, paste, and run the following commands to set some environment variables for your `conda` environment:

```
mkdir -p $CONDA_PREFIX/etc/conda/activate.d $CONDA_PREFIX/etc/conda/deactivate.d
echo "export OLD_DYLD_FALLBACK_LIBRARY_PATH=\$DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo "export DYLD_FALLBACK_LIBRARY_PATH=\$DYLD_FALLBACK_LIBRARY_PATH:\${CONDA_PREFIX}/lib" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo "export DYLD_FALLBACK_LIBRARY_PATH=\$OLD_DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
echo "unset OLD_DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
export OLD_DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH
export DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH:${CONDA_PREFIX}/lib
```

4. (Linux or Windows (WSL) only) Copy, paste, and run the following commands to set some environment variables for your `conda` environment:

```
mkdir -p $CONDA_PREFIX/etc/conda/activate.d $CONDA_PREFIX/etc/conda/deactivate.d
echo "export OLD_LD_LIBRARY_PATH=\$LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\${CONDA_PREFIX}/lib" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo "export LD_LIBRARY_PATH=\$OLD_LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
echo "unset OLD_LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
export OLD_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${CONDA_PREFIX}/lib
```

5. Run the following command to install your MPI dependencies:

```
conda install -y -q "openmpi>5" mpi4py -c conda-forge
```

6. Finally, install the `pip` package of `hnn_core` using the following command (make sure to include the "quotes"):

```
pip install "hnn_core[parallel]"
```

7. Let's test that the install worked. Run the following command:

```
python -c "
from hnn_core import jones_2009_model, MPIBackend, simulate_dipole
with MPIBackend():
    simulate_dipole(jones_2009_model(), tstop=20)
"
```

You should see output the looks somewhat similar to the following; this verifies that MPI, NEURON, and Python are all working together.

```
/opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/dipole.py:85: UserWarning: No external drives or biases loaded
  warnings.warn("No external drives or biases loaded", UserWarning)
MPI will run 1 trial(s) sequentially by distributing network neurons over 11 processes.
numprocs=11
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Building the NEURON model
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
Loading custom mechanism files from /opt/anaconda3/envs/hnn-core-env/lib/python3.12/site-packages/hnn_core/mod/arm64/.libs/libnrnmech.so
[Done]
Trial 1: 0.03 ms...
Trial 1: 10.0 ms...
```

8. For guidance on using MPI, see our "Using the HNN API" notebook in the sidebar [here](../08_using_hnn_api/parallelism_mpi.html)

</div>
</div>

<span style="height: 30px;" />

<div class="collapsible-section">
<h5 class="collapsible-header"> `pip` Source Installation </h5>
<div class="collapsible-content">

<a id="pip-source-installation"></a>

To begin installing HNN via source code, you first need to follow **all** of the instructions above in **`pip` Package Installation** for your desired platform and features **except** for the final `pip install "hnn_core[<features>]"` command. If you want to contribute to HNN development, then it is strongly recommended you also follow the MPI installation instructions in the previous **`pip` Package Installation** section.

### Installing custom versions with no changes:

If you only want to install a custom version of HNN from Github, but **you do NOT need to edit the code yourself**, then someone else has probably given you a specific URL to use. You can install the features you need with the URL you have been given using the following:

```
pip install "hnn_core[gui] @ git+https://github.com/asoplata/hnn-core"
```

where you would replace `[gui]` with the features you want, and `https://github.com/asoplata/hnn-core` with the URL of the Github code or fork you want to use.

### Installing custom versions, but supporting changes:

If instead you want to install a custom version of HNN from Github, but you **DO want to edit the code yourself**, you should do the following. **This is what you should do if you want to contribute to development**.

1. [Setup `git` using the instructions here](https://docs.github.com/en/get-started/git-basics/set-up-git). Note that you need to make sure that both 1. `git` is installed [using these steps](https://docs.github.com/en/get-started/git-basics/set-up-git#setting-up-git) **and** 2. that your `git` program has authenticated to Github [using these steps](https://docs.github.com/en/get-started/git-basics/set-up-git#authenticating-with-github-from-git).

2. You should do a `git clone <fork URL>` of the fork you are interested in, which will download the source code to a new directory. If you want to contribute to development, you should use your own personal fork. (You can create your own fork by going to our [code repository here](https://github.com/jonescompneurolab/hnn-core) and clicking the "Fork" button in the top right.) As an example, if you wanted to download `asoplata`'s fork, you could do either:

```
git clone https://github.com/asoplata/hnn-core.git
```

or

```
git clone git@github.com:asoplata/hnn-core
```

depending on whether you authenticated using HTTPS or SSH.

3. Enter the directory that you just downloaded, using the command `cd hnn-core`.

4. Install an "editable" version of the local source code with the features you want to use. If, for example, you do not want to contribute to development, but you want to install the GUI and Optimization features, you can use the following command:

```
pip install --editable ".[gui,opt]"
```

If you **want to contribute to development**, then you should instead use the following command, which installs all features including **special** features used in development:

```
pip install --editable ".[dev]"
```

If you want to contribute to development, then once you have installed HNN this way, please see our [Contributing Guide here](https://jonescompneurolab.github.io/hnn-core/stable/contributing.html).

</div>
</div>

<span style="height: 30px;" />

<div class="collapsible-section">
<h5 class="collapsible-header"> Testing Your Installation </h5>
<div class="collapsible-content">

<a id="testing-your-installation"></a>

To check whether HNN was installed correctly, you can run the following command:

```
python -c "from hnn_core import jones_2009_model, simulate_dipole ; simulate_dipole(jones_2009_model(), tstop=20) ; print('--> SUCCESS: The test worked!')"
```

This will run a very short test simulation, and should not give any Error messages (Warning messages are okay).

If you installed MPI, it is **strongly recommended** to test your install. You can test that HNN, NEURON, and MPI were all installed correctly and can talk to each other by running the following command:

```
python -c "
from hnn_core import jones_2009_model, MPIBackend, simulate_dipole
with MPIBackend():
    simulate_dipole(jones_2009_model(), tstop=20)
print('--> SUCCESS: The test worked!')
"
```

If either of the above commands run into Errors (Warnings are okay), then feel free to ask for help on [our GitHub Discussions page][].

</div>
</div>

[our HNN Textbook]: ../preface.html
[NEURON]: https://nrn.readthedocs.io/
[our HNN Textbook website]: https://jonescompneurolab.github.io/textbook/content/preface.html
[our GitHub Discussions page]: https://github.com/jonescompneurolab/hnn-core/discussions

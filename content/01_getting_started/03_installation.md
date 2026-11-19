<!--
# Title: 1.3 Installation
# Updated: 2026-10-15
#
# Contributors:
    # Austin Soplata
    # Joyce Gao
    # Dylan Daniels
-->


<!--
Reminder:
macOS zsh does not support "# " for comments by default, so there should be NO comments
in your command-line sections!
-->

use the collapsible here, but the one that still uses the border

    uv pip install -U "hnn-core[all]@git+https://github.com/jonescompneurolab/hnn-core.git@master"
    uv pip install -U --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --index-strategy unsafe-best-match "hnn-core[all]==1.0.0"
	uv pip install -U "hnn-core[all]"






TODO test if uvx works

Add popups from frontpage here

todo collapsible cloud (with linkage!)


https://jonescompneurolab.github.io/textbook/content/05_erps/erp_initial_simulation.html#api-walkthrough

# 1.3 Installation

## Running HNN in the cloud (no installation)

### Google CoLab

As an alternative to installing HNN locally, we provide Google CoLab notebooks that allow you to run HNN out of your browser, with access to your local filesystem.

- [GUI Colab Notebook](https://colab.research.google.com/drive/1yyjuEBimIu_f7_0Nf3YLwUiVOO7ZrKK3?usp=sharing)
- [API Colab Notebook](https://colab.research.google.com/drive/1FcNhHatsuxl-pACIFn7V6H5J4GPfZ1t8)

This is the quickest way to get up and running with HNN, though it does require a Google account. If you do not have a Google account, you can create one for free to run the notebooks. There is no charge associated with using Google CoLab.

### Neuroscience Gateway Portal

HNN is available for free, public use on the [Neuroscience Gateway Portal (NSG)](https://www.nsgportal.org/). You can find instructions for using HNN on NSG [at this page here](https://users.sdsc.edu/~kenneth/hnn/index.html).

----------------------------------------------

## Local Installation - Simple

If you want to install HNN-Core on your local computer with all features, including API, GUI, MPI, and others, follow the below steps.

Alternatively, if your circumstances are more complex (such as if you need to install into an existing `conda` environment, or you are using Brown University's OSCAR system, you want to install for development, etc.) then please see the **Local Installation - Detailed** section later. You can also always reach out to us at [our Github Discussions page][] for installation help. Additionally, if you are on Windows but are unable to install "Windows Subsystem for Linux", such as due to hospital IT policy, then see the **non-WSL Windows Installation** section later.

## Part 1. Platform-specific requirements

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> MacOS </h5>
<div class="collapsible-content">

<a id="macos"></a>

1. Before you install HNN-Core, you must install "Xcode Command-Line Tools". This can be
  done by opening the "Terminal" app, running the following command, and then clicking
  through the prompts in the window that will pop up.

    ```bash
    xcode-select --install
    ```

    If you see output that says `xcode-select: note: Command line tools are already installed.` then that's okay, continue.

2. **Restart your computer.**

3. Make sure your computer has the latest updates by opening the Settings app and going
   to "Software Update". Download and install all updates, then restart your computer
   again. **Note that you may have to do this multiple times**.


- TODO If you already installed the [NEURON][] software system-wide using its
  traditional installer package, you must **remove it** first. We
  will be installing NEURON using its `pip` package.


4. Once there are no more updates to your system, check that you are not on the "Low
   Battery" setting by clicking on your battery in the top bar, and switch it to a
   different mode. Then, proceed to Part 2.

</div>
</div>

<span style="height: 30px;" />

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> Windows (WSL) </h5>
<div class="collapsible-content">

<a id="windows-wsl"></a>

1. Install ["Windows Subsystem for Linux" (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). You can do this via following the steps at <https://learn.microsoft.com/en-us/windows/wsl/install> or the steps here:

    1.1. Open the Start Menu and type "Powershell", but do not hit enter or left-click the icon yet.

    1.2. Right-click on the icon for Powershell and select "Run as administrator". A new window should open.

    1.3. Inside the Powershell window, run the following command, which will take several minutes at least:

    ```bash
    wsl --install
    ```

	1.4 It should eventually prompt you to `Create a default Unix user account` and ask for a password. Provide a username and password, which can be anything, and write the password down!

    1.5 Once it has finished, close the PowerShell window.

2. You will now have a new App available from the Start Menu called `Ubuntu`. Run that app.

3. You should now see a prompt and a blinking cursor similar to PowerShell/Command Prompt. Copy, paste, and run the following commands. If you entered a password in Step 3, enter that when it prompts you for your password. When it asks 

    ```bash
    sudo apt-get update
    sudo apt-get -y install build-essential
    ```

5. Proceed to Part 2.

</div>
</div>

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> Linux (Debian/Ubuntu) </h5>
<div class="collapsible-content">

1. Install the fundamental software building packages for your distribution. For Debian/Ubuntu-based distributions (e.g. Debian, Ubuntu, Linux Mint, etc.), you can do this with the following command in your Terminal:

    ```bash
    sudo apt-get update
    sudo apt-get install build-essential
    ```


- TODO If you already installed the [NEURON][] software system-wide using its
  traditional installer package, you must **remove it** first. We
  will be installing NEURON using its `pip` package.



2. Proceed to Part 2.

</div>
</div>

<span style="height: 30px;" />


## Part 2. `uv` and HNN-Core installation

1. Open a new Terminal (MacOS / Linux) or Ubuntu (Windows Subsystem for Linux) window.

2. Download and [install the `uv` Python package and project
   manager](https://docs.astral.sh/uv/getting-started/installation/) by copying,
   pasting, and running the following command. (Note: if you are using an existing
   `conda` environment, then do not follow these directions, and instead refer to the
   later **Local Installation - Detailed** section.)

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    Note: If you are using "Windows Subsystem for Linux (WSL)" then do *not* use the "Windows" commands on `uv`'s installation page - instead, use the "macOS and Linux" version inside your Ubuntu window.

3. Close your Terminal or Ubuntu window, then open a new one.

4. Copy, paste, and run the following series of commands in order to install Python,
   create a new "virtual environment", install HNN-Core, and test HNN-Core. You can copy
   and paste all of them together *at one time*:

    TODO swap pip

    ```bash
    uv python install 3.14
    cd ~
    uv venv -p 3.14
    source .venv/bin/activate
    uv pip install -U --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --index-strategy unsafe-best-match "hnn-core[all]==1.0.0"
    python -c "
    from hnn_core import neymotin_2020_model, MPIBackend, simulate_dipole
    with MPIBackend():
        simulate_dipole(neymotin_2020_model(), tstop=20)
    print('--> SUCCESS: The test worked')"
    ```

    If you encounter any errors or problems with this step, please reach out to us on
    [our Github Discussions page][]. You can view [this
    page](https://docs.python.org/3/library/venv.html) or [this
    page](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)
    for more information on using "virtual environments".

5. Close your Terminal or Ubuntu window *again*, then open a new one.

6. Copy, paste, and run the following command to re-activate your "virtual environment"
   that contains HNN-Core. **Note that you will need to do this each time you open a new
   Terminal/Ubuntu window, or if you restart your computer and want to use HNN-Core**:

    ```bash
	source ~/.venv/bin/activate
	```

7. Once you have activated your environment, you can run the GUI using the following
   command:

    ```bash
    hnn-gui
    ```

8. Everything should be installed and working now! As a reminder, if you restart your
   computer or open new Terminal/Ubuntu windows, then you will have to "activate your
   virtual environment" once again to use the HNN-Core API or the GUI. You can do this
   using the following command:

    ```bash
    source ~/.venv/bin/activate
    ```

    After which you can run `hnn-gui` to open the GUI, run python code/files using
    `python`, or open Jupyter notebooks using `jupyter notebook`. Proceed to the rest of
    [our HNN Textbook][] to get started.


------------------------------------

##### "Alternative installations"


<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> non-WSL Windows Installation </h5>
<div class="collapsible-content">

On Windows, we strongly recommend you first try the "Windows (WSL)" (Windows Subsystem
for Linux) install above. The following instructions are only for those who strictly
cannot use WSL, such as due to hospital IT policy. Using "plain" Windows is discouraged
since we **do not support MPI usage on the platform (only on Windows-WSL)**, the
installation is complex, and it is more difficult to develop for HNN-Core on. If you run
into any issues installing on Windows, please feel free to reach out to us on [our
Github Discussions page][].


1. Before you install HNN, it is important that you **download** and then **install**
  the [NEURON][] software system-wide using its [Windows-specific binaries, such as this
  one](https://github.com/neuronsimulator/nrn/releases/download/9.0.2/nrn-9.0.2.w64-mingw-py-310-311-312-313-314-setup.exe);
  you can see more information at [this
  link](https://www.neuronsimulator.org/en/latest/install/install_instructions.html#windows).

<!--
Note from Austin on 2026-11-18:
Ugh. Both Windows' normal and hospital IT security policies can make Windows
installation difficult.  If the user is at this case, where they aren't allowed to
install WSL, then the following are our options, judging from my own testing of Windows
11:

1. We tell them to install `uv`, BUT, in order to run the script that activates their
  environment, they have to *first change their system's Powershell security policy*
  using:
  ```
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
  ```

2. We tell them to install Anaconda just in order to get Python, and then do a "pip"
   install like normal.

When trying to do the Anaconda method on 2026-11-18, I ran into a new issue: after a
completely fresh install of Anaconda, when I tried to use "Anaconda Prompt" (instead of
the Anaconda Navigator, which has issues about where it is legal to use), I couldn't
copy and paste instructions into the Prompt without it inserting the string ".anaconda"
at the beginning of every pasted line. This broke everything, and it's too much to ask
users to clean the strings.

Conclusion: For now, I'm recommending `uv` usage for non-WSL Windows users, despite the
need to change security settings (solely in order to run the
virtual-environment-activation script). If a user is in a hospital and they can't use
WSL nor use `uv`, then there's a very very good chance they won't be allowed to install
Anaconda (or ANY new software) either, and it will be better if we help them figure out
a solution specific to their case.
-->

2. Open the Start Menu and type "Powershell", but do not hit enter or left-click the icon yet.

3. Right-click on the icon for Powershell and select "Run as administrator". A new window should open.

4. Inside the Powershell window, copy, paste, and run the following command, then press `Y` for Yes. If you are unable to do this step, then reach out to us at [our Github Discussions page][].

     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
     ```

5. Copy, paste, and run the following commands (you can paste them all together), which will take several minutes:

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    # Install Python:
    uv python install 3.14
    # Move to your "home" directory (where the environment will live, feel free to change):
    cd ~
    # Create a virtual environment at `.venv/` that uses the above Python version:
    uv venv -p 3.14
    # Activate / enter the environment:
    .venv\Scripts\activate
    # Now that you're inside the environment, install HNN-Core:
    uv pip install -U --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --index-strategy unsafe-best-match "hnn-core[all]==1.0.0"
	# TODO uv pip install -U "hnn-core[all]"
    # Test that HNN-Core runs correctly
    python -c "
    from hnn_core import neymotin_2020_model, simulate_dipole
    simulate_dipole(neymotin_2020_model(), tstop=20)
    print('--> SUCCESS: The test worked')
    " # make sure to include this ending quote
    ```

5. Close the Powershell window, then open a new one.

6. Copy, paste, and run the following command to re-activate your "virtual environment"
   that contains HNN-Core. **Note that you will need to do this each time you open a new
   Powershell window, or if you restart your computer and want to use HNN-Core**:

    ```powershell
    TODO test combo
    cd ~
    .venv\Scripts\activate
	```

7. Once you have activated your environment, you can run the GUI using the following
   command. Do this now:

    ```bash
    hnn-gui
    ```

8. Everything should be installed and working now! As a reminder, if you restart your
   computer or open new Powershell windows, then you will have to "activate your
   virtual environment" once again to use the HNN-Core API or the GUI. You can do this
   using the following command:

    ```powershell
    cd ~
    .venv\Scripts\activate
    ```

    After which you can run `hnn-gui` to open the GUI, run python code/files using
    `python`, or open Jupyter notebooks using `jupyter notebook`. Proceed to the rest of
    [our HNN Textbook][] to get started.

</div>
</div>

<span style="height: 30px;" />

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> Local Installation - Detailed </h5>
<div class="collapsible-content">








# Run the GUI
hnn-gui

1. Install the [Anaconda Python Distribution](https://www.anaconda.com/download/success) (also known as "Conda"). If you are unsure which version to install, download the Graphical Installer for the Anaconda Distribution, though any option works. If you are unfamiliar with using Anaconda/Conda virtual environments, [you can find guidance about them here](https://www.anaconda.com/docs/getting-started/working-with-conda/conda-intro-tutorial).




<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> Which version to install? </h5>
<div class="collapsible-content">

<a id="which-version"></a>

We recommend that you install HNN from our **`conda` package** instead of from `pip`. This `conda` package is "batteries included" and contains ALL features of HNN: the HNN API, the HNN GUI, Optimization, Joblib Parallelism, and MPI Parallelism. This is *significantly* easier to install than using `pip`. The sole exception is on Windows: for Windows, the easiest way to install is using the **"`pip` Package Installation"** method listed below, but this does not include MPI parallelism automatically. You can install the `conda` package on Windows to get speedup from MPI, but you must install Windows Subsystem for Linux for this; instructions for every step are documented below.

However, there are some cases where you should **not** use the `conda` installation:

- **If you want to co-install HNN alongside MNE:** In this case, we strongly recommend that you install MNE *first* [(MNE install guides here)](https://mne.tools/stable/install/index.html). If you installed MNE using its `pip` or `conda` methods, then afterwards, you should install HNN using our **`pip` Package Installation** method below, but *in the same Python environment* that you installed MNE into.
- **If you are using your institution's High-Performance Computing (HPC) environment** (also called a "computing cluster" or supercomputer): The `conda` installation may work on your HPC, but if you want to use your HPC's custom MPI libraries, you should try using our **`pip` Package Installation** below. Your HPC usually has documentation on how they want you to load OpenMPI (which is not a Python package) and possibly `mpi4py` (which is a Python package). You can always ask us for help at [our Github Discussions page][].
- **If you are at Brown University and want to use HNN on the OSCAR system:** We have made custom instructions for you, which [can be found here at this other page](https://github.com/jonescompneurolab/oscar-install).
- **If you want to use a "custom" version of HNN's source code:** This includes if you need to use your own "Github fork", someone else's fork, or **if you want to contribute to HNN's development**. In this case, you should follow our **`pip` Source Installation** guide below.

The terms HNN, `hnn-core`, and `hnn_core` are effectively equivalent, as they are all different names for the same codebase. `hnn-core` or `hnn_core` are often used during the installation process or when you are using the API.

After you have installed HNN, we recommend you follow the **Testing Your Installation** section below to make sure it is installed correctly.

**If you have any questions or problems** while installing HNN, feel free to ask for help on [our GitHub Discussions page][]!


TODO conda package upgrade


</div>
</div>

<span style="height: 30px;" />


## Step 3. `pip` installation types

The instructions shown below are for installing each set of HNN features **separately**, meaning you need to follow the instructions for the features you want. The HNN API is the only feature included in **all install types**. You can easily install multiple sets of HNN features below by combining them like the following:

```bash
pip install "hnn_core[gui,parallel]"
```

### `pip` Basic (API-only) Installation

To install only the HNN API, open a Terminal or Command Prompt using a fresh virtual
environment, and enter:

```bash
pip install hnn_core
```

This will install only the HNN API along with its required dependencies, which include: [NumPy](https://numpy.org/), [SciPy](https://scipy.org/), [Matplotlib](https://matplotlib.org/), [NEURON][] (>=7.7), and [h5io](https://github.com/h5io/h5io).

For guidance on using the API, see our "Using the HNN API" notebooks in the sidebar such as [here](../08_using_hnn_api/plot_firing_pattern.html), or in-depth examples like our [tutorial of ERPs](../05_erps/erp_overview.html).

### `pip` Graphical User Interface (GUI) Installation

To install HNN with both its API and GUI support, run the following command (make sure to include the "quotes"):

```bash
pip install "hnn_core[gui]"
```

This automatically installs the following dependencies:
[ipykernel](https://ipykernel.readthedocs.io/en/stable/), [ipympl](https://matplotlib.org/ipympl/), [ipywidgets](https://github.com/jupyter-widgets/ipywidgets) >=8.0.0, and [voila](https://github.com/voila-dashboards/voila).

For guidance on using the GUI, see [our quickstart guide here](../04_using_hnn_gui/gui_quickstart.html), or in-depth examples like our [ERP tutorial](../05_erps/erp_overview.html).

### `pip` Optimization Installation

To install HNN with both its API and Optimization support, run the following command (make sure to include the "quotes"):

```bash
pip install "hnn_core[opt]"
```

This automatically installs the following dependencies: [`scikit-learn`](https://scikit-learn.org/stable/index.html).

If you are using Optimization, it is recommended to also install Joblib support (see below).

For guidance on using Optimization, see our "Using the HNN API" notebooks in the sidebar such as [here](../08_using_hnn_api/optimize_simulated_evoked_response_parameters.html) and [here](../08_using_hnn_api/optimize_simulated_rhythmic_response_parameters.html).

### `pip` Joblib Installation

To install HNN with both its API and Joblib support, run the following command (make sure to include the "quotes"):

```bash
pip install "hnn_core[parallel]"
```

This automatically installs the following dependencies: [Joblib](https://joblib.readthedocs.io/en/stable/) and [psutil](https://github.com/giampaolo/psutil).

Many of the examples in our Textbook make use of Joblib support, and we provide an explicit [tutorial for it here](../08_using_hnn_api/parallelism_joblib.html).

### `pip` MPI Installation

MPI installation is the most difficult installation type. If you want to use [MPI](https://www.open-mpi.org/), we recommend you first try to install our `conda` package detailed above. Otherwise, we **strongly** recommend you use a virtual environment created using the [Anaconda Python Distribution](https://www.anaconda.com/download/success) specifically, since Anaconda is the easiest way to download [MPI binaries](https://anaconda.org/conda-forge/openmpi), which are *not* Python packages.

To install HNN with its MPI dependencies using the `pip` method, follow the below instructions for your operating system.

#### `pip` MPI: Windows (native)

Unfortunately, we do not officially support MPI usage on native Windows due to the complexity required. However, we do support MPI through "Windows Subsystem for Linux" (WSL); see below.

#### `pip` MPI: MacOS, Linux, or Windows (WSL)

1. Install the [Anaconda Python Distribution](https://www.anaconda.com/download/success). (If you have followed instructions in Step 2 for Windows WSL above, you can skip this.)

2. Create and activate a new `conda` environment using commands like the following:

    ```bash
    conda create -y -q -n hnn-core-env python=3.12
    conda activate hnn-core-env
    ```

    You can change the environment name `hnn-core-env` to whatever you wish. Compatible Python versions currently include 3.9 to 3.13, inclusively.

3. (MacOS only) Copy, paste, and run the following commands to set some environment variables for your `conda` environment:

    ```bash
    mkdir -p $CONDA_PREFIX/etc/conda/activate.d $CONDA_PREFIX/etc/conda/deactivate.d
    echo "export OLD_DYLD_FALLBACK_LIBRARY_PATH=\$DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo "export DYLD_FALLBACK_LIBRARY_PATH=\$DYLD_FALLBACK_LIBRARY_PATH:\${CONDA_PREFIX}/lib" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo "export DYLD_FALLBACK_LIBRARY_PATH=\$OLD_DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
    echo "unset OLD_DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
    export OLD_DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH
    export DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH:${CONDA_PREFIX}/lib
    ```

4. (Linux or Windows (WSL) only) Copy, paste, and run the following commands to set some environment variables for your `conda` environment:

    ```bash
    mkdir -p $CONDA_PREFIX/etc/conda/activate.d $CONDA_PREFIX/etc/conda/deactivate.d
    echo "export OLD_LD_LIBRARY_PATH=\$LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\${CONDA_PREFIX}/lib" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo "export LD_LIBRARY_PATH=\$OLD_LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
    echo "unset OLD_LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
    export OLD_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${CONDA_PREFIX}/lib
    ```

5. Run the following command to install your MPI dependencies:

    ```bash
    conda install -y -q "openmpi>5" mpi4py -c conda-forge
    ```

6. Finally, install the `pip` package of `hnn_core` using the following command (make sure to include the "quotes"):

    ```bash
    pip install "hnn_core[parallel]"
    ```

7. Let's test that the install worked. Run the following command:

    ```bash
    python -c "
    from hnn_core import neymotin_2020_model, MPIBackend, simulate_dipole
    with MPIBackend():
        simulate_dipole(neymotin_2020_model(), tstop=20)
    "
    ```

    You should see output the looks somewhat similar to the following; this verifies that MPI, HNN, NEURON, and Python are all working together.

    ```bash
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

8. For guidance on using MPI, see our "Using the HNN API" notebook in the sidebar [here](../08_using_hnn_api/parallelism_mpi.html).

</div>
</div>

<span style="height: 30px;" />

<!-- Pip src ------------------------------------------------------- -->

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> `pip` Source Installation </h5>
<div class="collapsible-content">

<a id="pip-source-installation"></a>

This method should only be used if you need to install a custom version of HNN from Github, need to edit the code yourself, or want to contribute to HNN development. Otherwise, please use the **`conda` Package Installation** method above.

Please follow the instructions in Steps 1 through 5, *in that order*. This installation method for HNN currently supports Python 3.9 through 3.13, inclusively.

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

    ```bash
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

    ```bash
    python -c "import neuron"
    ```

- Note that MPI use is **not** supported on native Windows, but is supported on Windows using WSL (see below).
- If you want to contribute to HNN development, then native Windows is **not**
  recommended, and instead we recommend using WSL (see below).

### `pip` on Windows (WSL)

The following includes instructions on how to install both "Windows Subsystem for Linux" (WSL) and the [Anaconda Python Distribution](https://www.anaconda.com/download/success) inside WSL.

1. Install WSL: Open the "PowerShell" or "Windows Command Prompt" programs in administrator mode by right-clicking the program icon and selecting "Run as administrator". Then, in the window, run the following command:

    ```bash
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

## Step 3. (Optional) MPI installation

[MPI](https://www.open-mpi.org/) installation is the most difficult installation
type, but it is strongly recommended, *especially* if you want to contribute to
development. Our instructions below **assume** you are using a virtual environment created
using the [Anaconda Python Distribution](https://www.anaconda.com/download/success)
**specifically**, since Anaconda is the easiest way to download [MPI
binaries](https://anaconda.org/conda-forge/openmpi), which are *not* Python packages.

To install MPI and its dependencies, follow the below instructions for your platform.

### `pip` MPI: Windows (native)

Unfortunately, we do not officially support MPI usage on native Windows due to the complexity required. However, we do support MPI through "Windows Subsystem for Linux" (WSL); see below.

### `pip` MPI: MacOS, Linux, or Windows (WSL)

1. Create and activate a new `conda` environment using commands like the following:

    ```bash
    conda create -y -q -n hnn-core-env python=3.12
    conda activate hnn-core-env
    ```

    You can change the environment name `hnn-core-env` to whatever you wish. Compatible Python versions currently include 3.9 to 3.13, inclusively.

2. (MacOS only) Copy, paste, and run the following commands to set some environment variables for your `conda` environment:

    ```bash
    mkdir -p $CONDA_PREFIX/etc/conda/activate.d $CONDA_PREFIX/etc/conda/deactivate.d
    echo "export OLD_DYLD_FALLBACK_LIBRARY_PATH=\$DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo "export DYLD_FALLBACK_LIBRARY_PATH=\$DYLD_FALLBACK_LIBRARY_PATH:\${CONDA_PREFIX}/lib" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo "export DYLD_FALLBACK_LIBRARY_PATH=\$OLD_DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
    echo "unset OLD_DYLD_FALLBACK_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
    export OLD_DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH
    export DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH:${CONDA_PREFIX}/lib
    ```

3. (Linux or Windows (WSL) only) Copy, paste, and run the following commands to set some environment variables for your `conda` environment:

    ```bash
    mkdir -p $CONDA_PREFIX/etc/conda/activate.d $CONDA_PREFIX/etc/conda/deactivate.d
    echo "export OLD_LD_LIBRARY_PATH=\$LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\${CONDA_PREFIX}/lib" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo "export LD_LIBRARY_PATH=\$OLD_LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
    echo "unset OLD_LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
    export OLD_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${CONDA_PREFIX}/lib
    ```

4. Run the following command to install your MPI dependencies:

    ```bash
    conda install -y -q "openmpi>5" mpi4py -c conda-forge
    ```

## Step 4. Install `git`

[Setup `git` using the instructions
here](https://docs.github.com/en/get-started/git-basics/set-up-git). Note that you need
to do two steps:

1. Make sure that `git` is installed [using these
steps](https://docs.github.com/en/get-started/git-basics/set-up-git#setting-up-git)
**and**

2. Make sure that your `git` program has authenticated to Github [using these
steps](https://docs.github.com/en/get-started/git-basics/set-up-git#authenticating-with-github-from-git).

## Step 5. Download and install HNN-Core source code

1. It's finally time to download the source code. You should do a `git clone <fork URL>`
   of the fork you are interested in, which will download the source code to a new
   directory. If you want to contribute to development, you should use your own personal
   fork. (You can create your own fork by going to our [code repository
   here](https://github.com/jonescompneurolab/hnn-core) and clicking the "Fork" button
   in the top right.) As an example, if you wanted to download `asoplata`'s fork, you
   could run the following command:

    ```bash
    git clone https://github.com/asoplata/hnn-core.git
    ```

2. Enter the directory that you just downloaded, using the command `cd hnn-core`.

3. Use `pip` to install an "editable" version of the local source code with the features
   you want to use. If, for example, you want to install the GUI, Optimization, and
   Parallel features, you can use the following command:

    ```bash
    pip install --editable ".[gui,opt,parallel]"
    ```

    If you **want to contribute to development** or simply want to install all features,
    then you should instead use the following command, which installs all features including
    **special** features used in development:

    ```bash
    pip install --editable ".[dev]"
    ```

    For guidance on how to only install different subsets of features, see the previous
    section **`pip` Package Installation**.

    If you want to contribute to development, then once you have installed HNN this way,
    please see our [Contributing Guide
    here](https://jonescompneurolab.github.io/hnn-core/stable/contributing.html).

4. Test your installation by following the below **Testing Your Installation** section.

</div>
</div>

<span style="height: 30px;" />

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> Testing Your Installation </h5>
<div class="collapsible-content">

<a id="testing-your-installation"></a>

To check whether HNN was installed correctly, you can run the following command:

```bash
python -c "
from hnn_core import neymotin_2020_model, simulate_dipole
simulate_dipole(neymotin_2020_model(), tstop=20)
print('--> SUCCESS: The test worked')
"
```

This will run a very short test simulation, and should not give any Error messages (Warning messages are okay).

If you installed MPI, it is **strongly recommended** to test your install. You can test that HNN, NEURON, and MPI were all installed correctly and can talk to each other by running the following command:

```bash
python -c "
from hnn_core import neymotin_2020_model, MPIBackend, simulate_dipole
with MPIBackend():
    simulate_dipole(neymotin_2020_model(), tstop=20)
print('--> SUCCESS: The test worked')
"
```

If either of the above commands run into Errors (Warnings are okay), then feel free to ask for help on [our GitHub Discussions page][].

</div>
</div>

[our HNN Textbook]: ../preface.html
[NEURON]: https://nrn.readthedocs.io/
[our HNN Textbook website]: https://jonescompneurolab.github.io/textbook/content/preface.html
[our GitHub Discussions page]: https://github.com/jonescompneurolab/hnn-core/discussions

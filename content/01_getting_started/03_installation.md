<!--
# Title: 1.3 Installation
# Updated: 2026-10-15
#
# Contributors:
    # Austin Soplata
    # Joyce Gao
    # Dylan Daniels
-->

# 1.3 Installation

<!--
Developers: Reminder:
- macOS zsh does not support "# " for comments by default, so there should be NO
comments in your command-line sections!
-->

TODOs

- discuss HNN-Core vs HNN terminology with group
-- Add popups from frontpage here. NOPE tried, but even after adding CSS, could see the popup boxes on the main page, but clicking the boxes did NOT cause the big box overlay to actually spawn. Leaving this for another day.
- test mne hnn coinstall
- fix the missing 1.2 section install
- update oscar
- update readme


scratch pad:

uv pip install -U "hnn-core[all]@git+https://github.com/jonescompneurolab/hnn-core.git@master"
uv pip install -U --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --index-strategy unsafe-best-match "hnn-core[all]==1.0.0"
uv pip install -U "hnn-core[all]"
uvx --from="hnn_core[gui]" --python=3.13 hnn-gui


end of scratch pad

---------------------------------------

If you want to run HNN **for free** in the browser, click on the below box and follow the
directions:

<div class="collapsible-section collapsible-default">
<h4 class="collapsible-header">
Running HNN in the cloud (no installation)
</h4>
<div class="collapsible-content">

### Google CoLab

We provide Google CoLab notebooks that allow you to run HNN out of your browser, with
access to your local filesystem.

- [GUI Colab Notebook (Graphical User Interface)](https://colab.research.google.com/drive/1yyjuEBimIu_f7_0Nf3YLwUiVOO7ZrKK3?usp=sharing)
- [API Colab Notebook (Code-only, no GUI)](https://colab.research.google.com/drive/1FcNhHatsuxl-pACIFn7V6H5J4GPfZ1t8)

This is the quickest way to get up and running with HNN, though it does require a Google
account. If you do not have a Google account, you can create one for free to run the
notebooks. There is **no charge** associated with using Google CoLab.

### Neuroscience Gateway Portal

If you want, instead of using Google Colab, you can run HNN for free, public use on the
[Neuroscience Gateway Portal (NSG)](https://www.nsgportal.org/). You can find
instructions for using HNN on NSG [at this page
here](https://users.sdsc.edu/~kenneth/hnn/index.html).

</div>
</div>

## Local Installation - Simple

If you want to install HNN-Core on your local computer with all features, including API
(code), GUI (Graphical User Interface), MPI ([parallel
computing](file:///Users/austinsoplata/rep/brn/textbook/content/08_using_hnn_api/parallelism_mpi.html),
and others, follow [Part 1](#local-installation-part-1-platform-specific-requirements)
then [Part 2](#local-installation-part-2-uv-and-hnn-core-installation)
below. Alternatively, if your circumstances are more complex (e.g. if you are using
Anaconda/`conda`, you are using Brown University's OSCAR system, you want to install for
development, etc.) then please see the [**Local Installation - Detailed**
section](#local-installation---detailed). You can always reach out to us at [our Github
Discussions page][] for installation help!

-------------------------------------------------------------

## Local Installation Part 1: Platform-specific requirements

<!--
Developers: Austin note 2026-11-20:
Removing the step about uninstalling system-wide NEURON from all platforms. Doing this
in order to cut down on the number of steps, and because *most* users will *probably*
not have already installed the system-wide install of NEURON (as opposed to a different
tool's `pip` install, etc.).
-->

For Part 1, click on the section for your operating system and follow the directions
inside the box.

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header">
MacOS
</h5>
<div class="collapsible-content">

1. Before you install HNN-Core, you must install "Xcode Command-Line Tools". This can be
  done by opening the `Terminal` app, then copying, pasting, and running the following
  command, and then clicking through the prompts in the window that will pop up.

    ```bash
    xcode-select --install
    ```

    If you see output that says `xcode-select: note: Command line tools are already installed.` then that's okay, continue.

2. **Restart your computer.**

3. Make sure your computer has the latest updates by opening the Settings app and going
   to "Software Update". Download and install all updates, then restart your computer
   again, then check "Software Update" again for more updates. **Note that you may have
   to do this multiple times**.

4. Once there are **no more updates to your system available**, check that you are not
   on the `Low Battery` setting by clicking on your battery in the top bar. If you are
   set to `Low Battery` mode, switch it to a different battery mode.

5. Proceed to Part 2.

</div>
</div>
<span style="height: 30px;" />

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> Windows (WSL) </h5>
<div class="collapsible-content">

<a id="windows-wsl"></a>

1. Install ["Windows Subsystem for Linux" (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). You can do this via following the steps at <https://learn.microsoft.com/en-us/windows/wsl/install> or the steps here:

    1.1. Open the Start Menu and type `powershell`, but do not hit enter or left-click the icon yet.

    1.2. Right-click on the icon for Powershell and select `Run as administrator`. A new window should open.

    1.3. Inside the Powershell window, run the following command, which will take several minutes:

    ```bash
    wsl --install
    ```

    1.4. It should eventually prompt you to `Create a default Unix user account` and ask
    for a password. Provide a username and password, which can be anything, and write
    the password down!

    1.5. Once it has finished, close the PowerShell window.

2. You will now have a new App available from the Start Menu called `Ubuntu`. Run that app.

3. You should now see a prompt and a blinking cursor. Copy, paste, and run the following
   commands. When it asks for your password, provide the password you created in the
   prior step 1.4.

    ```bash
    sudo apt-get update
    sudo apt-get -y install build-essential
    ```

5. Proceed to Part 2.

</div>
</div>
<span style="height: 30px;" />

<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header"> Linux (Debian/Ubuntu) </h5>
<div class="collapsible-content">

1. Install the fundamental software building packages for your distribution. For
   Debian/Ubuntu-based distributions (e.g. Debian, Ubuntu, Linux Mint, etc.), you can do
   this with the following command in your Terminal:

    ```bash
    sudo apt-get update
    sudo apt-get -y install build-essential
    ```

2. Proceed to Part 2.

</div>
</div>
<span style="height: 30px;" />

## Local Installation Part 2: `uv` and HNN-Core installation

1. Open a new `Terminal` (MacOS / Linux) or `Ubuntu` (Windows Subsystem for Linux) window.

2. Download and [install the `uv` Python package and project
   manager](https://docs.astral.sh/uv/getting-started/installation/) by copying,
   pasting, and running the following command:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
3. Close your `Terminal` / `Ubuntu` window, then open a new one.

4. Copy, paste, and run the following series of commands in order to install Python,
   create a new "virtual environment", install HNN-Core, and test HNN-Core. You can copy
   and paste *all of them together at one time*:

    ```bash
    uv python install 3.14
    cd ~
    uv venv -p 3.14
    source .venv/bin/activate
    uv pip install -U "hnn-core[all]"
    python -c "
    from hnn_core import neymotin_2020_model, MPIBackend, simulate_dipole
    with MPIBackend():
        simulate_dipole(neymotin_2020_model(), tstop=20)
    print('--> SUCCESS: The test worked')"
    ```

    If you encounter any errors or problems with this step, please reach out to us on
    [our Github Discussions page][]. If you want, you can view [this
    page](https://docs.python.org/3/library/venv.html) or [this
    page](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)
    for more guidance on using "virtual environments".

5. Close your `Terminal` / `Ubuntu` window *again*, then open a new one.

6. Copy, paste, and run the following command to re-activate your "virtual environment"
   that contains HNN-Core. **Note that you will need to do this each time you open a new
   `Terminal`/`Ubuntu` window, or if you restart your computer and want to use HNN-Core
   again**:

    ```bash
    source ~/.venv/bin/activate
    ```

7. Once you have activated your environment, you can run the GUI using the following
   command:

    ```bash
    hnn-gui
    ```

8. Everything should be installed and working now! As a reminder, if you restart your
   computer or open new `Terminal`/`Ubuntu` windows, then you will have to "activate
   your virtual environment" once again to use the HNN-Core API or the GUI. You can do
   this using the following command:

    ```bash
    source ~/.venv/bin/activate
    ```

    After which you can run `hnn-gui` to open the GUI, run python code/files using
    `python` or `ipython`, or open Jupyter notebooks using `jupyter notebook`. Proceed to the rest of
    [our HNN Textbook][] to get started!


<!------------------------ Detailed/complex collapsible --------------------------->
<div class="collapsible-section collapsible-default">
<h4 class="collapsible-header">
Local Installation - Detailed
</h4>
<div class="collapsible-content">

This section intended for advanced users or if you are having issues installing HNN-Core on Windows. If the above [Windows (WSL)](#windows-wsl) install did not work for you, then please either try the [non-WSL Windows Installation section below](#non-wsl-windows-installation) or reach out to us on [our Github Discussions page][] and we will happily assist you.

There are a few cases where you should **not** follow the [above "simple" directions](#local-installation---simple):

- **If you want to co-install HNN alongside MNE:** In this case, we strongly recommend that you install MNE *first* [(MNE install guides here)](https://mne.tools/stable/install/index.html). If you installed MNE using its `pip` or `conda` methods, then afterwards, you should install HNN using the command `pip install "hnn-core[all]"`, but **only in the same Python environment that you installed MNE into**.

- **If you are using your institution's High-Performance Computing (HPC) environment** (also called a "computing cluster" or supercomputer): Refer to your HPC's documentation (or ask an HPC colleague) whether your HPC supports `conda` or `uv`. If they only support `conda`, then follow [these directions below](#anaconda--conda), except that you should not install Anaconda, and there will likely be additional steps that you need to *adapt to your HPC's configuration*. Additionally, if you are using an HPC, then **after you have installed HNN-Core, you should run `uv pip uninstall openmpi`**. This will allow you to use your HPC's custom MPI libraries, but this will require *additional configuration unique to your HPC*. You can always ask us for help at [our Github Discussions page][].

- **If you are at Brown University and want to use HNN on the OSCAR system:** We have made custom instructions for you, which [can be found here at this other page](https://github.com/jonescompneurolab/oscar-install).

- If you **previously installed our custom `conda` package** via `conda install hnn-core-all -c jonescompneurolab -c conda-forge` (note: this is *different* from our `pip` package at `pip install "hnn-core[all]"`), then we recommend you stop using that `conda` environment and instead reinstall HNN-Core using our [above "simple" directions](#local-installation---simple). We have discontinued our custom `conda` package, and are no longer updating it.

- **If you want to use a "custom" version of HNN's source code:** This includes if you need to use your own "Github fork", someone else's fork, or **if you want to contribute to HNN's development**. In this case, you should follow the [**Install from Source Code** section below](#install-from-source-code).


<!-------------------------- Anaconda sub-collapsible ------------------------------->


<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header">
Anaconda / `conda`
</h5>
<div class="collapsible-content">

We recommend using `uv` to install Python and manage your enviroments, but if you prefer
or must use the [Anaconda Python
Distribution](https://www.anaconda.com/download/success) (aka `conda`), then HNN-Core
works there too. You can install HNN-Core in a `conda` environment using the following:

1. Install [Anaconda Python Distribution](https://www.anaconda.com/download/success) if
   you have not already done so. If you are unfamiliar with using Anaconda/Conda virtual
   environments, [you can find guidance about them
   here](https://www.anaconda.com/docs/getting-started/working-with-conda/conda-intro-tutorial).

2. Open either your `Terminal` app (MacOS / Linux) or the `Anaconda Prompt` app if you
   installed Anaconda on Windows.

3. Accept the terms of service by copying, pasting, and running the following commands:

    ```bash
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
    ```

4. Create a `conda` environment if you have not already done so by copying, pasting, and
   running the following command:

    ```bash
    conda create -y -q -n hnn-core-env python=3.14

    ```

5. Activate the `conda` environment using the following command. **Note that you must do
   this every time you open a new `Terminal`/`Anaconda Prompt` window or after you
   restart your computer**.

    ```bash
    conda activate hnn-core-env
    ```

6. Finally, install and test HNN-Core using the following commands:

    ```bash
    pip install "hnn-core[all]"
    python -c "
    from hnn_core import neymotin_2020_model, simulate_dipole
    simulate_dipole(neymotin_2020_model(), tstop=20)
    print('--> SUCCESS: The test worked')"
    ```

7. You can start the GUI by running the following command:

    ```bash
    hnn-gui
    ```

8. Everything should be installed and working now! As a reminder, if you restart your
   computer or open new `Terminal`/`Anaconda Prompt` windows, then you will have to
   "activate your virtual environment" once again to use the HNN-Core API or the
   GUI. You can do this using the following command:

    ```bash
    source ~/.venv/bin/activate
    ```

    After which you can run `hnn-gui` to open the GUI, run python code/files using
    `python` or `ipython`, or open Jupyter notebooks using `jupyter notebook`. Proceed to the rest of
    [our HNN Textbook][] to get started!

</div>
</div>
<span style="height: 30px;" />


<!----------------------- non-WSL Windows sub-collapsible----------------------------->


<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header">
non-WSL Windows Installation
</h5>
<div class="collapsible-content">

On Windows, we strongly recommend you first try the ["Windows (WSL)" (Windows Subsystem
for Linux) install above](#windows-wsl). The following instructions are only for those who strictly
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
Developers: Note from Austin on 2026-11-18:
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

2. Open the Start Menu and type `powershell`, but do not hit enter or left-click the icon yet.

3. Right-click on the icon for Powershell and select "Run as administrator". A new window should open.

4. Inside the Powershell window, copy, paste, and run the following command, then press `Y` for Yes. If you are unable to do this step, then reach out to us at [our Github Discussions page][].

     ```bash
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
     ```

5. Copy, paste, and run the following commands (you can paste them all together), which will take several minutes:

    ```bash
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
    uv pip install -U "hnn-core[all]"
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

    ```bash
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

    ```bash
    cd ~
    .venv\Scripts\activate
    ```

    After which you can run `hnn-gui` to open the GUI, run python code/files using
    `python`, or open Jupyter notebooks using `jupyter notebook`. Proceed to the rest of
    [our HNN Textbook][] to get started.

</div>
</div>
<span style="height: 30px;" />


<!----------------------- Source Install sub-collapsible----------------------------->
<div class="collapsible-section collapsible-default">
<h5 class="collapsible-header">
Install from Source code
</h5>
<div class="collapsible-content">

This method should only be used if you need to install a custom version of HNN from Github, need to edit the code yourself, or want to contribute to HNN development.

1. First, follow all the instructions of [Part 1 of the simple installation.](#local-installation-part-1-platform-specific-requirements)

2. [Setup `git` using the instructions
here](https://docs.github.com/en/get-started/git-basics/set-up-git). Note that you need
to do two steps:

    2.1. Make sure that `git` is installed [using these
steps](https://docs.github.com/en/get-started/git-basics/set-up-git#setting-up-git). Note that if you are on Windows Subsystem for Linux, you need to install `git` using the *Linux* commands inside your `Ubuntu` window, not the *Windows* commands.

    2.2. Make sure that your `git` program has authenticated to Github [using these
steps](https://docs.github.com/en/get-started/git-basics/set-up-git#authenticating-with-github-from-git). Create a Github account if you do not have one.

3. Open a `Terminal` (MacOS / Linux) or `Ubuntu` window (Windows Subsystem for Linux).

4. Download and [install the `uv` Python package and project
   manager](https://docs.astral.sh/uv/getting-started/installation/) by copying,
   pasting, and running the following command:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

5. Close the `Terminal`/`Ubuntu` window, then open a new one.

6. Identify which Github "fork" you are interested in downloading. If you are working with a colleague then ask them which fork you should download. If not, then create your own fork of [https://github.com/jonescompneurolab/hnn-core](https://github.com/jonescompneurolab/hnn-core) , and clone your new fork.

7. In your `Terminal`/`Ubuntu` window, run the command

    ```bash
    git clone <fork URL>
    ```

    Where the URL is the website address of which fork you want to use. For example, if you wanted to download Austin Soplata's personal fork, you would run `git clone https://github.com/asoplata/hnn-core`.

8. Enter the directory that you just downloaded, using the command `cd hnn-core`.

9. Enter the command `pwd`. This will show you the path to where your code has been stored. **Write down this location**, since this is where you will be modifying the code of HNN.

10. If you are working with a colleague and they require you to switch to a different "`git` branch", then ask them which branch to use and for help doing so.

11. Copy, paste, and run the following series of commands in order to install Python,
   create a new "virtual environment", install HNN-Core, and test HNN-Core. You can copy
   and paste *all of them together at one time*:

      ```bash
    uv python install 3.14
    uv venv -p 3.14
    source .venv/bin/activate
    uv pip install --editable ".[dev]"
    python -c "
    from hnn_core import neymotin_2020_model, MPIBackend, simulate_dipole
    with MPIBackend():
        simulate_dipole(neymotin_2020_model(), tstop=20)
    print('--> SUCCESS: The test worked')"
    ```

12. You're done! If you had no errors, then HNN has been installed from source code!
    This is an "editable" Python install, so as you make changes to the Python code,
    rerunning your code should use your changes *automatically* (note that this does not
    apply to MOD files). If you encounter any errors or problems with this step, please
    reach out to us on [our Github Discussions page][]. If you want, you can view [this
    page](https://docs.python.org/3/library/venv.html) or [this
    page](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)
    for more guidance on using "virtual environments".

13. As a reminder, if you restart your computer or open new `Terminal`/`Ubuntu` windows,
   then you will have to "activate your virtual environment" once again to use the
   HNN. You can do this using the following command:

    ```bash
    source <where the code is located>/.venv/bin/activate
    ```

    After which you can run `hnn-gui` to open the GUI, run python code/files using
    `python` or `ipython`, or open Jupyter notebooks using `jupyter notebook`. Proceed
    to the rest of [our HNN Textbook][] to get started!

</div>
</div>
<span style="height: 30px;" />

</div>
</div>


[our HNN Textbook]: ../preface.html
[NEURON]: https://nrn.readthedocs.io/
[our HNN Textbook website]: https://jonescompneurolab.github.io/textbook/content/preface.html
[our GitHub Discussions page]: https://github.com/jonescompneurolab/hnn-core/discussions

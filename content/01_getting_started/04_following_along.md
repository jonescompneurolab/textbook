<!--
# Title: 1.4 Follow Along with the Textbook
# Updated: 2026-10-15
#
# Contributors:
    # Dylan Daniels
-->

# 1.4 Follow Along with the Textbook

## Set Up Your HNN Environment

To follow along with our detailed walkthroughs for simulating ERPs and rhythms, we assume that you have access to the latest stable version of the `hnn-core` software. If not, please follow the instructions on our [Installation page](https://jonescompneurolab.github.io/textbook/content/01_getting_started/installation.html) to set up HNN. We also recommend reading the remainder of this page in full, as there are additional instructions for following along with the walkthroughs.

Assuming you've completed the [Local Installation - Simple](https://jonescompneurolab.github.io/textbook/content/01_getting_started/installation.html#local-installation---simple) instructions, you can activate your environment with the following Terminal/Ubuntu command:

```bash
source ~/.venv/bin/activate
```

You can then launch the GUI from the active environment with the following command:

```bash
hnn-gui
```

## Follow Along With the Python API Tutorials

Note that any code blocks in our API walkthroughs are *cumulative*. That is to say, these code blocks are meant to be run in sequential order, as they are drawn from a single `ipython` notebook file.

By clicking the `Download Notebook` button at the top of any subpage, you can download the entire `.ipynb` file and run it interactively through Jupyter Notebook or through your preferred code editor (VS Code, PyCharm, etc.).

If you would like to launch a Jupyter Notebook server directly from the command line, can do so with the following command:

```bash
jupyter notebook
```

Alternatively, you can start an interactive `ipython` Python interpreter with the command below. This will allow you to run individual Python code lines without using Jupyter:

```bash
ipython
```

## Accessing Data and Network Files

At various points in the tutorials, we will reference particular network and/or data files found on our [hnn-data GitHub repository](https://github.com/jonescompneurolab/hnn-data/). **To follow the tutorials, you should download these files**.

In brief, the `MEG_detection_data` subdirectory contains the experimental MEG data referenced in our Jones et al. (2007) study [@jones_neural_2007], while the `network-configurations` subdirectory contains various network configuration files for simulating ERPs and rhythms.

You can download these files in two ways:

### 1. Simple clicking

A. First, go to our [hnn-data GitHub repository](https://github.com/jonescompneurolab/hnn-data/).

B. Click the green `Code` dropdown button.

C. Click where it says `Download ZIP` to download all the files in a single ZIP compressed file.

D. On your local computer, go to where you downloaded the file and either double-click on the ZIP file (MacOS) or right-click and then click on an option that says "Extract All" or "Extract Here" (Windows or Linux).

E. The files will now be available in a new folder.

### 2. Clone from `git`

A. [Setup `git` using the instructions
here](https://docs.github.com/en/get-started/git-basics/set-up-git), if you do not already have it installed.

B. Open a Terminal/Ubuntu window, and navigate to where you want the data to be downloaded to.

C. Clone our Github repository by running the following command:

```bash
git clone https://github.com/jonescompneurolab/hnn-data.git
```

D. We will periodically update or add new network configuration files, so we recommend occasionally pulling the latest changes from GitHub. You can do so with the following commands:

```bash
git checkout main
git pull origin main
```

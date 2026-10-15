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

Note that the [Installation page](https://jonescompneurolab.github.io/textbook/content/01_getting_started/installation.html) includes instructions for running HNN "through the cloud" and for installing HNN locally on your personal machine. 

While the cloud versions of HNN can be relatively easy to get up and running, they do come with certain limitations (such as limited access to compute cores in the case of Google Colab). As such, we recommend that you install HNN using one of the local installation methods. However, if you are unable to install HNN locally, using one of the cloud methods is a perfectly viable alternative. 

The easiest way to install HNN locally is by following our [Simple Installation Instructions](https://jonescompneurolab.github.io/textbook/content/01_getting_started/installation.html#local-installation---simple). This will install the basic version of both the HNN API and the HNN GUI, which is sufficient for following our walkthroughs for simulating ERPs and rhythms, but will lack the dependencies to run some of our advanced "Using the API" tutorials later on in the Textbook.  

If you want *all* features of HNN, we recommend that you follow our [Conda Package Installation](https://jonescompneurolab.github.io/textbook/content/01_getting_started/installation.html#conda-package-installation) instructions, which will not only install the latest stable version of `hnn-core` on your device, but will also install **all** optional dependencies, including those needed for running faster simulations using the MPI distribution for parallel simulation. 


Both of the above methods utilize `conda` environments. Once you've completed the installation instructions, you can activate your conda environment with the following terminal command:

```bash
conda activate hnn-core-env
```

You can then launch the GUI from the active conda environment with the following command:

```bash
hnn-gui
```

## Follow Along With the Python API Tutorials

Note that any code blocks in our **Simulating ERPs** walkthrough are *cumulative*. That is to say, these code blocks are meant to be run in sequential order, as they are drawn from a single `ipython` notebook file.

By clicking the `Download Notebook` button at the top of any subpage, you can download the entire `.ipynb` file and run it interactively through Jupyter Notebook or through your preferred code editor (VS Code, PyCharm, etc.).

Keep in mind that your code editor may install additional dependencies needed to open and run `.ipynb` files when using the `hnn-core-env` conda environment. 

If you would like to launch a Jupyter Notebook server directly from the command line, you will need to install Jupyter's `notebook` dependency directly into `hnn-core-env`. To do so, run the following command from your active `hnn-core-env` conda environment:

```bash
conda install -c conda-forge notebook
```

After installation, you can launch the jupyter server with the following command:

```bash
jupyter notebook
```

Alternatively, you can start an interactive `ipython` environment with the command below. This will allow you to run individual commands from your command line interface without needing to install the additional `notebook` dependency from Jupyter.  

```bash
ipython
```

## Accessing Data and Network Files

At various points in the tutorials, we will reference particular network and/or data files. These files can be found on our [hnn-data GitHub repository](https://github.com/jonescompneurolab/hnn-data/).

In brief, the `MEG_detection_data` subdirectory contains the experimental MEG data referenced in our Jones et al. (2007) study, while the `network-configurations` subdirectory contains various network configuration files for simulating ERPs and rhythms.

We recommend that you clone this repository to your local machine, as you will need several of these files to follow along with the tutorials.

You can clone this repository with the following command:

```bash
git clone https://github.com/jonescompneurolab/hnn-data.git
```

We will periodically update or add new network configuration files, so we recommend occasionally pulling the latest changes from GitHub. You can do so with the following commands:

```bash
git checkout main
git pull origin main
```

## References

Jones, S. R., Pritchett, D. L., Stufflebeam, S. M., Hämäläinen, M. & Moore, C. I. Neural correlates of tactile detection: a combined magnetoencephalography and biophysically based computational modeling study. J. Neurosci. 27, 10751–10764 (2007). [https://doi.org/10.1523/JNEUROSCI.0482-07.2007](https://doi.org/10.1523/JNEUROSCI.0482-07.2007)
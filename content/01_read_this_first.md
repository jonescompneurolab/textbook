<!--
# Title: 1. Read This First!
# Updated: 2026-10-05
#
# Contributors:
    # Austin E. Soplata
    # Dylan Daniels
-->

## 1. Read This First!

There are multiple ways to use HNN-Core, referred to as "the API" and "the GUI", and we will define them here.

### GUI: Graphical User Interface

First is the GUI, short for "Graphical User Interface". An example is shown below:

![Example of basic GUI operation, displaying simulation results of a default ERP simulation.](https://raw.githubusercontent.com/jonescompneurolab/jones-website/master/images/textbook/content/04_using_hnn_gui/4-1-quickstart/images/fig_03_run_first.png)

It is designed to teach users the ins-and-outs of simulating commonly-measured MEG/EEG signals. It allows users to freely explore the properties of the template network model, including the network connections and biophysical properties of the cells and synapses. Users can modify or add new exogenous inputs that activate the network (which we refer to as the "external drives"), adjust key simulation parameters, simulate multiple trials of a network model, and visualize cell- and circuit-level output data such as layer-specific dipoles, cell-specific spiking, spectrograms, and more. 

There is no Python programming required for starting or using the GUI. This allows users to learn how science is accomplished with HNN-Core using just the GUI and the accompanying Textbook website. 

You can run the GUI two different ways:

1. **"In the cloud"**: Run the GUI using either Google Colab or the Neuroscience Gateway Portal, as described in [our Installation Guide][]. Following the instructions there will eventually give you a link where you can access a live GUI instance, which is running on someone else's computer for free. This is the easiest way to use HNN-Core since you do not need to install anything, but is also the slowest.

2. **Local installation**: You can also install HNN-Core to your local computer with just a few steps, by following [our Installation Guide][] carefully. Once you have it installed, you can open the Terminal (on macOS or Linux) or the Command Prompt (on Windows), activate your Conda environment, then run the command `hnn-gui` to begin a new GUI instance. After this, a new tab should appear in your browser, which will be the GUI running on your own computer.

Note that the GUI is always a *tab* in your web browser (e.g. Google Chrome, Mozilla Firefox, Brave, Safari, etc.). This is true whether you are running it on your local computer or in the cloud!

Once you have the GUI running, you can begin exploring it by checking out the [GUI Quickstart here](04_using_hnn_gui/gui_quickstart.html).


### API: Coding

The GUI can do much of what's possible in HNN-Core, but it cannot do *everything* that HNN-Core has to offer. The most powerful way to use HNN-Core is through the API (Application Programming Interface), which is just a fancy way of saying "writing code in Python with the help of HNN-Core". HNN-Core is a "software library" which means it offers you "functions" and other pieces of code that you can use to do what you want, such as simulate a network with your own custom drives included.

Using the API means writing code that you save into either Python files (ending in `.py`) or [Jupyter notebook](https://jupyter.org/) files (ending in `.ipynb`), and which looks like the following:

```python
from hnn_core import read_network_configuration

net_default_gui = read_network_configuration("gui_default.json")
```

For learning what HNN-Core is and what it can do, the GUI is the best place to start. However, when you want to use complex custom networks or external drives, run a large number of simulations and trials, perform long optimization runs, customize your analysis and visualization code, or prepare your results for publication, then you should be using the API.

You can use the API (without installing it locally) via the [Google Colab notebook here](https://colab.research.google.com/drive/1FcNhHatsuxl-pACIFn7V6H5J4GPfZ1t8), but in general you will want to use the API after installing it locally on your machine, as described in [our Installation Guide][].

Using the API means programming in Python, but modern AI/LLMs can be extremely helpful for learning basic programming. Python is a very popular programming language in neuroscience, so learning how to read it will help in the long run.

To help our less "programming-savvy" users get comfortable with the API (and Python programming in general), our GUI video tutorials for simulating ERPs and rhythms (see, e.g., the [Simulating ERPs](05_erps/erp_overview.html) section) include accompanying instructions showing how to accomplish the *same* tasks using the API. The API walkthroughs also include additional code explanations that are designed to help users build the knowledge and confidence needed to use the API for scientific research. 

All API tutorials on this Textbook website, [such as the one here](08_using_hnn_api/plot_firing_pattern.html), have a button at the top marked **Download Notebook** where you can download the page and code as a Jupyter notebook file. If you have installed HNN-Core locally, then you can edit and/or run the code in these notebook files and build your own workflows off of them. 

In order to run notebooks locally, you will need to activate your hnn-core Conda environment (see [our Installation Guide] for details) and run `pip install notebook` followed by `jupyter notebook` in either the Terminal (macOS/Linux) or Command Prompt (Windows). This will open the Jupyter interface in your browser, which will allow you to open and interactively run `.ipynb` files. 

Another way to use notebooks is to download and install [VS Code](https://code.visualstudio.com/download) which is a popular code editor. In VS Code, you can load a notebook file, then select your Conda environment as the environment to use, then execute the notebook. (Note: VS Code will automatically prompt you to install the `notebook` dependency if you need it.)

[our Installation Guide]: 02_getting_started/installation.html

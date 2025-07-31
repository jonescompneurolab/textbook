<!--
# Title: Preface
# Updated: 2024-11-14
#
# Contributors:
    # Dylan Daniels
-->

## Preface

Welcome to our online textbook on using Human Neocortical Neurosolver (HNN) to study the cellular and circuit-level mechanisms of electro- and magneto-encephalography (EEG/MEG) signals. The core of HNN is a biophysically detailed model of a neocortical circuit activated by simulated thalamic and cortical inputs. HNN is designed to study the detailed neural generators of signals from a single brain area, with workflows focussed on event related potentials (ERPs) and brain rhythms.

This textbook provides a comprehensive introduction to how HNN can be used to develop and test hypotheses about the local micro-circuit generators of localized EEG/MEG signals. The chapters cover various topics, including background information on biophysical neural modeling, circuit dynamics, parameter optimization, model validation, and much more. You will learn how to use HNN to simulate commonly recorded EEG/MEG signals, including event-related potentials (ERPs) and low-frequency rhythms such as alpha (7-14 Hz), beta (15-29 Hz), and gamma (30-80 Hz) using examples from prior published studies.

HNN is an open-source software built in Python using the software NEURON, and it can be run through an interactive graphical user interface (GUI) or a command-line interface (CLI). In practice, users start by using the interactive GUI to learn how to activate the HNN model and adjust parameters to study ERPs and rhythms. Once a basic understanding is achieved, the same simulations can be run through the CLI. Most sections of the textbook will include workflows for using both the GUI and CLII, although some advanced features (e.g., batch simulation) are only available in the CLI, which allows for more advanced user-defined workflows.

Our Getting Started section provides an overview of key background information needed to follow along. Some basic background knowledge in neuroscience and neural modeling is assumed. Additionally, references are included at the end of each section for those who wish to dive deeper into the methods and underlying theory.

To get the most out of this textbook, we recommend that you [use HNN from the cloud](01_getting_started/installation.html#running-hnn-in-the-cloud) or [install HNN locally](01_getting_started/installation.html#local-installation) and follow along with the examples we provide.

If you have any questions, please visit our [HNN Discussion board](https://github.com/jonescompneurolab/hnn-core/discussions) on GitHub.

Happy modeling!

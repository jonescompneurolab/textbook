<!--
# Title: 2.1 Introducing HNN
# Updated: 2025-03-06
#
# Contributors:
    # Dylan Daniels
-->

## 2.1 Introducing the Human Neocortical Neurosolver (HNN)

HNN is an open-source software for developing and testing hypotheses on the cellular and circuit-level mechanisms of electro- and magneto-encephalography (EEG/MEG) signals from a localized neocortical area. The foundation of HNN is a biophysically-principled neocortical column model that simulates the electrical activity of the neocortical cells and circuits that generate the primary electrical currents underlying EEG/MEG recordings. It is designed around workflows to activate the neocortical model via thalamic and cortical inputs to examine the multi-scale generators of ERPs and brain rhythms. To learn more about the HNN model, see the [Template Model](template_model.html) section of the Textbook.

## Addressing The Challenge in Human Neuroscience

EEG/MEG are among the most powerful technologies to non-invasively record human brain activity with millisecond resolution, and they provide reliable markers of healthy brain function and disease states. A major limitation of EEG/MEG is that it can be difficult to connect the macroscopic signals to the underlying neural generators. This difficulty limits the translation of EEG/MEG studies into novel principles of information processing and also into new treatment modalities for neural pathologies.

HNN provides a novel solution to this challenge by giving researchers and clinicians the ability to develop hypotheses on the cell and circuit mechanism underlying their EEG/MEG data, using a previously developed and tuned neocortical Template Model. The multi-scale simulation possible with HNN (e.g., layer- and cell-specific spiking, LFP, CSD) allows for the empirical validation of model-derived predictions across multiple recordings scales and species. As such, HNN is a bidirectional hypothesis testing and development tool aimed to bridge macro-scale human EEG/MEG signals to the underlying micro/meso scale activity. Once you've used HNN to developed biophysically-principled hypotheses on the origins of your signal, your hypotheses can then be validated through invasive animal recordings.

Our goal is not to promote singular theories on the origin of any particular signal. Rather, our goal is to provide a tool based on known biophysics, and the knowledge to use the tool, so that researchers can develop testable predictions on the neural origins of their data.

## Getting Started with the HNN Textbook

The HNN Textbook covers many different topics at various levels of depth. We encourage you to start with the [Template Model](template_model.html) section to develop a deeper understanding of how and why we employ detailed biophysical modeling as opposed to other modeling frameworks. From there, you can explore our various workflows for studying the origins of event-related potentials (ERPs) and brain rhythms based on our lab's published studies. Our walkthroughs use real source-localized data and pre-tuned network configurations to teach you how to replicate the methods used in our own research. 

We recommend that users new to HNN start with our Graphical User Interface (HNN-GUI), as it is an excellent tool for building intuition and visualizing changes to network parameters. For each HNN-GUI workflow, we also include an accompanying workflow using the HNN Python API (HNN-API). The HNN-API is more feature rich than HNN-GUI, and so we encourage more experienced users to lean the HNN-API in tandem with HNN-GUI.  

After completing our workflows for studying the origins of ERPs and brain rhythms, you will be equipped with the tools to use HNN to develop and test hypotheses with your own source-localized data. Once you've mastered the basics, you'll be ready to explore the other sections of our Textbook, which include advanced demos that cover various topics, including: modifying local connectivity, running batch simulations, and more. 

If you have any questions while working through the Textbook, please visit our [HNN Discussions page](https://github.com/jonescompneurolab/hnn-core/discussions/categories/general). 

Happy modeling! 🧠

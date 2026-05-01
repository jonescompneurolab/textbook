<!--
# Title: 2.1 Cortical Column Structure
# Updated: 2024-11-14
#
# Contributors:
    # Dylan Daniels
-->

<!-- compare original: https://jonescompneurolab.github.io/hnn-under_the_hood/01_cortical-column-structure/01_cortical-column-structure -->

# 2.1 Cortical Column Structure

Neocortical circuits are organized with remarkably similar features across areas and species. These features include a common laminar structure with generalizable cell classes as well as similar local connectivity and input and output connectivity patterns. We have harnessed this generalization into HNN’s foundational neural model that is provided as a template circuit to work with.

<div style="display:block; width:50%; margin: 0 auto;">
![3D representation of our cortical model. Abstracted multi-compartment pyramidal neurons are aligned in a 10-by-10 grid in layer 2 and layer 5. Interneurons are shown as red point neurons near the pyramidal cell somas.](https://raw.githubusercontent.com/jonescompneurolab/jones-website/master/images/textbook/content/03_assumptions/images/netpyne-schematic-tilted-colored.png)
</div>

<p style="text-align:justify; display: block; margin: 0 auto;width: 90%; font-size: 1em;">
**Figure 1**: Most importantly, our model contains multi-compartment pyramidal neurons (PN) in supragranular and infragranular layers (layers 2/3 and 5, respectively), whose apical dendrites are spatially aligned and span the cortical layers as shown in the 3D visualization above. The primary electrical current signals simulated in HNN are derived from the intracellular current flow in the PN dendrites (see [2.2 Primary Electrical Currents][] for details). In the figure above, the green neurons represent the layer 2/3 PN and the blue the the layer 5 PN. Note that in both layers, the PN have two basal, one oblique, and one apical dendrite branch, and the layer 2/3 PN have shorter apical dendrites compared to the layer 5 PN.
</p>

The PN are synaptically coupled to each other and to a subset of inhibitory neurons in each layer in a 3/1 PN-to-interneuron ratio. The inhibitory neurons are simulated with single compartments and represent fast spiking basket cells, and are shown in red in the figure above. Details of the cells and synaptic connectivity structure are given under [2.3 Neurons: Morphology and Physiology][] and [2.4 Synaptic Connectivity][], respectively.

There are several ways to activate the local cortical column with layer specific synaptic (thalamo-cortical, and/or cortical-cortical) and tonic drive, as detailed in both [2.5 Evoked and Rhythmic Driving Inputs][] and [2.6 Tonic and Noisy Driving Inputs][].

The list below provides an overview of key features of the template model provided, further details are outlined in other pages under [1.2 Template Model][]

1. Supragranular layer (layer 2/3) with multi-compartment pyramidal and single compartment inhibitory neurons
2. Infragranular layer (layer 5) with multi-compartment pyramidal and single compartment inhibitory neurons
3. A scalable number of neurons per layer with 3/1 PN-to-interneuron ratio (default network contains 100 PN per layer)
4. Gabaergic (GABAA/GABAB) & Glutamatergic (AMPA/NMDA) synaptic connectivity between local cortical column cells
5. Membrane voltages simulated with Hodgkin-Huxley type dynamics, with active ionic currents in somatic and dendritic compartments
6. Layer specific exogenous driving inputs (synaptic and tonic/noisy)
7. Primary current dipole calculated as net intracellular current flow in PN dendrites (Units: nano-Ampere-meters (nAm))

Of note, the **granular layer is not explicitly included in the template circuit**. This initial design choice was based on the fact that macroscale current dipoles are dominated by PN activity in supragranular, and intragranular layers. Thalamic input to granular layers is presumed to propagate directly to basal and oblique dendrites of PN in layer 2/3 and 5 (see [2.5 Evoked and Rhythmic Driving Inputs][] for details). As the use of our open-source software grows, we hope that other cells and network configurations will be made available as template models to work with.

[1.2 Template Model]: ../01_getting_started/template_model.html
[2.1 Cortical Column Structure]: ./cortical_column_structure.html
[2.2 Primary Electrical Currents]: ./primary_electric_currents.html
[2.3 Neurons: Morphology and Physiology]: ./neurons_morphology_and_physiology.html
[2.4 Synaptic Connectivity]: ./synaptic_connectivity.html
[2.5 Evoked and Rhythmic Driving Inputs]: ./evoked_and_rhythmic_driving_inputs.html
[2.6 Tonic and Noisy Driving Inputs]: ./tonic_and_noisy_driving_inputs.html

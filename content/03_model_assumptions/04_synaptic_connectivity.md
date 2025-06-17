<!--
# Title: 2.4 Synaptic Connectivity
# Updated: 2024-01-16
#
# Contributors:
    # Dylan Daniels
-->

<!-- compare original: https://jonescompneurolab.github.io/hnn-under_the_hood/03_architecture-connectivity/03_architecture-connectivity -->

# 2.4 Synaptic Connectivity

<table style="border:none">
  <tr>
    <td style="border:none" width=>
    ![](https://raw.githubusercontent.com/jonescompneurolab/jones-website/master/images/textbook/content/03_assumptions/images/synaptic-connectivity.png)
    </td>
    <td style="border:none; vertical-align:middle;">
    ![](https://raw.githubusercontent.com/jonescompneurolab/jones-website/master/images/textbook/content/03_assumptions/images/3d-column-model.png)
    </td>
  </tr>
  <tr>
    <td style="border:none">
      <p style="text-align:justify; text-align-last:center; width:90%">
        Computational neural model written in NEURON-Python simulates the direction and time-course of the primary electrical currents (Jp; indicated via red arrows) via intracellular electrical currents in cortical pyramidal neuron dendrites (units: nano-Ampere-meters).
      </p>
    </td>
    <td style="border:none">
      <p style="text-align:justify; text-align-last:center; width:90%">
        Model of cortical column includes 100s to 1000s (scalable) of multicompartment pyramidal neurons and single compartment interneurons (model source code)
      </p>
    </td>
  </tr>
</table>

Neurons in the model are arranged in three dimensions. The XY plane is used to array cells on a regular grid while the Z-axis specifies cortical layer. HNN’s default model contains a regular 10 x 10 grid (arbitrary units) of pyramidal neurons in layer 2/3 and layer 5 for a total of 200 pyramidal neurons. There are also 35 interneurons per cortical layer, interspersed between the pyramidal neurons. In total, the default model therefore contains 270 neurons. The 3D visualization below shows the neurons, rotated to allow easier viewing. The top and bottom represent cortical layer 2/3 and layer 5. In the visualization, the following color code is used for the different cell types in the model– red: layer 5 pyramidal neurons; green: layer 2/3 pyramidal neurons; white: layer 2/3 interneurons; blue: layer 5 interneurons.


<div style="display:block; width:100%; margin: 0 auto;">
![](https://raw.githubusercontent.com/jonescompneurolab/jones-website/master/images/textbook/content/03_assumptions/images/colored-column-model.png)
</div>

The illustration below shows a schematic of local network connectivity. The blue cells are pyramidal cells, while the orange circles represent the interneurons. The lines between neurons represent local synaptic connections. Lines ending with a circle are excitatory (AMPA/NMDA) synapses, while lines ending with a line are inhibitory (GABAA/GABAB) synapses. Note that within a cortical layer there is recurrent connectivity between neurons of a given type (Pyramidal neuron to Pyramidal neuron, interneuron to interneuron), Pyramidal neuron to interneuron connectivity, and synaptic inhibition from interneurons onto pyramidal neurons. The following synaptic connections are present across cortical layers: layer 2/3 pyramidal neurons to layer 5 pyramidal neurons, layer 2/3 interneurons to layer 5 pyramidal neurons, layer 2/3 pyramidal neurons to layer 5 interneurons. Note that although not shown in the figure, there are also inhibitory synaptic connections between interneurons within a layer. The connectivity details are based on the neocortical microcircuit wiring patterns determined in experiments.

<div style="display:block; width:50%; margin: 0 auto;">
![](https://raw.githubusercontent.com/jonescompneurolab/jones-website/master/images/textbook/content/03_assumptions/images/detailed-connectivity.png)
</div>

Note that in the default model, within a layer, there is all-to-all connectivity between pyramidal neurons. The synaptic weights between neurons are scaled inversely by the distance in the XY plane (arbitrary units) between the neurons (d) using exponential fall-off following $e^{-d^2 / \lambda^2}$, and space constant $\lambda$. The synaptic delays are scaled in proportion to the XY plane distance (d) between the neurons following $1 / e^{-d^2 / \lambda^2}$ to account for the larger propagation. This scaling is illustrated in the figure below, with a $\lambda$ of 3. The figure below represents one neuron located at the center (x=0, y=0), with other neurons positioned relative to that neuron (neuron positions indicated with black dots). As shown, with increasing distance from the center, the synaptic weights decay, while the synaptic delays increase.

<div style="display:block; width:100%; margin: 0 auto;">
![](https://raw.githubusercontent.com/jonescompneurolab/jones-website/master/images/textbook/content/03_assumptions/images/weight-scaling.png)
</div>

In future versions of HNN, we will allow adjustments to the local circuit architecture and connection profiles. For more details of the default model see [@jones_quantitative_2009].

## Tutorial References

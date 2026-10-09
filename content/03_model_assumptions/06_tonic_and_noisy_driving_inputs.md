<!--
# Title: 3.6 Tonic and Noisy Driving Inputs
# Updated: 2024-01-16
#
# Contributors:
    # Dylan Daniels
-->

<!-- compare original: https://jonescompneurolab.github.io/hnn-under_the_hood/05_tonic-noisy-inputs/05_tonic-noisy-inputs -->

# 3.6 Tonic and Noisy Driving Inputs

HNN also provides Poisson-distributed inputs as well as tonic current clamps. The tonic inputs are modeled as somatic current clamps with a fixed current injection. These clamps can be used to adjust the resting membrane potential of a neuron, and bring it closer (with positive amplitude injection) or further from firing threshold (with a negative amplitude injection). You can set the current clamp amplitude, and start/stop time for each neuron type. HNN’s Poisson Inputs are excitatory AMPAergic synaptic inputs to the somata of different neurons, which follow a Poisson Process. You can set the average frequency, strength, and timing of these inputs to individual neuron populations. See Tour of the GUI for details on how to set these inputs.

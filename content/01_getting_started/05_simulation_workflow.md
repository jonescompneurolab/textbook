<!--
# Title: 1.5 Simulation Workflow
# Updated: 2026-10-19
#
# Contributors:
    # Dylan Daniels <dylan_s_daniels@alumni.brown.edu>
-->

# 1.5 Simulation Workflow in HNN

Before we dive into the details of using the software, we want to emphasize that HNN is designed around specific **workflows** for examining the multiscale generators of event-related potentials (ERPs) and low-frequency brain rhythms. 

Since HNN is designed to simulate the multiscale origin of source-localized primary current dipoles, i.e. the neural sources of the sensor-level EEG/MEG signals, experimental data should be source localized to a particular neocortical area for a direct comparison to HNN dipole outputs.

When using HNN to understand your own experimental data, you'll typically start with the workflow outlined below.

<div class="callout callout-note">

<div class="callout-header">
<div class="callout-icon">
<svg class="lightbulb-icon">
<use href="#lightbulb"></use>
</svg>
</div>

<div class="callout-title">
Typical HNN Workflow
</div>
</div>

<div class="callout-body">

1. Initialize the software
   - When starting the software with either the HNN-GUI or HNN-Core API, a network model is initialized that contains a pre-tuned neocortical column model and initial parameters for activating the network
2. Load your experimental data in the proper format
   - Note that HNN is **not** a source localization software. This step must be performed before loading your data into HNN
   - HNN expects source-localized data in nanoampere-meters (nAm) x milliseconds, so the data should be converted to the proper units before loading
3. Activate the network
   - All simulation experiments begin by activating the pre-tuned neocortical column model with a sequence of layer-specific excitatory synaptic drives
   - HNN is distributed with pre-defined patterns of drive to use as a starting point for studying ERPs and low-frequency oscillations (see our Textbook tutorials). We provide numerous network configurations for different experimental conditions that can be used as a starting point for simulating your data
   - To begin, one of these pre-tuned (“default”) patterns of drives is chosen and an initial simulation is run to compare the default model output to the experimental data. These pre-tuned drives can be found in our [hnn-data GitHub repository](https://github.com/jonescompneurolab/hnn-data/tree/main)
4. Adjust the scaling (and smoothing) of your signal
   - While the pre-tuned network model and driving pattern have proven to be a good starting point for many studies, often the size of the simulated dipole is not on the same scale as the empirical data.
   - A multiplicative scaling factor can be applied to the simulated current dipole to better match the empirical dipole magnitude. The proper scaling factor in HNN provides an estimate of the actual number of neurons representing the size of the area of cortex that contributes to the recorded signal
5. Identify parameters of interest for tuning to improve the fit between your experimental data and your simulations, and begin hand tuning the parameters
   - HNN is a large-scale model that contains many pre-tuned parameters that have proven to be a useful starting point for many studies. HNN is designed to be a hypothesis development and testing tool. When fitting model output to empirical data, users must first identify a limited set of “parameters of interest” hypothesized to be key contributing mechanisms to the recorded signals. Our tutorials guide users through an initial set of “parameters of interest” to tune based on many prior studies on the mechanisms contributing to ERPs and low-frequency oscillations
   - We recommend that you start by tuning the parameters of interest “by hand” using our interactive HNN-GUI (rather than using a parameter optimization algorithm) to gain intuition on how parameter changes impact the underlying multiscale simulation through parameter exploration. HNN’s model complexity is uniquely designed to enable this exploration. 
6. Algorithmic parameter optimization
   - Once a reasonable fit between the simulated and recorded data is obtained via hand tuning, parameter optimization algorithms can be applied to identify optimal parameter values that provide the best fit to your data
   - Parameter distributions and uniqueness of parameters can be quantified using a technique called Simulation-Based Inference, available only with the HNN-Core API
7. Multiscale examination and validation
   - The above workflow is designed around matching simulated and empirical current dipole signals. Once a good fit is obtained, users can examine the underlying microcircuit dynamics, such as cell- and layer-specific spike activity, layer-specific dipoles, and further details in the HNN-Core API, including LFP/CSD and pyramidal neuron calcium dynamics
   - The underlying multiscale dynamics provide targets for validating and/or further constraining model-derived predictions in follow-up experiments
   - As an alternative to the workflow described above, if data are available, users may start by constraining the model to micro- (e.g., cell spiking) or meso-scale (e.g., LFP/CSD) activity and predict the corresponding macroscale E/MEG current dipole signal

</div>

</div>
<!--
# Title: 4.4 Simulation Workflow
# Updated: 2026-07-11
#
# Contributors:
    # Dylan Daniels <dylan_s_daniels@alumni.brown.edu>
-->

# 4.4 Simulation Workflow in HNN

Before we dive into the details of using the software, we want to emphasize that HNN is designed around specific **workflows** for examining the multi-scale generators of event-related potentials (ERPs) and brain rhythms. 

Since HNN simulates the primary current dipoles, i.e. the neural sources of the sensor-level EEG/MEG signal, your experimental data must be source-localized to a particular neocoritcal area for a direct comparison to HNN simulation outputs

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

1. Load your experimental data in the proper format
    - Note that HNN is **not** a source localization software. This step must be performed before loading your data into HNN
    - HNN expects data in nanoampere-meters (nAm) x milliseconds, so you should convert your signal to the proper units before loading your data
2. Run an initial simulation using one of the default models
    - We provide numerous network configurations for different experimental conditions that can be used as a starting point for simulating your data
    - These can be found in our [hnn-data GitHub repository](https://github.com/jonescompneurolab/hnn-data/tree/main)
3. Adjust the scaling (and smoothing) of your signal
    - The scaling in HNN represents the size of the area of cortex that contributes to the recorded signal
    - There is no guarantee that your data will match the scale of HNN's default models, so you will typically need to adjust the scaling to bring them in line with each other
4. Hand tune the model parameters to improve the fit between your experimental data your simulations
    - HNN is a **hypothesis-testing tool** first and foremost. Our workflows are centered around making predictions about the cell- and circuit-level generators of your experimental signal, and then testing those predictions through simulation
    - For studying ERPs, we recommend that you start by tuning the timing and strengths of the external drives to the network
5. Optimize your simulation
    - Once you have obtained a reasonable fit from hand tuning, you run an optimization algorithm to find the optimal parameter values.
    - You can constrain the search space of the optimization based on what you discovered when you tuned the network by hand

</div>

</div>
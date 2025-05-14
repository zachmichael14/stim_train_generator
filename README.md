# Seáñez Lab Continuous Stimulation Generator
This application is used to deliver continous stimulation at variable frequencies and amplitudes.

## Hardware Requirements
- National Instruments data acquistion device (NI-DAQ/DAQ)
- Digitimer DS8R Electrical Stimulation
- Digitimer D188 channel switcher (optional)

## User Guide
### Cathode Selector
Two modes are available: single electrode mode and multiple electrode mode. Single electrode mode is selected by default with its sole electrode already enabled. Single electrode mode only requires the DS8Rs while the use of multiple electrode modes requires the use of the D188 channel switcher in conjunction with the DS8R.

To deliver stimulation via the selected electrode (electrode selection is indicated by a green color), switch the `Stimulation` toggle to the ON position, and stimulation will be delivered using the frequency and amplitude values specified.

When both the electrode button and the `Stimulation` toggle are enabled, de-selecting the electrode will stop stimulation, as evidenced by the `Stimulation` toggle switching to the OFF position. This behavior is the same for both single and multiple electrode mode.

![Single electrode toggled off](assets/single_electrode_off.gif)
*Toggling electrode off in single electrode mode also toggles stimulation off*

![Multiple electrode off](assets/multiple_electrode_off.gif)
*Toggling electrode off in multiple electrode mode also toggles stimulation off*

On the other hand, if both the electrode button and the `Stimulation` toggle are toggled off, switching the `Stimulation` toggle to the `On` position will trigger different behavior depending on the electrode mode:
- In single electrode mode, the electrode button is automatically enabled. The reason for automatic enabling is because there is no other device standing between the DS8R and the participant, so the stimulation will be delivered.  

![Single electrode toggled on](assets/single_electrode_on.gif)
*Toggling stimulation on in single electrode mode enables the sole electrode*

- When stimulation is toggle on in multiple electrode mode, the application makes no assumption about the channel on which stimulation should be delievered, so it does not enable one be default.  

![Multiple electrode not toggled on](assets/multiple_electrode_on.gif)
*Toggling stimulation on in multiple electrode mode does not enable an electrode by default*

#### Important Safety Note
If multiple electrode mode is used when there is no D188 physically connected, the aforementioned lack of an enabled electrode may make it appear to the user as though no stimulation is being delivered even when it is being delivered. 

Put another way, if the DS8R's output is connected to a D188 channel switcher, the channel switcher will safely prevent this stimulation from being delivered until the user enables an electrode button in mulitple electrode mode. *However, if there is no D188 physically connected to the DS8R when multiple electrode mode is used, there is nothing to prevent the DS8R's stimulation from being delivered.*

Therefore, use single electrode mode when your physical hardware configuration resembles the following:
![Single electrode mode configuration](assets/single_electrode_configuration.svg)  
*Hardware configuration for single electrode mode*

Use multiple electrode mode only if your hardware set up involves a D188 and resembles the following:
![Multiple electrode mode configuration](assets/multiple_electrode_configuration.svg)  
*Hardware configuration for multiple electrode mode*

### Adjusting Parameters
The `Current Value` input represents the value of the parameter that will be used when stimulation is delivered, with frequency in Hertz (Hz) and amplitude in milliamps (mA).  The `Current Value` will increase or decrease by the value in the `Step` input box each time the up or down arrow of `Current Value` is clicked, respectively. The up and down arrow keyboard keys may also be used to change the value in these boxes.
![Parameter increase by step](assets/parameter_step_increase.gif)

#### Note
As a precautionary measure, the most that `Current Value` can increase at once is limited to 50 Hz for frequency and 15 mA for amplitude. As such, it's not possible to set the value of `Step` above these numbers. There is no limit to decreases.

### Beginning Stimulation
When the `Stimulation` toggle is switched to the ON position, stimulation will be delivered on the selected channel using the parameter values in `Current Value` boxes.

#### Parameter Update Immediacy
There are two ways to update stimulation parameter values while `Stimulation` is ON: live or delayed. When the `Live Update` toggle is switced to the ON position, any changes to channel, frequency, or amplitude will be immediately applied.

When `Live Update` is OFF, changes to these parameter values will only be applied after clicking the `Send Update(s)` button.
The `Ramp Update Duration` input can be used to apply these updates over a specified time period, in seconds.

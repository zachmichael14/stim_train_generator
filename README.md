# Seáñez Lab Continuous Stimulation Generator
This application is used to deliver continous stimulation at variable frequencies and amplitudes.

## Hardware Requirements
- National Instruments data acquistion device (NI-DAQ/DAQ)
- Digitimer DS8R Electrical Stimulation
- Digitimer D188 channel switcher (optional)

### Cathode Selector
Two modes are available: single electrode mode and multiple electrode mode. A single electrode is supported by the DS8R, but the use of multiple electrodes requires the use of the D188 channel switcher in conjunction with the DS8R.

Single electrode mode is selected by default with its sole electrode enabled. 

To deliver stimulation via the selected electrode, switch the `Stimulation` toggle to the on position, and stimulation will be delivered using the frequency and amplitude values specified.

If both the electrode button and the `Stimulation` toggle are enabled, de-selecting the electrode will stop stimulation, as evidenced by the `Stimulation` toggle switching to the `Off` position. This behavior is the same for both single and multiple electrode mode.
![Single electrode toggled off](assets/single_electrode_off.gif)
![multiple electrode off](assets/multiple_electrode_on.gif)


#### Important Safety Note
Use single electrode mode when your physical hardware configuration resembles the following:
![Single Electrode Mode Configuration](assets/single_electrode_configuration.svg)

Use multiple electrode mode only if your hardware set up involves a D188 and resembles the following:
![Multiple Electrode Mode Configuration](assets/multiple_electrode_configuration.svg)

The application is unable to verify the presence of a D188, and it doesn't enable an electrode by default in multiple electrode mode. Therefore, if multiple electrode mode is used when there is no D188 physically connected, the lack of an enabled electrode may make it appear as though no stimulation is being delivered even when it is being delivered.




On the other hand, if both electrode button and the `Stimulation` toggle are toggled off, switching the `Stimulation` toggle to the `On` position will trigger different behavior depending on the electrode mode.
    - In single electrode mode, the electrode button is automatically enabled. The reason for automatic enabling is because there is no other device standing between the DS8R and the participant, so the stimulation will be delivered.
    {GIF}
    - In multiple electrode mode, amplitude and trigger control signals will be sent to the DS8R, which means its output will be live.
    However, the application makes no assumption about the channel on which stimulation should be delievered, so it does not enable one be default. If the DS8R's output is connected to a D188 channel switcher, the channel switcher will safely prevent this stimulation from being delivered until the user enables an electrode button in mulitple electrode mode. *However, if there is no D188 physically connected to the DS8R, there is nothing to prevent the DS8R's stimulation from being delivered.*



Important:
The connections between the DAQ and the DS8R's amplitude and trigger control is independent of the presenece of the D188 channel switcher. That is to say that selecting an electrode in the multiple electrode mode will still deliver stimulation via the DS8R's output even if no D188 is physically connected.
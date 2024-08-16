# Seáñez Lab Stim Train Visualizer and Executor

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
  - [Hardware](#hardware)
  - [Software](#software)
- [Project Organization](#project-organization)
  - [General Data Flow](#general-data-flow)
- [Challenges](#challenges)
  - [Hardware Challenges](#hardware-challenges)
  - [Implementation Challenges](#implementation-challenges)
    - [User Input Validation](#user-input-validation)
    - [Communication Synchronicity and Timing](#communication-synchronicity-and-timing)
- [Progress](#progress)
- [Current Work](#current-work)
- [Next Steps](#next-steps)
- [Design Questions](#design-questions)

## Overview
The goal of this project is to allow users to create, visualize, and edit stimulation paradigms in an intuitive manner. The interface allows users to create and visualize stim trains on up to 8 channels using various functions to generate stimulation parameters (amplitude, frequency, duration, etc.). This application includes the ability to use custom functions for parameter generation, write generated stim train to a CSV file, and execute stim trains read from CSVs.

## Requirements:
### Hardware
- Digitimer DS8R stimulator
- Digitimer D188 8-channel switcher
- NI-DAQ USB-6001 (DAQ)
- Raspberry Pi Pico

### Software
- Python
- PySide6
- nidaqmx
- pandas
- matplotlib

## Project Organization
The code in this application is broadly categorized into five main parts:  
    1. GUI  
    2. Train Data Manager  
    3. Stim Train Plotter  
    4. Stimulation Executor  
    5. Hardware Interfaces  

### General Data Flow
The user enters stim train parameters into the GUI which sends the info to the data manager. The manager acts as a link between the GUI, the plotter, and the executor. The plotter allows users to visualize and modify this data (ex., adding/deleting pulses), and informs the manager when these changes occur. When editing is finished, the executor pulls in the manager's updated data and utilizes the hardware interfaces to execute the user-created stim train.

## Challenges
### Hardware Challenges
In the current configuration, the D188 and DS8R have two main ways to interact with them programatically: the DAQ and the Pico. 

Ideally, there is only one device with which the application needs to communicate for simplicity/latency sake, but each device poses unique challenges:
    - The USB-6001 model DAQ only has counter input functionality, meaning its output timing is limited for HF triggering.
    - The Pico is fast enough for HF, but it lacks true digital-to-analog functionality, so it isn't suitable for setting the DS8R's amplitude.
        -Additionally, the Pico's +3.3V max output is shy of the +10V input required of the DS8R.
        
### Implementation Challenges
Despite the above Pico limitations, it does offer PWM, which can approximate an analog output. 

In light of this, a PWM output was configured for the Pico and that output was hooked up to the DAQ, which amplified the signal and wrote it to the DS8R via the DAQ's analog output pin. While this can work, the nature of the Pico's PWM output signal is far too erratic for use without additional methods to smooth out the voltage before it's read by the DAQ.
    - Possible solutions:
        1. An RC low-pass filter between the Pico and the DAQ seems to be common for smoothing out PWM voltage output.
        2. A DAC BoB for the Pico to stablize its output voltage. While most of these seem to have a +5V limitation, the DAQ can still be used as a pseudo-amplifier.
        3. Omit the DAQ entirely and use an op-amp with an external power source.

In lieu of additional circuitry, a combination of the DAQ and Pico is used here, with the Pico serving primarily as an HF stimulation trigger. The previous implementation of the Pico's firmware only has triggering capability, so new firmware was written. This new firmware lays the groundwork for allowing for stimulation control by the Pico only, pending a solution to the problem above.

#### User Input Validation
The first main challenge was the complexity of possible inputs and subsequent validation. 

Ideally, a single, intuitive interface manages all this complexity, which is both convenient for the user and can help simplify code maintenance. As such, the UI needed to be robust enough to handle the specification of both conventional and HF stimulation paradigms in addition to F-wave examination, recruitment curves, and any future experimental conditions. Ensuring the values input by the user are valid and logical poses special challenges when logic is conditional to this extent.

In response to this, the GUI allows for constant values and linearly spaced values, but also allows for the definition and reuse of custom functions for parameter generation. Custom functions afford flexibility for future experimental designs and ensure previous F-wave and RC stimulation paradigms are still possible, even on multiple channels.

#### Communication Synchronicity and Timing
The next challenge to solve was synchronous communication between components, and determining expected behavior for timing conflicts when they do occur.

Many of these challenges involve handling valid, but illogical, user-entered values. For example, how should the application respond if the user requests a 60 Hz pulse for 10ms, since 10ms is too short to complete even a single period of a 60 Hz pulse? In this case, the application adheres to the specified pulse duration in order to avoid offsetting all future pulse by *n* ms. 

Additional data synchronicity challenges are posed by the communication between the manager, plotter, and executor.

# Progress
Overall, the project is ~70% finished, not including integration into the analog streaming codebase.

The core functionality for conventioal stimulation is functional, however. Currently, it's possible to use the front end to generate a CSV of stimulation parameters, load that CSV into the executor, and execute the generated stim train using the DAQ. Though this requires manual linkage of the components, it's can attain millisecond accuracy in timing tests with durations as low as 5 ms and frequencies as high as 500 Hz.

## Current Work
The current goal is to finish the tasks for the individual components outlined below, then integrate the application into the analog streaming codebase. There aren't currently any glaring obstacles to integration, but specific features with regard to conditional stimulation based on EMG/IMU biofeedback will need to be discussed.

    1. GUI: ~66% finished.
        - All current infrastructure/signaling is finished, pending:
            - Define and conditionally display widgets for custom functions. This is the bulk of the remaining GUI work.
            - Give users the option to specify:
                - Loop stim train or quit when finished (in the case of RC, F-wave)
                - Rest amplitude (instead of returning to 0, return to *n* mA for participant tolerability)
                - The DS8R's V:mA conversion factor (if necessary)

    2. Data Manager: ~95% finished
        - May need changes as requirements change, but currently needed features are finished

    3. Stim Train Plotter: ~25% finished
        - Pan, zoom,
        - Right click to add/delete stims
        - Double left click to edit values (amplitude, frequency, duration)
        - Click-and-drag left/right to adjust duration
        - Notify manager of modifications

    4. Stimulation Executor: ~80% finished
        - DAQ stim train execution is finished (i.e., read in CSV and call DAQ commands accordingly)
        - Pico execution is mostly finished, but still needs commands for:
            - Beginning and halting execution
            - Adding/removing stored parameters
            - Live updates to parameters

    5. Hardware Interfaces: 90% finished
        - DAQ interface is finished
        - Pico firmware requires:
            - Store array of train parameters in RAM
            - Commands for:
                - Beginning and halting execution
                - Adding/removing stored parameters
                - Live updates to parameters

## Next steps,
After completion of the above, integration begins. Integrating this part of front end into the current code will be the most challening part.
The hardware interfaces don't require integration and all of the signaling to this application is internal, so it should function more or less as unit once it's dropeed in. 

After this is integrated into the analog streaming code base, Rod and I will need to get together to ensure the HF functionality works, which I suspect that will be its own mini project.

## Design Questions
- Is the goal of the plotter visualize *where* in the stim train the current stimuation is (as in Guitar Hero/sheet music), or just visualize/edit stim train?

- Is the DS8R's conversion factor expected to change (10V=1000mA)?

- How fast would parameters be expected to change? For example, when doing HF, it's not the amplitude or channel that changes rapidly necessarily (and even then, the frequency doesn't change rapidly, it just needs to send the trigger signal rapidly)?
- When two channels overlap and pulses need to be interleaved, the D188 needs to alternate back and forth rapidly, so how long should it stim on each channel before swithcing to the next? 1 ms, 1 period? If it's just a single pulse and then switch, it seems like frequency would be more or less a function of the number of active channels.


- Some of the general speed is hindered by more front end work. PRovindg more freedom to the user requires more validation and discipline to ensure data integrity and a smooth user experience. There is always the trade off between hard coding values and creating flexible applications in that hard coding values are faster and easier at the time by limit modularity and reuse. The deccsion i make are more long term focused, both in the sense of providin applications that allow for future flexibility but are also easier to maintain for other people.

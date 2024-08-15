The goal of this project is to add the ability to stimulate across multiple channels using the D188 channel switcher and the DS8R stimulator.

In the current configuration, the D188 has two main ways to interact with it programatically: the NIDAQ (DAQ) and the Raspberry Pi Pico.

The DAQ was hooked up originally, but the USB-6001 model lacks a "counter out" functionality, meaning it isn't suitable for HF triggering.

Firmware was written for the Pico, but it lacks digital-to-analog functionality, so PWM was used instead to approximate an analog output.
Since the Pico's +3.3V max output is shy of the +10V input required of the DS8R, the Pico's PWM pin was hooked up to the DAQ, which read the Pico's input
and wrote a scaled up output to its own analog pin, which was sent to the DS8R. However, without additioanal methods to smooth out the Pico's PWM output, the voltage is too erratic.

Instead, a combination will be used. The DAQ should work for convential stimulation, and the pico will continue to serve HF stimulation. 
The next challeng to solve becomes communication between the device. For example, if HF is to be used, will the Pico also control channel swithcing? If not, ensuring the code times switching is paramount.


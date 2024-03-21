### python-flying-balls-psu
<sub>
  A Python program to levitate superconducting spheres by ramping the currents of two concentric, superconducting coils connected to a PSU.


</sub>

#### Aims
<sub>

 * To ramp the currents of channels 1-4 of an Agilent 6629A DC PSU to levitate a superconducting ball bearing

 * To be able to record the currents for each ramp


</sub>

#### To Do
<sub>

   - [X] Ramp currents with manually entered parameters for I, dI and dt
   - [X] Ramp currents with default paramters for I, dI and dt
   - [X] Ramp currents to zero with a single click
   - [ ] Read current currents
   - [ ] Save currents for each ramp
   - [ ] Recognise coil quenches and automatically ramp to zero


</sub>

#### Log
<sub>

 **21-Mar-24**

 * Created GitHub repository and uploaded previous work

 * N.B. Ch1, Ch4 are connected in series to the outer coil; Ch2, Ch3 are connected in series to the inner coil

 * 'Start' button ramps to I, dI, dt values set at top

 * 'Stop' button stops the current ramp. This can also be achieved by pressing 'Start' during a ramp

 * 'Wingardium Leviosa' button ramps to default values of I, dI, dt

   * These are currently set to 1200 mA, 5.0 mA/s and 1/12 s for Ch1 and Ch4 (outer)

   * These are currently set to 1500 mA, 5.0 mA/s and 1/12 s for Ch2 and Ch3 (inner)

 * The 'Save to File' checkbox is not currently connected

 * Branch current-currents created and previous work updating currents uploaded



</sub>
# gym-timer

Gym Clock that uses a Raspberry Pi, ESP8266 and a computer monitor to replicate the functionality of [The Rogue Echo Timer](https://www.roguefitness.com/rogue-echo-gym-timer)
(for a lot less money)

# How it works

  * Raspberry Pi connected to a monitor
  * IR sensor connected to an ESP8266 for taking IR Remote Input
  * The ESP8266 Sends commands to the Pi over USB (can be changed to use a web server to allow for multiple remote inputs)
  
# Functionality
  * Clock
  * AMRP Tracking
    * Time working/Time resting, repeated a number of times
  * EMOM Style Tracking
    * EMOM Length, divided into a number of rounds
  * TABATA (Ten 
    * Work time/Rest Time, Duration

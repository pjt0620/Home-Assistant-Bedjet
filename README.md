# Home-Assistant-Bedjet
Bedjet Home Assistant Mqtt Integration

This is a reverse engineered bluetooth mqtt bridge for bedjet to connect with home assistant.
This has been tested with a raspbery pi and a bedjet v3.

Whats working:
  - Basic comunications with bedjet via bluetooth le
  - Controls
    - Modes (off, cool, heat, dry, turbo, ext heat)
    - Fan Up
    - Fan Down
    - Temp Up
    - Temp Down
    - Start Preset (m1, m2, m3)

  - Sensors
    - Mode
    - Current Temprature
    - Set Temprature
    - Time Remaining
    
  - Direct Setting
    - Temprature
    - Time Remaining
    - Fan Speed (5% increments) 
  
Todos:
  - Handle error conditions / disconnects
  - Better config example
  - Bedjet autodetection
    - Start multiple threads for multiple bedjets
  - MQTT discovery?
  - Setup instructions
  - Python package

Notes:
  - I will not be supporting setting and retreving wifi info as wifi serves no pratical use on the bedjet at this time and it is a pain to do.

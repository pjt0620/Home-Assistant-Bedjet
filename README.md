# Home-Assistant-Bedjet
Bedjet Home Assistant Mqtt Integration

This is a first attempt at a reverse engineered bluetooth mqtt bridge for bedjet (made at 2 in the morning).
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
  
Todos:
  - Handle error conditions / disconnects
  - Write code for direct temp, time and fan set points
  - Better config example
  - Setup instructions

## Program to control arduino based laser turret with rasbperry pi

At the moment, the bot only turns and usb-cable on and off on command, which in turn turns on the [laser turret](https://youtube.com/shorts/iM_XG_rG9lU). 

This is achieved with an [usb power switch module](https://thepihut.com/products/usb-power-switch-module)

To get the code running, you need to 

- Connect pins
  - EN -> any GPIO pin
  - GND -> GND
- Set up the telegram bot
  - see [this](https://www.youtube.com/watch?v=vZtm1wuA2yc) for example 
- Create secret_info.py
  - Add the usernames of who is allowed to use this
  - Add the bot token (if you didn't already)

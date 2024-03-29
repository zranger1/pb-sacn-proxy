# Retirement
This repository is now retired.  It served mostly as a demonstration, and has been superseded by the much more functional Flamecaster Art-Net-to-Pixelblaze router, found at https://github.com/zranger1/Flamecaster .

# pb-sacn-proxy
Enables sending e1.31 (sACN) data to a Pixelblaze LED controller
  
sacnproxy.py is a stand-alone script that listens for pixel data coming from an e1.31 compliant
source, converts it to packed RGB values and sends it to a Pixelblaze using pyblaze's setVariable()
command. It supports a maximum of 480 pixels per Pixelblaze.   

It was developed to provide easy integration with lightshowpi for holiday lighting 
displays, and has not yet been tested with other sACN controllers.

To use it, configure lightshowpi to use one or more strings of sACN leds, then in sacnproxy.py,
edit the line that creates the sacnProxy object (around line 168) with the IP address
of your proxy machine and the IP address of your Pixelblaze as parameters.  

Install and activate the pattern [RGB SACN Listener](https://github.com/zranger1/pb-sacn-proxy/blob/main/RGB%20SACN%20Listener.epe) on
your Pixelblaze.

Run sacnproxy.py on your proxy machine, then start the lightshowpi script.  If all is 
correctly configured, you should have blinking lights!    

## Requirements
Requires Python 3, websocket-client, sacn (available from PyPi) and pixelblaze-client (included in this repository)

## Installation
Add websocket-client and sacn to your python installation with pip or another library manager
Copy the repository files into a handy directory.  

#### TODO

 - provide a little more information on how to configure lightshowpi, even though that's
somewhat beyond the scope of this project.

## Donation
If this project saves you time and effort, please consider donating to help support further development.  Every donut or cup of coffee helps!  :-)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=YM9DKUT5V34G8)

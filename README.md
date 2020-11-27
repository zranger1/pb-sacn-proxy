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

Run sacnproxy.py on your proxy machine, then start the lightshowpi script.  If all is 
correctly configured, you should have blinking lights!    

#### TODO

 - provide a little more information on how to configure lightshowpi, even though that's
somewhat beyond the scope of this project.
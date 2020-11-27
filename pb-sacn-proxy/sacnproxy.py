"""
 sacntest.py

 Receives e1.31 packets containing pixel data from lightshowpi and sends
 them via setVars() to a Pixelblaze.
 
 Requires Python 3, websocket-client, sacn and pyblaze.py
 
 Copyright 2020 JEM (ZRanger1)

 Permission is hereby granted, free of charge, to any person obtaining a copy of this
 software and associated documentation files (the "Software"), to deal in the Software
 without restriction, including without limitation the rights to use, copy, modify, merge,
 publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
 to whom the Software is furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies or
 substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
 BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
 AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.

 Version  Date         Author Comment
 v0.0.1   11/27/2020   JEM(ZRanger1)    Created
"""

from pyblaze import *
import sacn
import time
import sys
import array

class sacnProxy:
    """
    Listens for e1.31 (sACN) data and forwards it to a Pixelblaze.
    """
    pb = None
    receiver = None
    pixelsPerUniverse = 170
    pixelCount = 0
    dataReady = False
    notifyTimer = 0
    FrameCount = 0
    delay = 0.033333  # default to 30 fps outgoing limit
    notify_ms = 3000  # throughput check every <notify_ms> milliseconds
    show_fps = False
    
    pixels = []
    
    def __init__(self, bindAddr, pixelBlazeAddr):       
        self.pixels = [0 for x in range(512)]  # max size of a dmx universe tuple

        self.pb = Pixelblaze(pixelBlazeAddr)   # create Pixelblaze object        
        result = self.pb.getHardwareConfig()   
        self.pixelCount = result['pixelCount']    

        # bind multicast receiver to specific IP address
        self.receiver = sacn.sACNreceiver(bind_address=bindAddr)     
        self.receiver.start()  # start receiver thread

        # define callback functions for the universes we're interested in
        # for this test, we arbitrarily allow 170 pixels per universe, and
        # listen to universes 1-4 for a total of 680 possible pixels.
        # Note that although the e1.31 protocol provides reliable transport,
        # due to throughput constraints, some frames may be dropped and will
        # not be sent to the Pixelblaze.  The goal is that the overall
        # visualization be reasonably smooth, accurate and timely.
       
        @self.receiver.listen_on('universe', universe=1) 
        def callback_one(packet):  # packet is type sacn.DataPacket.
            self.pack_data(packet.dmxData, 0)
            self.dataReady = True

        @self.receiver.listen_on('universe', universe=2) 
        def callback_two(packet):  
            self.pack_data(packet.dmxData, self.pixelsPerUniverse)
            self.dataReady = True        
            
        @self.receiver.listen_on('universe', universe=3) 
        def callback_three(packet):  
            self.pack_data(packet.dmxData, self.pixelsPerUniverse * 2)
            self.dataReady = True        
            
        @self.receiver.listen_on('universe', universe=4) 
        def callback_four(packet):  
            self.pack_data(packet.dmxData, self.pixelsPerUniverse * 3)
            self.dataReady = True
            
    def debugPrintFps(self):
        self.show_fps = True
                       
    def setPixelsPerUniverse(self, pix):
        self.pixelsPerUniverse =  max(1, min(pix, 170))  # clamp to 1-170 pixels
        
    def setMaxOutputFps(self, fps):
        self.delay = 1 / fps
        
    def setThroughputCheckInterval(self, ms):
        self.notify_ms = max(500,ms)  # min interval is 1/2 second, default should be about 3 sec
    
    def time_millis(self):
        return int(round(time.time() * 1000))
    
    def calc_frame_stats(self):
        self.FrameCount += 1
        
        t = self.time_millis() - self.notifyTimer
        if (t >= self.notify_ms):
            t = 1000 * self.FrameCount / self.notify_ms
            if (self.show_fps):
                print("Incoming fps: %d"%t)
            self.FrameCount = 0                                      
          
            self.notifyTimer = self.time_millis()                  
        pass
    
    def pack_data(self, dmxPixels,startPixel):
        index = 0
        pixNum = startPixel
        max = startPixel + self.pixelsPerUniverse
        while(pixNum < max):
            self.pixels[pixNum] = ((dmxPixels[index] << 16) | (dmxPixels[index + 1] << 8) | dmxPixels[index + 2]) / 256.0
            if (self.pixels[pixNum] > 32767) :
                self.pixels[pixNum] = self.pixels[pixNum] - 65536
            pixNum += 1
            index += 3             

    def send_frame(self, pb):
        self.pb.setVariable("pixels", self.pixels[0:self.pixelCount])
        
    def run(self):
                    
        # start listening for multicasts -- joining a single universe seems to get you 
        # multicast packets for all universes, at least from lightshowpi.
        # TODO - verify that this works with other sacn providers
        self.receiver.join_multicast(1)
        self.notifyTimer = self.time_millis() 
        
        # loop forever, listening for sacn packets and forwarding the pixel data
        # to Pixelblaze
        while True:    
            time.sleep(self.delay) # limit outgoing framerate
            
            if (self.dataReady == True):
                self.send_frame(self.pb)               
                self.calc_frame_stats()                                      
                self.dataReady = False
                
    def stop(self):
        self.receiver.stop()
        self.pb.close()
        
    

if __name__ == "__main__":

    mirror = sacnProxy("192.168.1.20","192.168.1.15")  # arguments: ip address of proxy machine, ip address of pixelblaze
    mirror.setPixelsPerUniverse(170)
    mirror.setMaxOutputFps(30)
    mirror.setThroughputCheckInterval(3000)
    mirror.debugPrintFps()
    
    try:    
        mirror.run()   # run forever (until stopped by ctrl-c or exception)
       
    except KeyboardInterrupt:
        mirror.stop()
        print("sacnProxy halted by keyboard interrupt")
    
    except Exception as blarf:
        mirror.stop()
        template = "sacnProxy halted by unexpected exception. Type: {0},  Args:\n{1!r}"
        message = template.format(type(blarf).__name__, blarf.args)
        print(message)         
        
        

    

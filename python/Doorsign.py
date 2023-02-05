# *****************************************************************************
# * | File        :	  Pico_ePaper-7.5.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-05-27
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

class EPD_7in5(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.spi = SPI(1)
        self.spi.init(baudrate=48_000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def WaitUntilIdle(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 0):    # Wait until the busy_pin goes LOW
            self.send_command(0x71)
            self.delay_ms(20)
        self.delay_ms(20) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x12) # DISPLAY REFRESH
        self.delay_ms(100)      #!!!The delay here is necessary, 200uS at least!!!
        self.WaitUntilIdle()
        
    def init(self):
        # EPD hardware init start     
        self.reset()
        
        self.send_command(0x01)  # POWER SETTING
        self.send_data(0x07)
        self.send_data(0x07)     # VGH=20V,VGL=-20V
        self.send_data(0x3f)     # VDH=15V
        self.send_data(0x3f)     # VDL=-15V
        
        self.send_command(0x04)  # POWER ON
        self.delay_ms(100)
        self.WaitUntilIdle()

        self.send_command(0X00)   # PANNEL SETTING
        self.send_data(0x1F)      # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x61)     # tres
        self.send_data(0x03)     # source 800
        self.send_data(0x20)
        self.send_data(0x01)     # gate 480
        self.send_data(0xE0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)     # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x10)
        self.send_data(0x00)

        self.send_command(0X60)     # TCON SETTING
        self.send_data(0x22)

        self.send_command(0x65)     # Resolution setting
        self.send_data(0x00)
        self.send_data(0x00)     # 800*480
        self.send_data(0x00)
        self.send_data(0x00)
        
        return 0;

    def Clear(self):
        before = utime.ticks_ms()

        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xff)
                
        self.send_command(0x13) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)
        after = utime.ticks_ms()
        print("Clear time: " + str(utime.ticks_diff(after, before)))

                
        self.TurnOnDisplay()
        
    def ClearBlack(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)
                
        self.send_command(0x13) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xff)
                
        self.TurnOnDisplay()
        
    def display(self,blackimage):
        before = utime.ticks_ms()
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(blackimage[i + j * wide])
                
        self.send_command(0x13) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(blackimage[i + j * wide])
        after = utime.ticks_ms()
        print("Transfer time: " + str(utime.ticks_diff(after, before)))
        self.TurnOnDisplay()


    def sleep(self):
        self.send_command(0x02) # power off
        self.WaitUntilIdle()
        self.send_command(0x07) # deep sleep
        self.send_data(0xa5)

def show_image(epd, path):
    print("Showing: " + path)
    epd.init()
    with open(path, "rb") as file:
        binary = file.read()
        epd.display(binary)
    epd.sleep()
    print("Done showing image")
        
def loop(epd, p0, p1, p2):
    while True:
        if p0.value():
            show_image(epd, "PleaseKnock.raw")
        elif p1.value():
            show_image(epd, "BRB.raw")
        elif p2.value():
            epd.init()
            epd.Clear()
            epd.sleep()
            #show_image(epd, "Lecturing.raw")

if __name__=='__main__':
    epd = EPD_7in5()
    p0 = Pin(0, Pin.IN, Pin.PULL_DOWN)
    p1 = Pin(1, Pin.IN, Pin.PULL_DOWN)
    p2 = Pin(2, Pin.IN, Pin.PULL_DOWN)
    show_image(epd, "PleaseKnock.raw")

    loop(epd, p0, p1, p2)

/*****************************************************************************
* | File      	:   EPD_7in5_V2_test.c
* | Author      :   Waveshare team
* | Function    :   7.5inch e-paper test demo
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2019-06-13
* | Info        :
#
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
******************************************************************************/
#include "EPD_Test.h"
#include "EPD_7in5_V2.h"
#include "Images.h"
#include "pico/stdlib.h"
#include "pico/sleep.h"
#include "hardware/gpio.h"

#include "hardware/clocks.h"
#include "hardware/rosc.h"
#include "hardware/structs/scb.h"

const uint INTERRUPT_PIN = 4;
const uint ONBOARD_LED = 25;
const uint BLINK_DELAY = 200;

void blink_onboard_led(int times) {
    for (int i = 0; i < times; i++) {
        gpio_put(ONBOARD_LED, 1);
        sleep_ms(BLINK_DELAY);
        gpio_put(ONBOARD_LED, 0);
        sleep_ms(BLINK_DELAY);
    }
}

int Draw(const unsigned char* image) {
    // Device setup
    if(DEV_Module_Init()!=0){
        return -1;
    }
    EPD_7IN5_V2_Init();
    EPD_7IN5_V2_Clear();
    DEV_Delay_ms(500);
    // Create framebuffer
    UBYTE *BlackImage;
    UWORD Imagesize = ((EPD_7IN5_V2_WIDTH % 8 == 0)? (EPD_7IN5_V2_WIDTH / 8 ): (EPD_7IN5_V2_WIDTH / 8 + 1)) * EPD_7IN5_V2_HEIGHT;
    // Handle allocation failure
    if((BlackImage = (UBYTE *)malloc(Imagesize)) == NULL) {
        return -1;
    }
    // Write image to framebuffer
    Paint_NewImage(BlackImage, EPD_7IN5_V2_WIDTH, EPD_7IN5_V2_HEIGHT, 0, WHITE);
    Paint_SelectImage(BlackImage);
    Paint_Clear(WHITE);
    Paint_DrawBitMap(image);
    // Display image
    EPD_7IN5_V2_Display(BlackImage);

    // Sleep and cleanup
    DEV_Delay_ms(500); // used to be 2000
    EPD_7IN5_V2_Sleep();
    free(BlackImage);
    BlackImage = NULL;
    DEV_Delay_ms(2000);//important, at least 2s
    // close 5V
    DEV_Module_Exit();
}

void setup_input_pin(int pin) {
    gpio_init(pin);
    gpio_set_dir(pin, GPIO_IN);
    gpio_pull_down(pin);
}

void setup_pins() {
    // stdio_init_all();

    // Setup pins 0--3 as input pins
    for (int i = 0; i < 3; i++) {
        setup_input_pin(i);
    }

    // Setup interrupt pin
    setup_input_pin(INTERRUPT_PIN);

    gpio_init(ONBOARD_LED);
    gpio_set_dir(ONBOARD_LED, GPIO_OUT);

}

void rosc_enable(void)
{
    uint32_t tmp = rosc_hw->ctrl;
    tmp &= (~ROSC_CTRL_ENABLE_BITS);
    tmp |= (ROSC_CTRL_ENABLE_VALUE_ENABLE << ROSC_CTRL_ENABLE_LSB);
    rosc_write(&rosc_hw->ctrl, tmp);
    // Wait for stable
    while ((rosc_hw->status & ROSC_STATUS_STABLE_BITS) != ROSC_STATUS_STABLE_BITS);
}

void recover_from_sleep() {
    //rosc_enable();
    clocks_init();
    return;
}


void setup_interrupt() {
    // Go to sleep until we see high edge on GPIO 4
    //
    // blink_onboard_led(3);
    sleep_run_from_rosc();
    setup_pins();
    sleep_goto_dormant_until_edge_high(INTERRUPT_PIN);
    recover_from_sleep();
    blink_onboard_led(3);

    if (gpio_get(0)) {
        Draw(PleaseKnock);
    } else if (gpio_get(1)) {
        Draw(BRB);
    } else if (gpio_get(2)) {
        Draw(OutOfDept);
    } else if (gpio_get(3)) {
        Draw(Lecturing);
    }
}

void read_inputs() {
    if (gpio_get(0)) {
        Draw(PleaseKnock);
    } else if (gpio_get(1)) {
        Draw(BRB);
    } else if (gpio_get(2)) {
        Draw(OutOfDept);
    } else if (gpio_get(3)) {
        Draw(Lecturing);
    }
}

int Doorsign(void)
{
    // Setup IO pins
    setup_pins();

    Draw(PleaseKnock);

    // Loop (eventually will replace with interrupt)
    while (true) {
        setup_interrupt();
        //read_inputs();
        //sleep_ms(500);
    }
    /*
    Draw(BRB);
    Draw(OutOfDept);
    */
    return 0;
}


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
        printf("Failed to apply for black memory...\r\n");
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
    DEV_Delay_ms(2000);
    EPD_7IN5_V2_Sleep();
    free(BlackImage);
    BlackImage = NULL;
    DEV_Delay_ms(2000);//important, at least 2s
    // close 5V
    DEV_Module_Exit();
}

int Doorsign(void)
{
    Draw(PleaseKnock);
    Draw(BRB);
    Draw(OutOfDept);
    return 0;
}


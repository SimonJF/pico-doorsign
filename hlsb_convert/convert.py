#!/usr/bin/env python3
# Converts B&W BMPs to MONO_HLSB format.
# Based on: https://github.com/phoreglad/img_to_mono_hlsb

from PIL import Image
import sys
from pathlib import Path

def load(path):
# Load image
    im = Image.open(path)

    width, height = im.size
# If image width not divisible by 8, correct it
    adj_width = width + width % 8

    if adj_width == width:
        print("Image size: {}x{}".format(adj_width, height))
    else:
        print("Adjusted image width")
        print("Adjusted image size: {}x{}".format(adj_width, height))
        print("Original image size: {}x{}".format(width, height))
    return (im, height, width, adj_width)

def convert(img, height, width, adj_width):
    # Create buffer for pixel data
    buf = bytearray(height*adj_width//8)
    i = 0
    for byte in range(len(buf)):
        for bit in range(7, -1, -1):
            if i % adj_width < width:
                px =  img.getpixel((i % adj_width, i // adj_width))
                if px < 128:
                    buf[byte] |= 1 << bit
            i += 1
    return buf

def save(buf, path):
    # Save data to file
    print("Saving data to file: {}".format(path))
    with open(path, "wb") as f:
        f.write(buf)
        #f.write("name = '{}'\nwidth = {}\nheight = {}\nformat = '{}'\nimg = {}"
        #        .format(im_name, adj_width, height, "MONO_HLSB", buf))

def get_all_bmps():
    p = Path(".")
    return list(p.glob('**/*.bmp'))



def main():
    inputs = []
    if len(sys.argv) < 2:
        inputs = get_all_bmps()
    else:
        inputs = [Path(sys.argv[1])]

    for path in inputs:
        print("Path: " + str(path))
        output = str(Path(path.stem).with_suffix(".raw"))
        print("Output: " + str(output))
        (img, height, width, adj_width) = load(path)
        out_buf = convert(img, height, width, adj_width)
        save(out_buf, output)
        print("Done!")


if __name__ == "__main__":
    main()

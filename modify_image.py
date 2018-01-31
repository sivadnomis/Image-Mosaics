from PIL import Image, ImageOps, ImageFilter, ImageChops
import os
import mosaic
import sys
import commands

image = Image.open(sys.argv[1])
image2 = Image.open(sys.argv[2])
blob = ImageChops.screen(image, image2)
blob.show()
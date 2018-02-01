from PIL import Image, ImageOps, ImageFilter, ImageChops, ImageEnhance
import os
import mosaic
import sys
import commands

image = Image.open(sys.argv[1])
image2 = Image.open(sys.argv[2])

red = Image.new('RGB',image2.size,(255,0,0))
mask = Image.new('RGBA',image2.size,(0,0,0,180))
pic = Image.composite(image2,red,mask).convert('RGB')
pic.show()

#blob = ImageChops.screen(image, image2)
#blob.show()
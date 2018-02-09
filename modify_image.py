from PIL import Image, ImageOps, ImageFilter, ImageChops, ImageEnhance
import os
import mosaic
import sys
import commands

image = Image.open(sys.argv[1])
#image2 = Image.open(sys.argv[2])

red = Image.new('RGB',image.size,(255,0,0))
mask = Image.new('RGBA',image.size,(0,0,0,95))
pic = Image.composite(image,red,mask).convert('RGB')
#pic.show()

pic.save('/home/mbax4sd2/3rd Year Project/output/masktest.jpg') 

#blob = ImageChops.screen(image, image2)
#blob.show()
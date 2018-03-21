from PIL import Image, ImageOps, ImageFilter, ImageChops, ImageEnhance
import os
import mosaic
import sys
import commands

def variance(data):
    # Use the Computational Formula for Variance.
    n = len(data)
    ss = sum(x**2 for x in data) - (sum(data)**2)/n
    return ss/(n-1)

image = Image.open(sys.argv[1])
#image2 = Image.open(sys.argv[2])
var = variance(image)
print var

#red = Image.new('RGB',image.size,(255,0,0))
#mask = Image.new('RGBA',image.size,(0,0,0,95))
#pic = Image.composite(image,red,mask).convert('RGB')
#pic.show()

#pic.save('/home/mbax4sd2/3rd Year Project/output/masktest.jpg') 

#blob = ImageChops.screen(image, image2)
#blob.show()
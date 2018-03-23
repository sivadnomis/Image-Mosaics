from PIL import Image, ImageOps
import os
import mosaic
import sys
import commands

mosaic_image = sys.argv[1]
source_image = sys.argv[2]

source_size = 500, 500
image = Image.open(source_image)
image.thumbnail(source_size, Image.ANTIALIAS)

image_name = '%ssmall.jpg' % os.path.splitext(source_image)[0]
image.save('/home/mbax4sd2/3rd Year Project/' + image_name) 

result = commands.getstatusoutput('compare -metric SSIM ' + mosaic_image + ' ' + image_name + ' output/diff.jpg')
print result[1]

#command for generating a SSIM diff on 2 images.
#compare -metric PSNR mesmall.jpg output/me2mosaic.jpg output/diff.jpg
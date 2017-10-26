from PIL import Image
import os
import mosaic
import sys
import commands

##################
#join 4 images together
##################
def four_image_mosaic(tile_size):
  images = map(Image.open, ['bronze.jpg', 'hut.jpg'])
  images.append(Image.open("frog.jpg"))
  images.append(Image.open("raven.jpg"))

  for i in images:
    i.thumbnail(tile_size, Image.ANTIALIAS)
  widths, heights = zip(*(i.size for i in images))

  total_width = sum(widths)/2
  total_height = sum(heights)/2
  #max_height = max(heights)

  mosaic = Image.new('RGB', (total_width, total_height))

  x_offset = 0
  y_offset = 0
  tile_index = 0
  for im in images:
    mosaic.paste(im, (x_offset,y_offset))
    if tile_index > (len(images)/2) - 2:
      tile_index = 0
      x_offset = 0
      y_offset += heights[0]
    else:
      x_offset += widths[0]
      tile_index += 1

  #mosaic.save('test.jpg')
  mosaic.show()

#four_image_mosaic(sys.argv[1])


mosaic_image = sys.argv[1]
source_image = sys.argv[2]

source_size = 500, 500
image = Image.open(source_image)
image.thumbnail(source_size, Image.ANTIALIAS)

image_name = '%ssmall.jpg' % os.path.splitext(source_image)[0]
print image_name
image.save('/home/mbax4sd2/3rd Year Project/' + image_name) 

result = commands.getstatusoutput('compare -metric SSIM ' + mosaic_image + ' ' + image_name + ' output/diff.jpg')
print result[1]

#command for generating a diff on 2 images. good enough for difference testing?
#compare -metric PSNR mesmall.jpg output/me2mosaic.jpg output/diff.jpg
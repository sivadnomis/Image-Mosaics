from PIL import Image, ImageOps
import os

##################
#open source image
##################
TargetImage = Image.open('monkey.jpg')

thumbnail_size = 250, 250
TargetImage = ImageOps.fit(TargetImage, thumbnail_size, Image.ANTIALIAS)
#TargetImage.thumbnail(thumbnail_size, Image.ANTIALIAS)
#TargetImage.show()

##################
#open tile images in library
##################
os.chdir(r'library')
for f in os.listdir(os.getcwd()):#os.listdir('library'):
    print f
    tile = Image.open(f)
    tile.thumbnail(thumbnail_size, Image.ANTIALIAS)
    #tile.show()

##################
#join 4 images together
##################
images = map(Image.open, ['bronze.jpg', 'hut.jpg'])
images.append(Image.open("bronze.jpg"))
images.append(Image.open("hut.jpg"))

for i in images:
  i.thumbnail(thumbnail_size, Image.ANTIALIAS)
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
  print "pasted image"

  if tile_index > 0:
    tile_index = 0
    x_offset = 0
    y_offset += heights[0]
    print "x,y offset is: ", x_offset, y_offset
  else:
    x_offset += widths[0]
    tile_index += 1
    print "x,y offset is: ", x_offset, y_offset
  
  print tile_index

mosaic.save('test.jpg')
mosaic.show()

##################
#calculate average RGB of source image
##################
width, height = TargetImage.size
print width, "X", height

PixelValues = list(TargetImage.getdata())
RValues = [x[0] for x in PixelValues]
GValues = [x[1] for x in PixelValues]
BValues = [x[2] for x in PixelValues]

AverageRGBValue = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )
print AverageRGBValue

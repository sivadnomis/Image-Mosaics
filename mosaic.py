from PIL import Image, ImageOps
import os

##################
#open source image
##################
TargetImage = Image.open('monkey.jpg')

source_size = 500, 500
#TargetImage = ImageOps.fit(TargetImage, thumbnail_size, Image.ANTIALIAS)
TargetImage.thumbnail(source_size, Image.ANTIALIAS)
#TargetImage.show()

##################
#open tile images in library
##################
tile_size = 50, 50
os.chdir(r'library')
for f in os.listdir(os.getcwd()):#os.listdir('library'):
    #print f
    tile = Image.open(f)
    tile.thumbnail(tile_size, Image.ANTIALIAS)
    #tile.show()

##################
#join 4 images together
##################
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
  #print "pasted image"
  #print len(images)/2
  if tile_index > (len(images)/2) - 2:
    tile_index = 0
    x_offset = 0
    y_offset += heights[0]
    #print "x,y offset is: ", x_offset, y_offset
  else:
    x_offset += widths[0]
    tile_index += 1
    #print "x,y offset is: ", x_offset, y_offset
  
  #print tile_index

#mosaic.save('test.jpg')
#mosaic.show()

##################
#calculate average RGB of source image
##################

def CalcAverageRGB( image ):
  width, height = image.size
  #print width, "X", height

  PixelValues = list(image.getdata())
  RValues = [x[0] for x in PixelValues]
  GValues = [x[1] for x in PixelValues]
  BValues = [x[2] for x in PixelValues]

  AverageRGBValue = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )
  #print AverageRGBValue
  return AverageRGBValue

##################
#divide source image into blocks for replacement
##################

def DivideImageIntoBlocks( image, block_x, block_y, output_dict ):
  width, height = image.size

  for i in range(0, width, block_x):
    for j in range(0, height, block_y):
      #print i, j
      cropped_image = image.crop((i, j, i+block_x, j+block_y))
      output_dict[cropped_image] = CalcAverageRGB( cropped_image )
      #cropped_image.show()
      #CalcAverageRGB(cropped_image)


CalcAverageRGB(TargetImage)

block_dict = {}
DivideImageIntoBlocks(TargetImage, 50, 50, block_dict)
print block_dict
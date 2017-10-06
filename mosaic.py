from PIL import Image, ImageOps
import os
import math

TargetImage = Image.open('monkey.jpg')
tile_size = 50, 50

##################
#open source image
##################
def ResizeSourceImage( image ):
  
  source_size = 500, 500
  #TargetImage = ImageOps.fit(TargetImage, thumbnail_size, Image.ANTIALIAS)
  image.thumbnail(source_size, Image.ANTIALIAS)
  #image.show()

##################
#open tile images in library
##################
def ResizeLibraryImages(): 
  images = []
  os.chdir(r'library')
  for f in os.listdir(os.getcwd()):#os.listdir('library'):
      #print f
      tile = Image.open(f)
      tile.thumbnail(tile_size, Image.ANTIALIAS)
      images.append(tile)
      #tile.show()
  return images

##################
#join 4 images together
##################
def FourImageMosaic():
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
      cropped_image = image.crop((i, j, i+block_x, j+block_y))
      output_dict[CalcAverageRGB( cropped_image )] = cropped_image
      #cropped_image.show()

##################
#main method
##################

ResizeSourceImage(TargetImage)
tiles = {}
tiles = ResizeLibraryImages()
FourImageMosaic()

#TargetImageRGBAverage = CalcAverageRGB(TargetImage)
#print "Source average RGB: ", TargetImageRGBAverage

TileRGBAverages = {}
for t in tiles:
  TileRGBAverages[CalcAverageRGB(t)] = t
#print TileRGBAverages

blockRGB_dict = {}
DivideImageIntoBlocks(TargetImage, 50, 50, blockRGB_dict)
#print blockRGB_dict

#print "tilergbaverages keys: ", TileRGBAverages.keys()
#print "tilergbaverages values: ", TileRGBAverages.values()
#print "blockRGB_dict keys: ", blockRGB_dict.keys()

def distance( x , y ):
  return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

#finds the closest tile colour to the first block of the source image
first_blocks_tile = min(TileRGBAverages.keys(), key=lambda x:distance(x, blockRGB_dict.keys()[0]))
print first_blocks_tile

#gives us the tile that best matches the first block in the source image
print TileRGBAverages.get(first_blocks_tile) 
#mos_test = Image.open(TileRGBAverages.get(first_blocks_tile))
#mos_test.show()
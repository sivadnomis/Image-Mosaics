from PIL import Image, ImageOps
import os
import math

##################
#open source image
##################
def ResizeSourceImage( image ):
  
  source_size = 500, 500
  #TargetImage = ImageOps.fit(TargetImage, thumbnail_size, Image.ANTIALIAS)
  image.thumbnail(source_size, Image.ANTIALIAS)
  print image.size
  image.show()
  return image

##################
#open tile images in library
##################
def ResizeLibraryImages(tile_size): 
  images = []
  os.chdir(r'library')
  for f in os.listdir(os.getcwd()):#os.listdir('library'):
      tile = Image.open(f)
      tile.thumbnail(tile_size, Image.ANTIALIAS)
      images.append(tile)
  return images

##################
#join 4 images together
##################
def FourImageMosaic(tile_size):
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

##################
#calculate average RGB of source image
##################
def CalcAverageRGB( image ):
  width, height = image.size

  PixelValues = list(image.getdata())
  RValues = [x[0] for x in PixelValues]
  GValues = [x[1] for x in PixelValues]
  BValues = [x[2] for x in PixelValues]

  AverageRGBValue = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )
  return AverageRGBValue

##################
#divide source image into blocks for replacement
##################
def DivideImageIntoBlocks( image, tile_size, output_dict ):
  width, height = image.size
  #print "width: ", width
  #print "height", height

  coordinate = 0;
  for i in range(0, width, tile_size[0]):
    for j in range(0, height, tile_size[1]):
      cropped_image = image.crop((i, j, i+tile_size[0], j+tile_size[1]))
      output_dict[coordinate] = CalcAverageRGB( cropped_image )
      coordinate += 1

  return ((i,j))

def distance( x , y ):
  return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

##################
#main method - construct mosaic from tiles in library
##################
def createMosaic(source_image, input_tile_size):
  TargetImage = Image.open(source_image)
  tile_size = input_tile_size, input_tile_size
  print "tile size is : ", tile_size

  TargetImage = ResizeSourceImage(TargetImage)
  tiles = {}
  tiles = ResizeLibraryImages(tile_size)
  #FourImageMosaic(tile_size)

  #Key = RGB, Value = Image
  TileRGBAverages = {}
  for t in tiles:
    TileRGBAverages[CalcAverageRGB(t)] = t

  #Key = coordinate, Value = rgb
  blockRGB_dict = {}
  CroppedImageXY = DivideImageIntoBlocks(TargetImage, tile_size, blockRGB_dict)

  #print "tilergbaverages keys: ", TileRGBAverages.keys()
  #print "tilergbaverages values: ", TileRGBAverages.values()
  #print "blockRGB_dict keys: ", blockRGB_dict.keys()
  #print "blockRGB_dict values: ", blockRGB_dict.values()

  #finds the closest tile colour to the first block of the source image
  first_blocks_tile = min(TileRGBAverages.keys(), key=lambda x:distance(x, blockRGB_dict.values()[0]))
  #print (first_blocks_tile)

  #gives us the tile that best matches the first block in the source image

  widths, heights = zip(*(i.size for i in TileRGBAverages.values()))

  #print TargetImage.size
  mosaic = Image.new('RGB', (TargetImage.size[0], TargetImage.size[1]))

  x_offset = 0
  y_offset = 0

  for i in range(0, len(blockRGB_dict.keys()), 1):
    #find closest colour tile in library to this specific block
    tile_to_replace_block = min(TileRGBAverages.keys(), key=lambda x:distance(x, blockRGB_dict.values()[i]))
    mosaic.paste(TileRGBAverages.get(tile_to_replace_block), (x_offset,y_offset))

    #sets the point to place the next tile
    if y_offset < CroppedImageXY[1]:
      y_offset += tile_size[1]#heights[0]
    else:
      y_offset = 0
      x_offset += tile_size[0]#widths[0]

  #mosaic.save('test.jpg')
  mosaic.show()
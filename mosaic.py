from PIL import Image, ImageOps
import os
import math

##################
#open source image
##################
def resize_source_image( image ):  
  #default dimensions to resize source image to
  source_size = 500, 500
  image.thumbnail(source_size, Image.ANTIALIAS)
  image.show()
  return image

##################
#open tile images in library
##################
def resize_library_images(tile_size): 
  images = []
  os.chdir(r'library')
  for f in os.listdir(os.getcwd()):
      tile = Image.open(f)
      tile = ImageOps.fit(tile, tile_size, Image.ANTIALIAS)
      #tile.thumbnail(tile_size, Image.ANTIALIAS)
      images.append(tile)
  return images

##################
#calculate average RGB of source image
##################
def calc_average_rgb( image ):
  width, height = image.size

  PixelValues = list(image.getdata())
  RValues = [x[0] for x in PixelValues]
  GValues = [x[1] for x in PixelValues]
  BValues = [x[2] for x in PixelValues]

  average_rgb_value = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )
  return average_rgb_value

##################
#divide source image into blocks for replacement
##################
def divide_image_into_blocks( image, tile_size, output_dict ):
  width, height = image.size

  coordinate = 0;
  for i in range(0, width, tile_size[0]):
    for j in range(0, height, tile_size[1]):
      cropped_image = image.crop((i, j, i+tile_size[0], j+tile_size[1]))
      output_dict[coordinate] = calc_average_rgb( cropped_image )
      coordinate += 1

  return ((i,j))

##################
#get euclidean distance between 2 RGB values
##################
def distance( x , y ):
  dist = math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)
  #if dist > 200:
    #print dist
  return dist

##################
#main method - construct mosaic from tiles in library
##################
def create_mosaic(source_image, input_tile_size, outlier_flagging):
  target_image = Image.open(source_image)
  tile_size = input_tile_size, input_tile_size

  target_image = resize_source_image(target_image)
  tiles = {}
  tiles = resize_library_images(tile_size)

  #Key = RGB, Value = Image
  tile_rgb_averages = {}
  for t in tiles:
    tile_rgb_averages[calc_average_rgb(t)] = t

  #Key = Coordinate in Source, Value = RGB
  block_rgb_dict = {}
  cropped_image_xy = divide_image_into_blocks(target_image, tile_size, block_rgb_dict)

  #gives us the tile that best matches the first block in the source image
  widths, heights = zip(*(i.size for i in tile_rgb_averages.values()))
  #create base mosaic image of default dimensions
  mosaic = Image.new('RGB', (target_image.size[0], target_image.size[1]), color=(255, 0, 255))

  x_offset = 0
  y_offset = 0
  num_tiles_placed = 0
  progress_percentage = 0

  for i in range(0, len(block_rgb_dict.keys()), 1):    
    #find closest colour tile in library to this specific block
    tile_to_replace_block = min(tile_rgb_averages.keys(), key=lambda x:distance(x, block_rgb_dict.values()[i]))

    #flag up when there isn't a close tile match, indicating we need a better library image
    #50 is a magic number, how do we determine where that comes from?
    if outlier_flagging & (distance(tile_to_replace_block, block_rgb_dict.values()[i]) > 50):
      print 'Distance between block: ', block_rgb_dict.keys()[i], 'and its tile is greater than 50'
    else:
      #paste tile into place in output mosaic image
      mosaic.paste(tile_rgb_averages.get(tile_to_replace_block), (x_offset,y_offset))
      
    #sets the point to place the next tile
    if y_offset < cropped_image_xy[1]:
      y_offset += tile_size[1]
    else:
      y_offset = 0
      x_offset += tile_size[0]

    num_tiles_placed += 1
    progress_percentage = num_tiles_placed/float(len(block_rgb_dict.keys())) * 100
    if progress_percentage % 5 == 0:
      print "Progress: ", progress_percentage, "%"

  os.path.splitext(source_image)[0]
  mosaic.save('/home/mbax4sd2/3rd Year Project/output/%s%smosaic.jpg' % (os.path.splitext(source_image)[0], input_tile_size)) 
  mosaic.show()
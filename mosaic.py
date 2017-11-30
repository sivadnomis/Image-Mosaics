from PIL import Image, ImageOps
from random import randint
import os
import math
import imagehash, sqlite3, time

##################
#open source image
##################
def resize_source_image( image ):  
  #default dimensions to resize source image to
  source_size = 500,500
  image.thumbnail(source_size, Image.ANTIALIAS)
  #image.show()
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
      images.append(tile)
  return images

##################
#calculate average RGB of image
##################
def calc_average_rgb(image, is_block):
  if not is_block:
    image = ImageOps.fit(image, (50,50), Image.ANTIALIAS)

  PixelValues = list(image.getdata())

  RValues = [x[0] for x in PixelValues]
  GValues = [x[1] for x in PixelValues]
  BValues = [x[2] for x in PixelValues]

  average_rgb_value = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )
  return average_rgb_value

##################
#calculate hash of image
##################
def calc_image_hash(image):
  hash1 = imagehash.whash(image)
  return hash1

##################
#divide source image into blocks for replacement
##################
def divide_image_into_blocks(image, tile_size, output_rgb_dict, output_hash_dict):
  width, height = image.size

  coordinate = 0;
  for i in range(0, width, tile_size[0]):
    for j in range(0, height, tile_size[1]):
      cropped_image = image.crop((i, j, i+tile_size[0], j+tile_size[1]))
      output_rgb_dict[coordinate] = calc_average_rgb(cropped_image, True)
      output_hash_dict[coordinate] = calc_image_hash(cropped_image)
      coordinate += 1

  return ((i,j))

##################
#get euclidean distance between 2 RGB values
##################
def distance( x , y ):
  dist = math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2 + (x[2] - y[2])**2)
  return dist

##################
#get euclidean distance between 2 RGB values
##################
def hash_diff( x , y ):
  diff = x - y
  return diff

##################
#returns closest tile to block
##################
def closest_tile(tile_rgb_averages, block_rgb_average, vary_tiles):
  sorted_rgb_values = sorted(tile_rgb_averages.keys(), key=lambda x:distance(x, block_rgb_average))

  if vary_tiles:
    return sorted_rgb_values[randint(0, 1)]
  else:
    return sorted_rgb_values[:2] #experiment with 3 closest rgb matches
  
##################
#main method - construct mosaic from tiles in library
##################
def create_mosaic(source_image, input_tile_size, outlier_flagging, vary_tiles):
  start = time.time()

  target_image = Image.open(source_image)
  tile_size = input_tile_size, input_tile_size
  target_image = resize_source_image(target_image)

  sqlite_file = 'image_library'

  db = sqlite3.connect(sqlite_file)
  cursor = db.cursor() 

  cursor.execute("SELECT * FROM tiles")
  db_tiles = cursor.fetchall()

  db.commit()
  db.close()

  #Key = hash, Value = Image
  tile_hashes = {}

  #Key = RGB, Value = Image
  tile_rgb_averages = {} 

  #put tile images from databse into our rgb/image dictionary
  print 'Gathering image tiles from library...'
  for i in range(0, len(db_tiles), 1):
    t = Image.open('library/'+(db_tiles[i])[0])

    if ((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3]) in tile_rgb_averages:
      print 'WARNING: 2 tiles with same RGB average: ', tile_rgb_averages[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])], '+', t
      tile_rgb_averages[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])].show()
      t.show()

    tile_rgb_averages[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])] = t

  #Key = Coordinate in Source, Value = RGB
  block_rgb_dict = {}
  #Key = Coordinate in Source, Value = hash
  block_hash_dict = {}

  #divide source image into blocks
  cropped_image_xy = divide_image_into_blocks(target_image, tile_size, block_rgb_dict, block_hash_dict)

  #create base mosaic image of default dimensions
  mosaic = Image.new('RGB', (target_image.size[0], target_image.size[1]), color=(255, 0, 255))

  x_offset = 0
  y_offset = 0
  num_tiles_placed = 0
  progress_percentage = 0
  
  db_tiles_rgb_values = []

  print 'Creating mosaic...'
  for i in range(0, len(block_rgb_dict.keys()), 1):
    #find closest colour tiles in library to this specific block
    closest_rgb_matches = closest_tile(tile_rgb_averages, block_rgb_dict.values()[i], vary_tiles)

    #perform wavelet analysis on the matches to pick the best
    closest_hashes = {}
    for rgb in closest_rgb_matches:
      closest_hashes[calc_image_hash(tile_rgb_averages[rgb])] = rgb
    hash_diffs = {}
    for h in closest_hashes.keys():
      hash_diffs[h - block_hash_dict.values()[i]] = h

    final_hash = hash_diffs[min(hash_diffs)]
    final_rgb = closest_hashes[final_hash]

    #flag up when there isn't a close tile match, indicating we need a better library image
    #50 is a magic number, how do we determine where that comes from?
    if outlier_flagging & (distance(final_rgb, block_rgb_dict.values()[i]) > 50):
      print 'Distance between block: ', block_rgb_dict.keys()[i], 'and its tile is greater than 50'
    else:
      #resize and paste tile into place in output mosaic image
      if tile_rgb_averages[final_rgb].size != tile_size:
        tile_rgb_averages[final_rgb] = ImageOps.fit(tile_rgb_averages.get(final_rgb), tile_size, Image.ANTIALIAS)
      
      mosaic.paste(tile_rgb_averages[final_rgb], (x_offset,y_offset))

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
  mosaic.save('/home/mbax4sd2/3rd Year Project/output/%s%smosaic.jpg' % (os.path.splitext(source_image)[0][14:], input_tile_size)) 
  #mosaic.show()

  end = time.time()
  print 'Time elapsed: ', end - start
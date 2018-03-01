from PIL import Image, ImageOps, ImageFilter, ImageChops
from random import randint
import os
import math
import imagehash, sqlite3, time

class Tree(object):
    def __init__(self):
        self.topleft = None
        self.bottomleft = None
        self.topright = None        
        self.bottomright = None
        self.data = None
        self.rgb_avg = None
        self.ID = 0
        self.coords = 0,0

variance_threshold = 600
num_blocks = 0

##################
#open source image
##################
def resize_source_image( image ):  
  #default dimensions to resize source image to
  source_size = 3000,3000
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
      tile = tile.filter(ImageFilter.BLUR)
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
  #image = ImageOps.fit(image, (50,50), Image.ANTIALIAS)
  hash1 = imagehash.whash(image)
  return hash1

##################
#divide source image into blocks for replacement
##################
def divide_image_into_blocks(image, tile_size, output_rgb_dict, output_hash_dict, blocks_list):
  width, height = image.size

  coordinate = 0;
  for i in range(0, width, tile_size[0]):
    for j in range(0, height, tile_size[1]):
      cropped_image = image.crop((i, j, i+tile_size[0], j+tile_size[1]))
      #blocks_list.append(cropped_image)
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
    return sorted_rgb_values[:3] #experiment with 3 closest rgb matches

##################
#fills the tile library (dictionary) with the images from the library database 
##################
def fill_tile_library(tile_dict):
  sqlite_file = 'image_library'

  db = sqlite3.connect(sqlite_file)
  cursor = db.cursor() 

  cursor.execute("SELECT * FROM tiles")
  db_tiles = cursor.fetchall()

  db.commit()
  db.close()

  R_overflow = 256
  G_overflow = 256
  B_overflow = 256
  #put tile images from database into our rgb/image dictionary
  print 'Gathering image tiles from library...'
  for i in range(0, len(db_tiles), 1):
    t = Image.open('library/'+(db_tiles[i])[0])

    if ((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3]) in tile_dict:
      print 'WARNING: 2 tiles with same RGB average: ', tile_dict[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])], '+', t
      #tile_dict[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])].show()
      #t.show()
      #tile_dict[(R_overflow, G_overflow, B_overflow)] = t
      R_overflow+=1
      G_overflow+=1
      B_overflow+=1
    else:
      tile_dict[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])] = t

def divide_image_into_quads(image):
  width, height = image.size
  quadlist = []
  coords = []

  if width > 1 and height > 1:
    for i in range(0, width, (width+1)/2):
      for j in range(0, height, (height+1)/2):
        print 'Coords:', i, j
        cropped_image = image.crop((i, j, i+(width+1)/2, j+(height+1)/2))
        quadlist.append(cropped_image)
        coords.append((i,j))
  else:
    print 'Error: Image is size of 1 pixel'

  return quadlist, coords

##################
#calculates colour variance between 4 image quads
##################
def calculate_variance(node, quad_rgb_dict):
  #divide image into quads
  quadlist, coords = divide_image_into_quads(node.data)
  quadlist_averages = []

  #get average rgb for each quad (for variance calculation) & put blocks into dict
  for i in quadlist:
    average_rgb = calc_average_rgb(i, True)
    quadlist_averages.append(average_rgb)

  #get mean rgb for all 4 quads
  RValues = [x[0] for x in quadlist_averages]
  GValues = [x[1] for x in quadlist_averages]
  BValues = [x[2] for x in quadlist_averages]

  average_quad_rgb_value = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )

  #get distances from quad averages to overall mean
  quadlist_distances = []
  for x in quadlist_averages:
    quadlist_distances.append(distance(x, average_quad_rgb_value))

  #square distances
  distances_squared = []
  for y in quadlist_distances:
    distances_squared.append(y**2)

  #calculate variance for image
  variance = sum(distances_squared) / len(distances_squared)
  return variance, quadlist, quadlist_averages, num_blocks, coords

##################
#recursively divides images into quads based on their colour variance
##################
def quadify_image(node, quad_rgb_dict):  
  variance, quadlist, quadlist_averages, num_blocks, coords = calculate_variance(node, quad_rgb_dict)

  #if variance is above threshold, quadify again
  print 'ID:', node.ID, 'variance:', variance
  if variance > variance_threshold and node.data.size > (10,10):
    #node.data.show()

    node.topleft = Tree()
    node.bottomleft = Tree()
    node.topright = Tree()
    node.bottomright = Tree()

    #put the image/rgb average/ID data into the new wuad children
    #ID: 1,2,3,4 represent tl,bl,tr,bl respectively
    #extra digits mean an extra division eg. 30 is top right quad of bottom right quad
    node.topleft.data = quadlist[0]
    node.topleft.rgb_avg = quadlist_averages[0]
    print 'Node ID, added num:', str(node.ID), str(1)
    node.topleft.ID = int(str(node.ID) + str(1))    
    node.topleft.coords = tuple(map(sum,zip(node.coords,coords[0])))
    print 'New quad created with ID #', node.topleft.ID
    #put rgb average data into the quad/block dict
    quad_rgb_dict[node.topleft.ID] = [node.topleft.rgb_avg, node.topleft.data, node.topleft.coords]

    node.bottomleft.data = quadlist[1]
    node.bottomleft.rgb_avg = quadlist_averages[1]
    node.bottomleft.ID = int(str(node.ID) + str(2))
    node.bottomleft.coords = tuple(map(sum,zip(node.coords,coords[1])))
    print 'New quad created with ID #', node.bottomleft.ID
    quad_rgb_dict[node.bottomleft.ID] = [node.bottomleft.rgb_avg, node.bottomleft.data, node.bottomleft.coords]

    node.topright.data = quadlist[2]
    node.topright.rgb_avg = quadlist_averages[2]
    node.topright.ID = int(str(node.ID) + str(3))
    node.topright.coords = tuple(map(sum,zip(node.coords,coords[2])))
    print 'New quad created with ID #', node.topright.ID
    quad_rgb_dict[node.topright.ID] = [node.topright.rgb_avg, node.topright.data, node.topright.coords]

    node.bottomright.data = quadlist[3]
    node.bottomright.rgb_avg = quadlist_averages[3]
    node.bottomright.ID = int(str(node.ID) + str(4))
    node.bottomright.coords = tuple(map(sum,zip(node.coords,coords[3])))
    print 'New quad created with ID #', node.bottomright.ID
    quad_rgb_dict[node.bottomright.ID] = [node.bottomright.rgb_avg, node.bottomright.data, node.bottomright.coords]

    global num_blocks
    num_blocks += 4

    #node.topleft.data.show()
    #node.bottomleft.data.show()
    #node.topright.data.show()
    #node.bottomright.data.show()
    #print 'quad topleft'
    quadify_image(node.topleft, quad_rgb_dict)
    #print 'quad bottomleft'
    quadify_image(node.bottomleft, quad_rgb_dict)
    #print 'quad topright'
    quadify_image(node.topright, quad_rgb_dict)
    #print 'quad bottomright'
    quadify_image(node.bottomright, quad_rgb_dict)

def calc_offset(key, previous_block):
  size = previous_block.size
  ID = key
  print 'current ID and size of prev block', ID, size

  last2 = ID % 100
  current_quad = str(last2)[:1]
  print 'Section to quad:', int(current_quad)

  if int(current_quad) == 0:
    print 'returning.......', -size[0], -size[1]
    return -size[0], -size[1]
  elif int(current_quad) == 1:
    return -size[0], 0
  elif int(current_quad) == 2:
    return 0, -size[1]
  else:
    return 0,0
  
##################
#main method - construct mosaic from tiles in library
##################
def create_mosaic(source_image, input_tile_size, outlier_flagging, vary_tiles, cheat, super_cheat, quadtree):
  start = time.time()

  target_image = Image.open(source_image)
  tile_size = input_tile_size, input_tile_size
  target_image = resize_source_image(target_image)  

  #Key = hash, Value = Image
  #tile_hashes = {}

  #Key = RGB, Value = Image
  tile_rgb_averages = {}
  fill_tile_library(tile_rgb_averages)  

  #Key = Coordinate in Source, Value = RGB
  block_rgb_dict = {}
  #Key = Coordinate in Source, Value = hash
  block_hash_dict = {}

  blocks_list = []
  #divide source image into blocks
  cropped_image_xy = divide_image_into_blocks(target_image, tile_size, block_rgb_dict, block_hash_dict, blocks_list)
  print 'cropped image x y',cropped_image_xy

  if quadtree:
    root = Tree()
    root.data = target_image
    root.ID = 0

    #Key = quad/block ID, Value = RGB avg, Image, Coord
    quad_rgb_dict = {}

    quadify_image(root, quad_rgb_dict)
    
    if num_blocks < 4:
      print 'Threshold is too high'

    print 'There are', num_blocks, 'blocks'
    #print quad_rgb_dict, '\n'

    node_iterator = root
    node_parent = None

    while node_iterator.topleft != None:
      print 'down topleft'
      print node_iterator.topleft.ID
      #node_iterator.topleft.data.show()
      node_parent = node_iterator #save node we were just in for back-travel
      node_iterator = node_iterator.topleft #move one step down into next child
    print 'up'
    node_iterator = node_parent

    while node_iterator.bottomleft != None:
      print 'down bottomleft'
      print node_iterator.bottomleft.ID
      #node_iterator.bottomleft.data.show()
      node_parent = node_iterator #save node we were just in for back-travel
      node_iterator = node_iterator.bottomleft #move one step down into next child
    print 'up'
    node_iterator = node_parent

    while node_iterator.topright != None:
      print 'down topright'
      print node_iterator.topright.ID
      #node_iterator.topright.data.show()
      node_parent = node_iterator #save node we were just in for back-travel
      node_iterator = node_iterator.topright #move one step down into next child
    print 'up'
    node_iterator = node_parent

    while node_iterator.bottomright != None:
      print 'down bottomright'
      print node_iterator.bottomright.ID
      #node_iterator.bottomright.data.show()
      node_parent = node_iterator #save node we were just in for back-travel
      node_iterator = node_iterator.bottomright #move one step down into next child
    print 'up'
    node_iterator = node_parent


  #create base mosaic image of default dimensions
  mosaic = Image.new('RGB', (target_image.size[0], target_image.size[1]), color=(255, 0, 255))

  x_offset = 0
  y_offset = 0
  num_tiles_placed = 0
  progress_percentage = 0

  #current_depth = 1 #tracks which layer of depth we are in
  previous_block = None #stores image
  
  #db_tiles_rgb_values = []

  block_list_counter = 0
  print 'Creating mosaic...'

  if quadtree:
    print sorted(quad_rgb_dict.keys())
    for key in sorted(quad_rgb_dict.keys()):
      block_image = quad_rgb_dict.get(key)[1]
      closest_rgb_matches = closest_tile(tile_rgb_averages, quad_rgb_dict.get(key)[0], vary_tiles)
      final_rgb = closest_rgb_matches[0] #to be replaced by hashing
      print '\n', key
      print 'Size:',block_image.size

      #resize and paste tile into place in output mosaic image
      if tile_rgb_averages[final_rgb].size != block_image.size:
        tile_rgb_averages[final_rgb] = ImageOps.fit(tile_rgb_averages.get(final_rgb), block_image.size, Image.ANTIALIAS)
      
      final_tile = tile_rgb_averages[final_rgb]


      digits = [int(d) for d in str(key)]
      print digits

      x_offset, y_offset = quad_rgb_dict.get(key)[2]
      print 'Offsets:', x_offset, y_offset

      #x_offset = 0
      #y_offset = 0
      #current_depth = 1
      #print 'Depth:', current_depth
      #for digit in digits:
      #  if digit == 1:
      #    y_offset += int(target_image.size[1] * math.pow(0.5, current_depth))
      #  if digit == 2:
      #    x_offset += int(target_image.size[0] * math.pow(0.5, current_depth))
      #  if digit == 3:
      #    x_offset += int(target_image.size[0] * math.pow(0.5, current_depth))
      #    y_offset += int(target_image.size[1] * math.pow(0.5, current_depth))
      #  else:
      #    print 'no change to offset'
      #
      #  current_depth += 1
      #print x_offset, y_offset
      #print 'Current depth:', current_depth
      #if len(str(key)) < current_depth + 1:
      #  last_digit = key % 10
      #  if last_digit == 0:
      #    print 'Parent Zone 0'
      #  elif last_digit == 1:
      #    print 'Parent Zone 1'
      #    y_offset += block_image.size[1]
      #  elif last_digit == 2:
      #    print 'Parent Zone 2'
      #    x_offset += block_image.size[0]
      #    y_offset -= block_image.size[1]
      #  else:
      #    print 'Parent Zone 3'          
      #    y_offset += block_image.size[1]
      #else:
      #  print 'prev block, ID', previous_block, key
      #  x_change, y_change = calc_offset(key, previous_block)
      #  print 'x_change, y_change:', x_change, y_change
      #  y_offset += y_change
      #  x_offset += x_change
      #  current_depth += 1   

      print 'X:', x_offset, 'Y:', y_offset
      
      mosaic.paste(final_tile, (x_offset,y_offset))


      #sets the point to place the next tile
      
      #code for pasting 4 quads      
      #if len(str(key)) < current_depth + 1:
      

        #if y_offset < target_image.size[1]:
          #y_offset += block_image.size[1]
        #else:
          #y_offset = 0
          #x_offset += block_image.size[0]
      #code for finding where to place first block of new quad area
      #else:
        

      #print 'X AFTER CHANGE:', x_offset, 'Y AFTER CHANGE:', y_offset

      num_tiles_placed += 1
      progress_percentage = num_tiles_placed/float(len(block_rgb_dict.keys())) * 100
      if progress_percentage % 5 == 0:
        print "Progress: ", progress_percentage, "%"

      block_list_counter += 1
      previous_block = final_tile #use to get size of prev block for offsetting

    print sorted(quad_rgb_dict.keys())

  else:    
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
        
        final_tile = tile_rgb_averages[final_rgb]

        if cheat:
          block_solid_rgb = Image.new('RGB',final_tile.size,block_rgb_dict.values()[i])
          mask = Image.new('RGBA',final_tile.size,(0,0,0,95)) #lower is more cheaty
          final_tile = Image.composite(final_tile,block_solid_rgb,mask).convert('RGB')
          #final_tile = ImageChops.blend(final_tile, block_solid_rgb, 0.5)

        mosaic.paste(final_tile, (x_offset,y_offset))

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

      block_list_counter += 1

  #mosaic = mosaic.filter(ImageFilter.MedianFilter)

  if super_cheat:
    mask = target_image
    mosaic = ImageChops.blend(mosaic, mask, 0.5)

  os.path.splitext(source_image)[0]
  mosaic.save('/home/mbax4sd2/3rd Year Project/output/%s%smosaic.jpg' % (os.path.splitext(source_image)[0][14:], input_tile_size)) 
  mosaic.show()

  end = time.time()
  print 'Time elapsed: ', end - start

#remove all unecessary code
#add hashing of quads + cheating
#fix recursive showing of images, not handling divisions well (not really necessary tbh, more for debugging)
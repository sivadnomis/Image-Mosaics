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

variance_threshold = 1000
num_blocks = 0

##################
#open source image
##################
def resize_source_image(image, quadtree):  
  #hard coded max dimensions to resize source image to
  source_size = 3000,3000
  image.thumbnail(source_size, Image.ANTIALIAS)
  new_x = image.size[0]
  new_y = image.size[1]

  if quadtree:
    #we must crop to a power of 64 so we can guarantee 6 levels of smooth quad divisions
    powers_of_64 = []
    base = 64
    for i in range(1,47): #47 * 16 is the closest number to 3000, our max size
      powers_of_64.append(base * i)

    new_x = min(powers_of_64, key=lambda x:abs(x-image.size[0]))
    #make sure the new x isn't larger than the original
    if new_x > image.size[0]:
      powers_of_64.remove(new_x)
      new_x = min(powers_of_64, key=lambda x:abs(x-image.size[0]))

    new_y = min(powers_of_64, key=lambda y:abs(y-image.size[1]))
    if new_y > image.size[1]:
      powers_of_64.remove(new_y)
      new_y = min(powers_of_64, key=lambda y:abs(y-image.size[1]))

    print 'Output mosaic size:', new_x, new_y

    image = image.crop((0,0,new_x,new_y))

  image.show()
  return image, new_x, new_y

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
    return sorted_rgb_values[:3] #returns 3 closest rgb matches

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

  #potential solution to images off same rgb
  #R_overflow = 256
  #G_overflow = 256
  #B_overflow = 256

  #put tile images from database into our rgb/image dictionary
  print 'Gathering image tiles from library...'
  for i in range(0, len(db_tiles), 1):
    t = Image.open('library/'+(db_tiles[i])[0])

    if ((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3]) in tile_dict:
      print 'WARNING: 2 tiles with same RGB average: ', tile_dict[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])], '+', t
      #tile_dict[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])].show()
      #t.show()
      #tile_dict[(R_overflow, G_overflow, B_overflow)] = t
      #R_overflow+=1
      #G_overflow+=1
      #B_overflow+=1
    else:
      tile_dict[((db_tiles[i])[1], (db_tiles[i])[2], (db_tiles[i])[3])] = t

##################
#divides an image into 4 equal size quads
##################
def divide_image_into_quads(image):
  width, height = image.size
  quadlist = []
  coords = []

  if width > 1 and height > 1:
    for i in range(0, width, (width+1)/2):
      for j in range(0, height, (height+1)/2):
        cropped_image = image.crop((i, j, i+(width+1)/2, j+(height+1)/2))
        quadlist.append(cropped_image)
        coords.append((i,j))
  else:
    print 'Error: Image is size of 1 pixel'

  return quadlist, coords

##################
#calculates colour variance between 4 image quads
##################
def calculate_variance(node):
  #divide image into quads
  quadlist, coords = divide_image_into_quads(node.data)
  quadlist_averages = []

  sub_quad_list = []
  sub_quad_list_averages = []
  #new_coords = []

  #divide quads into 4 further quads each to get a more representative variance over 16 blocks
  for q in quadlist:
    sub_quad, sub_quad_coords = divide_image_into_quads(q)
    sub_quad_list.append(sub_quad)
    #new_coords.append(sub_quad_coords)

  #get average rgb for each quad (for variance calculation) & put blocks into dict
  for i in quadlist:
    average_rgb = calc_average_rgb(i, True)
    quadlist_averages.append(average_rgb)

  for j in sub_quad_list:
    for k in j:
      average_rgb = calc_average_rgb(k, True)
      sub_quad_list_averages.append(average_rgb)

  #get mean rgb for all 4 quads
  RValues = [x[0] for x in sub_quad_list_averages]
  GValues = [x[1] for x in sub_quad_list_averages]
  BValues = [x[2] for x in sub_quad_list_averages]

  average_quad_rgb_value = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )

  #get distances from quad averages to overall mean
  sub_quad_list_distances = []
  for x in sub_quad_list_averages:
    sub_quad_list_distances.append(distance(x, average_quad_rgb_value))

  #square distances
  distances_squared = []
  for y in sub_quad_list_distances:
    distances_squared.append(y**2)

  #calculate variance for image
  variance = sum(distances_squared) / len(distances_squared)
  #print 'distsum, distlen, Var', sum(distances_squared), len(distances_squared), variance
  return variance, quadlist, quadlist_averages, num_blocks, coords

##################
#recursively divides images into quads based on their colour variance
##################
def quadify_image(node, quad_rgb_dict, quad_hash_dict):  
  variance, quadlist, quadlist_averages, num_blocks, coords = calculate_variance(node)

  if num_blocks < 4:
    print 'Initial variance:', variance
    #if the initial variance is below this value we need to allow more subtle differences
    if variance < 2500:
      global variance_threshold
      variance_threshold /= 2
      print 'Reduced variance threshold to', variance_threshold
  #if variance is above threshold, quadify again
  #print 'ID:', node.ID, 'variance:', variance
  if variance > variance_threshold and node.data.size > (10,10):
    node.topleft = Tree()
    node.bottomleft = Tree()
    node.topright = Tree()
    node.bottomright = Tree()

    #put the image/rgb average/ID data into the new wuad children
    #ID: 1,2,3,4 represent tl,bl,tr,bl respectively
    #extra digits mean an extra division eg. 30 is top right quad of bottom right quad
    node.topleft.data = quadlist[0]
    node.topleft.rgb_avg = quadlist_averages[0]
    node.topleft.ID = int(str(node.ID) + str(1))    
    node.topleft.coords = tuple(map(sum,zip(node.coords,coords[0])))
    #put rgb average data into the quad/block dict
    quad_rgb_dict[node.topleft.ID] = [node.topleft.rgb_avg, node.topleft.data, node.topleft.coords]
    quad_hash_dict[node.topleft.ID] = calc_image_hash(node.topleft.data)

    node.bottomleft.data = quadlist[1]
    node.bottomleft.rgb_avg = quadlist_averages[1]
    node.bottomleft.ID = int(str(node.ID) + str(2))
    node.bottomleft.coords = tuple(map(sum,zip(node.coords,coords[1])))
    quad_rgb_dict[node.bottomleft.ID] = [node.bottomleft.rgb_avg, node.bottomleft.data, node.bottomleft.coords]
    quad_hash_dict[node.bottomleft.ID] = calc_image_hash(node.bottomleft.data)

    node.topright.data = quadlist[2]
    node.topright.rgb_avg = quadlist_averages[2]
    node.topright.ID = int(str(node.ID) + str(3))
    node.topright.coords = tuple(map(sum,zip(node.coords,coords[2])))
    quad_rgb_dict[node.topright.ID] = [node.topright.rgb_avg, node.topright.data, node.topright.coords]
    quad_hash_dict[node.topright.ID] = calc_image_hash(node.topright.data)

    node.bottomright.data = quadlist[3]
    node.bottomright.rgb_avg = quadlist_averages[3]
    node.bottomright.ID = int(str(node.ID) + str(4))
    node.bottomright.coords = tuple(map(sum,zip(node.coords,coords[3])))
    quad_rgb_dict[node.bottomright.ID] = [node.bottomright.rgb_avg, node.bottomright.data, node.bottomright.coords]
    quad_hash_dict[node.bottomright.ID] = calc_image_hash(node.bottomright.data)

    global num_blocks
    num_blocks += 4

    quadify_image(node.topleft, quad_rgb_dict, quad_hash_dict)
    quadify_image(node.bottomleft, quad_rgb_dict, quad_hash_dict)
    quadify_image(node.topright, quad_rgb_dict, quad_hash_dict)
    quadify_image(node.bottomright, quad_rgb_dict, quad_hash_dict)
  
##################
#main method - construct mosaic from tiles in library
##################
def create_mosaic(source_image, input_tile_size, outlier_flagging, vary_tiles, cheat, super_cheat):
  start = time.time()

  quadtree = False
  if input_tile_size == 0:
    quadtree = True
    print 'Quadtree tiling is on'

  target_image = Image.open(source_image)
  tile_size = input_tile_size, input_tile_size
  target_image, width, height = resize_source_image(target_image, quadtree)  

  #Key = RGB, Value = Image
  tile_rgb_averages = {}
  fill_tile_library(tile_rgb_averages)  

  #create base mosaic image of default dimensions
  mosaic = Image.new('RGB', (width, height), color=(255, 0, 255))

  x_offset = 0
  y_offset = 0
  num_tiles_placed = 0
  progress_percentage = 0   
  
  print 'Creating mosaic...'

  if quadtree:
    #initial base image
    root = Tree()
    root.data = target_image
    root.ID = 0

    #stores parent quad
    previous_block = None

    #Key = quad/block ID, Value = RGB avg, Image, Coord
    quad_rgb_dict = {}
    #Key = quad/block ID, Value = hash
    quad_hash_dict = {}

    #recursively divide image into quads based on colour variance
    quadify_image(root, quad_rgb_dict, quad_hash_dict)
    
    if num_blocks < 4:
      print 'Threshold is too high'
    print 'There are', num_blocks, 'blocks'

    #print sorted(quad_rgb_dict.keys())
    for key in sorted(quad_rgb_dict.keys()):
      block_image = quad_rgb_dict.get(key)[1]
      closest_rgb_matches = closest_tile(tile_rgb_averages, quad_rgb_dict.get(key)[0], vary_tiles)
      
      #perform wavelet analysis on the matches to pick the best
      closest_hashes = {}
      for rgb in closest_rgb_matches:
        #fitted to block size to get accurate hash
        fitted_tile = ImageOps.fit(tile_rgb_averages[rgb], block_image.size, Image.ANTIALIAS)
        closest_hashes[calc_image_hash(fitted_tile)] = rgb
      hash_diffs = {}
      for h in closest_hashes.keys():
        hash_diffs[h - quad_hash_dict.get(key)] = h

      final_hash = hash_diffs[min(hash_diffs)]
      final_rgb = closest_hashes[final_hash]

      #resize and paste tile into place in output mosaic image
      if tile_rgb_averages[final_rgb].size != block_image.size:
        tile_rgb_averages[final_rgb] = ImageOps.fit(tile_rgb_averages.get(final_rgb), block_image.size, Image.ANTIALIAS)
      
      x_offset, y_offset = quad_rgb_dict.get(key)[2]

      #paste replacement tile into place
      final_tile = tile_rgb_averages[final_rgb]

      if cheat:
        quad_solid_rgb = Image.new('RGB',final_tile.size,quad_rgb_dict.get(key)[0])
        mask = Image.new('RGBA',final_tile.size,(0,0,0,95)) #lower is more cheaty
        final_tile = Image.composite(final_tile,quad_solid_rgb,mask).convert('RGB')

      mosaic.paste(final_tile, (x_offset,y_offset))

      #progress marker
      num_tiles_placed += 1
      progress_percentage = num_tiles_placed/float(len(quad_rgb_dict.keys())) * 100
      if progress_percentage % 5 == 0:
        print "Progress: ", progress_percentage, "%"

      #used to get size of prev block for offsetting
      previous_block = final_tile 

  else:
    #Key = Coordinate in Source, Value = RGB
    block_rgb_dict = {}
    #Key = Coordinate in Source, Value = hash
    block_hash_dict = {}

    #divide source image into blocks
    cropped_image_xy = divide_image_into_blocks(target_image, tile_size, block_rgb_dict, block_hash_dict)

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

  if super_cheat:
    mask = target_image
    mosaic = ImageChops.blend(mosaic, mask, 0.5)

  os.path.splitext(source_image)[0]
  mosaic.save('/home/mbax4sd2/3rd Year Project/output/%s%smosaic.jpg' % (os.path.splitext(source_image)[0][14:], input_tile_size)) 
  mosaic.show()

  end = time.time()
  print 'Time elapsed: ', end - start


#'share' cropped pixels between all sides, not just bottom/right
#try on laptop with huge library
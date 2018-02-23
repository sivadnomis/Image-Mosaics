#AIM IS TO REMOVE THIS FILE AND INTEGRATE EVERYTHING IN HERE INTO mosaic.py
#
#
#
#

from PIL import Image, ImageOps
import os, sys, commands, math, mosaic
from scipy.spatial import KDTree

class Tree(object):
    def __init__(self):
        self.topleft = None
        self.bottomleft = None
        self.topright = None        
        self.bottomright = None
        self.data = None

variance_threshold = 1500
num_blocks = 0

def divide_image_into_quads(image):
  width, height = image.size
  quadlist = []

  if width > 1 and height > 1:
    for i in range(0, width, (width+1)/2):
      for j in range(0, height, (height+1)/2):
        cropped_image = image.crop((i, j, i+(width+1)/2, j+(height+1)/2))
        quadlist.append(cropped_image)
  else:
    print 'Error: Image is size of 1 pixel'

  return quadlist

def calculate_variance(node, block_rgb_dict):
  #divide image into quads
  quadlist = divide_image_into_quads(node.data)
  quadlist_averages = []
  #node.data.show()

  #get average rgb for each quad (for variance calculation) & put blocks into dict
  for i in quadlist:
    average_rgb = mosaic.calc_average_rgb(i, True)
    quadlist_averages.append(average_rgb)

    global num_blocks
    block_rgb_dict[num_blocks] = average_rgb    
    num_blocks += 1

  #ignore block that has just been divided into 4 after initial quadify
  if num_blocks != 4:
    num_blocks -= 1 

  print block_rgb_dict
  print 'num_blocks: ', num_blocks

  #get mean rgb for all 4 quads
  RValues = [x[0] for x in quadlist_averages]
  GValues = [x[1] for x in quadlist_averages]
  BValues = [x[2] for x in quadlist_averages]

  average_quad_rgb_value = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )

  #get distances from quad averages to overall mean
  quadlist_distances = []
  for x in quadlist_averages:
    quadlist_distances.append(mosaic.distance(x, average_quad_rgb_value))

  #square distances
  distances_squared = []
  for y in quadlist_distances:
    distances_squared.append(y**2)

  #calculate variance for image
  variance = sum(distances_squared) / len(distances_squared)
  return variance, quadlist, num_blocks

def quadify_image(node, block_rgb_dict):  
  variance, quadlist, num_blocks = calculate_variance(node, block_rgb_dict)
  print 'Variance: ', variance, '\n', node.data
  print 'num_blocks: ', num_blocks

  #if variance is above threshold, quadify again
  print node.data.size, '\n'
  if variance > variance_threshold and node.data.size > (4,4):
    #node.data.show()

    node.topleft = Tree()
    node.bottomleft = Tree()
    node.topright = Tree()
    node.bottomright = Tree()

    node.topleft.data = quadlist[0]
    node.bottomleft.data = quadlist[1]
    node.topright.data = quadlist[2]
    node.bottomright.data = quadlist[3]

    #node.topleft.data.show()
    #node.bottomleft.data.show()
    #node.topright.data.show()
    #node.bottomright.data.show()

    quadify_image(node.topleft, block_rgb_dict)
    quadify_image(node.bottomleft, block_rgb_dict)
    quadify_image(node.topright, block_rgb_dict)
    quadify_image(node.bottomright, block_rgb_dict)

def distance( x , y ):
  dist = math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2 + (x[2] - y[2])**2)
  return dist

def closest_tile(tile_rgb_averages, block_rgb_average):
  sorted_rgb_values = sorted(tile_rgb_averages.keys(), key=lambda x:distance(x, block_rgb_average))
  return sorted_rgb_values[:3] #experiment with 3 closest rgb matches

target_image = Image.open(sys.argv[1])
root = Tree()
root.data = target_image

#Key = Coordinate in Source, Value = RGB
block_rgb_dict = {}

quadify_image(root, block_rgb_dict)
print 'there are', num_blocks, 'blocks'

#Key = RGB, Value = Image
tile_rgb_averages = {}
mosaic.fill_tile_library(tile_rgb_averages)  

mosaic = Image.new('RGB', (target_image.size[0], target_image.size[1]), color=(255, 0, 255))
mosaic.show()








x_offset = 0
y_offset = 0
num_tiles_placed = 0
progress_percentage = 0

for i in range(0, len(block_rgb_dict.keys()), 1):
  closest_rgb_matches = closest_tile(tile_rgb_averages, block_rgb_dict.values()[i])

  #perform wavelet analysis on the matches to pick the best
  closest_hashes = {}
  for rgb in closest_rgb_matches:
    closest_hashes[mosaic.calc_image_hash(tile_rgb_averages[rgb])] = rgb
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





try:
  #root.topright.data.show()
  print 'blah'
except:
  print 'This image was not quadded'

#find a way to display sourceimage indicating where the quads are
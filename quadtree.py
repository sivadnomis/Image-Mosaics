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

variance_threshold = 2000

def divide_image_into_quads(image):
  width, height = image.size
  quadlist = []

  for i in range(0, width, (width+1)/2):
    for j in range(0, height, (height+1)/2):
      cropped_image = image.crop((i, j, i+(width+1)/2, j+(height+1)/2))
      quadlist.append(cropped_image)

  return quadlist

def quadify_image(node):
  #divide image into quads
  quadlist = divide_image_into_quads(node.data)
  quadlist_averages = []
  node.data.show()
  print quadlist

  #get avrage rgb for each quad
  print 'Quad rgb averages: '
  for i in quadlist:
    average_rgb = mosaic.calc_average_rgb(i, True)
    quadlist_averages.append(average_rgb)
    print average_rgb

  #get mean rgb for all 4 quads
  RValues = [x[0] for x in quadlist_averages]
  GValues = [x[1] for x in quadlist_averages]
  BValues = [x[2] for x in quadlist_averages]

  average_quad_rgb_value = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )
  print 'Mean: ', average_quad_rgb_value

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
  print 'Variance: ', variance

  #if variance is above threshold, quadify again
  if variance > variance_threshold:
    node.topleft = Tree()
    node.bottomleft = Tree()
    node.topright = Tree()
    node.bottomright = Tree()

    node.topleft.data = quadlist[0]
    node.bottomleft.data = quadlist[1]
    node.topright.data = quadlist[2]
    node.bottomright.data = quadlist[3]

    quadify_image(node.topleft)
    quadify_image(node.bottomleft)
    quadify_image(node.topright)
    quadify_image(node.bottomright)


source = Image.open(sys.argv[1])
root = Tree()
root.data = source

quadify_image(root)

try:
  root.topright.data.show()
except:
  print 'This image was not quadded'

#calculate variance
#make it all recursive
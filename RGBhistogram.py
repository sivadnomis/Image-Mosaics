from PIL import Image, ImageOps
import numpy as np
import math, sys, os
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib import colors as mcolors
import mosaic

RValues = []
GValues = []
BValues = []

R_Bins = np.linspace(math.ceil(0), math.floor(255), 50);
G_Bins = np.linspace(math.ceil(0), math.floor(255), 50);
B_Bins = np.linspace(math.ceil(0), math.floor(255), 50);

def calculate_variance(library):
  for i in library:
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

def generate_RGB_buckets(image):
  image = ImageOps.fit(image, (50,50), Image.ANTIALIAS)
  #image.show()

  PixelValues = list(image.getdata())

  RValues = [x[0] for x in PixelValues] #list of all 'r' pixel values in image
  GValues = [x[1] for x in PixelValues]
  BValues = [x[2] for x in PixelValues]

  #Figure 2

  R_Bins = np.linspace(math.ceil(min(RValues)), 
                     math.floor(max(RValues)),
                     50) # fixed number of bins

  G_Bins = np.linspace(math.ceil(min(GValues)), 
                     math.floor(max(GValues)),
                     50) # fixed number of bins

  B_Bins = np.linspace(math.ceil(min(BValues)), 
                     math.floor(max(BValues)),
                     50) # fixed number of bins


  plt.xlim([min(B_Bins)-5, max(B_Bins)+5])
  plt.hist(BValues, bins=B_Bins, alpha=0.5)

  plt.xlim([min(G_Bins)-5, max(G_Bins)+5])
  plt.hist(GValues, bins=G_Bins, alpha=0.5)

  plt.xlim([min(R_Bins)-5, max(R_Bins)+5])
  plt.hist(RValues, bins=R_Bins, alpha=0.5)

  plt.title('Colour distribution in image')
  plt.xlabel('Pixel value')
  plt.ylabel('Count')


  #Figure 1

  RBuckets = [0] * 256
  for i in RValues:
    RBuckets[i]+=1

  GBuckets = [0] * 256
  for i in GValues:
    GBuckets[i]+=1

  BBuckets = [0] * 256
  for i in BValues:
    BBuckets[i]+=1

  bucket_list = [RBuckets, GBuckets, BBuckets]
  return bucket_list


image_name = 'library'

#Logic for image vs library
if len(sys.argv) >= 3:
  if sys.argv[2] == 'lib':
    os.chdir(sys.argv[1])
    num_images = 0

    #bucket_list = generate_RGB_buckets(Image.open(os.listdir(os.getcwd())[0]))
    bucket_list = [[0 for x in range(255)] for y in range(3)]
    image_averages = []

    for f in os.listdir(os.getcwd()):
      image = Image.open(f)
      temp_bucket_list = generate_RGB_buckets(image)
      for cb in range(3):
        for b in range(255):
          bucket_list[cb][b] += temp_bucket_list[cb][b]      

      #get average rgb for each quad (for variance calculation) & put blocks into dict
      average_rgb = mosaic.calc_average_rgb(image, True)
      image_averages.append(average_rgb)

      num_images += 1
      print 'Calculated image #', num_images, 'of', len(os.listdir(os.getcwd()))

    #get mean rgb for all 4 quads
    RValues = [x[0] for x in image_averages]
    GValues = [x[1] for x in image_averages]
    BValues = [x[2] for x in image_averages]

    average_quad_rgb_value = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )

    #get distances from quad averages to overall mean
    image_distances = []
    for x in image_averages:
      image_distances.append(mosaic.distance(x, average_quad_rgb_value))

    #square distances
    distances_squared = []
    for y in image_distances:
      distances_squared.append(y**2)

    #calculate variance for image
    variance = sum(distances_squared) / len(distances_squared)
    print 'Library variance:', variance

    for cb in range(3):
      for b in range(255):
        bucket_list[cb][b] /= num_images

else:
  image_name = sys.argv[1]
  image = Image.open(image_name)

  bucket_list = generate_RGB_buckets(image)

#Plot graphs
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

i = 0
for c, z in zip(['r', 'g', 'b'], [10, 20, 30]):
    xs = np.arange(len(bucket_list[0])) #max for x axis, creates [0,1,2,3,...,255]
    ys = bucket_list[i]
    i+=1

    cs = [c] * len(xs)
    ax.bar(xs, ys, zs=z, zdir='y', color=cs, alpha=0.8)

plt.title('Colour distribution in ' + image_name)
ax.set_xlabel('Pixel value')
ax.set_ylabel('R - G - B')
ax.set_zlabel('Count')

plt.show()
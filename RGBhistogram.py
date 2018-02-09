from PIL import Image
import numpy as np
import math, sys
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib import colors as mcolors

image_name = sys.argv[1]
image = Image.open(image_name)

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
print R_Bins

plt.title('Colour distribution in ' + image_name)
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

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

i = 0
for c, z in zip(['r', 'g', 'b'], [10, 20, 30]):
    xs = np.arange(len(RBuckets)) #max for x axis, creates [0,1,2,3,...,255]
    ys = bucket_list[i]
    i+=1

    cs = [c] * len(xs)
    ax.bar(xs, ys, zs=z, zdir='y', color=cs, alpha=0.8)

plt.title('Colour distribution in ' + image_name)
ax.set_xlabel('Pixel value')
ax.set_ylabel('R - G - B')
ax.set_zlabel('Count')

plt.show()
from PIL import Image
import numpy as np
import math, sys
from matplotlib import pyplot as plt

image_name = sys.argv[1]
image = Image.open(image_name)

PixelValues = list(image.getdata())

RValues = [x[0] for x in PixelValues]
GValues = [x[1] for x in PixelValues]
BValues = [x[2] for x in PixelValues]

R_Bins = np.linspace(math.ceil(min(RValues)), 
                   math.floor(max(RValues)),
                   50) # fixed number of bins

G_Bins = np.linspace(math.ceil(min(RValues)), 
                   math.floor(max(RValues)),
                   50) # fixed number of bins

B_Bins = np.linspace(math.ceil(min(RValues)), 
                   math.floor(max(RValues)),
                   50) # fixed number of bins

plt.xlim([min(R_Bins)-5, max(R_Bins)+5])

plt.hist(RValues, bins=R_Bins, alpha=0.5)
plt.title('Red colour distribution in ' + image_name)
plt.xlabel('Red pixel values')
plt.ylabel('count')

plt.show()

plt.xlim([min(G_Bins)-5, max(G_Bins)+5])

plt.hist(GValues, bins=G_Bins, alpha=0.5)
plt.title('Green colour distribution in ' + image_name)
plt.xlabel('Green pixel values')
plt.ylabel('count')

plt.show()

plt.xlim([min(B_Bins)-5, max(B_Bins)+5])

plt.hist(BValues, bins=B_Bins, alpha=0.5)
plt.title('Blue colour distribution in ' + image_name)
plt.xlabel('Blue pixel values')
plt.ylabel('count')

plt.show()
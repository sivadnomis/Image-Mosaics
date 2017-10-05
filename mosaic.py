from PIL import Image
import os

##################
#open source image
##################
TargetImage = Image.open('monkey.jpg')
size = 250, 250
TargetImage.thumbnail(size, Image.ANTIALIAS)
#TargetImage.show()

##################
#open tile images in library
##################
os.chdir(r'library')
for f in os.listdir(os.getcwd()):#os.listdir('library'):
    print f
    tile = Image.open(f)

    size = 250, 250
    tile.thumbnail(size, Image.ANTIALIAS)
    #tile.show()

##################
#join 2 images together
##################
images = map(Image.open, ['bronze.jpg', 'hut.jpg'])
size = 250, 250
for i in images:
  i.thumbnail(size, Image.ANTIALIAS)
widths, heights = zip(*(i.size for i in images))

total_width = sum(widths)
max_height = max(heights)

mosaic = Image.new('RGB', (total_width, max_height))

x_offset = 0
for im in images:
  mosaic.paste(im, (x_offset,0))
  x_offset += im.size[0]

mosaic.save('test.jpg')
mosaic.show()

##################
#calculate average RGB of source image
##################
width, height = TargetImage.size
print width, "X", height

PixelValues = list(TargetImage.getdata())
RValues = [x[0] for x in PixelValues]
GValues = [x[1] for x in PixelValues]
BValues = [x[2] for x in PixelValues]

AverageRGBValue = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )
print AverageRGBValue

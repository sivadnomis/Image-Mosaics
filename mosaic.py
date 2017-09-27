from PIL import Image

TargetImage = Image.open('monkey.jpg')
TargetImage.show()

width, height = TargetImage.size
print width, "X", height

PixelValues = list(TargetImage.getdata())
RValues = [x[0] for x in PixelValues]
GValues = [x[1] for x in PixelValues]
BValues = [x[2] for x in PixelValues]

AverageRGBValue = ( sum(RValues)/len(RValues), sum(GValues)/len(GValues), sum(BValues)/len(BValues) )
print AverageRGBValue

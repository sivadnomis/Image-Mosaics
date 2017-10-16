import mosaic
import sys

print ("Creating mosaic for: ", sys.argv[1], "with tile size: ", int(sys.argv[2]))
mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]))
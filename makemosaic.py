import mosaic
import sys

print ("Creating mosaic for: ", sys.argv[1], "with tile size: ", int(sys.argv[2]))
mosaic.createMosaic(sys.argv[1], int(sys.argv[2]))
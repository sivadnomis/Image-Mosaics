import mosaic

import sys
print "This is the name of the script: ", sys.argv[0]
print "This is the 1st arg ", sys.argv[1]
print "Number of arguments: ", len(sys.argv)
print "The arguments are: " , str(sys.argv)

mosaic.createMosaic(sys.argv[1])
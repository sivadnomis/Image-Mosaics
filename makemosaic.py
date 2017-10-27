import mosaic
import sys

print "Creating mosaic for:", sys.argv[1], "with tile size:", int(sys.argv[2])
if sys.argv[3] == 'y':
  print "Outlier flagging is on"
  mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]), True)
else:
  print "Outlier flagging is off"
  mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]), False)
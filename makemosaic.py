import mosaic
import sys

if len(sys.argv) >= 3:
  print "Creating mosaic for:", sys.argv[1], "with tile size:", int(sys.argv[2])
if len(sys.argv) >= 4:
  #no point in being able to flag and vary at the same time
  if sys.argv[3] == 'flag':
    print "Outlier flagging is on"
    mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]), True, False, False, False)
  elif sys.argv[3] == 'vary':
    print "Tile variance (closest 2 matches) is on"
    mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]), False, True, False, False)
  elif sys.argv[3] == 'cheat':
    print "RGB mask block cheating is on"
    mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]), False, False, True, False)
  elif sys.argv[3] == 'supercheat':
    print "Souce image mask cheating is on"
    mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]), False, False, False, True)
  else:
    mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]), False, False, False, False)

else:
  mosaic.create_mosaic(sys.argv[1], int(sys.argv[2]), False, False, False, False)

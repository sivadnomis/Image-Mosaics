import mosaic
import sys
import commands

def create_mosaics( argument ):
  commands.getstatusoutput('python makemosaic.py source_images/monkey.jpg 50 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/monkey.jpg 20 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/monkey.jpg 10 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/monkey.jpg 5 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/me.jpg 50 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/me.jpg 20 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/me.jpg 10 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/me.jpg 5 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/rainbow.jpg 50 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/rainbow.jpg 20 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/rainbow.jpg 10 ' + argument)
  commands.getstatusoutput('python makemosaic.py source_images/rainbow.jpg 5 ' + argument)

create_mosaics('')
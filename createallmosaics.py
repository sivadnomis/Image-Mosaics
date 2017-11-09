import mosaic
import sys
import commands

def create_mosaics( argument ):
  commands.getstatusoutput('python makemosaic.py monkey.jpg 50 ' + argument)
  commands.getstatusoutput('python makemosaic.py monkey.jpg 20 ' + argument)
  commands.getstatusoutput('python makemosaic.py monkey.jpg 10 ' + argument)
  commands.getstatusoutput('python makemosaic.py monkey.jpg 5 ' + argument)
  commands.getstatusoutput('python makemosaic.py me.jpg 50 ' + argument)
  commands.getstatusoutput('python makemosaic.py me.jpg 20 ' + argument)
  commands.getstatusoutput('python makemosaic.py me.jpg 10 ' + argument)
  commands.getstatusoutput('python makemosaic.py me.jpg 5 ' + argument)
  commands.getstatusoutput('python makemosaic.py rainbow.jpg 50 ' + argument)
  commands.getstatusoutput('python makemosaic.py rainbow.jpg 20 ' + argument)
  commands.getstatusoutput('python makemosaic.py rainbow.jpg 10 ' + argument)
  commands.getstatusoutput('python makemosaic.py rainbow.jpg 5 ' + argument)

create_mosaics('')
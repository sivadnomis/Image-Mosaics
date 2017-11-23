from PIL import Image, ImageOps
import os
import mosaic, createallmosaics
import sys
import commands

monkey_list = ['monkey50mosaic', 'monkey20mosaic', 'monkey10mosaic', 'monkey5mosaic']
monkey_naive_results = []

me_list = ['me50mosaic', 'me20mosaic', 'me10mosaic', 'me5mosaic']
me_naive_results = []

rainbow_list = ['rainbow50mosaic', 'rainbow20mosaic', 'rainbow10mosaic', 'rainbow5mosaic']
rainbow_naive_results = []
#createallmosaics.create_mosaics('')

print 'Naive mosaic SSIM results\n'
for mosaic in monkey_list:
  result = commands.getstatusoutput('python test_image.py output/' + mosaic + '.jpg source_images/monkey.jpg')[1]
  monkey_naive_results.append(float(result))
  print result, mosaic, 'naive'  
print '\n'

for mosaic in me_list:
  result = commands.getstatusoutput('python test_image.py output/' + mosaic + '.jpg source_images/me.jpg')[1]
  me_naive_results.append(float(result))
  print result, mosaic, 'naive' 
print '\n'

for mosaic in rainbow_list:
  result = commands.getstatusoutput('python test_image.py output/' + mosaic + '.jpg source_images/rainbow.jpg')[1]
  rainbow_naive_results.append(float(result))
  print result, mosaic, 'naive' 
print '\n------------------------------------\n'
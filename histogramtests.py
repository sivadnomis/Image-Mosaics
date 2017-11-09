from PIL import Image, ImageOps
import os
import mosaic, createallmosaics
import sys
import commands

monkey_list = ['monkey50mosaic', 'monkey20mosaic', 'monkey10mosaic', 'monkey5mosaic']
monkey_naive_results = []
monkey_histogram_results = []

me_list = ['me50mosaic', 'me20mosaic', 'me10mosaic', 'me5mosaic']
me_naive_results = []
me_histogram_results = []

rainbow_list = ['rainbow50mosaic', 'rainbow20mosaic', 'rainbow10mosaic', 'rainbow5mosaic']
rainbow_naive_results = []
rainbow_histogram_results = []

createallmosaics.create_mosaics('')

print 'Naive mosaic SSIM results\n'
for mosaic in monkey_list:
  result = commands.getstatusoutput('python tests.py output/' + mosaic + '.jpg monkey.jpg')[1]
  monkey_naive_results.append(float(result))
  print result, mosaic, 'naive'  
print '\n'

for mosaic in me_list:
  result = commands.getstatusoutput('python tests.py output/' + mosaic + '.jpg me.jpg')[1]
  me_naive_results.append(float(result))
  print result, mosaic, 'naive' 
print '\n'

for mosaic in rainbow_list:
  result = commands.getstatusoutput('python tests.py output/' + mosaic + '.jpg rainbow.jpg')[1]
  rainbow_naive_results.append(float(result))
  print result, mosaic, 'naive' 
print '\n------------------------------------\n'

createallmosaics.create_mosaics('histogram')

print 'Histogrammed mosaic SSIM results\n'
for mosaic in monkey_list:
  result = commands.getstatusoutput('python tests.py output/' + mosaic + '.jpg monkey.jpg')[1]
  monkey_histogram_results.append(float(result))
  print result, mosaic, 'histogram'  
print '\n'

for mosaic in me_list:
  result = commands.getstatusoutput('python tests.py output/' + mosaic + '.jpg me.jpg')[1]
  me_histogram_results.append(float(result))
  print result, mosaic, 'histogram'
print '\n'

for mosaic in rainbow_list:
  result = commands.getstatusoutput('python tests.py output/' + mosaic + '.jpg rainbow.jpg')[1]
  rainbow_histogram_results.append(float(result))
  print result, mosaic, 'histogram'
print '\n------------------------------------\n'

print 'Difference in SSIM result between naive and histogram\n'
for i in range(0, 4, 1):
  print monkey_list[i], 'Diff =', (monkey_histogram_results[i] - monkey_naive_results[i])

for i in range(0, 4, 1):
  print me_list[i], 'Diff =', (me_histogram_results[i] - me_naive_results[i])

for i in range(0, 4, 1):
  print rainbow_list[i], 'Diff =', (rainbow_histogram_results[i] - rainbow_naive_results[i])
ImageMosaics
------------

Given a image and a tile size (no. of pixels), this program generates an image mosaic from the source image, with tiles from the image library of the specified tile size.

------------

Main script as command line tool:

  -------------
  NOTE: processlibrary.py must be run first if this is the first time running the program*
  -------------

  makemosaic.py input tile_size [flag] [vary]

  Default arguments:

  input        Source image file
  tile_size    Pixel height and width of each tile

  Optional arguments (don't work together):

  [flag]       Highlights blocks in the output mosaic without a close colour match in the library
  [vary]       Selects randomly from the 2 closest tile matches rather than the closest
  [cheat]      Applies a solid colour mask of the average RGB block over each tile
  [supercheat] Applies a mask of the source image over the mosaic

  Outputs a mosaic of the provided source image in the format output/[input][tile_size]mosaic.jpg


Other scripts:

  *processlibrary.py

  This script must be run before makemosaic. It runs through all the images in the library, calculating their average RGB colour and storing the data in a Sqlite database for later use.

  
  test_image.py output_mosaic source_image

  Runs SSIM (Structural Similarity Index) test on a source image and its mosaic, returns a decimal score (higher = closer match).


  createallmosaics.py

  Creates 4 mosaics for each of my main test images (monkey.jpg, me.jpg, rainbow.jpg) for 4 different sizes (50, 20, 10, 5). Mainly used for cleanup after experimenting with different image techniques.


  SSIM_tests.py

  Runs suite of SSIM tests, on the 4 mosaics for each of the main test images.


  RGBhistogram.py image/library [lib]

  Genarates 2 histograms showing the RGB colour distribution of the image/library specified in the argument. Use 'lib' flag if argument is a library.

Notes:
  
  * To use a different image library, simply rename/replace the 'library' folder with a different folder.

  * Output size is currently fixed at 500,500 but the program works at higher resolutions too.

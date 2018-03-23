from PIL import Image, ImageOps
import mosaic, os
import sqlite3, imagehash

sqlite_file = 'image_library'

db = sqlite3.connect(sqlite_file)
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS tiles(file_name TEXT PRIMARY KEY, RValue INT, GValue INT, BValue INT)")
cursor.execute("SELECT * FROM tiles")

counter = 0
os.chdir(r'library')
for f in os.listdir(os.getcwd()):
    tile = Image.open(f)

    tile_RGB = mosaic.calc_average_rgb(tile, False)
    tile_RValue = tile_RGB[0]
    tile_GValue = tile_RGB[1]
    tile_BValue = tile_RGB[2]

    cursor.execute('''INSERT OR IGNORE INTO tiles(file_name, RValue, GValue, BValue)
                  VALUES(?,?,?,?)''', (f, tile_RValue, tile_GValue, tile_BValue))
    counter += 1
    print 'Added', f, '(', counter, '/', len(os.listdir(os.getcwd())), ')'
db.commit()
db.close()
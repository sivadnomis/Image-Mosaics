import mosaic
import sqlite3

sqlite_file = 'image_library'

db = sqlite3.connect(sqlite_file)
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS tiles(file_name TEXT PRIMARY KEY, RValue INT, GValue INT, BValue, INT, hash INT)")

cursor.execute("SELECT * FROM tiles")
print cursor.fetchall()

db.commit()
db.close()

#resize images
#put rgb/hash data into table
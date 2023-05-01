import sqlite3

# sql = '''
#     SELECT title
#     FROM hacks
#     WHERE id IN (
#         SELECT hack_id
#         FROM hack_authors
#         WHERE author = 'margot'
#     );
# '''

sql = '''
SELECT hacks.title, hack_paths.path, hacks.rating FROM hacks
JOIN hack_paths ON hacks.id = hack_paths.hack_id
JOIN hack_types ON hacks.id = hack_types.hack_id
WHERE hack_types.type LIKE '%Normal%'
AND hacks.rating > 3.9

'''

conn = sqlite3.connect('smwcentral.db')
c = conn.cursor()
c.execute(sql)
# Fetch the results and print them out
results = c.fetchall()
for title, path, rating in results:
    print(f"Title: {title}")
    print(f"Path: {path}")
    print(f"Rating: {rating}")
    print()

c.close()
conn.close()
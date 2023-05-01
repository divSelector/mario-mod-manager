import sqlite3

sql = '''
    SELECT *
    FROM hacks
    WHERE id IN (
        SELECT hack_id
        FROM hack_authors
        WHERE author = 'margot'
    );
'''

conn = sqlite3.connect('smwcentral.db')
c = conn.cursor()
c.execute(sql)
# Fetch the results and print them out
results = c.fetchall()
for row in results:
    print(row)

c.close()
conn.close()
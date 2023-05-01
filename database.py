from pathlib import Path
from typing import List, Optional, Callable, Any
import sqlite3


class SMWCentralDatabase:
    def __init__(self, db_path: str) -> None:
        self.db: Path = Path(db_path)
        if not self.db.exists():
            self.open_database(self.create_tables)
        else:
            print(f"Database Found at {self.db}")

    def open_database(self, action: Callable, action_param: Optional[Any] = None) -> Any:
        print(f"Opening Database Connection at {self.db}")
        with sqlite3.connect(self.db) as conn:
            ret = action(conn) if action_param is None else action(conn, action_param)
        print(f"Closing Database Connection at {self.db}")
        return ret

    def create_tables(self, conn: sqlite3.Connection, **kwargs):
        print(f"Creating TABLE hacks")
        conn.execute('''
        CREATE TABLE hacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            page_url TEXT NOT NULL UNIQUE,
            is_demo TEXT NOT NULL,
            is_featured TEXT NOT NULL,
            exit_count INTEGER NOT NULL,
            rating REAL NOT NULL,
            size REAL NOT NULL,
            size_units TEXT NOT NULL,
            download_url TEXT NOT NULL,
            downloaded_count INTEGER NOT NULL
            );
        ''') 
        print(f"Creating TABLE hack_types")
        conn.execute('''
            CREATE TABLE hack_types (
                hack_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
            );
        ''')
        print(f"Creating TABLE hack_authors")
        conn.execute('''
            CREATE TABLE hack_authors (
                hack_id INTEGER NOT NULL,
                author TEXT NOT NULL,
                FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
            );
        ''')
        print(f"Creating TABLE hack_paths")
        conn.execute('''
            CREATE TABLE hack_paths (
                hack_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
            );
        ''')
        conn.commit()

    def write_records(self, conn: sqlite3.Connection, records: List[dict] = []) -> None:
        print(f"Preparing to write {len(records)} records")
        for record in records:
            prepared_record: tuple = self.prepare_hack_record_for_db(record)
            c = conn.cursor()
            print(f"Inserting record for {record['title']} to hacks")
            c.execute("INSERT INTO hacks (title, page_url, is_demo, is_featured, exit_count, rating, size, size_units, "+\
                        "download_url, downloaded_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", prepared_record)
            hack_id = c.lastrowid

            print(f"Inserting record for {record['title']} to hack_authors")
            for author in record['authors']:
                c.execute("INSERT INTO hack_authors (hack_id, author) VALUES (?, ?)", (hack_id, author))

            print(f"Inserting record for {record['title']} to hack_types")
            for hack_type in record['types']:
                c.execute("INSERT INTO hack_types (hack_id, type) VALUES (?, ?)", (hack_id, hack_type))

            print(f"Inserting record for {record['title']} to hack_paths")
            for hack_path in record['sfc_files']:
                c.execute("INSERT INTO hack_paths (hack_id, path) VALUES (?, ?)", (hack_id, hack_path))
            
            print(f"Committing record for {record['title']}")
            conn.commit()
            print()

    @staticmethod
    def prepare_hack_record_for_db(hack: dict) -> tuple:
        return (
            hack['title'], 
            hack['page_url'], 
            hack['is_demo'], 
            hack['is_featured'], 
            hack['exit_count'], 
            hack['rating'], 
            hack['size']['value'], 
            hack['size']['units'], 
            hack['download_url'], 
            hack['downloaded_count']
        )

    def query_standard_normal_rated_over_3_9(self):
        sql = '''
            SELECT hacks.title, hack_paths.path, hacks.rating FROM hacks
            JOIN hack_paths ON hacks.id = hack_paths.hack_id
            JOIN hack_types ON hacks.id = hack_types.hack_id
            WHERE hack_types.type LIKE '%Normal%'
            AND hacks.rating > 3.9;
        '''
        results = self.open_database(self.query, action_param=sql)
        print(results)

    def query(self, conn: sqlite3.Connection, sql: str):
        c = conn.cursor()
        c.execute(sql)
        return c.fetchall()
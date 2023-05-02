from pathlib import Path
from typing import List, Tuple, Dict
import sqlite3


class SMWCentralDatabase:
    def __init__(self, db_path: str) -> None:
        self.db: Path = Path(db_path)
        if not self.db.exists():
            self.create_tables()
        else:
            print(f"Database Found at {self.db}")

    @staticmethod
    def read(path: str):
        p = Path(path)
        with p.open() as fo:
            sql = fo.read()
        return sql
    
    def create_tables(self, sql_file: str = 'smwc/sql/create_table.sql'):
        sql_queries: List[str] = self.read(sql_file).split(';')
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            for query in sql_queries:
                if query.strip():
                    cursor.execute(query)
            conn.commit()

    @staticmethod
    def prepare_hack_record_for_db(hack: dict) -> tuple:
        return (
            hack['title'],
            hack['created_on'],
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
    
    @staticmethod
    def db_results_to_dict(results: List[Tuple]) -> List[Dict]:
        keys = ['id', 'title', 'created_on', 'page_url', 'is_demo', 'is_featured',
                'exit_count', 'rating', 'size', 'size_units', 'download_url',
                'downloaded_count', 'hack_type', 'path', 'author']
        return [dict(zip(keys, row)) for row in results]

    def write_records(self, records: List[dict]):
        print(f"Preparing to write {len(records)} records")
        with sqlite3.connect(self.db) as conn:
            for record in records:
                print(f"Inserting records for {record['title']}")

                insert_hack_sql: str = self.read('smwc/sql/insert_hack.sql')
                insert_author_sql: str = self.read('smwc/sql/insert_author.sql')
                insert_type_sql: str = self.read('smwc/sql/insert_type.sql')
                insert_path_sql: str = self.read('smwc/sql/insert_path.sql')

                prepared_record: tuple = self.prepare_hack_record_for_db(record)
                
                c = conn.cursor()
                c.execute(insert_hack_sql, prepared_record)
                hack_id = c.lastrowid

                for author in record['authors']:
                    c.execute(insert_author_sql, (hack_id, author))

                for hack_type in record['types']:
                    c.execute(insert_type_sql, (hack_id, hack_type))

                for hack_path in record['sfc_files']:
                    c.execute(insert_path_sql, (hack_id, hack_path))

            conn.commit()

    def select_hacks_by_rating_type(self, sql_file: str, rating_threshold: float, type_substr: str) -> List[dict]:
        sql_query = self.read(sql_file)
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute(sql_query, (f'%{type_substr}%', rating_threshold))
            results = c.fetchall()
            return self.db_results_to_dict(results)
        
    def select_hack_by_id(self, _id: int) -> dict:
        sql_query = self.read('smwc/sql/select_hack_by_id.sql')
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute(sql_query, (_id,))
            results = c.fetchall()
            return self.db_results_to_dict(results)
        
    def select(self, sql_file: str):
        sql_query = self.read(sql_file)
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute(sql_query)
            results = c.fetchall()
            for row in results:
                print(row)
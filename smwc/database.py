from pathlib import Path
from typing import List, Tuple, Dict, Optional
import sqlite3

from .config import RETROARCH_CONFIG_DIR

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
                'downloaded_count', 'hack_type', 'author', 'path']
        structured_results = [dict(zip(keys, row)) for row in results]
        for result in structured_results:
            try:
                result['author'] = result['author'].split(',')
                result['path'] = result['path'].split(',')
                result['hack_type'] = result['hack_type'].split(',')
            except AttributeError as e:
                # This is how you can identify the hacks the need to be removed from the database because the paths don't exist.
                # print(result['title'])
                pass
        return structured_results

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

    def select_hacks_by_rating_type(self, rating_threshold: float, type_substr: str) -> List[dict]:
        sql_query = self.read('smwc/sql/select_hacks_by_rating_type.sql')
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute(sql_query, (f'%{type_substr}%', rating_threshold))
            results = c.fetchall()
            return self.db_results_to_dict(results)
        
    def select_hacks(self, 
            title_substr: str = '',
            type_substr: str = '',
            author_substr: str = '',
            rating_gt: float = -0.1,
            rating_lt: float = 5.1,
            exits_gt: int = 0,
            exits_lt: int = 255,
            downloads_gt: int = -1,
            downloads_lt: int = 99999,
            created_on_gt: str = '1999-08-24',
            created_on_lt: str = '2023-03-24',
            featured: str = '',
            demo: str = '') -> List[dict]:
        sql_query = self.read('smwc/sql/select_hacks.sql')
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            query_params: tuple = (
                f'%{title_substr}%', f'%{type_substr}%', f'%{author_substr}%',
                rating_gt, rating_lt, exits_gt, exits_lt, downloads_gt, downloads_lt,
                created_on_gt, created_on_lt, f'%{featured}%', f'%{demo}%'
            )
            c.execute(sql_query, query_params)
            results = c.fetchall()
            return self.db_results_to_dict(results)
        
    def select_hack_by_id(self, _id: int) -> dict:
        sql_query = self.read('smwc/sql/select_hack_by_id.sql')
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute(sql_query, (_id,))
            results = c.fetchall()
            return self.db_results_to_dict(results)
        
    def select_hack_by_title(self, title: str) -> dict:
        sql_query = self.read('smwc/sql/select_hack_by_title.sql')
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute(sql_query, (title,))
            results = c.fetchall()
            return self.db_results_to_dict(results)
        
    def select_hack_by_path(self, path: str):
        sql_query = self.read('smwc/sql/select_hack_id_from_path.sql')
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute(sql_query, (path,))
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

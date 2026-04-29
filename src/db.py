import sqlite3

from typing import Optional, Type
from pydantic import BaseModel

class SqlWrapper:
    def __init__(self, db_path: str, models: list[Type[BaseModel]]):
        self.db_path = db_path
        self._init_db(models)

    def _map_type(self, py_type) -> str:
        """maps python pydantic types to pure sqlite types"""
        # can unpack union or optional type if args are present
        if hasattr(py_type, "__args__"):
            py_type = py_type.__args__[0]

        mappings = {int: "INTEGER", str: "TEXT", bool: "INTEGER"}

        return mappings.get(py_type, "TEXT")

    def _init_db(self, models: list[Type[BaseModel]]):
        """Init db tables derived from pydantic models"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            for model in models:
                table_name = model.__name__.lower()
                cols = []  # columns

                for field_name, field_info in model.model_fields.items():
                    # check if field is defined by ID explicitly
                    is_pk = "PRIMARY KEY AUTOINCREMENT" if field_name == "id" else ""

                    # extract python type from pydantic field
                    sql_type = self._map_type(field_info.annotation)

                    cols.append(f"{field_name} {sql_type} {is_pk}".strip())

                schema = ", ".join(cols)
                sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
                cursor.execute(sql)

            conn.commit()

    def _get_connection(
        self,
    ):
        conn = sqlite3.connect(self.db_path)
        # Aloows accessing row columns by name
        conn.row_factory = sqlite3.Row
        return conn

    def query(self, sql, params=()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute(self, sql, params=()):
        """EXECUTE INSERT, UPDATE, DELETE queries"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid

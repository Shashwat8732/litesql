"""
Storage/persistent_table_manager.py - Wrapper with auto-save to MongoDB
"""

from .table_manager import TableManager
from .table_storage_mongo import MongoTableStorage
import json
import os

class PersistentTableManager(TableManager):
    def __init__(self, db_path="./Data", pickle_path="./Pickles", user_id=None):
        super().__init__(db_path, pickle_path)
        
        self.user_id = user_id
        self.mongo = MongoTableStorage()
        
        if user_id and self.mongo.client:
            self._load_all_from_mongo()
    
    def _load_all_from_mongo(self):
        """Load all tables from MongoDB on init"""
        print(f"🔄 Loading from MongoDB: {self.user_id}")
        
        tables = self.mongo.get_all_tables(self.user_id)
        
        for table in tables:
            table_file = f"{self.db_path}/{table['name']}.json"
            os.makedirs(self.db_path, exist_ok=True)
            
            with open(table_file, 'w') as f:
                json.dump({"columns": table['columns'], "rows": table['rows']}, f)
            
            print(f"  ✅ {table['name']} ({len(table['rows'])} rows)")
    
    def _sync_to_mongo(self, table_name):
        """Save to MongoDB after change"""
        if not self.user_id or not self.mongo.client:
            return
        
        table_file = f"{self.db_path}/{table_name}.json"
        
        if os.path.exists(table_file):
            with open(table_file, 'r') as f:
                data = json.load(f)
            self.mongo.save_table(self.user_id, table_name, data)
    
    # Override methods to add auto-save
    
    def create_table(self, table_name, columns):
        result = super().create_table(table_name, columns)
        self._sync_to_mongo(table_name)
        return result
    
    def insert_rows(self, table_name, values):
        result = super().insert_rows(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def update_rows(self, table_name, upd_col, upd_value, where_col, op, where_value):
        result = super().update_rows(table_name, upd_col, upd_value, where_col, op, where_value)
        self._sync_to_mongo(table_name)
        return result
    
    def delete_row(self, table_name, col, op, value):
        result = super().delete_row(table_name, col, op, value)
        self._sync_to_mongo(table_name)
        return result
    
    def addmore_col(self, table_name, values):
        result = super().addmore_col(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def delete(self, table_name):
        result = super().delete(table_name)
        if self.user_id and self.mongo.client:
            self.mongo.delete_table(self.user_id, table_name)
        return result
    
    def read_csv(self, table_name, csv_file):
        result = super().read_csv(table_name, csv_file)
        self._sync_to_mongo(table_name)
        return result
    
    def insert_from_excel(self, table_name, excel_file, sheet_name=None):
        result = super().insert_from_excel(table_name, excel_file, sheet_name)
        self._sync_to_mongo(table_name)
        return result
    
    def delete_all_rows(self, table_name):
        result = super().delete_all_rows(table_name)
        self._sync_to_mongo(table_name)
        return result
    
    def delete_all_col(self, table_name):
        result = super().delete_all_col(table_name)
        self._sync_to_mongo(table_name)
        return result

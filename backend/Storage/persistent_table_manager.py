"""
Storage/persistent_table_manager.py - Wrapper with auto-save to MongoDB
Automatically syncs all table operations to MongoDB Atlas
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
        
        if user_id and self.mongo and self.mongo.client:
            self._load_all_from_mongo()
    
    def _load_all_from_mongo(self):
        """Load all tables from MongoDB on init"""
    print(f"🔄 Loading tables from MongoDB for user: {self.user_id}")
    
    if not self.mongo or not self.mongo.client:
        print("⚠️ MongoDB not connected, skipping load")
        return
    
    tables = self.mongo.get_all_tables(self.user_id)
    print(f"📊 Found {len(tables)} tables to load")
    
    for table in tables:
        table_name = table['name']
        print(f"  Loading: {table_name}")
        
        table_file = f"{self.db_path}/{table_name}.json"
        os.makedirs(self.db_path, exist_ok=True)
        
        # Save with proper structure
        table_data = {
            "columns": table.get('columns', {}),
            "rows": table.get('rows', []),
            "indexes": table.get('indexes', {"hashing": [], "b_tree": []})
        }
        
        with open(table_file, 'w') as f:
            json.dump(table_data, f, indent=2)
        
        # Also load indexes
        if table_name not in self.memory_indexes:
            self._load_indexes(table_name)
        
        print(f"  ✅ Loaded: {table_name} ({len(table.get('rows', []))} rows)")
    def _sync_to_mongo(self, table_name):
        """Save to MongoDB after change"""
        if not self.user_id or not self.mongo or not self.mongo.client:
            return
        
        table_file = f"{self.db_path}/{table_name}.json"
        
        if os.path.exists(table_file):
            try:
                with open(table_file, 'r') as f:
                    data = json.load(f)
                self.mongo.save_table(self.user_id, table_name, data)
            except Exception as e:
                print(f"⚠️ MongoDB sync error for {table_name}: {e}")
    
    # Override all modification methods
    
    def create_table(self, table_name, columns):
        """Create table + auto-save"""
        result = super().create_table(table_name, columns)
        self._sync_to_mongo(table_name)
        return result
    
    def insert_rows(self, table_name, values):
        """Insert rows + auto-save"""
       print(f"🔵 PersistentTableManager.insert_rows called")
       print(f"   table: {table_name}")
       print(f"   values: {values}")
       print(f"   user_id: {self.user_id}")
    
       result = super().insert_rows(table_name, values)
    
       print(f"🔵 Parent insert_rows completed, now syncing to MongoDB...")
       self._sync_to_mongo(table_name)
       print(f"🔵 MongoDB sync completed")
    
       return result
       
    def insert_rows_csv(self, table_name, values):
        """Insert from CSV (internal) + auto-save"""
        result = super().insert_rows_csv(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def insert_col(self, table_name, values):
        """Insert columns + auto-save"""
        result = super().insert_col(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def addmore_col(self, table_name, values):
        """Add more columns + auto-save"""
        result = super().addmore_col(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def update_col(self, table_name, col, col_type):
        """Update column type + auto-save"""
        result = super().update_col(table_name, col, col_type)
        self._sync_to_mongo(table_name)
        return result
    
    def update_rows(self, table_name, upd_col, upd_value, where_col, op, where_value):
        """Update rows + auto-save"""
        result = super().update_rows(table_name, upd_col, upd_value, where_col, op, where_value)
        self._sync_to_mongo(table_name)
        return result
    
    def delete_row(self, table_name, col, op, value):
        """Delete rows + auto-save"""
        result = super().delete_row(table_name, col, op, value)
        self._sync_to_mongo(table_name)
        return result
    
    def delete_all_rows(self, table_name):
        """Delete all rows + auto-save"""
        result = super().delete_all_rows(table_name)
        self._sync_to_mongo(table_name)
        return result
    
    def delete_all_col(self, table_name):
        """Delete all columns + auto-save"""
        result = super().delete_all_col(table_name)
        self._sync_to_mongo(table_name)
        return result
    
    def delete(self, table_name):
        """Drop table + delete from MongoDB"""
        result = super().delete(table_name)
        if self.user_id and self.mongo and self.mongo.client:
            self.mongo.delete_table(self.user_id, table_name)
            print(f"🗑️  Deleted from MongoDB: {table_name}")
        return result
    
    def read_csv(self, table_name, csv_file):
        """Read CSV + auto-save"""
        result = super().read_csv(table_name, csv_file)
        self._sync_to_mongo(table_name)
        return result
    
    def insert_from_excel(self, table_name, excel_file, sheet_name=None):
        """Insert from Excel + auto-save"""
        result = super().insert_from_excel(table_name, excel_file, sheet_name)
        self._sync_to_mongo(table_name)
        return result

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
        
        print(f"🔧 PersistentTableManager initialized")
        print(f"   user_id: {user_id}")
        print(f"   mongo connected: {bool(self.mongo and self.mongo.client)}")
        
        if user_id and self.mongo and self.mongo.client:
            self._load_all_from_mongo()
    
    def _load_all_from_mongo(self):
        """Load all tables from MongoDB on init and rebuild indexes"""
        print(f"🔄 Loading tables from MongoDB for user: {self.user_id}")
        
        if not self.mongo or not self.mongo.client:
            print("⚠️ MongoDB not connected")
            return
        
        tables = self.mongo.get_all_tables(self.user_id)
        print(f"📊 Found {len(tables)} tables in MongoDB")
        
        for table in tables:
            table_name = table['name']
            
            table_file = f"{self.db_path}/{table_name}.json"
            os.makedirs(self.db_path, exist_ok=True)
            
            # Get indexes structure and rows
            indexes = table.get('indexes', {"hashing": [], "b_tree": []})
            rows = table.get('rows', [])
            
            # Save table data to JSON file
            table_data = {
                "columns": table.get('columns', {}),
                "rows": rows,
                "indexes": indexes
            }
            
            with open(table_file, 'w') as f:
                json.dump(table_data, f, indent=2)
            
            # IMPORTANT: Initialize indexes and rebuild from rows
            try:
                # Load index structure (creates empty indexes)
                self._load_indexes(table_name)
                
                # Rebuild indexes from existing rows
                if len(rows) > 0:
                    print(f"  🔄 Rebuilding indexes for {table_name} ({len(rows)} rows)...")
                    # Add all rows back to index
                    self._add_to_index(table_name, rows, save_to_disk=True)
                    print(f"  ✅ {table_name} - indexes rebuilt with {len(rows)} rows")
                else:
                    print(f"  ✅ {table_name} - no rows to index")
                    
            except Exception as e:
                print(f"  ⚠️ {table_name} - index rebuild failed: {e}")
                import traceback
                traceback.print_exc()
    
    def _sync_to_mongo(self, table_name):
        """Save to MongoDB after change"""
        if not self.user_id:
            print(f"⚠️ No user_id, skipping MongoDB sync")
            return
        
        if not self.mongo or not self.mongo.client:
            print(f"⚠️ MongoDB not connected, skipping sync")
            return
        
        table_file = f"{self.db_path}/{table_name}.json"
        
        if not os.path.exists(table_file):
            print(f"⚠️ Table file not found: {table_file}")
            return
        
        try:
            with open(table_file, 'r') as f:
                data = json.load(f)
            
            self.mongo.save_table(self.user_id, table_name, data)
            print(f"💾 Saved to MongoDB: {table_name} ({len(data.get('rows', []))} rows)")
        except Exception as e:
            print(f"❌ MongoDB sync error: {e}")
    
    # Override methods
    
    def create_table(self, table_name, columns):
        result = super().create_table(table_name, columns)
        self._sync_to_mongo(table_name)
        return result
    
    def insert_rows(self, table_name, values):
        print(f"🔵 insert_rows called: {table_name}")
        result = super().insert_rows(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def insert_rows_csv(self, table_name, values):
        result = super().insert_rows_csv(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def insert_col(self, table_name, values):
        result = super().insert_col(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def addmore_col(self, table_name, values):
        result = super().addmore_col(table_name, values)
        self._sync_to_mongo(table_name)
        return result
    
    def update_col(self, table_name, col, col_type):
        result = super().update_col(table_name, col, col_type)
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
    
    def delete_all_rows(self, table_name):
        result = super().delete_all_rows(table_name)
        self._sync_to_mongo(table_name)
        return result
    
    def delete_all_col(self, table_name):
        result = super().delete_all_col(table_name)
        self._sync_to_mongo(table_name)
        return result
    
    def delete(self, table_name):
        result = super().delete(table_name)
        if self.user_id and self.mongo and self.mongo.client:
            self.mongo.delete_table(self.user_id, table_name)
        return result
    
    def read_csv(self, table_name, csv_file):
        """Read CSV + auto-save with verification"""
        print(f"🔵 read_csv called: table={table_name}, file={csv_file}")
        
        try:
            # Call parent method
            result = super().read_csv(table_name, csv_file)
            
            print(f"🔵 CSV read completed, checking file...")
            
            # Verify file was updated
            table_file = f"{self.db_path}/{table_name}.json"
            if os.path.exists(table_file):
                with open(table_file, 'r') as f:
                    data = json.load(f)
                print(f"🔵 File has {len(data.get('rows', []))} rows")
            
            # Force sync to MongoDB
            print(f"🔵 Syncing to MongoDB...")
            self._sync_to_mongo(table_name)
            
            print(f"✅ CSV import and MongoDB sync completed")
            return result
            
        except Exception as e:
            print(f"❌ CSV read error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def insert_from_excel(self, table_name, excel_file, sheet_name=None):
        """Insert from Excel + auto-save"""
        print(f"🔵 insert_from_excel called: table={table_name}")
        
        try:
            result = super().insert_from_excel(table_name, excel_file, sheet_name)
            
            print(f"🔵 Excel read completed, syncing to MongoDB...")
            self._sync_to_mongo(table_name)
            
            print(f"✅ Excel import and MongoDB sync completed")
            return result
            
        except Exception as e:
            print(f"❌ Excel read error: {e}")
            import traceback
            traceback.print_exc()
            raise

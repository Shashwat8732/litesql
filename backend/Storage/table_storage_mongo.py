import os
from pymongo import MongoClient
from datetime import datetime

class MongoTableStorage:
    def __init__(self):
        mongo_url = os.environ.get('MONGO_URL', '')
        
        if not mongo_url:
            print("❌ MONGO_URL not set!")
            self.client = None
            return
        
        try:
            self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            self.db = self.client['litesql']
            self.tables_col = self.db['user_tables']
            
            self.tables_col.create_index([("user_id", 1), ("table_name", 1)], unique=True)
            
            print("✅ MongoDB table storage ready!")
        except Exception as e:
            print(f"❌ MongoDB table storage failed: {e}")
            self.client = None
    
    def save_table(self, user_id, table_name, table_data):
        """Save table to MongoDB with indexes"""
        if not self.client:
            return False
        
        try:
            self.tables_col.update_one(
                {"user_id": user_id, "table_name": table_name},
                {"$set": {
                    "user_id": user_id,
                    "table_name": table_name,
                    "columns": table_data.get("columns", {}),
                    "rows": table_data.get("rows", []),
                    "indexes": table_data.get("indexes", {"hashing": [], "b_tree": []}),
                    "updated_at": datetime.now().isoformat()
                }},
                upsert=True
            )
            print(f"💾 Saved to MongoDB: {table_name}")
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def load_table(self, user_id, table_name):
        """Load table from MongoDB with indexes"""
        if not self.client:
            return None
        
        try:
            result = self.tables_col.find_one({
                "user_id": user_id,
                "table_name": table_name
            })
            
            if result:
                return {
                    "columns": result.get("columns", {}),
                    "rows": result.get("rows", []),
                    "indexes": result.get("indexes", {"hashing": [], "b_tree": []})
                }
            return None
        except Exception as e:
            print(f"❌ Load error: {e}")
            return None
    
    def get_all_tables(self, user_id):
        """Get all tables for user with indexes"""
        if not self.client:
            return []
        
        try:
            tables = list(self.tables_col.find(
                {"user_id": user_id},
                {"_id": 0, "table_name": 1, "columns": 1, "rows": 1, "indexes": 1}
            ))
            
            return [{
                "name": t.get("table_name"),
                "columns": t.get("columns", {}),
                "rows": t.get("rows", []),
                "indexes": t.get("indexes", {"hashing": [], "b_tree": []})
            } for t in tables]
        except Exception as e:
            print(f"❌ Get tables error: {e}")
            return []
    
    def delete_table(self, user_id, table_name):
        """Delete table from MongoDB"""
        if not self.client:
            return False
        
        try:
            result = self.tables_col.delete_one({
                "user_id": user_id,
                "table_name": table_name
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ Delete error: {e}")
            return False

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from pymongo import MongoClient

class AuthManager:
    def __init__(self):
        mongo_url = os.environ.get('MONGO_URL', '')
        
        if not mongo_url:
            print("❌ MONGO_URL not set!")
            self.client = None
            return
        
        try:
            self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            self.db = self.client['litesql']
            self.users_col = self.db['users']
            self.sessions_col = self.db['sessions']
            
            self.client.server_info()
            print("✅ MongoDB connected - Auth ready!")
            
            self.users_col.create_index("username", unique=True)
            self.sessions_col.create_index("token", unique=True)
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self):
        return secrets.token_urlsafe(32)
    
    def register(self, username, password, email=None):
        if not self.client:
            return {"success": False, "error": "Database not connected"}
        
        try:
            if len(username) < 3:
                return {"success": False, "error": "Username must be at least 3 characters"}
            
            if len(password) < 6:
                return {"success": False, "error": "Password must be at least 6 characters"}
            
            if self.users_col.find_one({"username": username}):
                return {"success": False, "error": "Username already exists"}
            
            user_count = self.users_col.count_documents({})
            user_id = f"user_{user_count + 1}"
            
            self.users_col.insert_one({
                "username": username,
                "user_id": user_id,
                "password_hash": self.hash_password(password),
                "email": email,
                "created_at": datetime.now().isoformat()
            })
            
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.makedirs(os.path.join(BASE_DIR, "Data", user_id), exist_ok=True)
            os.makedirs(os.path.join(BASE_DIR, "Pickles", user_id), exist_ok=True)
            
            print(f"✅ Registered: {username} ({user_id})")
            return {"success": True, "message": "User registered successfully", "user_id": user_id}
            
        except Exception as e:
            print(f"❌ Register error: {e}")
            return {"success": False, "error": "Registration failed"}
    
    def login(self, username, password):
        if not self.client:
            return {"success": False, "error": "Database not connected"}
        
        try:
            user = self.users_col.find_one({"username": username})
            
            if not user:
                return {"success": False, "error": "Invalid username or password"}
            
            if user["password_hash"] != self.hash_password(password):
                return {"success": False, "error": "Invalid username or password"}
            
            session_token = self.generate_session_token()
            
            self.sessions_col.insert_one({
                "token": session_token,
                "user_id": user["user_id"],
                "username": username,
                "expires_at": (datetime.now() + timedelta(days=365)).isoformat(),
                "created_at": datetime.now().isoformat()
            })
            
            print(f"✅ Login: {username}")
            return {
                "success": True,
                "message": "Login successful",
                "session_token": session_token,
                "user_id": user["user_id"],
                "username": username
            }
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return {"success": False, "error": "Login failed"}
    
    def logout(self, session_token):
        if not self.client:
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.sessions_col.delete_one({"token": session_token})
            
            if result.deleted_count > 0:
                print(f"✅ Logout successful")
                return {"success": True, "message": "Logged out"}
            
            return {"success": False, "error": "Invalid session"}
            
        except Exception as e:
            print(f"❌ Logout error: {e}")
            return {"success": False, "error": "Logout failed"}
    
    def verify_session(self, session_token):
        if not self.client or not session_token:
            return None
        
        try:
            session = self.sessions_col.find_one({"token": session_token})
            
            if not session:
                return None
            
            try:
                expires_at = datetime.fromisoformat(session["expires_at"])
                if datetime.now() > expires_at:
                    # Delete expired session
                    self.sessions_col.delete_one({"token": session_token})
                    return None
            except:
                pass
            
            return {
                "user_id": session["user_id"],
                "username": session["username"]
            }
            
        except Exception as e:
            print(f"❌ Session verify error: {e}")
            return None

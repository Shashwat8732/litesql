import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, users_file="./Data/users.json"):
        self.users_file = users_file
        self.sessions = {}
        
        if not os.path.exists(users_file):
            os.makedirs(os.path.dirname(users_file), exist_ok=True)
            with open(users_file, 'w') as f:
                json.dump({"users": {}}, f)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self):
        return secrets.token_urlsafe(32)
    
    def register(self, username, password, email=None):
        try:
          with open(self.users_file, 'r') as f:
            data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
         data = {"users": {}}
    
        users = data.get("users", {})
    
        if username in users:
         return {"success": False, "error": "Username already exists"}
    
        if len(username) < 3:
          return {"success": False, "error": "Username must be at least 3 characters"}
    
        if len(password) < 6:
          return {"success": False, "error": "Password must be at least 6 characters"}
    
        user_id = f"user_{len(users) + 1}"
        password_hash = self.hash_password(password)
    
        print(f"\n{'='*60}")
        print(f"📝 REGISTER:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Password Hash: {password_hash[:30]}...")
        print(f"   User ID: {user_id}")
    
        users[username] = {
        "user_id": user_id,
        "password_hash": password_hash,
        "email": email,
        "created_at": datetime.now().isoformat(),
    }
    
        data["users"] = users  # ✅ CRITICAL!
    
        os.makedirs(f"./Data/{user_id}", exist_ok=True)
        os.makedirs(f"./Pickles/{user_id}", exist_ok=True)
    
    # ✅ WRITE with flush
        with open(self.users_file, 'w') as f:
         json.dump(data, f, indent=2)
         f.flush()  # ✅ Force write
         os.fsync(f.fileno())  # ✅ Ensure disk write
    
    # ✅ VERIFY WRITE
        with open(self.users_file, 'r') as f:
         verify_data = json.load(f)
        print(f"   ✅ Verified users in file: {list(verify_data.get('users', {}).keys())}")
    
        print(f"{'='*60}\n")
    
        return {"success": True, "message": "User registered successfully", "user_id": user_id}

    
    def login(self, username, password):
        with open(self.users_file, 'r') as f:
            data = json.load(f)
        
        users = data.get("users", {})
        
        # ✅ DEBUG: Check if user exists
        print(f"\n{'='*60}")
        print(f"🔐 LOGIN ATTEMPT:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   User exists: {username in users}")
        
        if username not in users:
            print(f"   ❌ User not found!")
            print(f"   Available users: {list(users.keys())}")
            print(f"{'='*60}\n")
            return {"success": False, "error": "Invalid username or password"}
        
        user = users[username]
        
        # ✅ DEBUG: Compare password hashes
        input_hash = self.hash_password(password)
        stored_hash = user["password_hash"]
        
        print(f"   Input Hash:  {input_hash[:30]}...")
        print(f"   Stored Hash: {stored_hash[:30]}...")
        print(f"   Match: {input_hash == stored_hash}")
        
        if stored_hash != input_hash:
            print(f"   ❌ Password mismatch!")
            print(f"{'='*60}\n")
            return {"success": False, "error": "Invalid username or password"}
        
        print(f"   ✅ Login successful!")
        print(f"{'='*60}\n")
        
        session_token = self.generate_session_token()
        self.sessions[session_token] = {
            "user_id": user["user_id"],
            "username": username,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        return {
            "success": True,
            "message": "Login successful",
            "session_token": session_token,
            "user_id": user["user_id"],
            "username": username
        }
    
    def logout(self, session_token):
        if session_token in self.sessions:
            del self.sessions[session_token]
            return {"success": True, "message": "Logged out"}
        return {"success": False, "error": "Invalid session"}
    
    def verify_session(self, session_token):
        if not session_token or session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            del self.sessions[session_token]
            return None
        
        return session
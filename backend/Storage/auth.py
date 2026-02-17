import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta

# ✅ Absolute path - same folder jahan auth.py hai
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data")

class AuthManager:
    def __init__(self, users_file=None):
        # ✅ Always use absolute path
        if users_file is None:
            users_file = os.path.join(DATA_DIR, "users.json")
        
        self.users_file = users_file
        self.sessions_file = os.path.join(os.path.dirname(users_file), "sessions.json")
        self.sessions = {}
        
        print(f"📁 Users file: {self.users_file}")
        print(f"📁 Sessions file: {self.sessions_file}")
        
        # ✅ Create folders
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        
        # ✅ Create users file if not exists
        if not os.path.exists(users_file):
            with open(users_file, 'w') as f:
                json.dump({"users": {}}, f)
        
        # ✅ Load sessions from file
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
                print(f"✅ Loaded {len(self.sessions)} sessions")
            except:
                self.sessions = {}
        
        # ✅ Clean expired sessions
        self._clean_expired()
    
    def _clean_expired(self):
        now = datetime.now()
        expired = [
            token for token, s in self.sessions.items()
            if datetime.fromisoformat(s["expires_at"]) < now
        ]
        for token in expired:
            del self.sessions[token]
        if expired:
            self._save_sessions()
            print(f"🧹 Removed {len(expired)} expired sessions")
    
    def _save_sessions(self):
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            print(f"❌ Session save error: {e}")
    
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
        
        users[username] = {
            "user_id": user_id,
            "password_hash": self.hash_password(password),
            "email": email,
            "created_at": datetime.now().isoformat(),
        }
        data["users"] = users
        
        # ✅ Create user folders with absolute path
        os.makedirs(os.path.join(DATA_DIR, user_id), exist_ok=True)
        os.makedirs(os.path.join(BASE_DIR, "Pickles", user_id), exist_ok=True)
        
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        return {"success": True, "message": "User registered successfully", "user_id": user_id}
    
    def login(self, username, password):
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
        except:
            return {"success": False, "error": "Server error"}
        
        users = data.get("users", {})
        
        if username not in users:
            return {"success": False, "error": "Invalid username or password"}
        
        user = users[username]
        
        if user["password_hash"] != self.hash_password(password):
            return {"success": False, "error": "Invalid username or password"}
        
        session_token = self.generate_session_token()
        self.sessions[session_token] = {
            "user_id": user["user_id"],
            "username": username,
            "expires_at": (datetime.now() + timedelta(days=36500)).isoformat()
        }
        
        # ✅ Save immediately
        self._save_sessions()
        
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
            self._save_sessions()
            return {"success": True, "message": "Logged out"}
        return {"success": False, "error": "Invalid session"}
    
    def verify_session(self, session_token):
        if not session_token or session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        try:
            expires_at = datetime.fromisoformat(session["expires_at"])
        except:
            return None
        
        if datetime.now() > expires_at:
            del self.sessions[session_token]
            self._save_sessions()
            return None
        
        return session



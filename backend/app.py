from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os
import json
from werkzeug.utils import secure_filename

from Storage.auth_mongo import AuthManager

auth = AuthManager()
app = Flask(__name__)

# ✅ FIXED CORS Configuration
CORS(app, 
     resources={r"/api/*": {"origins": [
            "http://localhost:3000",
            "https://litesql.vercel.app", 
            "https://*.vercel.app"  ]}},
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

print("\n" + "="*70)
print("🚀 LiteSQL Bridge - With Authentication")
print("="*70)

# Import from main.py
try:
    from main import run_sql_for_user, pr
    from Storage.persistent_table_manager import PersistentTableManager as TableManager
    print("✅ Imported from main.py")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

print("✅ Backend ready!")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_session_token():
    """Get session token from header"""
    return request.headers.get('Authorization')


def require_auth(f):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        session_token = get_session_token()
        session = auth.verify_session(session_token)
        
        if not session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        kwargs['session'] = session
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper


def get_tables_list(user_id):
    """Get user's tables from MongoDB"""
    try:
        from Storage.table_storage_mongo import MongoTableStorage
        mongo_storage = MongoTableStorage()
        
        print(f"🔍 Getting tables for user: {user_id}")
        
        if mongo_storage.client:
            tables = mongo_storage.get_all_tables(user_id)
            print(f"📊 MongoDB returned {len(tables)} tables")
            
            result = []
            for t in tables:
                table_info = {
                    'name': t['name'],
                    'columns': len(t.get('columns', {})),
                    'rows': len(t.get('rows', [])),
                    'icon': '📊'
                }
                print(f"  - {table_info}")
                result.append(table_info)
            
            return result
        
        print("⚠️ MongoDB not connected, checking local files")
        
        # Fallback to local
        data_path = f"./Data/{user_id}"
        if not os.path.exists(data_path):
            print(f"⚠️ No data path: {data_path}")
            return []
        
        tables = []
        for file in os.listdir(data_path):
            if file.endswith('.json'):
                table_name = file.replace('.json', '')
                try:
                    with open(f"{data_path}/{file}", 'r') as f:
                        data = json.load(f)
                    
                    tables.append({
                        'name': table_name,
                        'columns': len(data.get('columns', {})),
                        'rows': len(data.get('rows', [])),
                        'icon': '📊'
                    })
                except Exception as e:
                    print(f"⚠️ Error reading {file}: {e}")
        
        return tables
        
    except Exception as e:
        print(f"❌ Error in get_tables_list: {e}")
        import traceback
        traceback.print_exc()
        return []

# ============================================
# AUTH ENDPOINTS
# ============================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password required'}), 400
    
    result = auth.register(username, password, email)
    return jsonify(result)


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password required'}), 400
    
    result = auth.login(username, password)
    return jsonify(result)


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session_token = get_session_token()
    result = auth.logout(session_token)
    return jsonify(result)


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user(session):
    """Get current user info"""
    return jsonify({
        'success': True,
        'user': {
            'user_id': session['user_id'],
            'username': session['username']
        }
    })


# ============================================
# PROTECTED ENDPOINTS
# ============================================

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'name': '🗄️⚡ LiteSQL',
        'status': 'running',
        'message': 'LiteSQL API is live!',
        'endpoints': {
            'health': '/api/query/health',
            'tables': '/api/query/tables',
            'query': '/api/query',
            'upload': '/api/upload',
            'register': '/api/auth/register',
            'login': '/api/auth/login'
        }
    })



@app.route('/api/query/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'LiteSQL Bridge with Auth running',
        'features': ['SQL queries', 'File upload', 'Tables list', 'Authentication']
    })


@app.route('/api/query/tables', methods=['GET'])
@require_auth
def tables(session):
    """Get user's tables"""
    try:
        user_id = session['user_id']
        tables_list = get_tables_list(user_id)
        return jsonify({
            'success': True,
            'tables': tables_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_file(session):
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        table_name = request.form.get('table', '').strip()
        sheet_name = request.form.get('sheet', '').strip()
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not table_name:
            return jsonify({'success': False, 'error': 'Table name is required'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        user_id = session['user_id']
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{user_id}_{filename}")
        file.save(filepath)
        
        # ✅ Check if table exists BEFORE processing
        table_file = f"./Data/{user_id}/{table_name}.json"
        if not os.path.exists(table_file):
            os.remove(filepath)
            return jsonify({
                'success': False,
                'error': f"Table '{table_name}' does not exist! Create it first:\nCREATE TABLE {table_name} (col1 TYPE, col2 TYPE, ...)"
            }), 400
        
        print(f"\n{'='*60}")
        print(f"👤 User: {session['username']}")
        print(f"📁 File: {filename}")
        print(f"📊 Table: {table_name}")
        
        start = time.time()
        
        user_tm = TableManager(
            db_path=f"./Data/{user_id}",
            pickle_path=f"./Pickles/{user_id}",
            user_id=user_id
        )
        
        if filename.endswith('.csv'):
            print(f"📝 Processing CSV...")
            count = user_tm.read_csv(table_name, filepath)
            exec_time = round((time.time() - start) * 1000, 2)
            os.remove(filepath)
            
            print(f"✅ Imported {count} rows in {exec_time}ms")
            print(f"{'='*60}\n")
            
            return jsonify({
                'success': True,
                'message': f'Imported {count} rows from CSV',
                'table': table_name,
                'rows': count,
                'executionTime': exec_time
            })
        
        elif filename.endswith(('.xlsx', '.xls')):
            print(f"📊 Processing Excel...")
            sheet = sheet_name if sheet_name else None
            user_tm.insert_from_excel(table_name, filepath, sheet)
            exec_time = round((time.time() - start) * 1000, 2)
            os.remove(filepath)
            
            print(f"✅ Imported data in {exec_time}ms")
            print(f"{'='*60}\n")
            
            return jsonify({
                'success': True,
                'message': f'Imported data from Excel',
                'table': table_name,
                'sheet': sheet_name,
                'executionTime': exec_time
            })
        
        else:
            os.remove(filepath)
            return jsonify({'success': False, 'error': 'Unsupported file type'}), 400
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
@require_auth
def query(session):
    """Execute SQL for user"""
    try:
        data = request.json
        sql = data.get('sql', '').strip()
        
        if not sql:
            return jsonify({'success': False, 'error': 'No SQL provided'}), 400
        
        user_id = session['user_id']
        
        print(f"\n{'='*60}")
        print(f"👤 User: {session['username']}")
        print(f"📥 SQL: {sql}")
        print(f"{'='*60}")
        
        start = time.time()
        result_data, cmd_type = run_sql_for_user(sql, user_id)
        exec_time = round((time.time() - start) * 1000, 2)
        
        print(f"✅ Done in {exec_time}ms")
        
        # Type handling
        if isinstance(result_data, list) and len(result_data) > 0:
            print(f"   Rows: {len(result_data)}")
            column_names = list(result_data[0].keys())
            print(f"{'='*60}\n")
            return jsonify({
                'success': True,
                'columns': column_names,
                'data': result_data,
                'executionTime': exec_time
            })
        
        elif isinstance(result_data, list) and len(result_data) == 0:
            print(f"   No data")
            print(f"{'='*60}\n")
            return jsonify({
                'success': True,
                'data': [],
                'message': 'No data found',
                'executionTime': exec_time
            })
        
        elif isinstance(result_data, int):
            print(f"   Affected: {result_data} rows")
            print(f"{'='*60}\n")
            return jsonify({
                'success': True,
                'message': f'{result_data} row(s) affected',
                'executionTime': exec_time
            })
        
        elif isinstance(result_data, dict):
            print(f"   Data type: dict")
            print(f"   Keys: {list(result_data.keys())}")
            print(f"{'='*60}\n")
            return jsonify({
                'success': True,
                'data': result_data,
                'executionTime': exec_time
            })
        
        else:
            print(f"{'='*60}\n")
            return jsonify({
                'success': True,
                'message': f'{cmd_type} operation completed',
                'executionTime': exec_time
            })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print()
    print("="*70)
    print("✓ Server: http://localhost:5001")
    print("="*70)
    print()
    print("📋 Available Endpoints:")
    print("   POST /api/auth/register  → Register user")
    print("   POST /api/auth/login     → Login user")
    print("   POST /api/auth/logout    → Logout user")
    print("   GET  /api/auth/me        → Current user")
    print("   GET  /api/query/health   → Health check")
    print("   GET  /api/query/tables   → List tables (auth required)")
    print("   POST /api/query          → Execute SQL (auth required)")
    print("   POST /api/upload         → Upload file (auth required)")
    print()
    print("💡 Features:")
    print("   ✅ User authentication")
    print("   ✅ User-specific databases")
    print("   ✅ Session management")
    print("   ✅ File upload support")
    print()
    print()
    print("Ctrl+C to stop")
    print("="*70)
    print()
    
app.run(host='0.0.0.0', port=10000, debug=False)



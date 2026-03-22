# app.py - ملف رئيسي للخادم
import os
import sys

# إضافة المسار الحالي إلى sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📁 Files: {os.listdir('.')}")
    app.run(host='0.0.0.0', port=port, debug=False)
# app.py
import os
import sys

print("=" * 50)
print("Starting Family OS...")
print("=" * 50)
print(f"Current directory: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# التحقق من وجود مجلد backend
if os.path.exists('backend'):
    print("✅ backend folder exists")
    print(f"Files in backend: {os.listdir('backend')}")
else:
    print("❌ backend folder NOT found!")

try:
    # محاولة استيراد
    print("Importing from backend...")
    from backend import create_app
    print("✅ Import successful!")
    
    app = create_app()
    print("✅ App created!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    # في حالة الفشل، أنشئ تطبيق بسيط للاختبار
    print("\nCreating minimal app for testing...")
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "<h1>Family OS - Testing Mode</h1><p>Backend import failed. Please check logs.</p>"
    
    @app.route('/api/test')
    def test():
        return {"success": True, "message": "Test endpoint working"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
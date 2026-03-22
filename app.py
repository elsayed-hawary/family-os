# app.py - الملف الرئيسي لتشغيل التطبيق على Render
import os
import sys
import logging

# طباعة معلومات التصحيح
print("=" * 60)
print("🚀 Starting Family OS Application")
print("=" * 60)
print(f"📁 Current working directory: {os.getcwd()}")
print(f"📁 Files in current directory: {os.listdir('.')}")

# التحقق من وجود مجلد backend
if os.path.exists('backend'):
    print("✅ backend folder exists")
    print(f"📁 Files in backend: {os.listdir('backend')}")
else:
    print("❌ backend folder NOT found!")
    sys.exit(1)

# التحقق من وجود مجلد frontend
if os.path.exists('frontend'):
    print("✅ frontend folder exists")
    print(f"📁 Files in frontend: {os.listdir('frontend')}")
else:
    print("❌ frontend folder NOT found!")

# إضافة المسار الحالي إلى sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print(f"📁 Python path: {sys.path[:3]}...")

try:
    # محاولة استيراد التطبيق
    print("🔄 Importing backend module...")
    import backend
    print(f"✅ backend imported: {backend}")
    print(f"📁 backend location: {backend.__file__}")
    
    print("🔄 Importing create_app from backend...")
    from backend import create_app
    print("✅ create_app imported successfully")
    
    # إنشاء التطبيق
    print("🔄 Creating app instance...")
    app = create_app()
    print("✅ Application created successfully")
    
except ImportError as e:
    print(f"❌ ImportError: {e}")
    print("📁 Checking backend/__init__.py exists...")
    if os.path.exists('backend/__init__.py'):
        print("✅ backend/__init__.py exists")
        with open('backend/__init__.py', 'r') as f:
            print("📁 First 10 lines of backend/__init__.py:")
            for i, line in enumerate(f.readlines()[:10]):
                print(f"   {i+1}: {line.strip()}")
    else:
        print("❌ backend/__init__.py does NOT exist!")
    raise
    
except Exception as e:
    print(f"❌ Failed to create application: {e}")
    import traceback
    traceback.print_exc()
    raise

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🔌 Starting server on port {port}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
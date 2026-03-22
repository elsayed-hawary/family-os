# app.py - الملف الرئيسي لتشغيل التطبيق على Render
import os
import sys
import logging

# إضافة المسار الحالي إلى sys.path لضمان استيراد الوحدات بشكل صحيح
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# تكوين التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

try:
    # استيراد التطبيق من مجلد backend
    from backend import create_app
    
    # إنشاء التطبيق
    app = create_app()
    
    logger.info("✅ Application created successfully")
    
except Exception as e:
    logger.error(f"❌ Failed to create application: {e}")
    raise

# نقطة الدخول الرئيسية للتطبيق
if __name__ == '__main__':
    # الحصول على رقم المنفذ من متغيرات البيئة
    port = int(os.environ.get('PORT', 5000))
    
    # طباعة معلومات التشغيل
    print("=" * 50)
    print("🚀 Starting Family OS Application")
    print("=" * 50)
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📁 Files in directory: {os.listdir('.')}")
    print(f"🔌 Port: {port}")
    print(f"🌐 Host: 0.0.0.0")
    print("=" * 50)
    
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=port, debug=False)
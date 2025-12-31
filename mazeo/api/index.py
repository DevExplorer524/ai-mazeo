import sys
import os

# إضافة المجلد الرئيسي للمسارات لكي يستطيع العثور على mazeo.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mazeo import app

# Vercel looks for 'app' or 'handler'
handler = app
app = app

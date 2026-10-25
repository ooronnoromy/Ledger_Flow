"""Render the real account-menu component with sample data for the preview."""
import os
import re
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.template.loader import render_to_string

request = SimpleNamespace(user=SimpleNamespace(first_name='Tanvir Ahmed', username='tanvir', email='', is_staff=True, is_superuser=True))
menu = render_to_string('includes/account_menu.html', {'request':request,'app_lang':'en','account_role':'Superuser','is_driver':False,'csrf_token':'preview-only'})
path = ROOT / 'design_preview.html'
source = path.read_text(encoding='utf-8')
if '<!-- account-menu:start -->' in source:
    source = re.sub(r'<!-- account-menu:start -->.*?<!-- account-menu:end -->', lambda _: '<!-- account-menu:start -->'+menu+'<!-- account-menu:end -->', source, flags=re.S)
else:
    source, count = re.subn(r'<a class="user-quick">.*?</a>', lambda _: '<!-- account-menu:start -->'+menu+'<!-- account-menu:end -->', source, count=1)
    if count != 1: raise RuntimeError('Preview account trigger not found')
if 'static/css/account.css' not in source:
    source = source.replace('</head>', '<link rel="stylesheet" href="static/css/account.css"></head>')
if 'static/js/account.js' not in source:
    source = source.replace('</body>', '<script src="static/js/account.js"></script></body>')
path.write_text(source, encoding='utf-8')

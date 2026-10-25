from django.utils import timezone

TRANSLATIONS = {
'en': {
    'dashboard': 'Dashboard', 'overview': 'Your car expenses, all in one place', 'my_cars': 'My Cars',
    'fuel_records': 'Fuel Records', 'maintenance': 'Maintenance', 'expenses': 'All Expenses',
    'trip_cost': 'Trip Costs', 'drivers': 'Drivers', 'documents': 'Receipts', 'reports': 'Reports', 'reminders': 'Reminders',
    'settings': 'Settings', 'download_app': 'Install App', 'logout': 'Log out', 'login': 'Log in',
    'search': 'Search expenses, places, vehicles...', 'this_month': 'This month', 'total_cost': 'Total Cost',
    'fuel_cost': 'Fuel Cost', 'maintenance_cost': 'Maintenance', 'other_cost': 'Other Costs',
    'monthly_trend': 'Monthly Spending Trend', 'fuel_breakdown': 'Fuel Type Breakdown',
    'vehicle_spending': 'Spending by Car', 'recent_activity': 'Recent Activities',
    'upcoming': 'Upcoming Reminders', 'view_all': 'View all', 'my_vehicle': 'My Vehicles',
    'add_expense': 'Add Expense', 'add_vehicle': 'Add Vehicle', 'add_reminder': 'Add Reminder',
    'add_fuel': 'Add Fuel Record', 'save': 'Save Record', 'cancel': 'Cancel', 'date': 'Date',
    'vehicle': 'Vehicle', 'amount': 'Amount (৳)', 'category': 'Category', 'description': 'Description',
    'fuel_type': 'Fuel Type', 'quantity': 'Quantity (litres / units)', 'odometer': 'Odometer (km)',
    'location': 'Station / Location', 'notes': 'Notes', 'receipt': 'Receipt Photo',
    'meter_photo': 'Fuel Pump Meter Photo', 'upload_hint': 'JPG, PNG or WebP, up to 8 MB',
    'actions': 'Actions', 'edit': 'Edit', 'delete': 'Delete', 'confirm_delete': 'Delete this item?',
    'all': 'All', 'filter': 'Apply Filter', 'clear': 'Clear', 'name': 'Name', 'plate': 'Registration Plate',
    'brand': 'Brand', 'year': 'Model Year', 'colour': 'Colour', 'photo': 'Car Photo',
    'due_date': 'Due Date', 'due_km': 'Due at (km)', 'status': 'Status', 'mark_done': 'Mark done',
    'reopen': 'Reopen', 'active': 'Upcoming', 'completed': 'Completed', 'no_records': 'No records found',
    'no_cars': 'Add your first car to get started.', 'download_csv': 'Export CSV',
    'all_time': 'All time', 'yearly': 'Last 12 months', 'expenses_by_category': 'Expenses by Category',
    'settings_title': 'My Profile & Preferences', 'language': 'Language', 'profile': 'Profile',
    'display_name': 'Display Name', 'email': 'Email', 'save_changes': 'Save Changes',
    'get_app': 'Install AutoLedger BD', 'install_now': 'Install App Now',
    'pwa_help': 'Install on Android, iPhone, tablet, or laptop from your browser.',
    'offline_note': 'The installed app opens like a native app. A network connection is needed to save or sync data.',
    'welcome': 'Welcome back', 'new_vehicle': 'Add a car', 'new_expense': 'New expense',
    'powered': 'Designed & signed by', 'total_vehicles': 'My Car Collection',
    'currency': 'Bangladeshi Taka (BDT)', 'quantity_help': 'Litres for liquid fuels, station units for CNG',
    'all_cars': 'All Vehicles', 'record_details': 'Record Details',
},
'bn': {
    'dashboard': 'ড্যাশবোর্ড', 'overview': 'আপনার গাড়ির সকল খরচ এক জায়গায়', 'my_cars': 'আমার গাড়ি',
    'fuel_records': 'জ্বালানি রেকর্ড', 'maintenance': 'মেইনটেন্যান্স', 'expenses': 'সকল খরচ',
    'trip_cost': 'যাতায়াত খরচ', 'drivers': 'ড্রাইভার', 'documents': 'রসিদ ও ছবি', 'reports': 'রিপোর্ট', 'reminders': 'রিমাইন্ডার',
    'settings': 'সেটিংস', 'download_app': 'অ্যাপ ইনস্টল', 'logout': 'লগ আউট', 'login': 'লগ ইন',
    'search': 'খরচ, স্থান অথবা গাড়ি খুঁজুন...', 'this_month': 'এই মাসে', 'total_cost': 'মোট খরচ',
    'fuel_cost': 'জ্বালানি খরচ', 'maintenance_cost': 'মেইনটেন্যান্স', 'other_cost': 'অন্যান্য খরচ',
    'monthly_trend': 'মাসিক খরচের প্রবণতা', 'fuel_breakdown': 'জ্বালানি খরচ (ধরন অনুযায়ী)',
    'vehicle_spending': 'গাড়ি ভিত্তিক খরচ', 'recent_activity': 'সাম্প্রতিক লেনদেন',
    'upcoming': 'রিমাইন্ডার', 'view_all': 'সব দেখুন', 'my_vehicle': 'আমার গাড়ি',
    'add_expense': 'খরচ যোগ করুন', 'add_vehicle': 'গাড়ি যোগ করুন', 'add_reminder': 'রিমাইন্ডার যোগ করুন',
    'add_fuel': 'জ্বালানি রেকর্ড যোগ করুন', 'save': 'সংরক্ষণ করুন', 'cancel': 'বাতিল', 'date': 'তারিখ',
    'vehicle': 'গাড়ি', 'amount': 'খরচ (৳)', 'category': 'খরচের ধরন', 'description': 'বিবরণ',
    'fuel_type': 'জ্বালানির ধরন', 'quantity': 'পরিমাণ (লিটার / ইউনিট)', 'odometer': 'মিটার রিডিং (কিমি)',
    'location': 'পাম্প / অবস্থান', 'notes': 'মন্তব্য', 'receipt': 'বিল / রসিদের ছবি',
    'meter_photo': 'ফুয়েল মিটারের ছবি', 'upload_hint': 'JPG, PNG বা WebP, সর্বোচ্চ ৮ MB',
    'actions': 'কার্যক্রম', 'edit': 'সম্পাদনা', 'delete': 'মুছুন', 'confirm_delete': 'রেকর্ডটি মুছে ফেলবেন?',
    'all': 'সব', 'filter': 'ফিল্টার করুন', 'clear': 'রিসেট', 'name': 'গাড়ির নাম', 'plate': 'রেজিস্ট্রেশন নম্বর',
    'brand': 'ব্র্যান্ড', 'year': 'মডেল ইয়ার', 'colour': 'রং', 'photo': 'গাড়ির ছবি',
    'due_date': 'শেষ তারিখ', 'due_km': 'পরবর্তী কিমি', 'status': 'অবস্থা', 'mark_done': 'সম্পন্ন করুন',
    'reopen': 'পুনরায় চালু', 'active': 'আসন্ন', 'completed': 'সম্পন্ন', 'no_records': 'কোনো রেকর্ড পাওয়া যায়নি',
    'no_cars': 'শুরু করতে প্রথম গাড়িটি যোগ করুন।', 'download_csv': 'CSV ডাউনলোড',
    'all_time': 'সব সময়', 'yearly': 'শেষ ১২ মাস', 'expenses_by_category': 'খরচের বিবরণ',
    'settings_title': 'প্রোফাইল ও পছন্দ', 'language': 'ভাষা', 'profile': 'প্রোফাইল',
    'display_name': 'প্রদর্শিত নাম', 'email': 'ইমেইল', 'save_changes': 'সংরক্ষণ করুন',
    'get_app': 'AutoLedger BD ইনস্টল করুন', 'install_now': 'অ্যাপ ইনস্টল করুন',
    'pwa_help': 'অ্যান্ড্রয়েড, আইফোন, ট্যাবলেট ও ল্যাপটপে ব্রাউজার থেকে ইনস্টল করুন।',
    'offline_note': 'ইনস্টলের পর অ্যাপের মতো খুলবে। তথ্য সংরক্ষণ ও সিঙ্ক করতে ইন্টারনেট প্রয়োজন।',
    'welcome': 'স্বাগতম', 'new_vehicle': 'গাড়ি যোগ করুন', 'new_expense': 'নতুন খরচ',
    'powered': 'পরিকল্পনা ও স্বাক্ষর', 'total_vehicles': 'আমার গাড়ির তালিকা',
    'currency': 'বাংলাদেশি টাকা (BDT)', 'quantity_help': 'তরল জ্বালানিতে লিটার, CNG-তে পাম্পের ইউনিট',
    'all_cars': 'সকল গাড়ি', 'record_details': 'রেকর্ডের বিবরণ',
}}


def language_context(request):
    lang = request.session.get('app_language', 'bn')
    if lang not in TRANSLATIONS:
        lang = 'bn'
    from .access import is_driver
    from django.conf import settings
    driver_account = is_driver(request.user)
    role_label = 'Superuser' if request.user.is_superuser else 'Driver' if driver_account else 'Admin'
    from .models import ExpenseNotification
    unread = ExpenseNotification.objects.filter(recipient=request.user,read_at__isnull=True).count() if request.user.is_authenticated and not driver_account else 0
    return {'t': TRANSLATIONS[lang], 'app_lang': lang, 'today': timezone.localdate(), 'is_driver':driver_account, 'account_role':role_label, 'session_idle_timeout':settings.SESSION_IDLE_TIMEOUT, 'notification_unread':unread}

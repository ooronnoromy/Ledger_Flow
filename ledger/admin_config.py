from django.contrib.admin.apps import AdminConfig

class SuperuserAdminConfig(AdminConfig):
    default_site = 'ledger.admin_site.SuperuserAdminSite'

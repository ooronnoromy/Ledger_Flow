from django.contrib.admin import AdminSite

class SuperuserAdminSite(AdminSite):
    site_header = 'AutoLedger BD — Superuser administration'
    site_title = 'AutoLedger BD'

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

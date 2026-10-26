from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.urls import reverse_lazy
from ledger import views
from ledger.production_views import healthcheck, private_media

urlpatterns = [
    path('healthz/', healthcheck, name='healthcheck'),
    path('media/<path:path>', private_media, name='private_media'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/password/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html', success_url=reverse_lazy('password_change_done')), name='password_change'),
    path('account/password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('register/', views.register, name='register'),
    path('', include('ledger.urls')),
]

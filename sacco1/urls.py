"""sacco1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from user import views as user_view
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    
    path('', auth_views.LoginView.as_view(template_name='user/login.html'), name='user-login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'), name='user-logout'),
    path('view/borrower/', user_view.view_borrower, name='user-view-borrower'),
    path('view/member/', user_view.view_member, name='user-view-member'),
    path('add/borrower/', user_view.add_borrower, name='user-add-borrower'),
    path('member/update/<int:pk>/', user_view.member_update, name='user-member-update'),
    path('member/delete/<int:pk>/', user_view.member_delete, name='user-member-delete'),
    path('view/borrower/group/', user_view.view_borrower_group, name='user-view-borrower-group'),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

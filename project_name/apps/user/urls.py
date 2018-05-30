from django.urls import path
from django.contrib.auth.views import logout

from {{ project_name }}.apps.user.views import (
    Login, Register, ProfileView, confirm_register
)


urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),

    path('login/', Login.as_view(), name='login'),
    path('logout/', logout, {'next_page': '/'}, name='logout'),
    path('register/', Register.as_view(), name='register'),
    path('register/confirm/<str:confirm_hash>/', confirm_register, name='confirm_register'),
]

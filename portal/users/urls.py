from django.urls import path
from .import views
urlpatterns=[
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('forgot_password/',views.send_otp,name='forgot_password'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('setup_2fa/',views.setup_2fa,name='setup_2fa'),
    path('verify_2fa/',views.verify_2fa,name='verify_2fa'),
    path('register/',views.register,name='register'),
    ]
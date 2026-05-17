from django.urls import path
from .import views
urlpatterns=[
    path('',views.home,name='home'),
    path('add-payment/',views.add_payment,name='add_payment'),
    path('add-complaint/',views.add_complaint,name='add_complaint'),
    path('add-feedback/',views.add_feedback,name='add_feedback'),
    path('delete-payment/<int:id>/',views.delete_payment,name='delete_payment'),
    path('delete-complaint/<int:id>/',views.delete_complaint,name='delete_complaint'),
    path('delete-feedback/<int:id>/',views.delete_feedback,name='delete_feedback'),
    path('generate-qr/<int:payment_id>/',views.generate_qr,name='generate_qr'),
    path('generate-receipt/<int:payment_id>/',views.generate_receipt,name='generate_receipt'),
    path('payment-success/',views.payment_success,name='payment_success'),
    path('download-payment-report/',views.download_payment_report,name='download_payment_report'),
    path('house-report/',views.house_resident_report,name='house_report'),
]
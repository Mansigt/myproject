from django.contrib import admin
from .models import Payment,Event,PaymentCategory,HouseBill,ElectricityBill,InstallmentPayment
admin.site.register(Event)
admin.site.register(PaymentCategory)
admin.site.register(HouseBill)
admin.site.register(ElectricityBill)
admin.site.register(InstallmentPayment)
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
   list_display = (
        'house',
        'category',
        'event',
        'amount',
        'paid_by',
        'date'
    )

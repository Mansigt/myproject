from django.db import models
from django.contrib.auth.models import User
from users.models import House
from django.utils.timezone import now

class Event(models.Model):
    name=models.CharField(max_length=100)
    amount=models.IntegerField()
    def __str__(self):
        return self.name
class PaymentCategory(models.Model):
    name = models.CharField(max_length=50)
    is_event = models.BooleanField(default=False)
    is_maintenance=models.BooleanField(default=False)
    default_amount=models.IntegerField()
    fine_amount=models.IntegerField(default=100)
    def __str__(self):
        return self.name     

class HouseBill(models.Model):
    house=models.ForeignKey(House,on_delete=models.CASCADE)
    category=models.ForeignKey(PaymentCategory,on_delete=models.CASCADE)
    month=models.CharField(max_length=20)
    amount=models.IntegerField()
    fine_amount=models.IntegerField(default=0)
    is_paid=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (
            f"{self.house.house_no}"
            f" - {self.category.name}"
        )    

class Payment(models.Model):
    house=models.ForeignKey(House,on_delete=models.CASCADE)
    category=models.ForeignKey(PaymentCategory,on_delete=models.CASCADE)
    event=models.ForeignKey(Event,on_delete=models.CASCADE,null=True,blank=True)
    amount=models.IntegerField()
    description=models.CharField(max_length=200,null=True,blank=True)
    paid_by=models.ForeignKey(User,on_delete=models.CASCADE)
    transaction_id=models.CharField(max_length=200,blank=True,null=True)
    payment_status=models.CharField(max_length=20,default='Pending')
    fine_amount=models.IntegerField(default=0)
    date=models.DateTimeField(auto_now_add=True)
    PAYMENT_MONTHS=[
    ('January','January'),
    ('February','February'),
    ('March','March'),
    ('April','April'),
    ('May','May'),
    ('June','June'),
    ('July','July'),
    ('August','August'),
    ('September','September'),
    ('October','October'),
    ('November','November'),
    ('December','December'),
     ]
    payment_month=models.CharField(max_length=20,choices=PAYMENT_MONTHS,null=True,blank=True)
    def __str__(self):
        return f"{self.house.house_no} - {self.amount}"

class ElectricityBill(models.Model):
    house=models.ForeignKey(House,on_delete=models.CASCADE)
    month=models.CharField(max_length=20)
    previous_reading=models.IntegerField()
    current_reading=models.IntegerField()
    units_consumed=models.IntegerField()
    rate_per_unit=models.IntegerField(default=8)
    total_amount=models.IntegerField()
    remaining_amount=models.IntegerField(default=0)
    is_paid=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    def save(self,*args,**kwargs):
        self.units_consumed = (
            self.current_reading -
            self.previous_reading
        )
        self.total_amount = (
            self.units_consumed *
            self.rate_per_unit
        )
        if self.remaining_amount == 0:
            self.remaining_amount = self.total_amount

        super().save(*args,**kwargs)
    def __str__(self):
        return (
            f"{self.house.house_no}"
            f" - {self.month}")        

class InstallmentPayment(models.Model):
    electricity_bill=models.ForeignKey(ElectricityBill,on_delete=models.CASCADE,related_name='installments')
    paid_amount=models.IntegerField()
    payment_date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (
            f"{self.electricity_bill.house.house_no}"
            f" - ₹{self.paid_amount}"
        )

class Complaint(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    complaint=models.TextField(default="no message")
    date=models.DateTimeField(auto_now_add=True)    
class Feedback(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    feedback=models.TextField(default="no message")
    date=models.DateTimeField(auto_now_add=True)

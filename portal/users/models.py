from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class OTP(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)

class UserOTP(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    secret=models.CharField(max_length=32)
class House(models.Model):
    house_no=models.CharField(max_length=20,unique=True)
    owner_name=models.CharField(max_length=100)
    owner_contact=models.CharField(max_length=10)
    rent_price=models.IntegerField(default=0)
    is_rental=models.BooleanField(default=False)
    def __str__(self):
        return self.house_no
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=10,unique=True,blank=True,
    validators=[
        RegexValidator(
            regex=r'^\d{10}$',
            message="Enter valid 10 digit phone number"
        )
    ]
)
    aadhar_pan=models.CharField(max_length=20,blank=True)
    house=models.ForeignKey(House,on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return self.user.username

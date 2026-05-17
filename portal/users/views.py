from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import random
import pyotp
import qrcode
from io import BytesIO
import base64
from .models import UserOTP,House,Profile
from .models import OTP
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile

def user_login(request):
   if request.method == 'POST':
        entered_value = request.POST.get('username')
        password = request.POST.get('password')
        username = entered_value
        # 1. Try email login
        if '@' in entered_value:
            try:
                user_obj = User.objects.get(email=entered_value)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, "Email not found")
                return redirect('login')
        # 2. Try phone login
        elif entered_value.isdigit():
            try:
                profile = Profile.objects.get(phone=entered_value)
                username = profile.user.username
            except Profile.DoesNotExist:
                messages.error(request, "Phone number not found")
                return redirect('login')
        # 3. Else assume normal username login
        else:
            username = entered_value
        # Authenticate
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('login')
   return render(request, 'users/login.html') 
def user_logout(request):
    logout(request)
    return redirect('login')
def send_otp(request):
    if request.method=='POST':
        email=request.POST['email']
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request,'email not registered')
            return redirect('forgot_password')
        otp=str(random.randint(100000,999999))
        OTP.objects.filter(user=user).delete()
        OTP.objects.create(user=user,otp=otp)

        send_mail(
            'Your OTP',
            f'Your OTP is { otp }',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        request.session['user_id']= user.id
        return redirect('verify_otp')
    return render(request,'users/forgot_password.html')

def verify_otp(request):
    if request.method=='POST':
        entered_otp=request.POST['otp']
        user_id=request.session.get('user_id')
        otp_obj=OTP.objects.filter(user_id=user_id).last()

        if otp_obj and otp_obj.otp == entered_otp:
            otp_obj.delete()
            return redirect('reset_password')
        else:
           messages.error(request, "Invalid OTP")
    return render(request,'users/verify_otp.html')

def reset_password(request):
    if request.method=='POST':
        password=request.POST['password']
        user_id=request.session.get('user_id')
        user=User.objects.get(id=user_id)
        user.set_password(password)
        user.save()
        messages.success(request,"Password changed successfully")
        request.session.flush()
        return redirect('login')
    return render(request,'users/reset_password.html')

def setup_2fa(request):
    user=request.user
    #check if already exists
    obj,created=UserOTP.objects.get_or_create(user=user)
    if created:
        obj.secret=pyotp.random_base32()
        obj.save()
    totp=pyotp.TOTP(obj.secret)
    #qrcode url
    uri=totp.provisioning_uri(name=user.email,issuer_name='MyApp')  
    qr=qrcode.make(uri)
    buffer=BytesIO()
    qr.save(buffer,format='PNG')
    img_str=base64.b64encode(buffer.getvalue()).decode()
    return render(request,'users/setup_2fa.html',{'qr':img_str}) 
@login_required
def verify_2fa(request):
    if request.method=="POST":
        otp=request.POST.get('otp')
        obj = get_object_or_404(UserOTP,user=request.user)
        totp=pyotp.TOTP(obj.secret)
        if totp.verify(otp):
            return redirect('home')
        else:
            return render(request,'users/verify_2fa.html',{'error':'invalid otp'})
    return render(request,'users/verify_2fa.html')
def register(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        aadhar = request.POST.get('aadhar')
        house_id = request.POST.get('house')
        house = House.objects.get(id=house_id)
        
        #check if user exists
        if User.objects.filter(username=username).exists():
            messages.error(request,"username already exists")
            return redirect ('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        if Profile.objects.filter(phone=phone).exists():
            messages.error(request, "Phone already exists")
            return redirect('register')
        #create user
        user=User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        #get or create house
        
        
        #create profile
        Profile.objects.create(
            user=user,
            phone=phone,
            aadhar_pan=aadhar,
            house=house
        )
        messages.success(request,"Account created successfully")
        return redirect('login')
    houses = House.objects.all()
    return render(request,'users/register.html',{'houses': houses})
    
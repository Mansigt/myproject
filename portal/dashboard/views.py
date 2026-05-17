from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Payment,Feedback,Complaint,PaymentCategory,Event,HouseBill,InstallmentPayment,ElectricityBill
from django.contrib import messages
from users.models import House, Profile
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
import qrcode
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import csv
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required



# @login_required
# def home(request):

#     payments=Payment.objects.filter(user=request.user).order_by('-date')
#     complaints=Complaint.objects.filter(user=request.user).order_by('-date')
#     feedbacks=Feedback.objects.filter(user=request.user).order_by('-date')
#     return render(request,'dashboard/home.html',{'user_count':count,'payments':payments,'complaints':complaints,'feedbacks':feedbacks})

@login_required
def add_complaint(request):
    if request.method == 'POST':
        complaint_text = request.POST.get('complaint')
        Complaint.objects.create(
            user=request.user,
            complaint=complaint_text
        )
        messages.success(request,"Complaint Submitted")
    return redirect('home')

@login_required
def add_feedback(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        Feedback.objects.create(
            user=request.user,
            feedback=feedback_text
        )
        messages.success(request,"Feedback Submitted")
    return redirect('home')

@login_required
def delete_payment(request,id):
        payment = get_object_or_404(
            Payment,
            id=id,
            paid_by=request.user
            ) 
        payment.delete()
        messages.success(request, "Deleted successfully")
        return redirect('home')
      
@login_required
def delete_complaint(request,id):
    complaint = get_object_or_404(
    Complaint,
    id=id,
    paid_by=request.user
     )
    complaint.delete()
    messages.success(request, "Deleted successfully")
    return redirect('home')
 
@login_required
def delete_feedback(request,id):
    feedback = get_object_or_404(
    Feedback,
    id=id,
    paid_by=request.user
     )
    feedback.delete()
    messages.success(request, "Deleted successfully")
    return redirect('home')
@login_required
def home(request):
    profile, created = Profile.objects.get_or_create(
    user=request.user,
    defaults={
        'phone': str(request.user.id).zfill(10),
        'aadhar_pan': f'PAN{request.user.id}',
        'house': House.objects.first()
    }
    )
    all_users = Profile.objects.select_related(
        'user',
        'house'
        ).filter(house__isnull=False)
    categories=PaymentCategory.objects.all()
    events=Event.objects.all()
    houses=House.objects.all()
    count=User.objects.count()
    payments=Payment.objects.filter(house=profile.house).order_by('-date')
    complaints=Complaint.objects.filter(user=request.user).order_by('-date')
    feedbacks=Feedback.objects.filter(user=request.user).order_by('-date')
    current_month=datetime.now().month
    electricity_bill = ElectricityBill.objects.filter(house=profile.house).last()
    family_members=Profile.objects.filter(house=profile.house)
    house_bills=HouseBill.objects.filter(house=profile.house)
    months_paid = payments.exclude(
    payment_month__isnull=True
     ).exclude(payment_month='').values_list(
           'payment_month',
            flat=True
            )
    maintenance_paid=Payment.objects.filter(
    house=profile.house,
    category__is_maintenance=True,
    date__month=current_month
     ).exists()

    return render(request,'dashboard/home.html',{
        'categories':categories,
        'all_users':all_users,
        'events':events,
        'payments':payments,
        'family_members':family_members,
        'house':profile.house,
        'complaints':complaints,
        'feedbacks':feedbacks,
        'user_count':count,
        'electricity_bill':electricity_bill,
        'maintenance_paid':maintenance_paid,
        'months_paid':months_paid,
        'profile':profile,
        'houses':houses,
        'house_bills':house_bills,
        'months_paid':months_paid
    })


@login_required
def add_payment(request):

    if request.method == 'POST':
        profile=Profile.objects.get(user=request.user)
        category_id = request.POST.get('category')
        event_id = request.POST.get('event')
        description = request.POST.get('description')
        category=PaymentCategory.objects.get(id=category_id)
        event=None
        payment_month = request.POST.get('payment_month').strip()
        if category.name.lower() == 'electricity':
            try:
                electricity_bill = ElectricityBill.objects.get(house=profile.house,month=payment_month)
            except ElectricityBill.DoesNotExist:
                messages.error(request,'Electricity bill not generated for this month')
                return redirect('home')

            amount = request.POST.get('amount')
            if int(amount) > electricity_bill.remaining_amount:
                messages.error(request,'Amount exceeds remaining balance')
                return redirect('home')
        else:
            try:
                house_bill = HouseBill.objects.get(
                house=profile.house,
                category=category,
                month=payment_month
        )
            except HouseBill.DoesNotExist:
                messages.error(request,'Bill not generated for this month')
                return redirect('home')
            amount = house_bill.amount
        installment_amount = request.POST.get('installment_amount')
        payment_month=request.POST.get('payment_month')
        if event_id:
            event=Event.objects.get(id=event_id)
        already_paid=Payment.objects.filter(
            house=profile.house,
            category=category,
            event=event,
            date__month=now().month
        ).exists()
        if already_paid:
            messages.error(request,"payment already completed for this house")
            return redirect('home')
        
        fine_amount=category.fine_amount
        total_amount = int(amount) + fine_amount

        request.session['payment_data'] = {
            'category_id': category_id,
            'event_id': event_id,
            'amount': amount,
            'description': description,
            'payment_month':payment_month,
            'fine_amount':fine_amount,
            'installment_amount':installment_amount,
            'total_amount':total_amount
        }
        payable_amount = amount
        if installment_amount:
            payable_amount = int(installment_amount)

        upi_link = f"upi://pay?pa=nmber@ybl&pn=ResidentPortal&am={payable_amount}&cu=INR"

        qr = qrcode.make(upi_link)

        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        qr_code = base64.b64encode(buffer.getvalue()).decode()

        return render(request, 'dashboard/qr.html', {
            'qr_code': qr_code,
            'amount': amount,
            'fine_amount':fine_amount,
            'total_amount':total_amount,
            'house':profile.house
        })

    return redirect('home')
@login_required
def payment_success(request):

    data = request.session.get('payment_data')
    payable_amount = int(
         data.get(
        'installment_amount',
        data['amount']))

    if data:

        profile = Profile.objects.get(user=request.user)

        category = PaymentCategory.objects.get(
            id=data['category_id']
        )
        
        electricity_bill = ElectricityBill.objects.get(
    house=profile.house,
    month=data['payment_month'])
        event = None

        if data['event_id']:
            event = Event.objects.get(
                id=data['event_id']
            )
        if category.name == 'Electricity Bill':
            electricity_bill = ElectricityBill.objects.get(
            house=profile.house,
            month=data['payment_month'] )
            
            InstallmentPayment.objects.create(
            electricity_bill=electricity_bill,
            paid_amount=payable_amount)
            
            electricity_bill.remaining_amount -= payable_amount
            if electricity_bill.remaining_amount <= 0:
                electricity_bill.payment_completed = True
            electricity_bill.save()  
        
        Payment.objects.create(
    house=profile.house,
    category=category,
    event=event,
    amount=payable_amount,
    description=data['description'],
    paid_by=request.user,
    fine_amount=data['fine_amount'],
    payment_month=data['payment_month'],
    payment_status='Paid'
     )

        messages.success(
            request,
            "Payment Successful"
        )

        del request.session['payment_data']

    return redirect('home')
@login_required
def generate_qr(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    upi_link = (
        f"upi://pay?"
        f"pa=7024711072@ybl"
        f"&pn=ResidentPortal"
        f"&am={payment.amount}"
        f"&cu=INR"
    )
    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return render(request,'dashboard/qr.html',{
        'payment':payment,
        'qr_code':img_str
    })
@login_required
def generate_receipt(request,payment_id):
    payment = Payment.objects.get(id=payment_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="receipt_{payment.id}.pdf"'
    )
    p = canvas.Canvas(response,pagesize=letter)
    p.setFont("Helvetica-Bold",20)
    p.drawString(200,750,"PAYMENT RECEIPT")
    p.setFont("Helvetica",14)
    p.drawString(100,680,f"Receipt ID: {payment.id}")
    p.drawString(100,650,f"House No: {payment.house.house_no}")
    p.drawString(100,620,f"Paid By: {payment.paid_by.username}")
    p.drawString(100,590,f"Category: {payment.category.name}")
    p.drawString(100,560,f"Amount: Rs. {payment.amount}")
    p.drawString(100,530,f"Status: {payment.payment_status}")
    p.drawString(100,500,f"Date: {payment.date}")
    if payment.event:
        p.drawString(100,470,f"Event: {payment.event.name}")
    p.drawString(100,420,"Thank you for your payment")
    p.showPage()
    p.save()
    return response

@staff_member_required
def download_payment_report(request):
   response=HttpResponse(content_type='text/csv')
   response['Content-Disposition']='attachment; filename="payments_report.csv"'
   writer=csv.writer(response)
   writer.writerow([
        'House No',
        'User',
        'Category',
        'Month',
        'Amount',
        'Fine',
        'Status',
        'Transaction ID'
    ])
   payments=Payment.objects.all()
   for payment in payments:

        writer.writerow([
            payment.house.house_no,
            payment.paid_by.username,
            payment.category.name,
            payment.payment_month,
            payment.amount,
            payment.fine_amount,
            payment.payment_status,
            payment.transaction_id
        ])
   return response

@staff_member_required
def house_resident_report(request):
    houses=House.objects.all()
    data=[]

    for house in houses:
        residents=Profile.objects.filter(
            house=house
        )
        resident_names=[
            resident.user.username
            for resident in residents
        ]
        data.append({
            'house_no':house.house_no,
            'owner_name':house.owner_name,
            'owner_contact':house.owner_contact,
            'residents':resident_names
        })
    return render(
        request,
        'dashboard/house_report.html',
        {'data':data}
    )
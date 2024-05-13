from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from TSC.models import*
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import user_passes_test,login_required
from datetime import datetime
from django.contrib.auth.models import User
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.utils.dateparse import parse_date
from django.core.mail import send_mail
import re
# from django.conf import settings

def is_admin(user):
    return user.is_authenticated and user.is_staff

def AdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request,user)
            
            return redirect('/')
        else:
            messages.success(request, "Invalid username or password")
        return redirect('/AdminLogin/')
    return render(request, 'AdminLogin.html')
    
def Login(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        if not User.objects.filter(username=username).exists():
            messages.info(request, "Invalid Username")
            return redirect('/')
        user=authenticate(request,username=username,password=password)
        if user is None :
            messages.error(request, "Invalid Username or Password")
        else:
            login(request,user)
            return redirect('/')
    return render(request,"login.html")

@login_required(login_url="/login/")
def Logout(request):
    logout(request)
    return redirect('/login/')


def is_strong_password(password):
    # Define the criteria for a strong password
    min_length = 8
    has_uppercase = re.search(r'[A-Z]', password)
    has_lowercase = re.search(r'[a-z]', password)
    has_digit = re.search(r'[0-9]', password)
    has_special_char = re.search(r'[!@#$%^&*()\-_=+{}\[\]|\\;:\'",.<>/?]', password)

    # Check if the password meets all criteria
    if (len(password) < min_length or
            not has_uppercase or
            not has_lowercase or
            not has_digit or
            not has_special_char):
        return False
    else:
        return True

def register(request):
    if request.method=="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        role = request.POST.get('role')  # Get the role selected by the user
        if User.objects.filter(email=email).exists():
                messages.info(request, "An account with this email already exists.")
                return redirect('/register/')
        user=User.objects.filter(username=username)
        if user.exists():
            messages.info(request, "Username already taken")
            return redirect('/register/')
        
        if not is_strong_password(password):
            messages.error(request, "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
            return redirect('/register/')
        
        user=User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
        )
        user.set_password(password)
        UserProfile.objects.create(user=user, role=role)

        user.save()
        messages.info(request, "Accout Created Successfully")
        return redirect('/login/')
    return render(request,"register.html")

@user_passes_test(is_admin, login_url='/')
def AdminLogout(request):
    logout(request)
    return redirect('/AdminLogin/')

def home(request):
    return render(request,"base.html")

@user_passes_test(is_admin, login_url='/')
def Notices(request):
    if request.method == "POST":
        title = request.POST.get("title")
        pdf = request.FILES.get("pdf")
         
        if title and pdf:
            uploaded_at = datetime.now().date()
            Notice.objects.create(
                title=title,
                pdf=pdf,
                uploaded_at=uploaded_at,
            )
            messages.success(request, f'File added successfully.')
    return render(request, "Notice.html")

def Notices_list(request):
    notices = Notice.objects.all()
    paginator=Paginator(notices,10)
    page_no=request.GET.get('page')
    try:
        notices = paginator.page(page_no)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        notices = paginator.page('1')  
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        notices = paginator.page(paginator.num_pages)
    return render(request, "Notice_list.html", {'notices': notices,'page_name':"NOTICES"})


@user_passes_test(is_admin, login_url='/')
def RoomType(request):
    if(request.method=="POST"):
        roomtype=request.POST.get('roomtype')
        existing_type=Room_Type.objects.filter(roomtype=roomtype).first()
        if(existing_type):
            messages.success(request, "Type already exists")
        else:
            Room_Type.objects.create(
            roomtype=roomtype,
            ) 
            messages.success(request, f'{roomtype} added successfully.')
        return redirect('/')
    return render(request,"RoomType.html")

@user_passes_test(is_admin, login_url='/')
def AddRoom(request):
    roomt=Room_Type.objects.all()
    if(request.method=="POST"):
        room=request.POST.get('room')
        roomtype_id=request.POST.get('roomtype')
        description=request.POST.get('description')
        img=request.FILES.get('img')
        price=request.POST.get('price')
        roomtype= Room_Type.objects.get(pk=roomtype_id)  # Assuming the select field is named 'category'

        existing_room = Room.objects.filter(room=room).first()
        if existing_room:
            messages.success(request, "Room already exists")
        else:
            Room.objects.create(
            room=room ,
            roomtype=roomtype,
            description=description,
            img=img,
            price=price,
            ) 
            messages.success(request, f'Room {room} added successfully.')
        return redirect('/')
    context={
        'roomt':roomt ,
             }
    return render(request,"AddRoom.html",context)

def Room_list(request):
    available_room=Room.objects.all()
    if(request.method=="POST"):
        check_in=request.POST.get('check_in')
        check_out=request.POST.get('check_out')
        if not check_in or not check_out:
            messages.error(request, 'Please provide both check-in and check-out dates.')
        elif parse_date(check_in) >= parse_date(check_out):
            messages.error(request, 'Check-out date must be after the check-in date.')
        else:
            qs=Booking.objects.filter(
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        
            available_room = available_room.exclude(booking__in=qs)
    paginator=Paginator(available_room,3)
    page_no=request.GET.get('page')
    try:
        available_room = paginator.page(page_no)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        available_room = paginator.page('1')  
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        available_room = paginator.page(paginator.num_pages)
  
    context={
        'room':available_room,
        'page_name':"ROOMS",
    }
    return render(request,"Room_list.html",context)


@login_required
def Bookin(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        role = user_profile.role
    except UserProfile.DoesNotExist:
        # Handle the case where UserProfile doesn't exist for the user
        role = None
    room_no = request.GET.get('room_no')
    room = None  # Initialize room variable to None
    room_price=0
    if room_no:
        room = get_object_or_404(Room, room=room_no)
        room_price = room.price  # Get the price of the room

    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        # check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        payment_method = request.POST.get('payment_method')
        today = timezone.now().date()

        if not check_in or not check_out or not payment_method:
            messages.error(request, 'Please provide all')
        elif parse_date(check_in) >= parse_date(check_out):
            messages.error(request, 'Check-out date must be after the check-in date.')
        elif check_in_date <= today:
            messages.error(request, 'Provide future date to book room')
        else:
            qs = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            
            if qs.exists():
                messages.error(request, 'Room is not available for the selected dates.')
            else:
                room_price = room.price
                total_price = (parse_date(check_out) - parse_date(check_in)).days * room_price
                # subject = 'Welcome to Our Website'
                # message = f'Hello {user.email},\n\nWelcome to our website! Thank you for joining us.'
                # from_email = user_email
                # recipient = [settings.EMAIL_HOST_USER]
                # send_mail(subject, message, from_email, recipient)
                
                last_booking = Booking.objects.last()
                booking_id = 1 if last_booking is None else last_booking.booking_id + 1
                email=request.user.email
                # Create the Booking object with the booking_id
                Booking.objects.create(
                    booking_id=booking_id,
                    email=email,
                    user=user,
                    room=room,
                    check_in=check_in,
                    check_out=check_out,
                    tot_price=total_price,
                    payment_method=payment_method,
                    role=role,
                )
                messages.success(request, f'Booking request done successfully,Wait for the confirmation e-mail from us')
                return redirect('/Room_list/')
    return render(request,'Booking.html',{'room':room,'room_price':room_price,'page_name':"BOOKING"})

@user_passes_test(is_admin, login_url='/')
def Booking_list(request):
    booking_list=Booking.objects.all()
    return render(request,'Booking_list.html',{'booking_list':booking_list,'page_name':"BOOKING LIST"})

@user_passes_test(is_admin, login_url='/')
def reject_booking(request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        user_email = booking.email
        subject = 'Booking Rejection Notification'
        message = (
        f"Dear {booking.user},\n\n"
        f"We regret to inform you that your booking request (Booking ID: {booking_id}) has been rejected .\n\n"
        "If you have any questions, please feel free to contact us.\n\n"
        "Best regards,\nJUST TSC "
    )
        from_email = settings.EMAIL_HOST_USER
        to_email = [user_email]
        send_mail(subject, message, from_email, to_email)
        booking.delete() 
        return redirect('/Booking_list/')

@user_passes_test(is_admin, login_url='/')
def approve_booking(request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        user_email = booking.email
        subject = 'Booking Approval Notification'
        message = (
        f"Dear {booking.user},\n\n"
        f"We are happy to inform you that your booking request (Booking ID: {booking_id}) has been accepted .\n\n"
        "If you have any questions, please feel free to contact us.Please arrive before the check-in date.\n\n"
        "Best regards,\nJUST TSC "
    )
        from_email = settings.EMAIL_HOST_USER
        to_email = [user_email]
        send_mail(subject, message, from_email, to_email)
        booking.confirmed = True  # Set the confirmed field to True

        booking.save()        
        return redirect('/Booking_list/')
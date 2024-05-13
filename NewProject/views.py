from django.http import HttpResponse
from django.shortcuts import render,redirect
from .forms import userForm
from service.models import*

def home(request):
    serviceData=Service.objects.all().order_by('-service_title')[:3]
    # if i use'-dash' it will decending order,[:3] indicates 0 to 2 value take
    data={
        'serviceData': serviceData,
        
    }
    
    # ans=0
    # fm=userForm()
    # if request.method=="POST":
    #     n1=int(request.POST.get("num1"))
    #     n2=int(request.POST.get("num2"))
    #     ans=n1+n2
    # data={
    #     'final':ans,
    #     "form":fm
    # }
    
    return render(request,"index.html",data)

def submitform(request):
    if request.method=="POST":
        n1=int(request.POST.get("num1"))
        n2=int(request.POST.get("num2"))
        ans=n1+n2
    return HttpResponse(ans)
    
def AboutUs(request):
    return HttpResponse("Welcome")
def About(request,aboutID):
    return HttpResponse(aboutID)

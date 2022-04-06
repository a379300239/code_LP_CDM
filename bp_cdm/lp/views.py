from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

def lp(request):
    return render(request,'lp.html')

def dcm(request):
    return render(request,'dcm.html')

def submitLp(request):
    data = ''
    if(request.method == 'POST'):
        data = request.POST

    ans=[
        []
    ]

    return HttpResponse(data)
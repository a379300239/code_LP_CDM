from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
import time
from lpSolve.lpSolve import startLp

def lp(request):
    return render(request,'lp.html')

def dcm(request):
    return render(request,'dcm.html')

def submitLp(request):
    data = ''
    if(request.method == 'POST'):
        data = request.POST

    # 调用方法，得到最终结果
    ans = startLp(data)

    ansj={
        'data':ans
    }

    return JsonResponse(ansj)

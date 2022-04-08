from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
import time
from lpSolve.lpSolve import lpQuestion

def lp(request):
    return render(request,'lp.html')

def dcm(request):
    return render(request,'dcm.html')

def submitLp(request):
    data = ''
    if(request.method == 'POST'):
        data = request.POST

    # 创建线性规划问题对象
    lpq = lpQuestion(data)

    # 调用方法，得到最终结果
    ans = lpq.solvelp()

    # time.sleep(3)


    ans={
        'data':[
            [
                [' ','cj',' ','-2','-3','0','0','0','ci'],
                ['cb','xb','b','p1','p2','p3','p4','p5','ci'],
                ['0','x3','8','1','2','1','0','0','8/2'],
                ['0','x4','16','4','0','0','1','0','-'],
                ['0','x5','12','0','4','0','0','1','12/4'],
                [' ','cj',' ','-1','-3','0','0','0',' '],
            ],
                        [
                [' ','cj',' ','-2','-3','0','0','0','ci'],
                ['cb','xb','b','p1','p2','p3','p4','p5','ci'],
                ['0','x3','8','1','2','1','0','0','8/2'],
                ['0','x4','16','4','0','0','1','0','-'],
                ['0','x5','12','0','4','0','0','1','12/4'],
                [' ','cj',' ','-1','-3','0','0','0',' '],
            ]
        ],
        'zyj':{
            'minZ':'-14',
            'minX':'(4,2)'
        }
    }

    return JsonResponse(ans)

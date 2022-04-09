import numpy as np
import time as t
import json

from zmq import FD


global maxNum 
maxNum = 9999999999


def formatData(data):
    # 目标函数处理
    C = data['C'].split(' ')

    questionType_f = C[0]
    C_f = np.array(C[1:]).astype(float)
    
    # 约束条件处理
    symbolMatrix_f = np.array([])     # 符号矩阵
    A_f = np.array([])              # 系数矩阵

    for i in data['A'].split('\n'):
        i = i.split(' ')
        symbolMatrix_f = np.append(symbolMatrix_f,i[-1])
        if A_f.size>0:
            A_f = np.vstack([A_f,i[:-1]])
        else:
            A_f = np.array(i[:-1])
    A_f = A_f.astype(float)

    # 取值范围处理
    xRange = data['xRange']

    xRange_f = np.array([eval(i) for i in xRange.replace('(','[').\
                                replace(')',']').\
                                replace('e',str(maxNum)).\
                                strip('\n').
                                split('\n')
            ])

    # 右端向量处理
    B = data['B']
    B_f = np.array(B.split(' ')).astype(float)

    data_f={
        'questionType':questionType_f,
        'C':C_f,
        'A':A_f,
        'symbolMatrix':symbolMatrix_f,
        'B':B_f,
        'xRange':xRange_f,
        }

    return data_f


# 标准化
def standard(data):
    print('原数据：')

    # 检查是哪一类
    erroTypeList = checkErroType(data)
    print('错误类型有：'+str(erroTypeList))

    # 处理决策变量范围不对
    if '3' in erroTypeList:
        data = handleXrange(data)

    # 处理限额系数为负数
    if '4' in erroTypeList:
        data = handleB(data)

    # 处理约束为不等式
    if '2' in erroTypeList:
        data = handlesymbolMatrix(data)

    # # 处理目标函数极大化
    if '1' in erroTypeList:
        data = handleC(data)

    # 删掉-0.0
    data = delNzero(data)

    return data



def checkErroType(data):
    erroTypeList = []   

    # 1.目标函数极大化
    if data['questionType'] != 'min':
        erroTypeList.append('1')

    # 2.约束为不等式
    if np.sum(data['symbolMatrix']=='=') != data['symbolMatrix'].size:
        erroTypeList.append('2')

    # 3.决策变量范围不对
    if np.sum(data['xRange']==[0,maxNum]) != data['xRange'].size:
        erroTypeList.append('3')

    # 4.限额系数为负数
    if np.sum(data['B'].astype(float)>=0) != data['B'].size:
        erroTypeList.append('4')

        
    return erroTypeList

# 处理决策变量范围不对
def handleXrange(data):
    saveXrange = data['xRange']

    # 偏移量
    offset = 0
    for (index,i) in enumerate(saveXrange):
        offIndex = offset+index

        # 小于0
        if (i ==[-maxNum,0]).all():
            # 变量名处理
            # xIndex = delX(getXname(index))
            # insertX(getXPname(index),xIndex)

            # 矩阵处理
            data['xRange'] = np.delete(data['xRange'],offIndex,axis=0)
            data['xRange'] = np.insert(data['xRange'],offIndex,[0,maxNum],axis=0)

            data['A'][:,offIndex] = np.dot(-1,data['A'][:,offIndex])

            data['C'][offIndex] = data['C'][offIndex]*-1
            

        # 无限制
        if (i == [-maxNum,maxNum]).all():
            data['xRange'] = np.delete(data['xRange'],offIndex,axis=0)
            data['xRange'] = np.insert(data['xRange'],offIndex,[0,maxNum],axis=0)
            data['xRange'] = np.insert(data['xRange'],offIndex,[0,maxNum],axis=0)

            c = data['A'][:,offIndex]*-1
            data['A'] = np.insert(data['A'],offIndex+1,c,axis=1)
            
            c = data['C'][offIndex]*np.array([1,-1])
            data['C'] = np.delete(data['C'],offIndex)
            data['C'] = np.insert(data['C'],offIndex,c)

            offset+=1

        # 小于常数
        if (i[0]==-maxNum and i[1]!=maxNum and i[1]!=0).all():

            # 常数项改变            
            data['B'] = data['B']-data['A'][:,offIndex]*data['xRange'][offIndex][1]

            # 变量变为相反数
            data['xRange'] = np.delete(data['xRange'],offIndex,axis=0)
            data['xRange'] = np.insert(data['xRange'],offIndex,[0,maxNum],axis=0)

            data['A'][:,offIndex] = -1 * data['A'][:,offIndex]

            data['C'][offIndex] = -1 * data['C'][offIndex]


        # 范围
        if (i[0]!=-maxNum and i[1]!=maxNum).all():

            
            # 常数项改变
            data['B'] = data['B']-data['A'][:,offIndex]*data['xRange'][offIndex][0]

            # 新增式子
            row = np.zeros(data['A'][0].size)
            row[-1] = 1
            data['A'] = np.insert(data['A'],data['A'][:,0].size,row,axis=0)
            
            col = np.zeros(data['A'][:,0].size)
            col[-1] = 1
            data['A']= np.insert(data['A'],data['A'][0].size,col,axis=1)

            data['B'] = np.append(data['B'],data['xRange'][offIndex][1]-data['xRange'][offIndex][0])

            data['C'][offIndex] = data['C'][offIndex]*-1
            data['C'] = np.append(data['C'],0) 

            data['xRange'] = np.delete(data['xRange'],offIndex,axis=0)
            data['xRange'] = np.insert(data['xRange'],offIndex,[0,maxNum],axis=0)
            data['xRange'] = np.insert(data['xRange'],offIndex,[0,maxNum],axis=0)

            data['symbolMatrix'] = np.insert(data['symbolMatrix'],offIndex,'=',axis=0)
            offset+=1
            
    return data

# 处理限额系数为负数
def handleB(data):
    for (index,i) in enumerate(data['B']):
        if i <0:
            data['A'][index] = data['A'][index]*-1
            data['B'][index] = data['B'][index]*-1
    
    return  data

# 处理约束为不等式
def handlesymbolMatrix(data):
    for (index,i) in enumerate(data['symbolMatrix']):

        # 大于约束，减去松弛变量
        if '>' in i:
            sc=-1

        # 小于约束，增加松弛变量
        elif '<' in i:
            sc=1
        else:
            continue
        
        data = addX(data,index,sc)


    return data

# index为第几个式子 sc 加变量或者减变量 cj 价格系数
def addX(data,index,sc=1,cj=0):
    data['xRange'] = np.append(data['xRange'],np.array([0,maxNum]).reshape(1,2),axis=0)

    c = np.zeros(data['A'][:,0].size)
    c[index] = sc

    data['A'] = np.append(data['A'],c.reshape(data['A'][:,0].size,1),axis=1)
    data['C'] = np.append(data['C'],cj)

    data['symbolMatrix'][index] = '='

    return data


# 处理目标函数极大化
def handleC(data):
    data['questionType'] = 'min'
    data['C'] = data['C']*-1

    return data

# 去除-0
def delNzero(data):

    
    for i in  np.where(data['C'] == -0):
        data['C'][i] = 0
     
    return data
        

# 闲心规划问题求解


def getAns(data):
    ans = []
    baseX = []

    while 1:
        # 确定基变量
        if baseX == []:
            baseX = haveUnitArray(data)   # 寻找单位阵
        else:
            pass
        
        # 计算单纯形表，返回表及换入换出变量
        result = getSimplexTable(data,baseX)

        inAndoutX = result['inAndoutX']

        # 解
        solution = getSolution(result['solution'],data['A'][0].size)

        # 值
        value = getFinalValue(solution,data['C'])


        # 退出条件
        if inAndoutX[0] == -maxNum:
            item = {'st':result['st'],'solution':solution,'value':value,'inAndoutX':inAndoutX}
            ans.append(item)
            break
        else:
            # 存入单纯形表
            item = {'st':result['st'],'solution':solution,'value':value,'inAndoutX':inAndoutX}
            ans.append(item)
        
            # 交换变量，并单位化
            baseX[baseX.index(inAndoutX[1])] = inAndoutX[0] 
            data = vectorUnit(data,inAndoutX[2],inAndoutX[0])

    return ans

# 解
def getSolution(data,n):
    xList = {}
    sol = []
    for (index,i) in enumerate(data[0]):    
        xList[eval(i[0].replace('x',''))]=data[1][index][0]

    for i in range(1,n+1):
        if i in xList.keys():
            sol.append(xList[i])
        else:
            sol.append(0)

    return sol

# 值
def getFinalValue(solution,c):
    solution = np.array(solution)
    c = np.array(c)

    ans = np.dot(solution,c.T)

    return ans


# 根据方程及基变量，生成单纯形表
def getSimplexTable(data,baseX):
    # 初始化单纯性表
    st = initSt(data)
    
    # 填入目标函数
    st = fillSt(st,[data['C'].tolist()],0,3)

    # 填入系数矩阵
    st = fillSt(st,data['A'].tolist(),2,3)

    # 填入左边
    Cb = []
    Xb = []
    b = []
    for (index,i) in enumerate(baseX):
        Cb.append(data['C'][i])
        Xb.append('x{}'.format(showNum(i)))
        b.append(data['B'][index])

    Cb = np.array(Cb).reshape(data['A'][:,0].size,1)
    Xb = np.array(Xb).reshape(data['A'][:,0].size,1)
    b = np.array(b).reshape(data['A'][:,0].size,1)
    jblList = np.append(Cb,Xb,axis=1)
    jblList = np.append(jblList,b,axis=1).tolist()

    st = fillSt(st,jblList,2,0)

    # 填入检验数σ
    jysList = []
    for (index,i) in enumerate(data['C']):
        c = i- np.dot(Cb.T,data['A'][:,index])
        jysList.append(c)
    
    jysList = [i.tolist()[0] for i in jysList]
    st = fillSt(st,[jysList],data['A'][:,0].size+2,3)

    # 判断换入变量，并填入θ
    jysList = np.array(jysList)
    if np.sum(jysList < 0) >0:
        inIndex = np.argmin(jysList)
    else:
        # 没有负分量，结束
        inIndex = -maxNum
        return {'st':st,'inAndoutX':[inIndex,'-','-'],'solution':[Xb,b]}
# ----------------------------------------------------------
    np.seterr(divide='ignore', invalid='ignore')  # 消除被除数为0的警告
    sitaI = b.T/data['A'][:,inIndex]

    # 小于等于0，丢掉
    for i in np.where(sitaI <= 0):
        sitaI[0][i] = maxNum
        

    c = sitaI.T.tolist()
    st = fillSt(st,c,2,-1)

    # 找到换出变量，利用xb确定index
    outInTable = np.argmin(sitaI)                  # 换出变量在表中的位置
    outIndex = eval(Xb[outInTable][0].replace('x',''))-1
    
 

    return {'st':st,'inAndoutX':[inIndex,outIndex,outInTable],'solution':[Xb,b]}


# 是否有单位阵，并返回数字，暂时无法解决无单位基问题，需用大M法
def haveUnitArray(data):
    
    xNum = data['A'][0].size    # 变量个数
    cNum = data['A'][:,0].size  # 式子个数
    allOneArray = []            # 存所有1矩阵

    for index in range(xNum):
        if np.sum(data['A'][:,index]) == 1:
            onePos = np.where(data['A'][:,index] == 1)[0][0]
            allOneArray.append([index,onePos])
    
    allOneArray = np.array(allOneArray)

    ans = []

    for index in range(cNum):
        try:
            onepos1 = np.where(allOneArray[:,1] == index)[0][0]
        except:
            continue

        # 存在
        if onepos1 != None:
            ans.append(allOneArray[:,0][onepos1])

    return ans

# 向量单位化
def vectorUnit(data,row,col):
    # A B 统一
    cData = np.append(data['A'],data['B'].reshape(data['A'][:,0].size,1),axis=1)

    aim = cData[row]/cData[row][col]
    cData[row] =aim

    for (index,i) in enumerate(cData):
        if index != row:
            cData[index] = i-aim*i[col]

    data['A'] = cData[:,:-1]
    data['B'] = cData[:,-1]

    return data


# 初始化结果矩阵，全0的列表
def initSt(data):
    rowNum = data['A'][:,0].size+3
    colNum = data['A'][0].size+4

    st = []

    for j in range(rowNum):
        st.append([' ' for i in range(colNum)])

    st = fillSt(st,[[' ','cj',' '],['Cb','Xb','b']],0,0) # 左上角
    st = fillSt(st,[['θj'],['θj']],0,colNum-1)           # 右上角
    st = fillSt(st,[[' ','σj',' ']],rowNum-1,0)          # 左下角

    # 系数名称
    pName = []
    for i in range(data['C'].size):
        pName.append('p{}'.format(showNum(i)))

    st = fillSt(st,[pName],1,3)
    st = fillSt(st,[['Cb','Xb','b']],1,0)
    st = fillSt(st,[[' ']],-1,-1)

    return st
    
# 结果填入矩阵
def fillSt(st,data,srow,scol):
    for (indexRow,j) in enumerate(data):
        for (indexCol,val) in enumerate(j):
             st[srow+indexRow][scol+indexCol] = val
    return st

def showNum(i):
    return str(i+1)


def resBeauty_st(data):
    for (indexJ,j) in enumerate(data):
        for (indexItem,item) in enumerate(j):
            if item == 9999999999.0:
                data[indexJ][indexItem] = '-'
            data[indexJ][indexItem] = str(data[indexJ][indexItem])

    return data

def resBeauty_inAndoutX(data):
    print(data)
    for (indexj,j) in enumerate(data):
        if isinstance(j,int) or isinstance(j,np.int64):
            data[indexj] = str(j+1)
        else:
            data[indexj] = str(j)
    return data

def startLp(data):

    fData = formatData(data)

    stdData = standard(fData)

    ans = getAns(stdData)
    
    for (index,i) in enumerate(ans):
        ans[index]['st'] = resBeauty_st(i['st'])
        ans[index]['inAndoutX'] = resBeauty_inAndoutX(i['inAndoutX'])


    return ans
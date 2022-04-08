import imp


import numpy as np


class lpQuestion:
    def __init__(self,data):
        self.data=data

    def solvelp(self):
        # 格式化
        fData = self.formatData(self.data)

        # 标准化
        stdData = self.standard(fData)

        print(self.data)
        
        # 求解线性规划问题
        ans = self.getAns(stdData)

        return ans

    # 格式化
    # <QueryDict: {'C': ['min -1 -1'], 'A': ['1 2 1 0 =\n3 5 0 1 ='], 'xRange': ['[0,e)\n[0,e)\n[0,e)\n[0,e)\n'], 'B': ['4 10']}>
    def formatData(self,data):
        # 目标函数处理
        C = data['C'].split(' ')

        questionType = C[0]
        C_f = np.array(C[1:])
        
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

        # 取值范围处理
        xRange = data['xRange']

        xRange_f = np.array([eval(i) for i in xRange.replace('(','[')\
                                    .replace(')',']')\
                                    .replace('e','9999999999')\
                                    .strip('\n')\
                                    .split('\n')
                            ])

        # 右端向量处理
        B = data['B']
        B_f = np.array(B.split(' '))

        data_f={
            'C':C_f,
            'A':A_f,
            'XRang':xRange_f,
            'symbolMatrix':symbolMatrix_f,
            'B':B_f
            }

        return data_f
        


    # 标准化
    def standard(self,data):
        # 判断错误类型

        # 分别解决错误类型
        pass
    
    # 求解线性规划问题
    def getAns(self,stdData):
        pass

    def erro():
        return  '运行出错'












        # ans={
        #     'data':[
        #         [
        #             [' ','cj',' ','-2','-3','0','0','0','ci'],
        #             ['cb','xb','b','p1','p2','p3','p4','p5','ci'],
        #             ['0','x3','8','1','2','1','0','0','8/2'],
        #             ['0','x4','16','4','0','0','1','0','-'],
        #             ['0','x5','12','0','4','0','0','1','12/4'],
        #             ['cj','cj','cj','-1','-3','0','0','0',' '],
        #         ],
        #                     [
        #             [' ','cj',' ','-2','-3','0','0','0','ci'],
        #             ['cb','xb','b','p1','p2','p3','p4','p5','ci'],
        #             ['0','x3','8','1','2','1','0','0','8/2'],
        #             ['0','x4','16','4','0','0','1','0','-'],
        #             ['0','x5','12','0','4','0','0','1','12/4'],
        #             ['cj','cj','cj','-1','-3','0','0','0',' '],
        #         ]
        #     ],
        #     'zyj':{
        #         'minZ':'-14',
        #         'minX':'(4,2)'
        #     }
        # }
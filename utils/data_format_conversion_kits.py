import numpy as np

def intlist2strings(li):
    li = [str(fac) for fac in li]
    return ','.join(li)

def strings2intlist(strings):
    return strings.split(',')

def list2matrix(li):
    return np.array(li).reshape(8,8).tolist()

def matrix2list(matrix):
    return np.array(matrix).reshape(1,-1).tolist()[0]

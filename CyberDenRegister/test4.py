from math import *


def dec_to_bin(x):
    return int(bin(x)[2:])
s = int(input())
ast = str(dec_to_bin(s))
sss =""
#print(ast)
num = len(ast)
if(num%2!=0):
    num-=1
#print(num)
for i in range(0,num,2):
    if(ast[i]==ast[i+1] and ast[i]=='0'):
        sss+='0'
        sss+='0'
    if (ast[i] == ast[i + 1] and ast[i] == '0'):
        sss += '0'
        sss += '0'
    else:
        sss+=ast[i]
        sss+=ast[i+1]

#print(sss)
sss = int(sss,2)
print (sss)
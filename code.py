

a=0
b=[]
c="hello world"

d,e,f=1,2,3

e,f=f,e#buggy

e,h,i=range(3)

temp="whatever"#global variable definition

def say(string):
    temp="I say "#local variable
    print(temp+string)

def hear():
    global temp
    temp="this"#global variable
    print(temp)

l=[x*2-1 for x in range(100)]#list comprehension

muldim=[[x for x in range(y)] for y in range(10)]#2D list comprehension
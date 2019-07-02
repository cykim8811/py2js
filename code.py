

a,b=1,2
b,c,d=range(3)

temp="whatever"#global variable definition

def say(string):
    temp="I say "#local variable
    print(temp+string)

def hear():
    global temp
    temp="this"#global variable
    print(temp)
#list comprehension
l=[x*2-1 for x in range(100)]
#2D list comprehension
muldim=[[x for x in range(y)] for y in range(10)]
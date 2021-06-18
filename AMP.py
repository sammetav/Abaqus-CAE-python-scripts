
def amp(displacement, velocity):
    time=displacement/velocity
    return time
n=amp(40, 500)
time_step=0.01
print(n)
nr_of_iterations = n*100
nr_of_iterations=int(nr_of_iterations)

data1=[]

data1.append( (0.0,0.0) )



for i in range(nr_of_iterations):
               data1.append( ((i+1)*time_step, 1.0) )

data1.append( (n+time_step, 0.0) )


print(data1)

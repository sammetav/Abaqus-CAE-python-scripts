def amp(displacement, velocity):
    n=displacement/velocity
    time_step=0.01
    nr_of_iterations = n*100
    nr_of_iterations=int(nr_of_iterations)
    data1=[]
    data1.append((0.0,0.0))
    for i in range(nr_of_iterations):
                   data1.append( ((i+1)*time_step, 1.0) )
    data1.append( (n+time_step, 0.0) )
    return tuple(data1)

#Abaqus scriting
mdb.models['Model-1'].TabularAmplitude(name='Amplitude-1', timeSpan=STEP, smooth=SOLVER_DEFAULT, data=amp(35, 500))

#COPY
    p1 = mdb.models['Model-1'].parts['Part-1']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    #1 mirror
    p = mdb.models['Model-1'].Part(name='Part-1' + '-zy', 
        objectToCopy=mdb.models['Model-1'].parts['Part-1'], 
        compressFeatureList=ON, mirrorPlane=YZPLANE)
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    p1 = mdb.models['Model-1'].parts['Part-1']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)

    #2 mirror
    p = mdb.models['Model-1'].Part(name='Part-1' + '-yx1', 
        objectToCopy=mdb.models['Model-1'].parts['Part-1'], 
        compressFeatureList=ON, mirrorPlane=XYPLANE)
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    p1 = mdb.models['Model-1'].parts['Part-1' + '-zy']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    p = mdb.models['Model-1'].Part(name='Part-1' + '-yx2', 
        objectToCopy=mdb.models['Model-1'].parts['Part-1' + '-zy'], 
        compressFeatureList=ON, mirrorPlane=XYPLANE)
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    p1 = mdb.models['Model-1'].parts['Part-1']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)

    #3 mirror
    p = mdb.models['Model-1'].Part(name='Part-1' + '-xz11', 
        objectToCopy=mdb.models['Model-1'].parts['Part-1'], 
        compressFeatureList=ON, mirrorPlane=XZPLANE)
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    p1 = mdb.models['Model-1'].parts['Part-1' + '-yx1']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)

    p = mdb.models['Model-1'].Part(name='Part-1' + '-xz12', 
        objectToCopy=mdb.models['Model-1'].parts['Part-1' + '-yx1'], 
        compressFeatureList=ON, mirrorPlane=XZPLANE)
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    p1 = mdb.models['Model-1'].parts['Part-1' + '-yx2']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)

    p = mdb.models['Model-1'].Part(name='Part-1' + '-xz13', 
        objectToCopy=mdb.models['Model-1'].parts['Part-1' + '-yx2'], 
        compressFeatureList=ON, mirrorPlane=XZPLANE)
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    p1 = mdb.models['Model-1'].parts['Part-1' + '-zy']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)

    p = mdb.models['Model-1'].Part(name='Part-1' + '-xz14', 
        objectToCopy=mdb.models['Model-1'].parts['Part-1' + '-zy'], 
        compressFeatureList=ON, mirrorPlane=XZPLANE)
    session.viewports['Viewport: 1'].setValues(displayedObject=p)

    #Instance 
    a = mdb.models['Model-1'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    a = mdb.models['Model-1'].rootAssembly
    p = mdb.models['Model-1'].parts['Part-1' + '-xz11']
    a.Instance(name='Part-1' + '-xz11-1', part=p, dependent=ON)
    p = mdb.models['Model-1'].parts['Part-1' + '-xz12']
    a.Instance(name='Part-1' + '-xz12-1', part=p, dependent=ON)
    p = mdb.models['Model-1'].parts['Part-1' + '-xz13']
    a.Instance(name='Part-1' + '-xz13-1', part=p, dependent=ON)
    p = mdb.models['Model-1'].parts['Part-1' + '-xz14']
    a.Instance(name='Part-1' + '-xz14-1', part=p, dependent=ON)
    p = mdb.models['Model-1'].parts['Part-1' + '-yx1']
    a.Instance(name='Part-1' + '-yx1-1', part=p, dependent=ON)
    p = mdb.models['Model-1'].parts['Part-1' + '-yx2']
    a.Instance(name='Part-1' + '-yx2-1', part=p, dependent=ON)
    p = mdb.models['Model-1'].parts['Part-1' + '-zy']
    a.Instance(name='Part-1' + '-zy-1', part=p, dependent=ON)

    #merge instances
    a = mdb.models['Model-1'].rootAssembly
    a.InstanceFromBooleanMerge(name='Part-1', instances=(
        a.instances[baseInstance], a.instances['Part-1' + '-xz11-1'], 
        a.instances['Part-1' + '-xz12-1'], a.instances['Part-1' + '-xz13-1'], 
        a.instances['Part-1' + '-xz14-1'], a.instances['Part-1' + '-yx1-1'], 
        a.instances['Part-1' + '-yx2-1'], a.instances['Part-1' + '-zy-1'], ), 
        originalInstances=DELETE, mergeNodes=BOUNDARY_ONLY, 
        nodeMergingTolerance=1e-06, domain=BOTH)

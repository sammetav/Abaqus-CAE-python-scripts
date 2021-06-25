
import numpy as np
import math
import os
import shutil
import sys
from abaqus import *
from abaqusConstants import *

from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()

sys.path.insert(1, 'G:/OlivermutualFolder/Copy/femframework/functions')
import function_general as fl 

# Filepath of the stepfile
step = mdb.openStep(
    'G:/OlivermutualFolder/StepFiles/quarter_2_50_BCC.stp', scaleFromFile=OFF)
mdb.models['Model-1'].PartFromGeometryFile(name='Part-1', geometryFile=step,
                                           combine=False, dimensionality=THREE_D, type=DEFORMABLE_BODY)


class Base:
    def __init__(self, density, Emoduli, poisson, size, direction, timePeriod, BoundaryCondition):
        self.density = density
        self.Emoduli = Emoduli
        self.poisson = poisson
        self.size = size
        self.direction = direction
        # self.magnitude=magnitude
        self.timePeriod = timePeriod
        self.BoundaryCondition = BoundaryCondition


# set of parameters to control the analysis
# size is the mesh seeding size
# Direction can be x, y, z, or Multi
# timePeriod is the time take for the whole step also can be used to control displacement while applying velocity BC
# BoundaryCondition can be displacement or velocity
# As EXPLICIT always try giving apt time period (Very small similar to 0.05)

#########################################

b = Base(2.7e-09, 70000, 0.33, 15, 'x', 0.06, 'velocity')
magnitude = [-300, -700, -500]
plasticity = ((350.0, 0.0, 0.0), (600.0, 0.02, 0.0), (650.0, 0.15, 0.0))
StrainRate = False
Contactplate = True
JobSubmit = False
ContactplateMeshSize=25  #For testing purpose
AmpData = ((0.0, 0.0), (b.timePeriod, 1.0))

#########################################
# multi velocity BC---Amplitude insertion
# surface to surface contact single and multi
# Test single and multi (quasi and dynamic)

mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Density(table=((b.density, ), ))
mdb.models['Model-1'].materials['Material-1'].Elastic(
    table=((b.Emoduli, b.poisson), ))

# mdb.models['Model-1'].Material(name='Material-1')
if StrainRate:
    mdb.models['Model-1'].materials['Material-1'].Plastic(rate=ON, table=plasticity)

if not StrainRate:
    mdb.models['Model-1'].materials['Material-1'].Plastic(rate=OFF, table=plasticity)

mdb.models['Model-1'].HomogeneousSolidSection(
    name='Section-1', material='Material-1', thickness=None)
p = mdb.models['Model-1'].parts['Part-1']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
region = p.Set(cells=cells, name='Set-1')
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
                    offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)


# Mehing of the part, the seed size must be kept above 1
p.seedPart(b.size, deviationFactor=0.1, minSizeFactor=0.1)
# c = p.cells
pickedRegions = c.getSequenceFromMask(mask=('[#1 ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)

# c = p.cells
# cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
pickedRegions = (cells, )
p.setElementType(regions=pickedRegions, elemTypes=(
    elemType1, elemType2, elemType3))
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
elemType1 = mesh.ElemType(elemCode=UNKNOWN_HEX, elemLibrary=EXPLICIT)
elemType2 = mesh.ElemType(elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT)
elemType3 = mesh.ElemType(elemCode=C3D10M, elemLibrary=EXPLICIT,
                          secondOrderAccuracy=OFF, distortionControl=DEFAULT)
# p = mdb.models['modelName'].parts['PartName']
# c = p.cells
# cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
pickedRegions = (cells, )
p.setElementType(regions=pickedRegions, elemTypes=(
    elemType1, elemType2, elemType3))

# Mirroring which is already implimented in easypbc
f = p.faces
p.Mirror(mirrorPlane=f[9], keepOriginal=ON)
f1 = p.faces
p.Mirror(mirrorPlane=f1[15], keepOriginal=ON)
f = p.faces
p.Mirror(mirrorPlane=f[28], keepOriginal=ON)
# session.viewports['Viewport: 1'].view.setValues(session.views['Iso'])

# Regenerate mesh
p.generateMesh()
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
a.Instance(name='Part-1-1', part=p, dependent=ON)


# Import Easypbc
sys.path.insert(15, r'c:/temp/abaqus_plugins/easypbc')
# mdb.models['modelName'].rootAssembly.features.changeKey(fromName='part-1-1-1', toName='Part-1-1')

# EasyPBC keep E33 true for the constraints
import easypbc
easypbc.feasypbc(part='Model-1', inst='Part-1-1', meshsens=1E-01, CPU=1,
    E11=True, E22=False, E33=False, G12=False, G13=False, G23=False,
    onlyPBC=True, CTE=False, intemp=0, fntemp=100)
#: ----------------------------------
#: -------- Start of EasyPBC --------
#: ----------------------------------
#: ------ End of Sets Creation ------
#: Job job-E33: Analysis Input File Processor completed successfully.
#: Job job-E33: Abaqus/Standard completed successfully.
#: Job job-E33 completed successfully.
#: Model: C:/temp/job-E33.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     1
#: Number of Meshes:             2
#: Number of Element Sets:       3
#: Number of Node Sets:          1101
#: Number of Steps:              1
#: ----------------------------------------------------
#: ----------------------------------------------------
#: The homogenised elastic properties:
#: E11=N/A Stress units
#: V12=N/A ratio
#: V13=N/A ratio
#: E22=N/A Stress units
#: V21=N/A ratio
#: V23=N/A ratio
#: E33=8.75561139633 Stress units
#: V31=0.976258391683 ratio
#: V32=0.972923808747 ratio
#: G12=N/A Stress units
#: G13=N/A Stress units
#: G23=N/A Stress units
#: CTE X=N/A N/A
#: CTE Y=N/A N/A
#: CTE Z=N/A N/A
#: ----------------------------------------------------
#: Total mass=8.70615705097e-06 Mass units
#: Homogenised density=1.39298482827e-10 Density units
#: ----------------------------------------------------
#: Processing duration 113.920000076 seconds
#: ----------------------------------------------------
#: The homogenised elastic properties are saved in ABAQUS Work Directory under modelName_elastic_properties.txt
#: Citation: Omairey S, Dunning P, Sriramula S (2018) Development of an ABAQUS plugin tool for periodic RVE homogenisation.
#: Engineering with Computers. https://doi.org/10.1007/s00366-018-0616-4
#: ----------------------------------------------------
#: ---------------------------------------
#: --------- End of EasyPBC (3D) ---------
#: ---------------------------------------

mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-1', previous='Initial',
    timePeriod=b.timePeriod, improvedDtMethod=ON)
mdb.models['Model-1'].steps['Step-1'].setValues(massScaling=((SEMI_AUTOMATIC, 
    MODEL, AT_BEGINNING, 2875.0, 0.0, None, 0, 0, 0.0, 0.0, 0, None), ), 
    improvedDtMethod=ON)

fl.pbcFixation(-35.355339, -35.355339, -50, 35.355339, 35.355339, 50, 'Model-1', 'Part-1-1', 0.4, 'Step-1', 'direction', True)

# surface creation
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['Part-1-1'].faces
side1Faces1 = s1.getSequenceFromMask(mask=('[#ffffffff #ffffff ]', ), )
a.Surface(side1Faces=side1Faces1, name='surface-1')
#: The surface 'surface-1' has been created (56 faces).

# Interaction - Self contact
mdb.models['Model-1'].ContactProperty('InteractionProperty-1')
mdb.models['Model-1'].interactionProperties['InteractionProperty-1'].TangentialBehavior(
    formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF,
    pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((
    0.0, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION,
    fraction=0.005, elasticSlipStiffness=None)
mdb.models['Model-1'].interactionProperties['InteractionProperty-1'].NormalBehavior(
    pressureOverclosure=HARD, allowSeparation=ON,
    constraintEnforcementMethod=DEFAULT)
#: The interaction property "InteractionProperty-1" has been created.
a = mdb.models['Model-1'].rootAssembly
region = a.surfaces['surface-1']
mdb.models['Model-1'].SelfContactExp(name='Int-1', createStepName='Step-1',
    surface=region, mechanicalConstraint=KINEMATIC,
    interactionProperty='InteractionProperty-1')
#: The interaction "Int-1" has been created.


'''#General contact
mdb.models['Model-1'].ContactExp(name='Int-2', createStepName='Step-1')
mdb.models['Model-1'].interactions['Int-2'].includedPairs.setValuesInStep(
    stepName='Step-1', useAllstar=ON)
mdb.models['Model-1'].interactions['Int-2'].contactPropertyAssignments.appendInStep(
    stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
#: The interaction "Int-2" has been created.'''

#####Amplitude######
mdb.models['Model-1'].TabularAmplitude(name='Amplitude-1', timeSpan=STEP,
    smooth=SOLVER_DEFAULT, data=AmpData)

if Contactplate:
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=100.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(35.0, 35.0), point2=(-35.0, -35.0))
    p = mdb.models['Model-1'].Part(name='Plate', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Plate']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['Plate']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['Model-1'].sketches['__profile__']
    mdb.models['Model-1'].Material(name='Plate_Material')
    mdb.models['Model-1'].materials['Plate_Material'].Density(table=((2.7e-09, ), 
        ))
    mdb.models['Model-1'].materials['Plate_Material'].Elastic(table=((900000.0, 
        0.33), ))
    mdb.models['Model-1'].HomogeneousShellSection(name='Section-2', 
        preIntegrate=OFF, material='Plate_Material', thicknessType=UNIFORM, 
        thickness=5.0, thicknessField='', nodalThicknessField='', 
        idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT, 
        thicknessModulus=None, temperature=GRADIENT, useDensity=OFF, 
        integrationRule=SIMPSON, numIntPts=5)
    p = mdb.models['Model-1'].parts['Plate']
    f = p.faces
    faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
    region = p.Set(faces=faces, name='Set-1')
    p = mdb.models['Model-1'].parts['Plate']
    p.SectionAssignment(region=region, sectionName='Section-2', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)



if b.direction == 'x' and b.BoundaryCondition == 'displacement':
    refpoint = 'RP4'
    displacement = 'U1'
    Reactionforce = 'RF1'
    magnitude = magnitude[0]
    a = mdb.models['Model-1'].rootAssembly
    region = a.sets[refpoint]
    mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', region=region, u1=magnitude, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET,
        ur3=UNSET, amplitude='Amplitude-1', fixed=OFF, distributionType=UNIFORM,
        fieldName='', localCsys=None)

    # F-Output-1 and H-Output-1 for RP6
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(
        numIntervals=100)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        displacement, ), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
        createStepName='Step-1', variables=(Reactionforce, ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)





    if Contactplate:
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='X_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['Plate'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        mdb.models['Model-1'].parts.changeKey(fromName='Plate', toName='X_Plate_Top')


        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        a.Instance(name='X_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('X_Plate_Bottom-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(0.0, 10.0, 0.0), angle=90.0)
        #: The instance X_Plate_Bottom-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 10., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('X_Plate_Bottom-1', ), vector=(18.0, 0.0, 0.0))
        #: The instance X_Plate_Bottom-1 was translated by 18., 0., 0. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        a.Instance(name='X_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('X_Plate_Top-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(0.0, 10.0, 0.0), angle=90.0)
        #: The instance X_Plate_Top-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 10., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('X_Plate_Top-1', ), vector=(-18.0, 0.0, 0.0))
        #: The instance X_Plate_Top-1 was translated by -18., 0., 0. with respect to the assembly coordinate system


        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['X_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='X-Plate-Lower')
        #: The set 'X-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['X_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='X-Plate-Upper')


        mdb.models['Model-1'].Equation(name='Constraint-x1', terms=((-1.0, 
            'X-Plate-Lower', 1), (0.5, 'RP4', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-x2', terms=((1.0, 
            'X-Plate-Upper', 1), (0.5, 'RP4', 1)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['X_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='x-plate-surface-Lower')
        #: The surface 'x-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['X_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='x-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).

        mdb.models['Model-1'].ContactExp(name='Int-2', createStepName='Step-1')
        mdb.models['Model-1'].interactions['Int-2'].includedPairs.setValuesInStep(
            stepName='Step-1', useAllstar=ON)
        mdb.models['Model-1'].interactions['Int-2'].contactPropertyAssignments.appendInStep(
            stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
        #: The interaction "Int-2" has been created.


        #Mesh
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        p.seedPart(size=ContactplateMeshSize, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        p.generateMesh()
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        p.seedPart(size=ContactplateMeshSize, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        p.generateMesh()


if b.direction == 'x' and b.BoundaryCondition == 'velocity':
    refpoint = 'RP4'
    displacement = 'U1'
    Reactionforce = 'RF1'
    magnitude = magnitude[0]
    a = mdb.models['Model-1'].rootAssembly
    region = a.sets[refpoint]
    mdb.models['Model-1'].VelocityBC(name='BC-1', createStepName='Step-1',
    region=region, v1=magnitude, v2=UNSET, v3=UNSET, vr1=UNSET, vr2=UNSET,
    vr3=UNSET, amplitude='Amplitude-1', localCsys=None, distributionType=UNIFORM,
    fieldName='')

        # F-Output-1 and H-Output-1 for RP6
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(
        numIntervals=100)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        displacement, ), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
        createStepName='Step-1', variables=(Reactionforce, ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)





    if Contactplate:
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='X_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['Plate'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        mdb.models['Model-1'].parts.changeKey(fromName='Plate', toName='X_Plate_Top')

        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        a.Instance(name='X_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('X_Plate_Bottom-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(0.0, 10.0, 0.0), angle=90.0)
        #: The instance X_Plate_Bottom-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 10., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('X_Plate_Bottom-1', ), vector=(18.0, 0.0, 0.0))
        #: The instance X_Plate_Bottom-1 was translated by 18., 0., 0. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        a.Instance(name='X_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('X_Plate_Top-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(0.0, 10.0, 0.0), angle=90.0)
        #: The instance X_Plate_Top-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 10., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('X_Plate_Top-1', ), vector=(-18.0, 0.0, 0.0))
        #: The instance X_Plate_Top-1 was translated by -18., 0., 0. with respect to the assembly coordinate system

        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['X_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='X-Plate-Lower')
        #: The set 'X-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['X_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='X-Plate-Upper')

        mdb.models['Model-1'].Equation(name='Constraint-x1', terms=((-1.0, 
            'X-Plate-Lower', 1), (0.5, 'RP4', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-x2', terms=((1.0, 
            'X-Plate-Upper', 1), (0.5, 'RP4', 1)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['X_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='x-plate-surface-Lower')
        #: The surface 'x-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['X_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='x-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).


        mdb.models['Model-1'].ContactExp(name='Int-2', createStepName='Step-1')
        mdb.models['Model-1'].interactions['Int-2'].includedPairs.setValuesInStep(
            stepName='Step-1', useAllstar=ON)
        mdb.models['Model-1'].interactions['Int-2'].contactPropertyAssignments.appendInStep(
            stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
        #: The interaction "Int-2" has been created.

        #Mesh
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        p.generateMesh()
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        p.generateMesh()


if b.direction == 'y' and b.BoundaryCondition == 'displacement':
    refpoint = 'RP5'
    displacement = 'U2'
    Reactionforce = 'RF2'
    magnitude = magnitude[1]
    a = mdb.models['Model-1'].rootAssembly
    region = a.sets[refpoint]
    mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', region=region, u1=UNSET, u2=magnitude, u3=UNSET, ur1=UNSET, ur2=UNSET,
        ur3=UNSET, amplitude='Amplitude-1', fixed=OFF, distributionType=UNIFORM,
        fieldName='', localCsys=None)

    # F-Output-1 and H-Output-1 for RP6
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(
        numIntervals=100)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        displacement, ), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
        createStepName='Step-1', variables=(Reactionforce, ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)




    if Contactplate:
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='Y_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['Plate'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        mdb.models['Model-1'].parts.changeKey(fromName='Plate', toName='Y_Plate_Top')

        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        a.Instance(name='Y_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('Y_Plate_Bottom-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        #: The instance Y_Plate_Bottom-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 10., 0., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Y_Plate_Bottom-1', ), vector=(0.0, 18.0, 0.0))
        #: The instance Y_Plate_Bottom-1 was translated by 0., 18., 0. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Y_Plate_Top']
        a.Instance(name='Y_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('Y_Plate_Top-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        #: The instance Y_Plate_Top-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 10., 0., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Y_Plate_Top-1', ), vector=(0.0, -18.0, 0.0))
        #: The instance Y_Plate_Top-1 was translated by 0., -18., 0. with respect to the assembly coordinate system

        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Y_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Y-Plate-Lower')
        #: The set 'X-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Y_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Y-Plate-Upper')

        mdb.models['Model-1'].Equation(name='Constraint-y1', terms=((-1.0, 
            'Y-Plate-Lower', 2), (0.5, 'RP5', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-y2', terms=((1.0, 
            'Y-Plate-Upper', 2), (0.5, 'RP5', 2)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Y_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='y-plate-surface-Lower')
        #: The surface 'x-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Y_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='y-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).

        mdb.models['Model-1'].ContactExp(name='Int-2', createStepName='Step-1')
        mdb.models['Model-1'].interactions['Int-2'].includedPairs.setValuesInStep(
            stepName='Step-1', useAllstar=ON)
        mdb.models['Model-1'].interactions['Int-2'].contactPropertyAssignments.appendInStep(
            stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
        #: The interaction "Int-2" has been created.

        #Mesh
        p = mdb.models['Model-1'].parts['Y_Plate_Top']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['Y_Plate_Top']
        p.generateMesh()
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        p.generateMesh()

if b.direction == 'y' and b.BoundaryCondition == 'velocity':
    refpoint = 'RP5'
    displacement = 'U3'
    Reactionforce = 'RF3'
    magnitude = magnitude[1]
    a = mdb.models['Model-1'].rootAssembly
    region = a.sets[refpoint]
    mdb.models['Model-1'].VelocityBC(name='BC-1', createStepName='Step-1',
    region=region, v1=UNSET, v2=magnitude, v3=UNSET, vr1=UNSET, vr2=UNSET,
    vr3=UNSET, amplitude='Amplitude-1', localCsys=None, distributionType=UNIFORM,
    fieldName='')

        # F-Output-1 and H-Output-1 for RP6
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(
        numIntervals=100)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        displacement, ), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
        createStepName='Step-1', variables=(Reactionforce, ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)



    if Contactplate:
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='Y_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['Plate'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        mdb.models['Model-1'].parts.changeKey(fromName='Plate', toName='Y_Plate_Top')

        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        a.Instance(name='Y_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('Y_Plate_Bottom-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        #: The instance Y_Plate_Bottom-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 10., 0., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Y_Plate_Bottom-1', ), vector=(0.0, 18.0, 0.0))
        #: The instance Y_Plate_Bottom-1 was translated by 0., 18., 0. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Y_Plate_Top']
        a.Instance(name='Y_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('Y_Plate_Top-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        #: The instance Y_Plate_Top-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 10., 0., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Y_Plate_Top-1', ), vector=(0.0, -18.0, 0.0))
        #: The instance Y_Plate_Top-1 was translated by 0., -18., 0. with respect to the assembly coordinate system

        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Y_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Y-Plate-Lower')
        #: The set 'X-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Y_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Y-Plate-Upper')

        mdb.models['Model-1'].Equation(name='Constraint-y1', terms=((-1.0, 
            'Y-Plate-Lower', 2), (0.5, 'RP5', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-y2', terms=((1.0, 
            'Y-Plate-Upper', 2), (0.5, 'RP5', 2)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Y_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='y-plate-surface-Lower')
        #: The surface 'x-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Y_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='y-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).

        mdb.models['Model-1'].ContactExp(name='Int-2', createStepName='Step-1')
        mdb.models['Model-1'].interactions['Int-2'].includedPairs.setValuesInStep(
            stepName='Step-1', useAllstar=ON)
        mdb.models['Model-1'].interactions['Int-2'].contactPropertyAssignments.appendInStep(
            stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
        #: The interaction "Int-2" has been created.

        #Mesh
        p = mdb.models['Model-1'].parts['Y_Plate_Top']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['Y_Plate_Top']
        p.generateMesh()
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        p.generateMesh()





if b.direction == 'z' and b.BoundaryCondition == 'displacement':
    refpoint = 'RP6'
    displacement = 'U3'
    Reactionforce = 'RF3'
    magnitude = magnitude[2]
    a = mdb.models['Model-1'].rootAssembly
    region = a.sets[refpoint]
    mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', region=region, u1=UNSET, u2=UNSET, u3=magnitude, ur1=UNSET, ur2=UNSET,
        ur3=UNSET, amplitude='Amplitude-1', fixed=OFF, distributionType=UNIFORM,
        fieldName='', localCsys=None)

        # F-Output-1 and H-Output-1 for RP6
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(
        numIntervals=100)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        displacement, ), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef = mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
        createStepName='Step-1', variables=(Reactionforce, ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)




    if Contactplate:
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='Z_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['Plate'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        mdb.models['Model-1'].parts.changeKey(fromName='Plate', toName='Z_Plate_Top')

        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        a.Instance(name='Z_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Z_Plate_Bottom-1', ), vector=(0.0, 0.0, 25.0))
        #: The instance Z_Plate_Bottom-1 was translated by 0., 0., 25. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Z_Plate_Top']
        a.Instance(name='Z_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Z_Plate_Top-1', ), vector=(0.0, 0.0, -25.0))
        #: The instance Z_Plate_Top-1 was translated by 0., 0., -25. with respect to the assembly coordinate system

        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Z_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Z-Plate-Lower')
        #: The set 'Z-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Z_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Z-Plate-Upper')

        mdb.models['Model-1'].Equation(name='Constraint-z1', terms=((-1.0, 
            'Z-Plate-Lower', 3), (0.5, 'RP6', 3)))
        mdb.models['Model-1'].Equation(name='Constraint-z2', terms=((1.0, 
            'Z-Plate-Upper', 3), (0.5, 'RP6', 3)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Z_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='z-plate-surface-Lower')
        #: The surface 'z-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Z_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='z-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).

        mdb.models['Model-1'].ContactExp(name='Int-2', createStepName='Step-1')
        mdb.models['Model-1'].interactions['Int-2'].includedPairs.setValuesInStep(
            stepName='Step-1', useAllstar=ON)
        mdb.models['Model-1'].interactions['Int-2'].contactPropertyAssignments.appendInStep(
            stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
        #: The interaction "Int-2" has been created.

        #Mesh
        p = mdb.models['Model-1'].parts['Z_Plate_Top']
        p.seedPart(size=ContactplateMeshSize, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['Z_Plate_Top']
        p.generateMesh()
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        p.seedPart(size=ContactplateMeshSize, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        p.generateMesh()



if b.direction == 'z' and b.BoundaryCondition == 'velocity':
    refpoint='RP6'
    displacement='U3'
    Reactionforce='RF3'
    magnitude=magnitude[2]
    a=mdb.models['Model-1'].rootAssembly
    region=a.sets[refpoint]
    mdb.models['Model-1'].VelocityBC(name='BC-1', createStepName='Step-1',
    region=region, v1=UNSET, v2=UNSET, v3=magnitude, vr1=UNSET, vr2=UNSET,
    vr3=UNSET, amplitude='Amplitude-1', localCsys=None, distributionType=UNIFORM,
    fieldName='')


    # F-Output-1 and H-Output-1 for RP6
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(
        numIntervals=100)
    regionDef=mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        displacement, ), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets[refpoint]
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
        createStepName='Step-1', variables=(Reactionforce, ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)




    if Contactplate:
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='Z_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['Plate'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        mdb.models['Model-1'].parts.changeKey(fromName='Plate', toName='Z_Plate_Top')

        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        a.Instance(name='Z_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Z_Plate_Bottom-1', ), vector=(0.0, 0.0, 25.0))
        #: The instance Z_Plate_Bottom-1 was translated by 0., 0., 25. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Z_Plate_Top']
        a.Instance(name='Z_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Z_Plate_Top-1', ), vector=(0.0, 0.0, -25.0))
        #: The instance Z_Plate_Top-1 was translated by 0., 0., -25. with respect to the assembly coordinate system

        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Z_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Z-Plate-Lower')
        #: The set 'Z-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Z_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Z-Plate-Upper')

        mdb.models['Model-1'].Equation(name='Constraint-z1', terms=((-1.0, 
            'Z-Plate-Lower', 3), (0.5, 'RP6', 3)))
        mdb.models['Model-1'].Equation(name='Constraint-z2', terms=((1.0, 
            'Z-Plate-Upper', 3), (0.5, 'RP6', 3)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Z_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='z-plate-surface-Lower')
        #: The surface 'z-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Z_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='z-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).

        mdb.models['Model-1'].ContactExp(name='Int-2', createStepName='Step-1')
        mdb.models['Model-1'].interactions['Int-2'].includedPairs.setValuesInStep(
            stepName='Step-1', useAllstar=ON)
        mdb.models['Model-1'].interactions['Int-2'].contactPropertyAssignments.appendInStep(
            stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
        #: The interaction "Int-2" has been created.

        #Mesh
        p = mdb.models['Model-1'].parts['Z_Plate_Top']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['Z_Plate_Top']
        p.generateMesh()
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        p.generateMesh()



if b.direction == 'Multi' and b.BoundaryCondition == 'displacement':
    displacement='U3'
    Reactionforce='RF3'

    a=mdb.models['Model-1'].rootAssembly
    region=a.sets['RP4']
    mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
        region=region, u1=magnitude[0], u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET,
        ur3=UNSET, amplitude='Amplitude-1', fixed=OFF, distributionType=UNIFORM,
        fieldName='', localCsys=None)
    a=mdb.models['Model-1'].rootAssembly
    region=a.sets['RP5']
    mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
        region=region, u1=UNSET, u2=magnitude[1], u3=UNSET, ur1=UNSET, ur2=UNSET,
        ur3=UNSET, amplitude='Amplitude-1', fixed=OFF, distributionType=UNIFORM,
        fieldName='', localCsys=None)
    a=mdb.models['Model-1'].rootAssembly
    region=a.sets['RP6']
    mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
        region=region, u1=UNSET, u2=UNSET, u3=magnitude[2], ur1=UNSET, ur2=UNSET,
        ur3=UNSET, amplitude='Amplitude-1', fixed=OFF, distributionType=UNIFORM,
        fieldName='', localCsys=None)

        # F-Output-1 and H-Output-1 for RP4, RP5, RP6
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP4']
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        'RF1', ), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP4']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
        createStepName='Step-1', variables=('U1', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP5']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-3',
        createStepName='Step-1', variables=('RF2', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP5']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-4',
        createStepName='Step-1', variables=('U2', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP6']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-5',
        createStepName='Step-1', variables=('RF3', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP6']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-6',
        createStepName='Step-1', variables=('U3', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)



    if Contactplate:
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='X_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['Plate'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['Plate']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        mdb.models['Model-1'].parts.changeKey(fromName='Plate', toName='X_Plate_Top')


        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        a.Instance(name='X_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('X_Plate_Bottom-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(0.0, 10.0, 0.0), angle=90.0)
        #: The instance X_Plate_Bottom-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 10., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('X_Plate_Bottom-1', ), vector=(18.0, 0.0, 0.0))
        #: The instance X_Plate_Bottom-1 was translated by 18., 0., 0. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        a.Instance(name='X_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('X_Plate_Top-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(0.0, 10.0, 0.0), angle=90.0)
        #: The instance X_Plate_Top-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 10., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('X_Plate_Top-1', ), vector=(-18.0, 0.0, 0.0))
        #: The instance X_Plate_Top-1 was translated by -18., 0., 0. with respect to the assembly coordinate system


        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['X_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='X-Plate-Lower')
        #: The set 'X-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['X_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='X-Plate-Upper')


        mdb.models['Model-1'].Equation(name='Constraint-x1', terms=((-1.0, 
            'X-Plate-Lower', 1), (0.5, 'RP4', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-x2', terms=((1.0, 
            'X-Plate-Upper', 1), (0.5, 'RP4', 1)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['X_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='x-plate-surface-Lower')
        #: The surface 'x-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['X_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='x-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).


        #Mesh
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['X_Plate_Top']
        p.generateMesh()
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
        p = mdb.models['Model-1'].parts['X_Plate_Bottom']
        p.generateMesh()

        #y plate
        p1 = mdb.models['Model-1'].parts['X_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='Y_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['X_Plate_Bottom'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['X_Plate_Top']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='Y_Plate_Top', 
            objectToCopy=mdb.models['Model-1'].parts['X_Plate_Top'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)

        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Y_Plate_Bottom']
        a.Instance(name='Y_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('Y_Plate_Bottom-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        #: The instance Y_Plate_Bottom-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 10., 0., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Y_Plate_Bottom-1', ), vector=(0.0, 18.0, 0.0))
        #: The instance Y_Plate_Bottom-1 was translated by 0., 18., 0. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Y_Plate_Top']
        a.Instance(name='Y_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.rotate(instanceList=('Y_Plate_Top-1', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        #: The instance Y_Plate_Top-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 10., 0., 0.
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Y_Plate_Top-1', ), vector=(0.0, -18.0, 0.0))
        #: The instance Y_Plate_Top-1 was translated by 0., -18., 0. with respect to the assembly coordinate system

        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Y_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Y-Plate-Lower')
        #: The set 'X-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Y_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Y-Plate-Upper')

        mdb.models['Model-1'].Equation(name='Constraint-y1', terms=((-1.0, 
            'Y-Plate-Lower', 2), (0.5, 'RP5', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-y2', terms=((1.0, 
            'Y-Plate-Upper', 2), (0.5, 'RP5', 2)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Y_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='y-plate-surface-Lower')
        #: The surface 'x-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Y_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='y-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).

        #z plate
        p1 = mdb.models['Model-1'].parts['X_Plate_Bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='Z_Plate_Bottom', 
            objectToCopy=mdb.models['Model-1'].parts['X_Plate_Bottom'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        p1 = mdb.models['Model-1'].parts['X_Plate_Top']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].Part(name='Z_Plate_Top', 
            objectToCopy=mdb.models['Model-1'].parts['X_Plate_Top'])
        session.viewports['Viewport: 1'].setValues(displayedObject=p)

        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Z_Plate_Bottom']
        a.Instance(name='Z_Plate_Bottom-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Z_Plate_Bottom-1', ), vector=(0.0, 0.0, 25.0))
        #: The instance Z_Plate_Bottom-1 was translated by 0., 0., 25. with respect to the assembly coordinate system
        a = mdb.models['Model-1'].rootAssembly
        p = mdb.models['Model-1'].parts['Z_Plate_Top']
        a.Instance(name='Z_Plate_Top-1', part=p, dependent=ON)
        a = mdb.models['Model-1'].rootAssembly
        a.translate(instanceList=('Z_Plate_Top-1', ), vector=(0.0, 0.0, -25.0))
        #: The instance Z_Plate_Top-1 was translated by 0., 0., -25. with respect to the assembly coordinate system

        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Z_Plate_Bottom-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Z-Plate-Lower')
        #: The set 'Z-Plate-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        f1 = a.instances['Z_Plate_Top-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Set(faces=faces1, name='Z-Plate-Upper')

        mdb.models['Model-1'].Equation(name='Constraint-z1', terms=((-1.0, 
            'Z-Plate-Lower', 3), (0.5, 'RP6', 3)))
        mdb.models['Model-1'].Equation(name='Constraint-z2', terms=((1.0, 
            'Z-Plate-Upper', 3), (0.5, 'RP6', 3)))

        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Z_Plate_Bottom-1'].faces
        side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side2Faces=side2Faces1, name='z-plate-surface-Lower')
        #: The surface 'z-plate-surface-Lower' has been created (1 face).
        a = mdb.models['Model-1'].rootAssembly
        s1 = a.instances['Z_Plate_Top-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
        a.Surface(side1Faces=side1Faces1, name='z-plate-suraface-upper')
        #: The surface 'x-plate-suraface-upper' has been created (1 face).


    mdb.models['Model-1'].ContactExp(name='Int-8', createStepName='Step-1')
    mdb.models['Model-1'].interactions['Int-8'].includedPairs.setValuesInStep(
        stepName='Step-1', useAllstar=ON)
    r11=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r12=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r21=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r22=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r31=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r32=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r41=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r42=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r51=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r52=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r61=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r62=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r71=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r72=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r81=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r82=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r91=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r92=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r101=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r102=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r111=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r112=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r121=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r122=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r131=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r132=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r141=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r142=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r151=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r152=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r161=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r162=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r171=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r172=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r181=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r182=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r191=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r192=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r201=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r202=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r211=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r212=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r221=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r222=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r231=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r232=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r241=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r242=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']

    mdb.models['Model-1'].interactions['Int-8'].excludedPairs.setValuesInStep(
    stepName='Step-1', addPairs=((r11, r12), (r21, r22), (r31, r32), (r41, 
    r42), (r51, r52), (r61, r62), (r71, r72), (r81, r82), (r91, r92), (r101, 
    r102), (r111, r112), (r121, r122), (r131, r132), (r141, r142), (r151, 
    r152), (r161, r162), (r171, r172), (r181, r182), (r191, r192), (r201, 
    r202), (r211, r212), (r221, r222), (r231, r232), (r241, r242)))
    mdb.models['Model-1'].interactions['Int-8'].contactPropertyAssignments.appendInStep(
        stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
    #: The interaction "Int-8" has been created.


if b.direction == 'Multi' and b.BoundaryCondition == 'velocity':

    a=mdb.models['Model-1'].rootAssembly
    region=a.sets['RP4']
    mdb.models['Model-1'].VelocityBC(name='BC-1', createStepName='Step-1',
        region=region, v1=magnitude[0], v2=UNSET, v3=UNSET, vr1=UNSET, vr2=UNSET,
        vr3=UNSET, amplitude=UNSET, localCsys=None, distributionType=UNIFORM,
        fieldName='')
    a=mdb.models['Model-1'].rootAssembly
    region=a.sets['RP5']
    mdb.models['Model-1'].VelocityBC(name='BC-2', createStepName='Step-1',
        region=region, v1=UNSET, v2=magnitude[1], v3=UNSET, vr1=UNSET, vr2=UNSET,
        vr3=UNSET, amplitude=UNSET, localCsys=None, distributionType=UNIFORM,
        fieldName='')
    a=mdb.models['Model-1'].rootAssembly
    region=a.sets['RP6']
    mdb.models['Model-1'].VelocityBC(name='BC-3', createStepName='Step-1',
        region=region, v1=UNSET, v2=UNSET, v3=magnitude[2], vr1=UNSET, vr2=UNSET,
        vr3=UNSET, amplitude=UNSET, localCsys=None, distributionType=UNIFORM,
        fieldName='')

        # F-Output-1 and H-Output-1 for RP4, RP5, RP6
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP4']
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        'RF1', ), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP4']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
        createStepName='Step-1', variables=('U1', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP5']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-3',
        createStepName='Step-1', variables=('RF2', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP5']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-4',
        createStepName='Step-1', variables=('U2', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP6']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-5',
        createStepName='Step-1', variables=('RF3', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)
    regionDef=mdb.models['Model-1'].rootAssembly.sets['RP6']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-6',
        createStepName='Step-1', variables=('U3', ), region=regionDef,
        sectionPoints=DEFAULT, rebar=EXCLUDE)



    mdb.models['Model-1'].ContactExp(name='Int-8', createStepName='Step-1')
    mdb.models['Model-1'].interactions['Int-8'].includedPairs.setValuesInStep(
        stepName='Step-1', useAllstar=ON)
    r11=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r12=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r21=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r22=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r31=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r32=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r41=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r42=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r51=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r52=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r61=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r62=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r71=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r72=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r81=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r82=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r91=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r92=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r101=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r102=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r111=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r112=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r121=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r122=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r131=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r132=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r141=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r142=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r151=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r152=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r161=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r162=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r171=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r172=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r181=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r182=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r191=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r192=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r201=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-suraface-upper']
    r202=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']
    r211=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r212=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-suraface-upper']
    r221=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r222=mdb.models['Model-1'].rootAssembly.surfaces['x-plate-surface-Lower']
    r231=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r232=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-suraface-upper']
    r241=mdb.models['Model-1'].rootAssembly.surfaces['z-plate-surface-Lower']
    r242=mdb.models['Model-1'].rootAssembly.surfaces['y-plate-surface-Lower']

    mdb.models['Model-1'].interactions['Int-8'].excludedPairs.setValuesInStep(
    stepName='Step-1', addPairs=((r11, r12), (r21, r22), (r31, r32), (r41, 
    r42), (r51, r52), (r61, r62), (r71, r72), (r81, r82), (r91, r92), (r101, 
    r102), (r111, r112), (r121, r122), (r131, r132), (r141, r142), (r151, 
    r152), (r161, r162), (r171, r172), (r181, r182), (r191, r192), (r201, 
    r202), (r211, r212), (r221, r222), (r231, r232), (r241, r242)))
    mdb.models['Model-1'].interactions['Int-8'].contactPropertyAssignments.appendInStep(
        stepName='Step-1', assignments=((GLOBAL, SELF, 'InteractionProperty-1'), ))
    #: The interaction "Int-8" has been created.


# Job creation and submission
if JobSubmit:
    mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS,
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
    memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
    nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
    contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
    resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=1,
    activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1)
    mdb.jobs['Job-1'].submit(consistencyChecking=OFF)

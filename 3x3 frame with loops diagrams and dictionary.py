# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 14:01:24 2022

@author: bruno
"""

#____________________________SETTING UP MODEL_________________________________

import openseespy.opensees as ops #importing opensees library
import openseespy.postprocessing.ops_vis as opsvis #importing opensees visualization library

import matplotlib.pyplot as plt #importing python module to plot general stuff
import openseespy.postprocessing.Get_Rendering as opsplt
ops.wipe() #cleaning model before running analysis

#-------------Change line below if model is in 3D-----------------------------

ops.model('basic','-ndm',2,'-ndf',3) #creating model


#____________________________SETTING UP UNITS_________________________________
#-------------Results of this analysis will be in inch, lbs, psi, change below if needed
inch = 1.
ft = 12*inch
lb = 1.
kip = 1000*lb
plf = 1*lb/(1*ft)
klf = 1*kip/(1*ft)
ksi = 1000*lb/inch**2

beamL = 24*ft
colL = 12*ft
E = 29000*ksi
I = 758*inch**4
A = 100*inch**2



#_____________________SETTING UP NODES AND CONNECTIVITY________________________

#Build nodes left to right, bottom to top

print('node generation below')

for y in range(0,40,10):
    for x in range(0,4): 
        ops.node((x+y),x*beamL,y/10*colL)
        print(x+y)
        
#support definition
for f in range(0,4):
    ops.fix(f,1,1,1)

ops.geomTransf('Linear',1,) #transforms stiffness and force from local to global coords

#column definition
n=0 #counter for columns
for vert in range(0,30,10):
    for hor in range(0,4):
        n=n+1
        ops.element('elasticBeamColumn',n,hor+vert,hor+vert+10,A,E,I,1)

print('Final column tag is')
print(n)

#beam definition
m=0 #counter for beams
for vert in range(10,40,10):
    for hor in range(0,3):
        m=m+1
        ops.element('elasticBeamColumn',m+n,hor+vert,hor+vert+1,A,E,I,1)
        
print('Final beam tag is')
print(m+n)        
        
#element(’elasticBeamColumn’, eleTag, *eleNodes, Area, E_mod, Iz, transfTag, <’-mass’, mass>, <’-cMass’>, <’-release’, releaseCode>)
#ops.element('elasticBeamColumn',1,1,2,A,E,I,1)

#creating TimeSeries (relationship between time and load)
ops.timeSeries('Linear',1)
ops.pattern('Plain',1,1)

#load format is  ops.load(nodetag,Px,Py,Mz)

ops.load(10,1.5*kip,0,0)
ops.load(20,3*kip,0,0)
ops.load(30,4.5*kip,0,0)

Wy = -1.1*klf
Wx = 0.
Ew = {1:['-beamUniform',Wy,Wx]}

for dead in range(13,22):
    ops.eleLoad('-ele',dead,'-type',Ew[1][0],Ew[1][1],Ew[1][2])

#_______________TYPE OF ANALYSIS____________

ops.system('BandGen') #has to do with stiffness matrix and if its banded
ops.numberer('RCM') #provides mapping between dof at nodes and equation numbers
ops.constraints('Plain') #constraint handler
ops.integrator('LoadControl',1.0) #can be load control, or displacement control
ops.algorithm('Linear') #linear takes one iteration, this is where newton-raphson could be used
ops.analysis('Static') #type of analysis
ops.analyze(1)
#ops.loadConst('-time',0.0)



print('Displacements at top level')
print(ops.nodeDisp(30,1))
print(ops.nodeDisp(30,2))
print(ops.nodeDisp(30,3))

print('Displacement at 3rd level')
print(ops.nodeDisp(20,1))
print(ops.nodeDisp(20,2))
print(ops.nodeDisp(20,3))

print('Displacement at 2nd level')
print(ops.nodeDisp(10,1))
print(ops.nodeDisp(10,2))
print(ops.nodeDisp(10,3))

print('Displacement at base level')
print(ops.nodeDisp(0,1))
print(ops.nodeDisp(0,2))
print(ops.nodeDisp(0,3))


opsplt.plot_model()
opsvis.plot_defo()



plt.figure()
minVal,maxVal = opsvis.section_force_diagram_2d('M',Ew,4.5e-5)
plt.title(f'Bending moments,max ={maxVal:.2f}, min ={minVal:.2f}')

plt.show()

'''
Created on 2012-12-02

@author: Claude Vervoort
'''

import FabricEngine.Core
import FabricEngine.CreationPlatform
import FabricEngine.CreationPlatform.RT
import FabricEngine.CreationPlatform.RT.Math

from FabricEngine.CreationPlatform.RT.Math.Vec3Impl import Vec3

import copy

FabricCoreClient = FabricEngine.Core.createClient()

# Not sure why we need to register those types again, to strip the preprocessor? Had to remove vec3 from math.kl to get it to compile
# Code as per Particle Demo
def registerType(name, desc):
    """Registers a new data type by a given name and description dictionary."""
    # we make a deep copy here because we will remove members from the desc during registration.
    desc = copy.deepcopy(desc)
    constructor = desc['constructor']
    if desc.has_key('klBindings'):
        klCode = desc['klBindings']
        if klCode.has_key('fileName'):
            klCode['sourceCode'] = open(klCode['fileName']).read()
            klCode['filename'] = klCode['fileName']
            del klCode['fileName']
        if klCode.has_key('sourceCode') and klCode.has_key('preProcessorDefinitions'):
            for defName in klCode['preProcessorDefinitions']:
                klCode['sourceCode'] = klCode['sourceCode'].replace(defName, klCode['preProcessorDefinitions'][defName])
                del klCode['preProcessorDefinitions']
    print name
    FabricCoreClient.RegisteredTypesManager.registerType( name, copy.deepcopy(desc) )
    return constructor

for regType in FabricEngine.CreationPlatform.RT.getRegisteredTypes():
    registerType(regType['name'], regType['desc'] )


gol = FabricCoreClient.DG.createNode('gol')
gol.addMember('halfBoundingBox', 'Size', 3)
gol.addMember('spawnInterval', 'Size', 10)
gol.addMember('numPoints', 'Size')
gol.addMember('positions', 'Integer[100000][3]')

timerNode = FabricCoreClient.DG.createNode('timer')
timerNode.addMember('time', 'Float32', 0)

gol.setDependency('timer', timerNode)

golOperator = FabricCoreClient.DG.createOperator('GameOfLife')
golOperator.setEntryPoint('GameOfLife')
golOperator.setSourceCode(open('GameOfLifeArrayInfluenceMap.kl').read())

binding = FabricCoreClient.DG.createBinding()
binding.setOperator(golOperator)
binding.setParameterLayout([
 'timer.time',
 'self.spawnInterval',
 'self.halfBoundingBox',
 'self.numPoints',
 'self.positions'
])

gol.bindings.append(binding)


transform = FabricCoreClient.DG.createOperator('transform')
transform.addMember('globalXfo', 'Xfo') #hanging here...
transform.setEntryPoint('fromGridCoordToSlicedTransform')
transform.setSourceCode(open('FromGridCoordToSlicedTransform.kl').read())
transform.setDependency('grid', gol )
bindings = FabricCoreClient.DG.createBinding()
binding.setOperator(transform)
binding.setParameterLayout([
 'gol.positions',
 'gol.numPoints',
 'self',
 'self.globalXfo<>'
])

transform.bindings.append(binding)

# Simulate 100 frames
print "starting 100 iterations"
for i in range(0, 100):
    timerNode.setData('time', i*0.1)
    transform.evaluate()
    print 'At frame: {0}, there are: {1} points and bounding box is {2}'.format(i, gol.getData('numPoints'), gol.getData('halfBoundingBox'))

FabricCoreClient.close()
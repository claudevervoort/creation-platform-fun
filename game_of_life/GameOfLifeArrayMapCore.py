'''
Created on 2012-12-02

@author: Claude Vervoort
'''

import FabricEngine.Core

FabricCoreClient = FabricEngine.Core.createClient()
pointsNode = FabricCoreClient.DG.createNode('points')
pointsNode.addMember(memberName='halfBoundingBox', memberType='Size', defaultValue=3)
pointsNode.addMember(memberName='spawnInterval', memberType='Size', defaultValue=10)
pointsNode.addMember('numPoints', 'Size')
pointsNode.addMember('positions', 'Integer[100000][3]')

timerNode = FabricCoreClient.DG.createNode('timer')
timerNode.addMember('frame', 'Integer', 0)

pointsNode.setDependency(dependencyNode=timerNode, dependencyName='timer')

golOperator = FabricCoreClient.DG.createOperator('GameOfLife')
golOperator.setEntryPoint('GameOfLife')
golOperator.setSourceCode('None', sourceCode = open('GameOfLifeArrayInfluenceMap.kl').read())

binding = FabricCoreClient.DG.createBinding()
binding.setOperator(golOperator)
binding.setParameterLayout([
 'timer.frame',
 'self.spawnInterval',
 'self.halfBoundingBox',
 'self.numPoints',
 'self.positions'
])

pointsNode.bindings.append(binding)

# Simulate 100 frames
for i in range(0, 100):
    timerNode.setData('frame', i)
    pointsNode.evaluate()
    print 'At frame: {0}, there are: {1} points and bounding box is {2}'.format(i, pointsNode.getData('numPoints'), pointsNode.getData('halfBoundingBox'))

    
FabricCoreClient.close()
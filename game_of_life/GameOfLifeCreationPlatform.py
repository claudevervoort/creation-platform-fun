import FabricEngine.CreationPlatform
from FabricEngine.CreationPlatform.PySide import *
from FabricEngine.CreationPlatform.Nodes.Rendering import *
from FabricEngine.CreationPlatform.Nodes.Lights import *
from FabricEngine.CreationPlatform.Nodes.Kinematics.TransformImpl import Transform
from FabricEngine.CreationPlatform.Nodes.Primitives.PolygonMeshCuboidImpl import PolygonMeshCuboid
from FabricEngine.CreationPlatform.RT.Math import *

# Could be abstracted into a based class that returns points in grid coord (integer[3])
class GameOfLife(SceneGraphNode):
	def __init__(self, scene, timeCPNode, **options):
		super(GameOfLife, self).__init__(scene, **options)
		dgNode = self.constructDGNode()
		dgNode.addMember('halfBoundingBox', 'Size', 3)
		dgNode.addMember('spawnInterval', 'Size', 10)
		dgNode.addMember('numPoints', 'Size')
		dgNode.addMember('positions', 'Integer[100000][3]')
		def __onChangeTimeCallback(data):
			timeController = data['node']
			self.getDGNode().setDependency( timeController.getDGNode(), 'time')
		self.addReferenceInterface(name='Time', cls=Time, isList=False, changeCallback=__onChangeTimeCallback)
		self.setTimeNode( timeCPNode );
		self.bindDGOperator(dgNode.bindings,
						name = 'GameOfLife',
						fileName = FabricEngine.CreationPlatform.buildAbsolutePath('GameOfLifeArrayInfluenceMap.kl'),
						layout =[
						 'time.time',
						 'self.spawnInterval',
						 'self.halfBoundingBox',
						 'self.numPoints',
						 'self.positions'
						])
		

		
# Does the translation from Grid Coord to Global Transform Sliced so that it can be fed into GeometryInstance
# Re-uses the original Transform but substitute the KL logic, and adds a new reference interface to hook in the GOL
# Will need a Scale input (as it seems it cannot be set as a member it is sliced data). For the time being the Scale
# is hard coded in the KL Operator
class GridCoordToTransform(Transform):
	def __init__(self, scene, gol, scale, **options):
		super(GridCoordToTransform, self).__init__(scene, **options)
		dgNode = self.getDGNode()
		dgNode.addMember('scale', 'Vec3', scale) #unused now, seems this approach does not work with the sliced mode used here
		#dgNode.addMember('globalXfo', 'Xfo') already defined by the DG Node created in Base Transform
		def __onChangeGOLCallback(data):
			golCPNode = data['node']
			self.getDGNode().setDependency( golCPNode.getDGNode(), 'gol')
		self.addReferenceInterface(name='GOL', cls=GameOfLife, isList=False, changeCallback=__onChangeGOLCallback)
		self.setGOLNode(gol)
		self.bindDGOperator(dgNode.bindings,
						name = 'fromGridCoordToSlicedTransform',
						fileName = FabricEngine.CreationPlatform.buildAbsolutePath('FromGridCoordToSlicedTransform.kl'),
						layout =[
						 'gol.positions',
						 'gol.numPoints',
						 'self',
						 'self.globalXfo<>'
						], index=0)


class GameOfLifeCreationPlatform(CreationPlatformApplication):
	def __init__(self):	  
		super(GameOfLifeCreationPlatform, self).__init__(
	      cameraPosition=Vec3(4, 7, 10),
	      setupSelection = True,
	      setupGrid=True,
	      setupGlobalTimeNode=True,
	      timeRange=Vec2(0.0,10.0),
	      fps = 5
	    )
		self.setWindowTitle("Creation Platform Game Of Life")
		self.resize(1000,600)
		
		scene = self.getScene()
		
		golNode = GameOfLife(scene, self.getGlobalTimeNode())
		
		scale = Vec3(0.5,0.5,0.5)
		
		gridToXfoNode = GridCoordToTransform( scene, golNode, scale)
		
		# create the shaders
		phongMaterial = Material(scene, xmlFile='PhongMaterial')
		phongMaterial.addPreset(name='red',diffuseColor=Color(1.0,0.0,0.0))
		
		#transform = Transform(scene)
		#transform.getDGNode().setCount(2)
		#transform.setGlobalXfo(Xfo(Vec3(-50, 10, 0),Quat(),Vec3(1.0,1.0,1.0)),0)
		#transform.setGlobalXfo(Xfo(Vec3(-30, 0, 0),Quat(),Vec3(1.0,1.0,1.0)),1)
							
		GeometryInstance(scene,
	  			geometry=PolygonMeshCuboid(scene,
										   length=1.0,
										   width= 1.0,
										   height=1.0
	  			),
	  			transform=gridToXfoNode,
	  			transformIndex=-1,
	  			material=phongMaterial,
	  	  		materialPreset='red'
		)
		# check for errors
		self.constructionCompleted()
		
GameOfLifeCreationPlatform().exec_()	
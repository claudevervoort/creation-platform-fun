import FabricEngine.CreationPlatform
from FabricEngine.CreationPlatform.PySide import *
from FabricEngine.CreationPlatform.Nodes.Kinematics.TransformImpl import Transform
from FabricEngine.CreationPlatform.Nodes.Primitives.PolygonMeshCuboidImpl import PolygonMeshCuboid
from FabricEngine.CreationPlatform.Nodes.SceneGraphNodeImpl import SceneGraphNode
from FabricEngine.CreationPlatform.Nodes.Rendering.CameraImpl import Camera


# Could be abstracted into a based class that returns points in grid coord (integer[3])
class GameOfLife(SceneGraphNode):
	def __init__(self, scene, timeCPNode, **options):
		super(GameOfLife, self).__init__(scene, **options)
		dgNode = self.constructDGNode()
		dgNode.addMember('halfBoundingBox', 'Size', 3)
		dgNode.addMember('spawnInterval', 'Size', 7)
		dgNode.addMember('numPoints', 'Size')
		dgNode.addMember('positions', 'Integer[100000][3]')
		dgNode.addMember( 'step', 'Integer', 1 ); #update every 1 second
		self._addMemberInterface(self.getDGNode(), 'step', True)
		dgNode.addMember( 'min', 'Size', 3 ); #Less than 3, die!
		self._addMemberInterface(self.getDGNode(), 'min', True)
		dgNode.addMember( 'max', 'Size', 6 ); #More than 6, die!
		self._addMemberInterface(self.getDGNode(), 'max', True)
		dgNode.addMember( 'spawn', 'Size', 5 ); #Spawn at 5
		self._addMemberInterface(self.getDGNode(), 'spawn', True)
		def __onChangeTimeCallback(data):
			timeController = data['node']
			self.getDGNode().setDependency( 'time', timeController.getDGNode() )
		self.addReferenceInterface(name='Time', cls=Time, isList=False, changeCallback=__onChangeTimeCallback)
		self.setTimeNode( timeCPNode );
		self.bindDGOperator(dgNode.bindings,
						name = 'GameOfLife',
						fileName = FabricEngine.CreationPlatform.buildAbsolutePath('GameOfLifeArrayInfluenceMap.kl'),
						layout =[
						 'time.time',
						 'self.spawnInterval',
						 'self.step', 'self.min', 'self.max', 'self.spawn',
						 'self.halfBoundingBox',
						 'self.numPoints',
						 'self.positions'
						])
		if ( options.get('debug', False) == True ):
			dgNode.addMember( 'scale', 'Vec3', options.get('scale', Vec3(0.5,0.5,0.5)) );
			dgNode.addMember( 'debugGeometry', 'InlineGeometryType')
			self.bindDGOperator(dgNode.bindings,
							name = 'GOLVisualDebug',
							fileName = FabricEngine.CreationPlatform.buildAbsolutePath('GOLInlineGeoDebug.kl'),
							layout =[
							 'self.positions',
							 'self.numPoints',
							 'self.scale',
							 'self.debugGeometry'
							])
			self.constructSubNode(InlineGeometryInstance,
				source=self,
				sourceDGNodeName='DGNode',
				sourceMemberName='debugGeometry'
			)		
		

		
# Does the translation from Grid Coord to Global Transform Sliced so that it can be fed into GeometryInstance
# Re-uses the original Transform but substitute the KL logic, and adds a new reference interface to hook in the GOL
# Will need a Scale input (as it seems it cannot be set as a member it is sliced data). For the time being the Scale
# is hard coded in the KL Operator
class GridCoordToTransform(Transform):
	def __init__(self, scene, gol, scale, **options):
		super(GridCoordToTransform, self).__init__(scene, **options)
		paramsDGNode = self.constructDGNode('Params') # unsliced node to feed into the sliced OP
		paramsDGNode.addMember('scale', 'Vec3', scale) 
		dgNode = self.getDGNode()
		dgNode.setDependency('params', paramsDGNode );
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
						 'params.scale',
						 'self',
						 'self.globalXfo<>'
						])


class OrbitTransform(Component):
	
	def apply(self, node):
		super(OrbitTransform, self).apply(node)
		dgNode = node.getDGNode();
		dgNode.addMember("radius", "Scalar", 1)
		dgNode.addMember("speed", "Scalar", 0.5)
		node._addMemberInterface(node.getDGNode(), 'speed', True)
		dgNode.addMember("zoom", "Scalar", 0.8)
		node._addMemberInterface(node.getDGNode(), 'zoom', True)
		# add time node to CP Node
		def __onChangeTimeCallback(data):
			timeController = data['node']
			node.getDGNode().setDependency( 'time', timeController.getDGNode() )
		node.addReferenceInterface(name='Time', cls=Time, isList=False, changeCallback=__onChangeTimeCallback)
		
		# add GOL, ideally would be nicer to expose just a reference to Integer so that it can be driven by something else
		# How to expose a CP outside node
		def __onChangeGOLCallback(data):
			gol = data['node']
			node.getDGNode().setDependency( 'gol', gol.getDGNode() )
		node.addReferenceInterface(name='GOL', cls=GameOfLife, isList=False, changeCallback=__onChangeGOLCallback)
		
		node.setTimeNode( self.timeCPNode );
		node.setGOLNode( self.golCPNode );		
		#dgNode.setDependency('time', self.timeCPNode.getDGNode())
		node.bindDGOperator(dgNode.bindings, 
							  name="orbitBoundingBox",
							  fileName= FabricEngine.CreationPlatform.buildAbsolutePath('OrbitTransform.kl'),
							  layout= ["time.time", "self.speed", "self.zoom", "gol.halfBoundingBox", "self.radius", "self.globalXfo"])

	def __init__(self, timeCPNode, golCPNode, speed, radius):
		super(OrbitTransform, self).__init__()
		self.timeCPNode = timeCPNode
		self.golCPNode = golCPNode
	
	# ensure that we apply this component to a Transform only
	@staticmethod	
	def canApplyTo(geometry):
		return isinstance(geometry, Transform)	
		
		

class GameOfLifeCreationPlatform(CreationPlatformApplication):
	
	def initOrbitingCamera(self, golNode):
		transform = Transform(self.getScene())
		transform.setGlobalXfo(Xfo(Vec3(-50, 10, 0),Quat(),Vec3(1.0,1.0,1.0)),0)	
		orbitComponent = OrbitTransform(self.getGlobalTimeNode(), golNode, 0.5, 1.0)
		transform.addComponent(orbitComponent)
		camera = Camera(self.getScene(), transform=transform)
		self.getViewport().setCameraNode(camera)
		
	def __init__(self):	  
		super(GameOfLifeCreationPlatform, self).__init__(
	      cameraPosition=Vec3(4, 7, 10),
	      setupSelection = True,
	      setupGrid=True,
	      setupGlobalTimeNode=True,
	      timeRange=Vec2(0.0,240.0),
	      fps = 24
	    )
		self.setWindowTitle("Creation Platform Game Of Life")
		self.resize(1000,600)
		scale = Vec3(0.5,0.5,0.5)
		scene = self.getScene()
		
		golNode = GameOfLife(scene, self.getGlobalTimeNode(), debug=False, scale = scale)
		
		
		
		gridToXfoNode = GridCoordToTransform( scene, golNode, scale)
		
		# create the shaders
		phongMaterial = Material(scene, xmlFile='PhongMaterial')
		phongMaterial.addPreset(name='red',diffuseColor=Color(1.0,0.0,0.0))
		
		self.initOrbitingCamera(golNode);
							
		GeometryInstance(scene,
	  			geometry=PolygonMeshCuboid(scene,
										   length=1.9,
										   width= 1.9,
										   height=1.9
	  			),
	  			transform=gridToXfoNode,
	  			transformIndex=-1,
	  			material=phongMaterial,
	  	  		materialPreset='red'
		)
		# check for errors
		self.constructionCompleted()
		
GameOfLifeCreationPlatform().exec_()	
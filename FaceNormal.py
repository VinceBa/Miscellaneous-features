#
# A python feature make a normal vector on a surface
# wrote by Vincent Ballu
# any remarks: vincent.ballu@gmx.com
# release as a freeware: on your risks.
#
# versions:
#01/01/2021 first release
#21/02/2021 make a cone at the vector end
#22/06/2021 the vector values added
#           reverse option added
#           choose center of mass or face center
#19/02/2023 normal on any vertex added
#20/02/2023 Cone On/off
#25/02/2023 normal on any edge added
#           Vector parameter added



from __future__ import division
import FreeCAD
import Part

class NormalFace:
    def __init__(self, obj, linkface,linkpoint):
    
        obj.addProperty("App::PropertyInteger","Length","Parameters","Length of the arrow").Length = 5
        obj.addProperty("App::PropertyLinkSub","TargetFace","Parameters","Target face").TargetFace = linkface
        obj.addProperty("App::PropertyBool","Reverse","Parameters","Reverse the vector if the face is reversed").Reverse = False
        obj.addProperty("App::PropertyBool","ShowCone","Parameters","Showing the cone").ShowCone = True
        obj.addProperty("App::PropertyEnumeration","Origin","Parameters","Choose origin")
        if linkpoint:
            obj.addProperty("App::PropertyLinkSub","TargetVertex","Parameters","Target vertex").TargetVertex = linkpoint
            self.TargetVertex = True
            obj.Origin = ["On Vertex/Edge","Face Center","Mass Center"]
        else: 
            self.TargetVertex = False
            obj.Origin = ["Face Center","Mass Center"]
            
        obj.addProperty("App::PropertyFloat","NormOriginX","Parameters","Origin x value").NormOriginX = 0
        obj.addProperty("App::PropertyFloat","NormOriginY","Parameters","Origin y value").NormOriginY = 0
        obj.addProperty("App::PropertyFloat","NormOriginZ","Parameters","Origin z value").NormOriginZ = 0
        obj.setEditorMode("NormOriginX", 1)        
        obj.setEditorMode("NormOriginY", 1)
        obj.setEditorMode("NormOriginZ", 1)
        
        obj.addProperty("App::PropertyFloat","NormEndX","Parameters","Vector x value").NormEndX = 0
        obj.addProperty("App::PropertyFloat","NormEndY","Parameters","Vector y value").NormEndY = 0
        obj.addProperty("App::PropertyFloat","NormEndZ","Parameters","Vector z value").NormEndZ = 0
        obj.setEditorMode("NormEndX", 1)         
        obj.setEditorMode("NormEndY", 1)
        obj.setEditorMode("NormEndZ", 1)
        
        obj.addProperty("App::PropertyFloat","NormVectorX","Parameters","Vector x value").NormVectorX = 0
        obj.addProperty("App::PropertyFloat","NormVectorY","Parameters","Vector y value").NormVectorY = 0
        obj.addProperty("App::PropertyFloat","NormVectorZ","Parameters","Vector z value").NormVectorZ = 0
        obj.setEditorMode("NormVectorX", 1)        
        obj.setEditorMode("NormVectorY", 1)
        obj.setEditorMode("NormVectorZ", 1)
        
        obj.Proxy = self

    def onChanged(self, obj, prop):
        if prop == "Length":   self.execute(obj)

    def execute(self, obj):
        f = obj.TargetFace[0].getSubObject(obj.TargetFace[1][0])
        face = Part.Face (f)
        
        if self.TargetVertex:
            subobj = obj.TargetVertex[0].getSubObject(obj.TargetVertex[1][0])
            
            if isinstance(subobj,Part.Vertex):
                Vstart = subobj.Point
            if isinstance(subobj,Part.Edge): 
                curve = subobj.Curve.trim(subobj.FirstParameter, subobj.LastParameter)
                Vstart =curve.value(curve.parameterAtDistance(curve.length()/2, curve.FirstParameter))
                
        if obj.Origin == "Face Center" :
            (umin, umax, vmin, vmax) = face.ParameterRange
            Vstart = face.valueAt((umax+umin)/2,(vmax+vmin)/2)
        if obj.Origin == "Mass Center":
            Vstart = face.CenterOfMass    
   
        if obj.Reverse == False:
            Vend = Vstart+face.normalAt(*face.Surface.parameter(Vstart))*obj.Length
        else:
            Vend = Vstart-face.normalAt(*face.Surface.parameter(Vstart))*obj.Length
       
        norm = Part.makeLine(Vstart,Vend)              #creer le segment
        rc = obj.Length/10                             #rayon du cone 1/10 du segement
        hc = rc*3                                       #hauteur du cone 3x le rayon
        cone = Part.makeCone(0,rc,hc,Vend,Vstart-Vend)   #creer le cone
        if obj.ShowCone == True:
            obj.Shape = Part.Compound([norm,cone])
        else:
            obj.Shape = norm 
        
        obj.NormEndX = Vend.x                      #Affecte les valeurs aux paramêtres
        obj.NormEndY = Vend.y
        obj.NormEndZ = Vend.z
        
        obj.NormOriginX = Vstart.x
        obj.NormOriginY = Vstart.y
        obj.NormOriginZ = Vstart.z
        
        obj.NormVectorX = (obj.NormEndX - obj.NormOriginX)/obj.Length
        obj.NormVectorY = (obj.NormEndY - obj.NormOriginY)/obj.Length
        obj.NormVectorZ = (obj.NormEndZ - obj.NormOriginZ)/obj.Length


def MakeNormal():
    LinkFace = False
    LinkObject = False
    try:                                                        
        What = Gui.Selection.getSelectionEx()[0]              
        subname = What.SubElementNames[0]                       
        subobject = What.Object.getSubObject(What.SubElementNames[0])
      
        if isinstance(subobject,Part.Face):
            LinkFace = (What.Object,subname)                    
            try:        
                subname = What.SubElementNames[1]                
                subobject = What.Object.getSubObject(What.SubElementNames[1])
                if isinstance(subobject,Part.Vertex) or isinstance(subobject,Part.Edge):
                    LinkObject = (What.Object,subname)
            except: 
                LinkObject = False 
                
        else:
            if isinstance(subobject,Part.Vertex) or isinstance(subobject,Part.Edge):
                LinkObject = (What.Object,subname)
                try:
                    subname = What.SubElementNames[1] 
                    subobject = What.Object.getSubObject(What.SubElementNames[1])             
                    if isinstance(subobject,Part.Face):
                        LinkFace = (What.Object,subname)
                    else:
                        LinkFace = False
                except:                                         
                    LinkFace = False
    
        # print ("Selection face:", LinkFace)   
        # print ("Selection autre:", LinkObject)
        
        if LinkFace:    
            doc = FreeCAD.activeDocument()
            obj = doc.addObject("Part::FeaturePython","FaceNormal")           
            NormalFace(obj,LinkFace,LinkObject)
            obj.ViewObject.Proxy = 0         
        else:
            print("Selection error: Select a face or a vertex/edge and a face.")
    except:                                                      
        print("Selection error: Select a face or a vertex/edge and a face.")       
  
   
MakeNormal()
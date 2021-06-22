#
# A python feature make a normal vector on a surface
# wrote by Vincent Ballu
# any remarks: vincent.ballu@gmx.com
# release as a freeware: on your risks.
#
# versions:
#01/01/2021 first release
#21/02/2021 make a cone at the vector end
#           start on the surface instead the center mass
#22/02/2021 check if select object is a face
#22/06/2021 the vector values added
#           reverse option added
#           choose center of mass or geometrical

#           to do: normal on a point and a face


from __future__ import division
import FreeCAD
import Part

class NormalFace:
    def __init__(self, obj, face):
        obj.addProperty("App::PropertyInteger","Length","Parameters","Length of the arrow").Length = 5
        obj.addProperty("App::PropertyLinkSub","Target","Parameters","Target face").Target = face
        obj.addProperty("App::PropertyFloat","VectorX","Parameters","Vector x value").VectorX = 0
        obj.addProperty("App::PropertyFloat","VectorY","Parameters","Vector y value").VectorY = 0
        obj.addProperty("App::PropertyFloat","VectorZ","Parameters","Vector z value").VectorZ = 0
        obj.setEditorMode("VectorX", 1)         # user doesn't change !
        obj.setEditorMode("VectorY", 1)
        obj.setEditorMode("VectorZ", 1)
        obj.addProperty("App::PropertyBool","Reverse","Parameters","Reverse the vector if the face is reversed").Reverse = False
        obj.addProperty("App::PropertyEnumeration","Origin","Parameters","Choose either geometrical center or mass center of the face")
        obj.Origin = ["Face Center","Mass Center"]
        
        obj.Proxy = self

    def onChanged(self, obj, prop):
        if prop == "Length":   self.execute(obj)

    def execute(self, obj):
        f = obj.Target[0].getSubObject(obj.Target[1][0])
        face = Part.Face (f)
         
        if obj.Origin == "Face Center":
            (umin, umax, vmin, vmax) = face.ParameterRange
            center = face.valueAt((umax+umin)/2,(vmax+vmin)/2)
        else :
            center = face.CenterOfMass
            
        if obj.Reverse == False:
            vector = face.normalAt(*face.Surface.parameter(center))
        else:
            vector = -face.normalAt(*face.Surface.parameter(center))
            
            
        VL = center+vector*obj.Length
        norm = Part.makeLine(center,VL)
        r1 = obj.Length/10
        hc = r1*3
        cone = Part.makeCone(0,r1,hc,VL,center-VL)
        comp=Part.Compound([norm,cone]) 
        obj.Shape = comp
        
        obj.VectorX = vector.x
        obj.VectorY = vector.y
        obj.VectorZ = vector.z


def MakeNormal():
    try:
       
        What = Gui.Selection.getSelectionEx()[0]
        sub0 = What.SubElementNames[0]
        
        linksub = (What.Object, sub0)
       
        if sub0[0:4] == "Face":
            doc = FreeCAD.activeDocument()
            obj = doc.addObject("Part::FeaturePython","FaceNormal")           
            NormalFace(obj, linksub)
            obj.ViewObject.Proxy = 0
            
        elif sub0[0:6] == "Vertex":
            print ("Vertex...")
        else:
            print("Select a face or a vertex, then run the macro.")
        
    except:
        print("Select a face or a vertex, then run the macro.")
        
MakeNormal()
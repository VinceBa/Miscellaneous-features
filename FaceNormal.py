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
#24/06/2021: normal on a point and a face


from __future__ import division
import FreeCAD
import Part

class NormalFace:
    def __init__(self, obj, linkface,linkpoint):
        obj.addProperty("App::PropertyInteger","Length","Parameters","Length of the arrow").Length = 5
        obj.addProperty("App::PropertyLinkSub","TargetFace","Parameters","Target face").TargetFace = linkface
        if linkpoint:
            obj.addProperty("App::PropertyLinkSub","TargetVertex","Parameters","Target vertex").TargetVertex = linkpoint
            self.TargetVertex = True
        else : self.TargetVertex = False
        obj.addProperty("App::PropertyFloat","VectorX","Parameters","Vector x value").VectorX = 0
        obj.addProperty("App::PropertyFloat","VectorY","Parameters","Vector y value").VectorY = 0
        obj.addProperty("App::PropertyFloat","VectorZ","Parameters","Vector z value").VectorZ = 0
        obj.setEditorMode("VectorX", 1)         # user doesn't change !
        obj.setEditorMode("VectorY", 1)
        obj.setEditorMode("VectorZ", 1)
        obj.addProperty("App::PropertyFloat","OriginX","Parameters","Origin x value").OriginX = 0
        obj.addProperty("App::PropertyFloat","OriginY","Parameters","Origin y value").OriginY = 0
        obj.addProperty("App::PropertyFloat","OriginZ","Parameters","Origin z value").OriginZ = 0
        obj.setEditorMode("OriginX", 1)         # user doesn't change !
        obj.setEditorMode("OriginY", 1)
        obj.setEditorMode("OriginZ", 1)
        obj.addProperty("App::PropertyBool","Reverse","Parameters","Reverse the vector if the face is reversed").Reverse = False
        obj.addProperty("App::PropertyEnumeration","Origin","Parameters","Choose either geometrical center or mass center of the face")
        if linkpoint:   obj.Origin = ["On Vertex","Face Center","Mass Center"]
        else :          obj.Origin = ["Face Center","Mass Center"]
        
        obj.Proxy = self

    def onChanged(self, obj, prop):
        if prop == "Length":   self.execute(obj)

    def execute(self, obj):
        f = obj.TargetFace[0].getSubObject(obj.TargetFace[1][0])
        face = Part.Face (f)
        if self.TargetVertex:
            start = obj.TargetVertex[0].getSubObject(obj.TargetVertex[1][0]).Point
        if obj.Origin == "Face Center" :
            (umin, umax, vmin, vmax) = face.ParameterRange
            start = face.valueAt((umax+umin)/2,(vmax+vmin)/2)
        if obj.Origin == "Mass Center":
            start = face.CenterOfMass    
   
        if obj.Reverse == False:
            vector = face.normalAt(*face.Surface.parameter(start))
        else:
            vector = -face.normalAt(*face.Surface.parameter(start))
            
            
        VL = start+vector*obj.Length                #Fin de la fleche
        norm = Part.makeLine(start,VL)              #creer le segment
        rc = obj.Length/10                          #rayon du cone 1/10 du segement
        hc = rc*3                                   #hauteur du cone 3x le rayon
        cone = Part.makeCone(0,rc,hc,VL,start-VL)   #creer le cone
        comp=Part.Compound([norm,cone])             #creer un compound
        obj.Shape = comp
        
        obj.VectorX = vector.x                      #Affecte les valeurs aux paramêtres
        obj.VectorY = vector.y
        obj.VectorZ = vector.z
        
        obj.OriginX = start.x
        obj.OriginY = start.y
        obj.OriginZ = start.z


def MakeNormal():

    doc = FreeCAD.activeDocument()
    try:
        What = Gui.Selection.getSelectionEx()[0]
        sub0 = What.SubElementNames[0]                          #essaye de récuperer le point
        sub1 = What.SubElementNames[1]                          #essaye de recuperer la face
        print ("Selection :",sub0,sub1)
                
        if sub0[0:4] == "Face" and sub1[0:6] == "Vertex":       #associe correctement face et vertex
            linkface =  (What.Object, sub0)
            linkpoint = (What.Object, sub1)
        elif sub0[0:6] == "Vertex" and sub1[0:4] == "Face":
            linkface =  (What.Object, sub1)
            linkpoint = (What.Object, sub0)
        
        obj = doc.addObject("Part::FeaturePython","FaceNormal")           
        NormalFace(obj, linkface,linkpoint)
        obj.ViewObject.Proxy = 0    
 
    except:                                                     #error pas de sub1
        try:                                                    #donc uniquement une face
            What = Gui.Selection.getSelectionEx()[0]
            sub0 = What.SubElementNames[0]
            print ("Selection :",sub0)
            
            linkface = (What.Object, sub0)
            linkpoint = False
           
            if sub0[0:4] == "Face":
                obj = doc.addObject("Part::FeaturePython","FaceNormal")           
                NormalFace(obj, linkface,linkpoint)
                obj.ViewObject.Proxy = 0
                
            else: print("Select a face or a vertex with his face, then run the macro.")
            
        except: print("Select a face or a vertex with his face, then run the macro.")
   
MakeNormal()
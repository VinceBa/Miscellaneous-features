
# A python feature make a normal vector on a surface
# wrote by Vincent Ballu
# any remarks: vincent.ballu@gmx.com
# release as a freeware: on your risks.
#
# versions:
#01/01/2021 first release
#21/02/2021 make a cone at the vector end
#           start on the surface instead the center mass




from __future__ import division
import FreeCAD
import Part

class Normal:
    def __init__(self, obj, face):
        obj.addProperty("App::PropertyFloat","Length","Parameters","Lenght of the edge").Length = 1.0
        obj.addProperty("App::PropertyLinkSub","Target","Parameters","Target face").Target = face
        obj.Proxy = self

    def onChanged(self, obj, prop):
        if prop == "Length":
            self.execute(obj)

    def execute(self, obj):
        f = obj.Target[0].getSubObject(obj.Target[1][0])
        # g = f.CenterOfMass
        (umin, umax, vmin, vmax) = f.ParameterRange
        c = f.valueAt((umax-umin)/2,(vmax-vmin)/2)
        pc = c+f.normalAt(*f.Surface.parameter(c))*obj.Length
        norm = Part.makeLine(c,pc)
        r1 = obj.Length/10
        h = r1*3
        cone = Part.makeCone(r1,0,h,pc,pc-c)
        comp=Part.Compound([norm,cone]) 
        obj.Shape = comp

def MakeNormal():
    doc = FreeCAD.activeDocument()
    obj = doc.addObject("Part::FeaturePython","FaceNormal") 
    try:
        f = Gui.Selection.getSelectionEx()[0]
        linksub = (f.Object, (f.SubElementNames[0]))
        Normal(obj, linksub)
        obj.ViewObject.Proxy = 0
        viewObject = Gui.ActiveDocument.getObject(obj.Name)
        viewObject.DisplayMode = "Flat Lines"
    except:
        print("Select a face, then run the macro.")
        
MakeNormal()
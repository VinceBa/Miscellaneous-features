

# A python feature for Freecad
# to make a Lame Curve, Super Egg or Squircle
# by changing the N parameter:
# 0 to 1 give an Astroid      https://en.wikipedia.org/wiki/Astroid
# 1 give a Diamond
# 2 give an Ellipse           https://en.wikipedia.org/wiki/Ellipse
# 2 to 4 give a Super Egg     https://en.wikipedia.org/wiki/Superegg
# 4 and more give a Squircle  https://en.wikipedia.org/wiki/Squircle
# wrote by Vincent Ballu
# any remarks: vincent.ballu@gmx.com
# release as a freeware: on your risks.



from __future__ import division
import FreeCAD, Part, math, Draft
from FreeCAD import Base
from math import pi


class LameCurve:
   def __init__(self, obj):
      
      obj.addProperty("App::PropertyFloat","RadiusX","Parameters","Set radius on X axle").RadiusX = 3.0
      obj.addProperty("App::PropertyFloat","RadiusY","Parameters","Set radius on Y axle").RadiusY = 2.0
      obj.addProperty("App::PropertyFloat","DeltaZ","Parameters","Set a Z variation on X").DeltaZ = 0
      obj.addProperty("App::PropertyFloat","N","Parameters","Factor N 0-1: Astroid 1:Diamond 2:Ellipse 2+:SuperOeuf 4+:Squircle").N = 4.0
      obj.addProperty("App::PropertyInteger","Iterations","Curve","Number of iterations by quadrant. Smooths the curve").Iterations = 20
      obj.addProperty("App::PropertyBool","CreateFace","Curve","Wheter to create a face or not").CreateFace = False
      obj.addProperty("App::PropertyInteger","Quadrant","Curve","Number of quadrant: wheter 1, 2, 3 or 4").Quadrant = 4
      obj.Proxy = self

   def onChanged(self, obj, prop):
      if prop == "RadiusX" or prop == "RadiusY" or prop == "N" or prop == "Iterations" or prop == "CreateFace" or prop == "Quadrant" or prop == "DeltaZ":
        self.execute(obj)

   def execute(self, obj):
      a = obj.RadiusX
      b = obj.RadiusY
      it = obj.Iterations 
      dz = obj.DeltaZ/it
      z = 0
      
      
      if obj.N <= 0:
        obj.N = 0.1
      n = obj.N
      if obj.Quadrant <= 0:
        obj.Quadrant = 1
      if obj.Quadrant > 4:
        obj.Quadrant = 4
      quad = int(obj.Quadrant)
      
      
      intv = pi/2 / (it-1)
      matriz = []
      
      t = 0
      for i in range(it):
        x = (a*math.cos(t)**(2/n)).real
        y = (b*math.sin(t)**(2/n)).real
        matriz.append(Base.Vector(x,y,z))
        t+= intv
        z+=dz
        
      if quad > 1:
        t = pi/2
        for i in range(it):
            x = -(a*math.cos(t)**(2/n)).real
            y = (b*math.sin(t)**(2/n)).real
            matriz.append(Base.Vector(x,y,z))
            t-= intv
            z-=dz
      
      if quad > 2:
        t = 0
        for i in range(it):
            x = -(a*math.cos(t)**(2/n)).real
            y = -(b*math.sin(t)**(2/n)).real
            matriz.append(Base.Vector(x,y,z))
            t+= intv
            z+=dz
       
      if quad > 3: 
        t = pi/2
        for i in range(it):
            x = (a*math.cos(t)**(2/n)).real
            y = -(b*math.sin(t)**(2/n)).real
            matriz.append(Base.Vector(x,y,z))
            t-= intv
            z-=dz
        
      curve = Part.BSplineCurve(matriz)
      #curve.interpolate(matriz)
      
      if quad == 4:
         curve.setPeriodic()
            
      if obj.CreateFace == True:
         sh = Part.Face(Part.Wire(curve.toShape()))
      else:
         sh = curve.toShape()
      sh.Placement = obj.Placement
      obj.Shape = sh
       

def MakeLameCurve():
   doc = FreeCAD.activeDocument()
   if doc == None:
      doc = FreeCAD.newDocument()
   obj=doc.addObject("Part::FeaturePython","LameCurve") 
   obj.addExtension("Part::AttachExtensionPython","obj")
   LameCurve(obj)
   obj.ViewObject.Proxy=0
   viewObject = Gui.ActiveDocument.getObject(obj.Name)
   viewObject.DisplayMode = "Flat Lines"
 
               
MakeLameCurve()

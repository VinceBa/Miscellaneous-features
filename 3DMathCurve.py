from __future__ import division
import FreeCAD, Part, Draft
from FreeCAD import Base
from math import *

# Crée un object courbe 3D paramétrique à 5 paramètres:
# X(a,b,c,d,e)
# Y(a,b,c,d,e)
# Z(a,b,c,d,e)
# La courbe est décrite par un nombre de points
# par défaut une spline est crée, un polyline est possible en option
# CreateFace semble buggé... mais est ce vraiment utile? :-D


class MathCurve(object):
   def __init__(self, obj):
       
      obj.addProperty("App::PropertyString","a","Parameters","Set a parameter a(t)").a = "1"
      obj.addProperty("App::PropertyString","b","Parameters","Set b parameter b(a,t)").b = "0"
      obj.addProperty("App::PropertyString","c","Parameters","Set c parameter c(a,b,t)").c = "0"
      obj.addProperty("App::PropertyString","d","Parameters","Set d parameter d(a,b,c,t)").d = "0"
      obj.addProperty("App::PropertyString","e","Parameters","Set e parameter e(a,b,c,d,t)").e = "0"
      obj.addProperty("App::PropertyString","X","Equation","X expression X(a,b,c,d,e,t)").X = "t"
      obj.addProperty("App::PropertyString","Y","Equation","Y expression Y(a,b,c,d,e,t)").Y = "a*sin(t)"
      obj.addProperty("App::PropertyString","Z","Equation","Z expression Z(a,b,c,d,e,t)").Z = "0"
      obj.addProperty("App::PropertyFloat","CurveStart","Curve","Start t").CurveStart = 0
      obj.addProperty("App::PropertyFloat","CurveEnd","Curve","End t").CurveEnd = 6.283185
      obj.addProperty("App::PropertyInteger","NbPts","Curve","Number of points").NbPts = 20
      obj.addProperty("App::PropertyBool","CreateFace","Curve","Wheter to create a face or not").CreateFace = False
      obj.addProperty("App::PropertyBool","Close","Curve","close the curve or not").Close = False
      obj.addProperty("App::PropertyBool","Wire","Curve","Make a wire instead a Spline").Wire = False
      obj.Proxy = self
       
   def onChanged(self, obj, prop):
      if prop == "a" or prop == "b" or prop == "c" or prop == "d" or prop == "e" or prop == "X" or prop == "Y"or prop == "Z" or prop == "start" or prop == "end" or prop == "interval" or prop == "createFace" or prop == "close":
        self.execute(obj)

   def execute(self, obj):
      
      dt = (obj.CurveEnd-obj.CurveStart)/(obj.NbPts-1)
      pts = []
      t = obj.CurveStart
      a = b = c = d = x = y = z = 0
        
      for i in range(obj.NbPts):
        try:
            value = "a"
            a = eval(obj.a)
            value = "b"
            b = eval(obj.b)
            value = "c"
            c = eval(obj.c)
            value = "d"
            d = eval(obj.d)
            value = "e"
            e = eval(obj.e)
            value = "x"
            x = eval(obj.X)
            value = "y"
            y = eval(obj.Y)
            value = "z"
            z = eval(obj.Z)
            
        except ZeroDivisionError:
            print("Warning: Error division by zero in calculus of "+ value +" for t=" +str(t)+" !")
        except:
            print("Error in the formula of " + value +" !")
                      
        pts.append(FreeCAD.Vector(x,y,z))
        t += dt
      
      if obj.Close:                # pour fermer la courbe on ajoute un point au début
            t = obj.CurveStart
            a = eval(obj.a)
            b = eval(obj.b)
            c = eval(obj.c)
            d = eval(obj.d)
            e = eval(obj.e)
            x = eval(obj.X)
            y = eval(obj.Y)
            z = eval(obj.Z)
            pts.append(FreeCAD.Vector(x,y,z))
            
      if obj.Wire == False:
        curve = Part.BSplineCurve(pts)
        if obj.Close:
            curve.setPeriodic()
        if obj.CreateFace:
            sh = Part.Face(Part.Wire(curve.toShape()))
        else:
            sh = curve.toShape()
      else:
        
        wire = Part.makePolygon(pts)
        if obj.CreateFace == False:
            sh = Part.Wire(wire)
        else:
            sh = Part.Face(wire)
  
      sh.Placement = obj.Placement
      obj.Shape = sh

class ViewProviderMath3DCurve(object):
    def __init__(self, obj, icon):
        obj.Proxy = self
        self.icone = icon
        self.ViewObject = obj
                
    def getIcon(self):
        return self.icone

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
          
    
    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
     
def MakeMathCurve():
    doc = FreeCAD.activeDocument()
    if doc == None:
        doc = FreeCAD.newDocument()
    obj=doc.addObject("Part::FeaturePython","Math3DCurve")    
    obj.addExtension("Part::AttachExtensionPython","obj")
    
    ViewProviderMath3DCurve (obj.ViewObject, setIconInMacro(""))
    MathCurve(obj) 
     
def setIconInMacro(self):
    return """
    /* XPM */
    static char * xpm[] = {
    /* width height num_colors chars_per_pixel */
    "22 22 8 1",
    /* colors */
    "` c #000000",
    ". c #242424",
    "# c #484848",
    "a c #6d6d6d",
    "b c #919191",
    "c c #b6b6b6",
    "d c #dadada",
    "e c #ffffff",
    /* pixels */
    "aeeeb.beeeeeeeeeeeeeee",
    "#eea```#eeeeeeeeeeeeee",
    "#ed``a``beeeeeeeeeeeee",
    "#ea`beb`.eeeeeeeeeeeee",
    "#d`.eee#`beeeeeeeeeeee",
    "#b`aeeec`.eeeeeeeeeeee",
    "##`ceeee.`ceeeeeeeeeee",
    "...deeeea`beeeeeeeeeee",
    ".`#eeeeec`#eeeeeeeeeee",
    "``bfeeeee.`deeeeeeeeee",
    "``#aaaaabb`bbaaaaaaaaa",
    ".aaaaaaabc`#caaaaaa#`#",
    "#eeeeeeeee..eeeeeeea`c",
    "#eeeeeeeee#`beeeeee.`d",
    "#eeeeeeeeea`#eeeeed`.e",
    "#eeeeeeeeed``deeeeb`ae",
    "#eeeeeeeeeea`beeee.`ce",
    "#eeeeeeeeeec`.eeec`.ee",
    "#eeeeeeeeeee#`bee#`bee",
    "#eeeeeeeeeeec``ba`.eee",
    "#eeeeeeeeeeeeb````ceee",
    "aeeeeeeeeeeeeeb..ceeee"};
    """

if __name__ == '__main__':
    MakeMathCurve()
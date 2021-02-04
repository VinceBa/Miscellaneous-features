from __future__ import division
import FreeCAD, Part, math, Draft
from FreeCAD import Base
from math import pi


class TileFace:
   def __init__(self, obj, face):
        obj.addProperty("App::PropertyInteger","U","Parameters","").U = 8
        obj.addProperty("App::PropertyInteger","V","Parameters","").V = 6
        obj.addProperty("App::PropertyLinkSub","Face","Parameters","Target face").Face = face
        obj.addProperty("App::PropertyFloat","Length","Parameters","Length").Length = 0.0
        obj.addProperty("App::PropertyEnumeration","Style","Parameters","")
        obj.Style = ["Points","Straight","Streched","Diamonds"]
      
        obj.Proxy = self
 
   def onChanged(self, obj, prop):
        if prop == "U" or prop == "V":  self.execute(obj)

   def execute(self, obj):
        l = obj.Length
        f = obj.Face[0].getSubObject(obj.Face[1][0])
        face = Part.Face (f)
        (umin, umax, vmin, vmax) = face.ParameterRange
        # print (umin,umax,vmin,vmax)
    
        nbU = obj.U
        nbV = obj.V
        nbptsU = nbU + 1
        nbptsV = nbV + 1
        
        comp = 0
        lattice = [[0] * nbptsV for j in range(nbptsU)] #tableau coordonnées des points
        shapes = [] 
  
        i = j = 0
        for u in [umin + x * (umax-umin)/nbU for x in range(nbptsU)]:
            for v in [vmin + x * (vmax-vmin)/nbV for x in range(nbptsV)]:
                lattice[i][j] = face.valueAt(u,v)
                j += 1
            j = 0       
            i += 1    
            
        if obj.Style == "Points" :
            if l: 
                for i in range (nbptsU):
                    for j in range(nbptsV):
                        pts2 = lattice[i][j]+face.normalAt(*face.Surface.parameter(lattice[i][j]))*l
                        shapes.append (Part.makeLine(lattice[i][j],pts2))
            else:
                for i in range (nbptsU):
                    for j in range(nbptsV):
                        shapes.append(Part.Vertex(lattice[i][j]))
   
        if obj.Style == "Straight" or obj.Style == "Streched":
            for i in range (nbU):
                for j in range(nbV):
                    p1 = lattice[i][j]
                    p2 = lattice[i][j+1]
                    p3 = lattice[i+1][j]
                    p4 = lattice[i+1][j+1]
                    w1 = Part.makeLine (p1,p2)
                    w2 = Part.makeLine (p3,p4)
                    lf = Part.makeRuledSurface (w1,w2)
                    if obj.Style == "Straight" and l:
                        g = lf.CenterOfMass
                        v = lf.normalAt(*lf.Surface.parameter(g))*l
                        shapes.append(lf.extrude(v))
                    if obj.Style == "Streched" and l:    
                        q1 = p1+face.normalAt(*face.Surface.parameter(p1))*l
                        q2 = p2+face.normalAt(*face.Surface.parameter(p2))*l
                        q3 = p3+face.normalAt(*face.Surface.parameter(p3))*l
                        q4 = p4+face.normalAt(*face.Surface.parameter(p4))*l
                        poly1 = Part.makePolygon ([p1,p2,p4,p3,p1])
                        poly2 = Part.makePolygon ([q1,q2,q4,q3,q1])
                        tour = Part.makeLoft ([poly1,poly2])
                        line1 = Part.makeLine (q1,q2)
                        line2 = Part.makeLine (q3,q4)
                        line3 = Part.makeLine (p1,p2)
                        line4 = Part.makeLine (p3,p4)
                        rs1 = Part.makeRuledSurface (line1,line2)
                        rs2 = Part.makeRuledSurface (line3,line4)
                        shell = Part.Shell(tour.Faces+rs1.Faces+rs2.Faces)
                        shell.sewShape()
                        solid = Part.Solid(shell)
                        shapes.append(solid)
                    else: shapes.append(lf)
                
        if obj.Style == "Diamonds" and (nbU%2) == 0 and (nbV%2) == 0: # check if U and V are even:
            for i in range (0,nbU,2):
                for j in range(0,nbV,2):
                    p1 = lattice[i+1][j]
                    p2 = lattice[i][j+1]
                    p3 = lattice[i+2][j+1]
                    p4 = lattice[i+1][j+2]
                    w1 = Part.makeLine (p1,p2)
                    w2 = Part.makeLine (p3,p4)
                    lf = Part.makeRuledSurface (w1,w2)
                    print(i,j)
                    if l:
                        pc = lattice[i+1][j+1]
                        v = pc-lf.normalAt(*lf.Surface.parameter(pc))*l
                        line1 = Part.makeLine (p1,p2)
                        line2 = Part.makeLine (p1,v)
                        rs1 = Part.makeRuledSurface (line1,line2)
                        line1 = Part.makeLine (p2,p4)
                        line2 = Part.makeLine (p2,v)
                        rs2 = Part.makeRuledSurface (line1,line2)
                        line1 = Part.makeLine (p1,p3)
                        line2 = Part.makeLine (p1,v)
                        rs3 = Part.makeRuledSurface (line1,line2)
                        line1 = Part.makeLine (p3,p4)
                        line2 = Part.makeLine (v,p4)
                        rs4 = Part.makeRuledSurface (line1,line2)
                       
                        shell = Part.Shell(lf.Faces+rs1.Faces+rs2.Faces+rs3.Faces+rs4.Faces)
                        shell.sewShape()
                        solid = Part.Solid(shell)
                        shapes.append(solid)
                        
                    else: shapes.append(lf)
            
         
        if shapes: comp=Part.Compound(shapes) 
        if comp: obj.Shape = comp
        
def MakeTileFace():
    doc = FreeCAD.activeDocument()
    if doc == None:
        doc = FreeCAD.newDocument()
    try:
        f = Gui.Selection.getSelectionEx()[0]
        linksub = (f.Object, (f.SubElementNames[0]))  
        obj=doc.addObject("Part::FeaturePython","TileFace") 
        TileFace(obj,linksub)
        obj.ViewObject.Proxy=0
   
    except:
        print("Select a face, then run the macro.")
 
MakeTileFace()

# A python faeture to rig some patterns on a surface
# wrote by Vincent Ballu
# any remarks: vincent.ballu@gmx.com
# release as a freeware: on your risks.
#
# versions:
#03/02/2021 first release
#04/02/2021 honeycomb added
#19/02/2021 honeycomb updated

from __future__ import division
import FreeCAD, Part, math, Draft, random, DraftVecUtils

class TileFace:
   def __init__(self, obj, face):
        obj.addProperty("App::PropertyInteger","U","Parameters","").U = 8
        obj.addProperty("App::PropertyInteger","V","Parameters","").V = 6
        obj.addProperty("App::PropertyLinkSub","Face","Parameters","Target face").Face = face
        obj.addProperty("App::PropertyFloat","Length","Parameters","Length").Length = 0.0
        obj.addProperty("App::PropertyFloat","Random","Parameters","Random the tiles").Random = 0.0
        obj.addProperty("App::PropertyEnumeration","Style","Parameters","")
        obj.Style = ["Points","Straight","Streched","Diamonds","Bubble","Straight Honeycomb"]
      
        obj.Proxy = self
 
   def onChanged(self, obj, prop):
        if prop == "U" or prop == "V":  self.execute(obj)

   def execute(self, obj):
        l = obj.Length
        rf = obj.Random
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
                        pts2 = lattice[i][j]+face.normalAt(*face.Surface.parameter(lattice[i][j]))*(l+rf*random.random())
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
                        v = lf.normalAt(*lf.Surface.parameter(g))*(l+rf*random.random())
                        shapes.append(lf.extrude(v))
                    if obj.Style == "Streched" and l:    
                        haz = rf*random.random()
                        q1 = p1+face.normalAt(*face.Surface.parameter(p1))*(l+haz)
                        q2 = p2+face.normalAt(*face.Surface.parameter(p2))*(l+haz)
                        q3 = p3+face.normalAt(*face.Surface.parameter(p3))*(l+haz)
                        q4 = p4+face.normalAt(*face.Surface.parameter(p4))*(l+haz)
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
                
        if obj.Style == "Diamonds":
            if nbU%2 == 0 and nbV%2 == 0: # check if U and V are even:
                for i in range(0,nbU,2):
                    for j in range(0,nbV,2):
                        p1 = lattice[i+1][j]
                        p2 = lattice[i][j+1]
                        p3 = lattice[i+2][j+1]
                        p4 = lattice[i+1][j+2]
                        w1 = Part.makeLine (p1,p2)
                        w2 = Part.makeLine (p3,p4)
                        lf = Part.makeRuledSurface (w1,w2)
                        if l:
                            pc = lattice[i+1][j+1]
                            v = pc-lf.normalAt(*lf.Surface.parameter(pc))*(l+rf*random.random())
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
            else:
                print ("U and V must a multiple of 2")
            
        if obj.Style == "Bubble":
            if nbU%2 == 0 and nbV%2 == 0: # check if U and V are even:
                nbU=nbV=2
                for i in range (0,nbU,2):
                    for j in range(0,nbV,2):
                        pts=[]
                        # pts.append(lattice[i][j+1])
                        # pts.append(lattice[i+1][j+2])
                        # pts.append(lattice[i+2][j+1])
                        # pts.append(lattice[i+1][j])
                        pts.append(lattice[i+1][j])
                        pts.append(lattice[i+2][j+1])
                        pts.append(lattice[i+1][j+2])
                        pts.append(lattice[i][j+1])
                        
                        curve=Part.BSplineCurve()
                        # curve.increaseDegree(4)
                        curve.interpolate(pts,True)
                        # curve.setPeriodic()
                        # pc = lattice[i+1][j+1]
                        # norm = face.normalAt(*face.Surface.parameter(pc))
                        print(pts)
 
                        shapes.append(curve)
            else:
                print ("U and V must a multiple of 2")        
         
        if obj.Style == "Straight Honeycomb":
            if nbU%3 == 0 and nbV%3 == 0:
               for i in range(0,nbU,3):
                    for j in range(0,nbV,3): 
                        p1 = lattice[i+1][j]
                        p2 = lattice[i][j+1]
                        p3 = lattice[i][j+2]
                        p4 = lattice[i+1][j+3]
                        p5 = lattice[i+2][j+3]
                        p6 = lattice[i+3][j+2]
                        p7 = lattice[i+3][j+1]
                        p8 = lattice[i+2][j]
                        L1 = Part.makeLine(p1, p2)
                        L2 = Part.makeLine(p2, p3)
                        L3 = Part.makeLine(p3, p4)
                        L4 = Part.makeLine(p4, p5)
                        L5 = Part.makeLine(p5, p6)
                        L6 = Part.makeLine(p6, p7)
                        L7 = Part.makeLine(p7, p8)
                        L8 = Part.makeLine(p8, p1)
                       
                        hexa = Part.Wire([L1,L2,L3,L4,L5,L6,L7,L8])
                       
                        p1 = lattice[i+1][j+1]
                        p2 = lattice[i+2][j+1]
                        p3 = lattice[i+2][j+2]
                        p4 = lattice[i+1][j+2]
                        L1 = Part.makeLine(p1, p2)
                        L2 = Part.makeLine(p2, p3)
                        L3 = Part.makeLine(p3, p4)
                        L4 = Part.makeLine(p4, p1)
                        SquareWire = Part.Wire([L1,L2,L3,L4])
                        SquareFace = Part.makeRuledSurface (L1,L3)
                       
                        if l:
                            g = SquareFace.CenterOfMass
                            v = SquareFace.normalAt(*SquareFace.Surface.parameter(g))*(l+rf*random.random())
                            shapes.append(hexa.extrude(v))
                        else :  shapes.append(hexa)
            else:
                print ("U and V must a multiple of 3")      
                
        if shapes: comp=Part.Compound(shapes) 
        if comp: obj.Shape = comp
        
#from :  https://wiki.freecadweb.org/FreeCAD_vector_math_library 
def sub(first, other): 
    """sub(Vector,Vector) - subtracts second vector from first one"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return FreeCAD.Vector(first.x-other.x, first.y-other.y, first.z-other.z)
 
def length(first):
    """lengh(Vector) - gives vector length"""
    if isinstance(first,FreeCAD.Vector):
        return math.sqrt(first.x*first.x + first.y*first.y + first.z*first.z)
 
def dist(first, other):
    """dist(Vector,Vector) - returns the distance between both points/vectors"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return length(sub(first,other))

        
        
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
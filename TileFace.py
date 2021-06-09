
# A python faeture to rig some patterns on a surface
# wrote by Vincent Ballu
# any remarks: vincent.ballu@gmx.com
# release as a freeware: on your risks.
#
# versions:
#03/02/2021 first release
#04/02/2021 added honeycomb
#19/02/2021 upgrated honeycomb
#22/05/2021 added hatch
#22/05/2021 added limit
#23/05/2021 upgrated Diamond, added sharp and solid 
#09/06/2021 upgrated limit mode

from __future__ import division
import FreeCAD, Part, math, Draft, random, DraftVecUtils

class TileFace:
   def __init__(self, obj, link):
        obj.addProperty("App::PropertyInteger","U","Parameters","").U = 18  
        obj.addProperty("App::PropertyInteger","V","Parameters","").V = 12
        obj.addProperty("App::PropertyLinkSub","Face","Parameters","Target face").Face = link
        obj.addProperty("App::PropertyFloat","Thickness","Parameters","Thickness").Thickness = 0.0
        obj.addProperty("App::PropertyFloat","Random","Parameters","Randomise the tiles").Random = 0.0
        obj.addProperty("App::PropertyBool","Solid","Parameters","Either oulined or solid with thickness").Solid = True
        obj.addProperty("App::PropertyBool","Limit","Parameters","Try to limit the tile on the face").Limit = False
        obj.addProperty("App::PropertyBool","Sharp","Parameters","Sharp the pattern").Sharp = False
        obj.addProperty("App::PropertyEnumeration","Style","Parameters","")
        
        obj.Style = ["Points","Hatch","Squares","Squares Streched","Small Squares","Checkers","Diamonds","Honeycomb","Bricks"]
      
        obj.Proxy = self
 
   def onChanged(self, obj, prop):
        if prop == "U" or prop == "V":  self.execute(obj)

   def execute(self, obj):
        l = obj.Thickness
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
   
        if obj.Style == "Squares" or obj.Style == "Squares Streched":
            for i in range (nbU):
                for j in range(nbV):
                    p1 = lattice[i][j]
                    p2 = lattice[i][j+1]
                    p3 = lattice[i+1][j]
                    p4 = lattice[i+1][j+1]
                    w1 = Part.makeLine (p1,p2)
                    w2 = Part.makeLine (p3,p4)
                    lf = Part.makeRuledSurface (w1,w2)
                    
                    if obj.Style == "Squares" and l:
                        g = lf.CenterOfMass
                        v = lf.normalAt(*lf.Surface.parameter(g))*(l+rf*random.random())
                        shapes.append(lf.extrude(v))
                    if obj.Style == "Squares Streched" and l:    
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
                        
                        if l and obj.Sharp:
                            pc = lattice[i+1][j+1]
                            v = pc+lf.normalAt(*lf.Surface.parameter(pc))*(l+rf*random.random())
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
                            
                        if l and not obj.Sharp:  
                            p1 = lattice[i+1][j]
                            p2 = lattice[i][j+1]
                            p3 = lattice[i+1][j+2]
                            p4 = lattice[i+2][j+1]
                            
                            L1 = Part.makeLine (p1,p2)
                            L2 = Part.makeLine (p2,p3)
                            L3 = Part.makeLine (p3,p4)
                            L4 = Part.makeLine (p4,p1)
                            diams1 = Part.Wire([L1,L2,L3,L4])
                            
                            p1_2 = p1+face.normalAt(*face.Surface.parameter(p1))*(l+rf*random.random())
                            p2_2 = p2+face.normalAt(*face.Surface.parameter(p2))*(l+rf*random.random())
                            p3_2 = p3+face.normalAt(*face.Surface.parameter(p3))*(l+rf*random.random())
                            p4_2 = p4+face.normalAt(*face.Surface.parameter(p4))*(l+rf*random.random())
                            L1 = Part.makeLine (p1_2,p2_2)
                            L2 = Part.makeLine (p2_2,p3_2)
                            L3 = Part.makeLine (p3_2,p4_2)
                            L4 = Part.makeLine (p4_2,p1_2)
                            diams2 = Part.Wire([L1,L2,L3,L4])
                            cotes = Part.makeLoft([diams1,diams2])
                            L3 = Part.makeLine (p4_2,p3_2)
                            haut = Part.makeRuledSurface (L1,L3)
       
                            if obj.Solid:
                                shell = Part.Shell(haut.Faces+cotes.Faces+lf.Faces)
                                shell.sewShape()
                                diams = Part.Solid(shell)
                               
                            else : diams = Part.makeLoft([diams1,diams2],False,True)
                            shapes.append(diams)
                            
                            
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
         
        if obj.Style == "Honeycomb":
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
     
                        rand = rf*random.random()
                        if l:
                            p1_2 = p1+f.normalAt(*f.Surface.parameter(p1))*(l+rand)
                            p2_2 = p2+f.normalAt(*f.Surface.parameter(p2))*(l+rand)
                            p3_2 = p3+f.normalAt(*f.Surface.parameter(p3))*(l+rand)
                            p4_2 = p4+f.normalAt(*f.Surface.parameter(p4))*(l+rand)
                            p5_2 = p5+f.normalAt(*f.Surface.parameter(p5))*(l+rand)
                            p6_2 = p6+f.normalAt(*f.Surface.parameter(p6))*(l+rand)
                            p7_2 = p7+f.normalAt(*f.Surface.parameter(p7))*(l+rand)
                            p8_2 = p8+f.normalAt(*f.Surface.parameter(p8))*(l+rand)
                            
                            L1 = Part.makeLine(p1_2, p2_2)
                            L2 = Part.makeLine(p2_2, p3_2)
                            L3 = Part.makeLine(p3_2, p4_2)
                            L4 = Part.makeLine(p4_2, p5_2)
                            L5 = Part.makeLine(p5_2, p6_2)
                            L6 = Part.makeLine(p6_2, p7_2)
                            L7 = Part.makeLine(p7_2, p8_2)
                            L8 = Part.makeLine(p8_2, p1_2)
                       
                            hexa2 = Part.Wire([L1,L2,L3,L4,L5,L6,L7,L8])
                            loft = Part.makeLoft([hexa,hexa2])
                            
                            shapes.append(loft)
                        else :  shapes.append(hexa)
            else:
                print ("U and V must be a multiple of 3")      
                                
        if obj.Style == "Small Squares":
            if nbU%3 == 0 and nbV%3 == 0:
               for i in range(0,nbU,3):
                    for j in range(0,nbV,3): 
                        p1 = lattice[i+1][j+1]
                        p2 = lattice[i+1][j+2]
                        p3 = lattice[i+2][j+2]
                        p4 = lattice[i+2][j+1]
         
                        w1 = Part.makeLine (p1,p2)
                        w2 = Part.makeLine (p4,p3)
                        lf = Part.makeRuledSurface (w1,w2)
                        
                        if l:
                            g = lf.CenterOfMass
                            v = lf.normalAt(*lf.Surface.parameter(g))*(l+rf*random.random())
                            shapes.append(lf.extrude(v))   
                        else: shapes.append(lf)
            else:
                print ("U and V must be a multiple of 3")    

        if obj.Style == "Checkers":
            if nbU%2 == 0 and nbV%2 == 0:
               for i in range(0,nbU,1):
                    d = 0
                    if i%2 !=0 : d = 1
                    for j in range(0,nbV-d,2): 
                        
                        p1 = lattice[i][j+d]
                        p2 = lattice[i+1][j+d]
                        p3 = lattice[i][j+1+d]
                        p4 = lattice[i+1][j+1+d]
         
                        w1 = Part.makeLine (p1,p2)
                        w2 = Part.makeLine (p3,p4)
                        lf = Part.makeRuledSurface (w1,w2)
                        
                        if l:
                            g = lf.CenterOfMass
                            v = lf.normalAt(*lf.Surface.parameter(g))*(l+rf*random.random())
                            shapes.append(lf.extrude(v))   
                        else: shapes.append(lf)
            else:
                print ("U and V must be a multiple of 2")            
                
        if obj.Style == "Hatch":
            
           for i in range(0,nbU):
                for j in range(0,nbV): 
                    p1 = lattice[i][j]
                    p2 = lattice[i+1][j+1]
                        
                    L1 = Part.makeLine(p1, p2)
                    seg1 = Part.Wire([L1])
                    rand = rf*random.random()
                    if l:
                        p1_2 = p1+f.normalAt(*f.Surface.parameter(p1))*(l+rand)
                        p2_2 = p2+f.normalAt(*f.Surface.parameter(p2))*(l+rand)
                        L2 = Part.makeLine(p1_2, p2_2)
                        seg2 = Part.Wire([L2])
                        loft = Part.makeLoft([seg1,seg2])
                            
                        shapes.append(loft)
                    else :  shapes.append(seg1)
             
  
        if shapes: comp=Part.Compound(shapes) 
        if comp: 
            if obj.Limit:
                if l:
                    c = face.valueAt((umax+umin)/2,(vmax+vmin)/2)
                    Vup = c+face.normalAt(*face.Surface.parameter(c))*l
                    Vdn = c+face.normalAt(*face.Surface.parameter(c))*l
                    ShapeFace1 = face.extrude(Vup-c)
                    ShapeFace = ShapeFace1.fuse(face.extrude(Vdn-c))
                    obj.Shape = comp.common(ShapeFace)
                else:
                    obj.Shape = comp.common(face,0.01)
               
            else:   obj.Shape = comp
        
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
"""PR quadtree original, entero, capacidad 1; sin bibliotecas de estructuras.
Dominio [0, 2**bits)². Las divisiones son exactas. Duplicados no se insertan.
Cada evento lleva una instantánea real: Manim no decide la topología.
"""
from dataclasses import dataclass, field
from copy import deepcopy

@dataclass(frozen=True)
class Point:
    x: int
    y: int
    name: str = ''

@dataclass
class Node:
    x: int
    y: int
    side: int
    path: str = 'R'
    point: Point | None = None
    children: list = field(default_factory=list)

class QuadTree:
    ORDER = ('NO', 'NE', 'SO', 'SE')
    def __init__(self, bits=8, trace=True):
        if not isinstance(bits, int) or not 1 <= bits <= 30:
            raise ValueError('bits debe estar entre 1 y 30')
        self.trace = trace
        self.root = Node(0, 0, 1 << bits)
        self.events = []

    def snapshot(self):
        def pack(n):
            return dict(x=n.x,y=n.y,side=n.side,path=n.path,
                        point=vars(n.point) if n.point else None,
                        children=[pack(c) for c in n.children])
        return deepcopy(pack(self.root))

    def event(self, kind, node, **data):
        if not self.trace: return
        self.events.append(dict(kind=kind,path=node.path,state=self.snapshot(),**data))

    @staticmethod
    def quadrant(n,p):
        half=n.side//2
        return (0 if p.y >= n.y+half else 2)+(1 if p.x >= n.x+half else 0)

    def valid(self,p):
        return (type(p.x) is int and type(p.y) is int and
                0 <= p.x < self.root.side and 0 <= p.y < self.root.side)

    def insert(self,p):
        self.events=[]
        if not self.valid(p):
            self.event('outside',self.root); return False
        def put(n,p):
            self.event('visit',n)
            if not n.children:
                if n.point is None:
                    n.point=p; self.event('store',n); return True
                if (n.point.x,n.point.y)==(p.x,p.y):
                    self.event('duplicate',n); return False
                old=n.point; n.point=None; h=n.side//2
                assert h >= 1  # dos coordenadas enteras distintas caben antes del nivel bits
                n.children=[Node(n.x+dx*h,n.y+dy*h,h,n.path+'/'+label)
                            for label,dx,dy in [('NO',0,1),('NE',1,1),('SO',0,0),('SE',1,0)]]
                self.event('split',n)
                put(n.children[self.quadrant(n,old)],old)
            return put(n.children[self.quadrant(n,p)],p)
        return put(self.root,p)

    def delete(self,p):
        self.events=[]
        if not self.valid(p):
            self.event('outside',self.root); return False
        def remove(n):
            self.event('visit',n)
            if not n.children:
                found=n.point is not None and (n.point.x,n.point.y)==(p.x,p.y)
                if found: n.point=None
                self.event('delete' if found else 'absent',n)
                return found
            found=remove(n.children[self.quadrant(n,p)])
            if found and all(not c.children for c in n.children):
                occupied=[c.point for c in n.children if c.point is not None]
                if len(occupied)<=1:
                    n.children=[]; n.point=occupied[0] if occupied else None
                    self.event('merge',n)
            return found
        return remove(self.root)

    def traverse(self):
        self.events=[]; result=[]
        def walk(n):
            self.event('visit',n)
            if n.children:
                for c in n.children: walk(c)
            elif n.point:
                result.append(n.point); self.event('emit',n,output=[p.name for p in result])
        walk(self.root)
        return result

    def stats(self):
        def count(n,d):
            sub=[count(c,d+1) for c in n.children]
            return (1+sum(s[0] for s in sub),max([d]+[s[1] for s in sub]))
        return count(self.root,0)

POINTS=[Point(48,208,'A'),Point(208,208,'B'),Point(48,48,'C'),Point(208,48,'D')]
EXTRA=Point(80,176,'E')
def example(extra=False):
    q=QuadTree()
    for p in POINTS+([EXTRA] if extra else []): q.insert(p)
    return q

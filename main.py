"""Escenas independientes de Manim. Topología y pasos: quadtree.py.
Ejemplo: python -m manim -qh main.py S02Insercion
"""
from manim import *
from pathlib import Path
import json
from quadtree import QuadTree, Point, POINTS, EXTRA, example

BASE=Path(__file__).resolve().parent
TIMES=json.loads((BASE/'tiempos.json').read_text())
BG='#101827'; WHITE_C='#E8EEF8'; MUTED='#98A9C4'; CYAN='#45D7DC'; GOLD='#FFCA68'; RED_C='#FF7F83'
config.background_color=BG
config.max_files_cached=500
config.disable_caching=True

def txt(s,size=24,color=WHITE_C):
    return Text(s,font='DejaVu Sans',font_size=size,color=color)

def fit(m,w=6.5,h=4.9):
    if m.width>w: m.scale_to_fit_width(w)
    if m.height>h: m.scale_to_fit_height(h)
    return m

def flatten(n):
    yield n
    for c in n['children']: yield from flatten(c)

class Base(Scene):
    title=''; number=''
    def setup(self):
        self.camera.background_color=BG
        self.add(txt('CS2023  /  ALGORITMOS Y ESTRUCTURAS DE DATOS',15,MUTED).to_edge(UP,buff=.23))
        self.add(txt(self.title,32).move_to([0,3.15,0]))
        self.add(Line([-6.55,2.7,0],[6.55,2.7,0],color='#314159'))
        self.add(txt(self.number+' / 07',16,CYAN).move_to([6.2,3.65,0]))
        self.add(txt('PR QUADTREE  •  CAPACIDAD 1',14,MUTED).move_to([-4.7,-2.95,0]))
        self.panel=None; self.spatial=None; self.status=None; self.progress=None
    def cue(self,key,action):
        start=self.time
        action()
        left=TIMES[key]-(self.time-start)
        if left < -.04: raise RuntimeError(f'{key}: animación excede el tiempo asignado en {-left:.2f}s')
        if left>.001: self.wait(left)
    def show_panel(self,lines,code=False):
        if isinstance(lines,str): lines=lines.split('\n')
        g=VGroup()
        for i,line in enumerate(lines):
            if not line.strip(): continue
            indent=len(line)-len(line.lstrip()) if code else 0
            m=Text(line.lstrip() if code else line,font='DejaVu Sans Mono' if code else 'DejaVu Sans',font_size=21 if code else 25,color=WHITE_C)
            m.shift(RIGHT*(-m.get_left()[0]+indent*.12))
            m.set_y(-i*(.39 if code else .57))
            g.add(m)
        fit(g,6.65,4.7); g.move_to([3.1,.15,0])
        if self.panel: self.play(ReplacementTransform(self.panel,g),run_time=.35)
        else: self.play(FadeIn(g,shift=UP*.1),run_time=.35)
        self.panel=g
    def status_text(self,s):
        g=fit(txt(s,20,GOLD),12.6,.4).move_to([0,-2.5,0])
        if self.status: self.remove(self.status)
        self.add(g); self.status=g
    def spatial_group(self,state,active='',box=None,targets=None):
        # Coordenadas y divisiones siempre proceden de la instantánea.
        x0,y0,side=box or (0,0,state['side']); k=4.65/side
        def xy(x,y): return [-3.8+(x-x0-side/2)*k,.05+(y-y0-side/2)*k,0]
        g=VGroup(Square(side_length=4.65,color=MUTED,stroke_width=2).move_to([-3.8,.05,0]))
        for n in flatten(state):
            if n['x']<x0 or n['y']<y0 or n['x']+n['side']>x0+side or n['y']+n['side']>y0+side: continue
            if n['path']==active:
                g.add(Square(side_length=n['side']*k,stroke_width=0,fill_color=CYAN,fill_opacity=.13).move_to(xy(n['x']+n['side']/2,n['y']+n['side']/2)))
            if n['children']:
                mx=n['x']+n['side']/2; my=n['y']+n['side']/2
                g.add(Line(xy(mx,n['y']),xy(mx,n['y']+n['side']),color=CYAN,stroke_width=1.8))
                g.add(Line(xy(n['x'],my),xy(n['x']+n['side'],my),color=CYAN,stroke_width=1.8))
            if n['point'] and targets is None:
                p=n['point']; pos=xy(p['x'],p['y'])
                g.add(Dot(pos,radius=.062,color=GOLD),txt(p['name'],19,GOLD).move_to(np.array(pos)+[.16,.16,0]))
        if targets:
            for p in targets:
                if x0<=p.x<x0+side and y0<=p.y<y0+side:
                    pos=xy(p.x,p.y); g.add(Dot(pos,radius=.055,color=GOLD))
                    if side<=4: g.add(txt(p.name,19,GOLD).move_to(np.array(pos)+[.18,.2,0]))
        g.add(txt(f'[{x0}, {x0+side}) × [{y0}, {y0+side})',15,MUTED).move_to([-3.8,2.52,0]))
        return g
    def tree_group(self,state,active=''):
        leaves=[]
        def collect(n):
            if n['children']:
                for c in n['children']: collect(c)
            else: leaves.append(n['path'])
        collect(state); positions={}; edges=VGroup(); nodes=VGroup()
        def place(n,d):
            if n['children']:
                xs=[place(c,d+1) for c in n['children']]; x=sum(xs)/len(xs)
            else: x=.15+6.0*(leaves.index(n['path'])+.5)/len(leaves)
            y=1.8-d*1.2; positions[n['path']]=[x,y,0]
            return x
        place(state,0)
        for n in flatten(state):
            pos=positions[n['path']]
            for c in n['children']: edges.add(Line(pos,positions[c['path']],color='#60738F',stroke_width=1.5))
            color=GOLD if n['path']==active else CYAN if n['point'] else MUTED
            nodes.add(Circle(radius=.20,color=color,fill_color=BG,fill_opacity=1,stroke_width=2).move_to(pos))
            label=n['point']['name'] if n['point'] else '•' if n['children'] else '∅'
            nodes.add(txt(label,17,color).move_to(pos))
            label='raíz' if n['path']=='R' else n['path'].split('/')[-1]
            nodes.add(txt(label,13,MUTED).move_to(np.array(pos)+[0,-.35,0]))
        return VGroup(edges,nodes,txt('ÁRBOL  /  NO → NE → SO → SE',16,MUTED).move_to([3.2,2.4,0]))
    def display(self,state,active='',tree=False,box=None,targets=None,rt=.22):
        g=self.spatial_group(state,active,box,targets)
        animations=[]
        if self.spatial: animations.append(ReplacementTransform(self.spatial,g))
        else: animations.append(FadeIn(g))
        self.spatial=g
        if tree:
            t=self.tree_group(state,active)
            if self.panel: animations.append(ReplacementTransform(self.panel,t))
            else: animations.append(FadeIn(t))
            self.panel=t
        self.play(*animations,run_time=rt)
    def replay(self,q,tree=False,kinds=None,rt=.35):
        words={'visit':'Visitar','store':'Guardar punto','split':'Subdividir y redistribuir','delete':'Eliminar punto','merge':'Fusionar hojas','emit':'Emitir punto','duplicate':'Duplicado: sin cambios','absent':'Punto ausente: sin cambios','outside':'Fuera del dominio: rechazado'}
        for e in q.events:
            if kinds and e['kind'] not in kinds: continue
            self.status_text(words[e['kind']]+'  ·  '+e['path'])
            self.display(e['state'],e['path'],tree,rt=rt)
            if e['kind']=='emit': self.status_text('Salida: '+ ' → '.join(e['output']))

INSERT=['INSERTAR(n, p)', 'si n es hoja:', '  si vacía: guardar p; retornar', '  si misma coordenada: rechazar', '  anterior ← n.punto', '  crear 4 hijos; vaciar n', '  INSERTAR(hijo(anterior), anterior)', 'INSERTAR(hijo(p), p)', '', 'hijo: comparar x, y con el centro']
DELETE=['ELIMINAR(n, p)', 'si n es hoja:', '  borrar solo si coincide; retornar', 'ELIMINAR(hijo(p), p)', 'si los 4 hijos son hojas', '   y contienen ≤ 1 punto:', '  mover ese punto a n, si existe', '  eliminar los 4 hijos', '', 'Repetir la comprobación al regresar']
WALK=['RECORRER(n)', 'si n es hoja:', '  si tiene punto: EMITIR(n.punto)', 'si no:', '  para hijo en [NO, NE, SO, SE]:', '    RECORRER(hijo)', '', 'Se visitan también las hojas vacías.']

class S01Concepto(Base):
    title='Quadtree | El espacio se convierte en árbol'; number='01'
    def construct(self):
        q=example(True)
        self.cue('titulo',lambda:self.display(q.snapshot(),tree=True,rt=1))
        self.cue('tda',lambda:self.show_panel(['TDA: conjunto de puntos 2D','Insertar · Eliminar · Recorrer','Índices geográficos','Candidatos a colisiones 2D']))
        self.cue('reglas',lambda:self.show_panel(['Variante: PR quadtree','Particiones por el centro','4 hijos: NO · NE · SO · SE','Hoja: 0 o 1 punto','Interno: región, sin punto']))

class S02Insercion(Base):
    title='Inserción | Dividir solo cuando hace falta'; number='02'
    def construct(self):
        q=QuadTree()
        def first():
            self.display(q.snapshot(),tree=True)
            for p in POINTS[:2]: q.insert(p); self.replay(q,True,rt=.5)
        self.cue('base',first)
        def four():
            for p in POINTS[2:]: q.insert(p); self.replay(q,True,rt=.5)
        self.cue('cuatro',four)
        self.cue('pseudo_insert',lambda:self.show_panel(INSERT,True))
        def extra():
            q.insert(EXTRA); self.replay(q,rt=.65)
            self.display(q.snapshot(),tree=True)
            self.status_text('E(80,176): raíz → NO → SE')
        self.cue('extra',extra)

class S03Eliminacion(Base):
    title='Eliminación | Borrar y reunir regiones'; number='03'
    def construct(self):
        q=example(True)
        def intro(): self.display(q.snapshot()); self.show_panel(DELETE,True)
        self.cue('pseudo_delete',intro)
        def remove(): q.delete(EXTRA); self.replay(q,True,rt=.75)
        self.cue('delete',remove)
        self.cue('merge_rule',lambda:self.show_panel(['Condición de fusión','4 hijos que sean hojas','0 o 1 punto entre los cuatro','Costo por comprobación: Θ(1)','Se revisa cada ancestro del camino']))

class S04Recorrido(Base):
    title='Recorrido | Profundidad y orden espacial'; number='04'
    def construct(self):
        q=example(True)
        def intro(): self.display(q.snapshot()); self.show_panel(WALK,True)
        self.cue('pseudo_walk',intro)
        def walk(): q.traverse(); self.replay(q,True,rt=.55)
        self.cue('walk',walk)

class S05Bordes(Base):
    title='Casos borde | Reglas que evitan ambigüedades'; number='05'
    def construct(self):
        q=QuadTree()
        def empty():
            q.traverse(); self.display(q.snapshot(),tree=True); self.status_text('Conjunto vacío: salida []')
            self.wait(1); q.insert(Point(128,128,'M')); self.replay(q,True,rt=.5)
            q.delete(Point(1,2)); self.replay(q,True,rt=.5)
        self.cue('empty',empty)
        def duplicate():
            q.insert(Point(128,128,'X')); self.replay(q,True,rt=.7)
            self.show_panel(['M(128,128) = X(128,128)','Conjunto: no admite duplicados','Una sola hoja, sin subdivisión','Fuera de [0,256)²: rechazar'])
            q.insert(Point(256,0)); self.replay(q,rt=.6)
        self.cue('duplicate',duplicate)
        def boundary():
            q.insert(Point(0,0,'O')); self.replay(q,True,rt=.45)
            self.show_panel(['x < centro: oeste','x ≥ centro: este','y < centro: sur','y ≥ centro: norte','M(128,128) pertenece a NE'])
        self.cue('boundary',boundary)

class S06PeorCaso(Base):
    title='Peor caso | Dos puntos, una rama profunda'; number='06'
    def construct(self):
        q=QuadTree(); p=Point(0,0,'P'); r=Point(1,1,'Q'); q.insert(p); q.insert(r)
        events=q.events[:]; splits=[e for e in events if e['kind']=='split']
        def near():
            self.display(events[0]['state'],targets=[p,r])
            self.show_panel(['P = (0,0)     Q = (1,1)','Solo n = 2 puntos','Mismo cuadrante una y otra vez','La cercanía aumenta la profundidad'])
        self.cue('near',near)
        def zoom():
            for i,e in enumerate(splits):
                n=next(n for n in flatten(e['state']) if n['path']==e['path'])
                self.display(e['state'],e['path'],box=(n['x'],n['y'],n['side']),targets=[p,r],rt=.6)
                self.show_panel([f'Subdivisión {i+1} de {len(splits)}',f'Lado de la región: {n["side"]}',f'Profundidad creada: {i+1}', 'P y Q distintos' if i==7 else 'P y Q siguen en SO'])
            self.status_text('Acercamientos geométricos a regiones de la estructura real')
        self.cue('zoom',zoom)
        def deep():
            count,height=q.stats(); q.traverse(); visits=[e for e in q.events if e['kind']=='visit']
            self.show_panel([f'n = 2    h = {height}    V = {count}','8 internos + 25 hojas','Recorrido: visita todos los nodos','Emite únicamente P y Q'])
            for i,e in enumerate(visits):
                self.status_text(f'Visita {i+1}/{count}  ·  '+e['path']); self.wait(.11)
        self.cue('deep',deep)
        def cascade():
            q.delete(r); merges=[e for e in q.events if e['kind']=='merge']
            for i,e in enumerate(merges):
                n=next(n for n in flatten(e['state']) if n['path']==e['path'])
                self.display(e['state'],e['path'],box=(n['x'],n['y'],n['side']),rt=.55)
                self.show_panel([f'Fusión {i+1} de {len(merges)}',f'Región de lado {n["side"]}','Solo queda el punto P','Se comprueban cuatro hijos'])
            self.status_text('Estado final: una raíz, un punto, altura 0')
        self.cue('cascade',cascade)

class S07Complejidad(Base):
    title='Complejidad | Demostración y conclusiones'; number='07'
    def construct(self):
        def left(lines):
            g=VGroup(*[txt(l,26,CYAN if i==0 else WHITE_C) for i,l in enumerate(lines)]).arrange(DOWN,buff=.35,aligned_edge=LEFT)
            fit(g,5.1,4.5); g.move_to([-3.8,.1,0])
            if self.spatial: self.play(ReplacementTransform(self.spatial,g),run_time=.4)
            else: self.play(FadeIn(g),run_time=.4)
            self.spatial=g
        def height():
            left(['Parámetros','n: puntos almacenados','h: altura en aristas','V: nodos totales','b: bits por coordenada'])
            self.show_panel(['Modelo de costo','Aritmética de tamaño fijo: O(1)','Capacidad de hoja: 1','Sin costo de dibujar ni copiar','Raíz: profundidad cero'])
        self.cue('height',height)
        def ins():
            left(['INSERCIÓN','T(h) ≤ c(h + 1)','Peor camino: Ω(h + 1)','⇒ Θ(h + 1) en el peor caso'])
            self.show_panel(['Por cada nivel:','1 selección de cuadrante','≤ 4 hijos nuevos','≤ 1 reubicación del punto anterior','h incluye la profundidad creada'])
        self.cue('proof_insert',ins)
        def delete():
            left(['ELIMINACIÓN','T(h) = T(h − 1) + c','T(0) = d','T(h) = ch + d','⇒ Θ(h + 1), peor caso'])
            self.show_panel(['Descenso: un único camino','Ascenso: ≤ 4 hijos por nivel','Ejemplo extremo: 8 fusiones','Si se encuentra antes: menor costo'])
        self.cue('proof_delete',delete)
        def walk():
            left(['RECORRIDO','T = Σ costo de cada nodo','c₁V ≤ T ≤ c₂V','⇒ Θ(V)'])
            self.show_panel(['Identidad de un árbol lleno','Aristas = V − 1 = 4I','⇒ V = 4I + 1','I = 8  ⇒  V = 33','Pila recursiva: O(h + 1)'])
        self.cue('proof_walk',walk)
        def limits():
            left(['ALTURA','Equilibrado: n ≍ 4ʰ','⇒ h = Θ(log₄ n)','No se garantiza equilibrio'])
            self.show_panel(['Dominio entero: [0, 2ᵇ)²','Lado a profundidad h: 2ᵇ / 2ʰ','En h = b, lado 1: un punto posible','⇒ h ≤ b; aquí b = 8','Sin precisión fija: n no acota h'])
        self.cue('limits',limits)
        def end():
            left(['DOS CONCLUSIONES','1. La partición sigue a los datos.','2. La altura depende del espacio.'])
            names=json.loads((BASE/'integrantes.json').read_text())
            self.show_panel(['QUADTREE · CS2023', *names, 'Implementación original + Manim'])
            self.status_text('Cada operación visualizada se ejecuta en quadtree.py')
        self.cue('conclusion',end)

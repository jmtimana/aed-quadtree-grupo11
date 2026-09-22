"""
quadtree.py
Implementacion real de un Quadtree (arbol de particion espacial 2D).

Cada operacion (insert, query_range, remove) registra una bitacora de
"eventos" en self.events. La animacion (scene_quadtree.py) NO simula
pasos a mano: simplemente reproduce esta bitacora, que proviene de la
ejecucion real de esta estructura de datos.

Grupo 11 - CS2023 Algoritmos y Estructuras de Datos
Integrantes: Jose Timana, Alondra Solange, Josue Huaman
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Point:
    x: float
    y: float
    label: str = ""

    def as_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Boundary:
    """Region rectangular representada por su centro y semi-ancho/alto."""
    cx: float
    cy: float
    half_w: float
    half_h: float

    def contains(self, p: Point) -> bool:
        return (self.cx - self.half_w <= p.x <= self.cx + self.half_w and
                self.cy - self.half_h <= p.y <= self.cy + self.half_h)

    def intersects(self, other: "Boundary") -> bool:
        return not (other.cx - other.half_w > self.cx + self.half_w or
                    other.cx + other.half_w < self.cx - self.half_w or
                    other.cy - other.half_h > self.cy + self.half_h or
                    other.cy + other.half_h < self.cy - self.half_h)


class QuadtreeNode:
    def __init__(self, boundary: Boundary, capacity: int = 4, depth: int = 0):
        self.boundary = boundary
        self.capacity = capacity
        self.depth = depth
        self.points: List[Point] = []
        self.divided = False
        self.nw = self.ne = self.sw = self.se = None  # type: Optional['QuadtreeNode']


class Quadtree:
    """
    TDA: conjunto de puntos en el plano 2D.
    Operaciones: insert (O(log N) promedio), query_range (busqueda por
    rango) y remove. Cuando un nodo excede su capacidad se subdivide en
    4 cuadrantes (NW, NE, SW, SE).
    """

    MAX_DEPTH = 8  # evita recursion infinita en el peor caso (puntos casi identicos)

    def __init__(self, boundary: Boundary, capacity: int = 4):
        self.root = QuadtreeNode(boundary, capacity)
        self.events: List[dict] = []  # bitacora para la animacion
        self._n = 0

    # ---------- utilidades de eventos ----------
    def _log(self, ev_type: str, **kwargs):
        self.events.append({"type": ev_type, **kwargs})

    def reset_events(self):
        self.events = []

    # ---------- insercion ----------
    def insert(self, p: Point) -> bool:
        self._log("insert_start", point=p.as_tuple(), label=p.label)
        ok = self._insert(self.root, p)
        self._log("insert_end", point=p.as_tuple(), ok=ok)
        if ok:
            self._n += 1
        return ok

    def _insert(self, node: QuadtreeNode, p: Point) -> bool:
        if not node.boundary.contains(p):
            self._log("reject_out_of_bounds", point=p.as_tuple(),
                       boundary=self._b(node.boundary))
            return False

        if not node.divided and len(node.points) < node.capacity:
            node.points.append(p)
            self._log("place_point", point=p.as_tuple(),
                       boundary=self._b(node.boundary), depth=node.depth)
            return True

        if not node.divided:
            if node.depth >= self.MAX_DEPTH:
                # caso borde: profundidad maxima (puntos casi coincidentes)
                node.points.append(p)
                self._log("place_point_maxdepth", point=p.as_tuple(),
                           boundary=self._b(node.boundary), depth=node.depth)
                return True
            self._subdivide(node)

        for child in (node.nw, node.ne, node.sw, node.se):
            if child.boundary.contains(p):
                return self._insert(child, p)
        return False

    def _subdivide(self, node: QuadtreeNode):
        cx, cy = node.boundary.cx, node.boundary.cy
        hw, hh = node.boundary.half_w / 2, node.boundary.half_h / 2
        node.nw = QuadtreeNode(Boundary(cx - hw, cy + hh, hw, hh), node.capacity, node.depth + 1)
        node.ne = QuadtreeNode(Boundary(cx + hw, cy + hh, hw, hh), node.capacity, node.depth + 1)
        node.sw = QuadtreeNode(Boundary(cx - hw, cy - hh, hw, hh), node.capacity, node.depth + 1)
        node.se = QuadtreeNode(Boundary(cx + hw, cy - hh, hw, hh), node.capacity, node.depth + 1)
        node.divided = True
        self._log("subdivide", boundary=self._b(node.boundary), depth=node.depth,
                   children=[self._b(c.boundary) for c in
                             (node.nw, node.ne, node.sw, node.se)])

        old_points = node.points
        node.points = []
        for old in old_points:
            for child in (node.nw, node.ne, node.sw, node.se):
                if child.boundary.contains(old):
                    child.points.append(old)
                    self._log("reinsert_after_subdivide", point=old.as_tuple(),
                               boundary=self._b(child.boundary))
                    break

    # ---------- busqueda por rango ----------
    def query_range(self, rng: Boundary) -> List[Point]:
        found: List[Point] = []
        self._log("query_start", boundary=self._b(rng))
        self._query(self.root, rng, found)
        self._log("query_end", found=[p.as_tuple() for p in found])
        return found

    def _query(self, node: QuadtreeNode, rng: Boundary, found: List[Point]):
        if not node.boundary.intersects(rng):
            self._log("query_skip", boundary=self._b(node.boundary))
            return
        self._log("query_visit", boundary=self._b(node.boundary))
        for p in node.points:
            if rng.contains(p):
                found.append(p)
                self._log("query_hit", point=p.as_tuple())
        if node.divided:
            for child in (node.nw, node.ne, node.sw, node.se):
                self._query(child, rng, found)

    # ---------- eliminacion ----------
    def remove(self, p: Point) -> bool:
        self._log("remove_start", point=p.as_tuple())
        ok = self._remove(self.root, p)
        self._log("remove_end", point=p.as_tuple(), ok=ok)
        if ok:
            self._n -= 1
        return ok

    def _remove(self, node: QuadtreeNode, p: Point) -> bool:
        if not node.boundary.contains(p):
            return False
        for i, q in enumerate(node.points):
            if q.as_tuple() == p.as_tuple():
                node.points.pop(i)
                self._log("remove_point", point=p.as_tuple(),
                           boundary=self._b(node.boundary))
                return True
        if node.divided:
            for child in (node.nw, node.ne, node.sw, node.se):
                if self._remove(child, p):
                    return True
        return False

    # ---------- helpers ----------
    @staticmethod
    def _b(b: Boundary) -> Tuple[float, float, float, float]:
        return (b.cx, b.cy, b.half_w, b.half_h)

    def __len__(self):
        return self._n


if __name__ == "__main__":
    # Prueba rapida de humo (no requiere Manim).
    import random
    random.seed(1)
    qt = Quadtree(Boundary(0, 0, 4, 4), capacity=3)
    for _ in range(15):
        qt.insert(Point(random.uniform(-4, 4), random.uniform(-4, 4)))
    print(f"Puntos insertados: {len(qt)}")
    hits = qt.query_range(Boundary(0, 0, 2, 2))
    print(f"Puntos en el rango central: {len(hits)}")
    print(f"Eventos totales registrados: {len(qt.events)}")

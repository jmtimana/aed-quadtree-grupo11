"""
scene_quadtree.py
Animacion (Manim Community) construida a partir de la ejecucion REAL de
quadtree.py. Ningun paso se dibuja "a mano": cada evento registrado por
la estructura de datos (subdivide, place_point, query_visit, etc.) se
traduce a una animacion.

Requiere: manim (Manim Community Edition) >= 0.18, ffmpeg, LaTeX (opcional
si se usan Tex/MathTex; este script solo usa Text, por lo que LaTeX no
es obligatorio).

Ejecutar (calidad baja, rapido, para revisar):
    manim -pql scene_quadtree.py QuadtreeDemo

Ejecutar (alta resolucion, para la entrega final):
    manim -pqh scene_quadtree.py QuadtreeDemo

Grupo 11 - CS2023 Algoritmos y Estructuras de Datos
Integrantes: Jose Timana, Alondra Solange, Josue Huaman
"""

import random

from manim import (
    Scene, Text, VGroup, Rectangle, Dot, Write, FadeIn, FadeOut, Create,
    Indicate, UP, DOWN, LEFT, DR, YELLOW, GREEN, RED, BLUE_D, ORANGE,
)

from quadtree import Quadtree, Boundary, Point


class QuadtreeDemo(Scene):
    def construct(self):
        self.show_title()
        self.demo_empty_and_insertions()
        self.demo_query()
        self.demo_worst_case()
        self.show_complexity()
        self.show_credits()

    # ---------------- 0) Titulo ----------------
    def show_title(self):
        title = Text("Anima tu Estructura de Datos", font_size=40)
        subtitle = Text("Quadtree", font_size=32, color=YELLOW)
        team = Text("Jose Timana | Alondra Solange | Josue Huaman", font_size=22)
        group = VGroup(title, subtitle, team).arrange(DOWN, buff=0.4)
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.play(FadeIn(team))
        self.wait(1)
        self.play(FadeOut(group))

    # ---------------- utilidades de dibujo a partir de eventos ----------------
    def _rect_from_boundary(self, b, color="#3B82F6", stroke_width=2):
        cx, cy, hw, hh = b
        return Rectangle(width=2 * hw, height=2 * hh, color=color,
                          stroke_width=stroke_width).move_to([cx, cy, 0])

    def _run_events(self, qt: Quadtree, rect_map: dict, point_dots: dict,
                     skip_types=()):
        for ev in qt.events:
            t = ev["type"]
            if t in skip_types:
                continue
            if t == "subdivide":
                new_rects = []
                for cb in ev["children"]:
                    r = self._rect_from_boundary(cb, color=BLUE_D)
                    rect_map[cb] = r
                    new_rects.append(r)
                self.play(*[Create(r) for r in new_rects], run_time=0.5)
            elif t in ("place_point", "place_point_maxdepth", "reinsert_after_subdivide"):
                p = ev["point"]
                dot = Dot(point=[p[0], p[1], 0], color=YELLOW, radius=0.06)
                point_dots[p] = dot
                self.play(FadeIn(dot, scale=2), run_time=0.25)
            elif t == "query_visit":
                r = rect_map.get(ev["boundary"])
                if r:
                    self.play(Indicate(r, color=GREEN, scale_factor=1.02), run_time=0.2)
            elif t == "query_hit":
                p = ev["point"]
                dot = point_dots.get(p)
                if dot:
                    self.play(dot.animate.set_color(RED).scale(1.6), run_time=0.2)
            elif t == "remove_point":
                p = ev["point"]
                dot = point_dots.pop(p, None)
                if dot:
                    self.play(FadeOut(dot, scale=0.2), run_time=0.25)

    # ---------------- 1) Caso vacio + inserciones ----------------
    def demo_empty_and_insertions(self):
        header = Text("1) Estructura vacia e inserciones", font_size=28).to_edge(UP)
        self.play(Write(header))

        boundary = Boundary(0, 0, 3.5, 3.5)
        qt = Quadtree(boundary, capacity=3)
        root_rect = self._rect_from_boundary(qt._b(boundary))
        self.play(Create(root_rect))
        self.wait(0.5)  # caso borde: quadtree vacio, sin puntos aun

        rect_map = {qt._b(boundary): root_rect}
        point_dots = {}

        random.seed(7)
        pts = [Point(random.uniform(-3, 3), random.uniform(-3, 3), f"P{i}")
               for i in range(9)]
        for p in pts:
            qt.insert(p)

        self._run_events(qt, rect_map, point_dots)
        self.wait(0.5)
        self.play(FadeOut(header))

        self.qt = qt
        self.rect_map = rect_map
        self.point_dots = point_dots

    # ---------------- 2) Busqueda por rango ----------------
    def demo_query(self):
        header = Text("2) Busqueda por rango", font_size=28).to_edge(UP)
        self.play(Write(header))

        qt = self.qt
        qt.reset_events()
        rng = Boundary(1, 1, 1.5, 1.5)
        rng_rect = self._rect_from_boundary(qt._b(rng), color=GREEN, stroke_width=3)
        self.play(Create(rng_rect))

        qt.query_range(rng)
        self._run_events(qt, self.rect_map, self.point_dots, skip_types=("subdivide",))

        self.wait(0.5)
        self.play(FadeOut(rng_rect), FadeOut(header))
        for dot in self.point_dots.values():
            dot.set_color(YELLOW)

    # ---------------- 3) Caso borde: puntos casi coincidentes ----------------
    def demo_worst_case(self):
        header = Text("3) Caso borde: puntos casi coincidentes", font_size=26).to_edge(UP)
        self.play(Write(header))

        boundary = Boundary(0, -0.2, 1.2, 1.2)
        qt2 = Quadtree(boundary, capacity=2)
        r0 = self._rect_from_boundary(qt2._b(boundary), color=ORANGE)
        r0.scale(0.9).to_corner(DR)
        self.play(Create(r0))

        for i in range(6):
            qt2.insert(Point(0.001 * i, -0.2 + 0.001 * i, f"C{i}"))

        subdivisions = sum(1 for e in qt2.events if e["type"] == "subdivide")
        info = Text(f"Subdivisiones generadas: {subdivisions}"
                    f" (profundidad max = {Quadtree.MAX_DEPTH})", font_size=22)
        info.next_to(r0, LEFT, buff=0.8)
        self.play(Write(info))
        self.wait(1.2)
        self.play(FadeOut(header), FadeOut(info), FadeOut(r0))

    # ---------------- 4) Complejidad ----------------
    def show_complexity(self):
        header = Text("Analisis de complejidad", font_size=30).to_edge(UP)
        lines = VGroup(
            Text("Insercion:   O(log N) promedio, O(N) peor caso", font_size=24),
            Text("Busqueda:    O(log N) promedio, O(N) peor caso", font_size=24),
            Text("Eliminacion: O(log N) promedio, O(N) peor caso", font_size=24),
            Text("N = numero de puntos; el peor caso ocurre con puntos", font_size=20),
            Text("muy agrupados que fuerzan subdivision hasta MAX_DEPTH.", font_size=20),
        ).arrange(DOWN, buff=0.3)
        self.play(Write(header))
        self.play(FadeIn(lines, shift=UP))
        self.wait(2)
        self.play(FadeOut(header), FadeOut(lines))

    # ---------------- 5) Creditos ----------------
    def show_credits(self):
        credits = VGroup(
            Text("Anima tu Estructura de Datos - Quadtree", font_size=30),
            Text("Jose Timana | Alondra Solange | Josue Huaman", font_size=24),
            Text("CS2023 - Algoritmos y Estructuras de Datos, 2026-2", font_size=20),
        ).arrange(DOWN, buff=0.3)
        self.play(FadeIn(credits))
        self.wait(2)
        self.play(FadeOut(credits))

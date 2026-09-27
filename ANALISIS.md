# Análisis de la implementación

## Variante y modelo

PR quadtree de capacidad uno, sin compresión de caminos. Todos los nodos internos tienen exactamente cuatro hijos, incluidas las hojas vacías. TDA: conjunto de coordenadas enteras bidimensionales; el nombre del punto es una etiqueta visual y no su identidad.

Dominio semiabierto `[0, 2^b) × [0, 2^b)`. Usamos b=8 en el video. La implementación admite b entre 1 y 30. Los duplicados se rechazan; fuera del dominio o coordenadas no enteras se rechazan. En un centro, la igualdad en x elige este y la igualdad en y elige norte.

Sean n el número de puntos, V el número de nodos, I el número de internos y h la altura en aristas (raíz de altura cero). El modelo RAM supone aritmética y comparaciones de coordenadas en O(1). Para medir la estructura se usa `QuadTree(trace=False)`: el costo de copiar instantáneas y de dibujar NO se incluye.

## Inserción

Sea H la máxima profundidad alcanzada durante la operación, incluyendo las nuevas divisiones. En cada nivel del camino del punto nuevo se selecciona un hijo con dos comparaciones. Si una hoja ocupada se divide, se crean cuatro nodos, se mueve su punto anterior a un hijo recién creado (que está vacío) y se continúa con el nuevo punto. No se recorren todos los puntos existentes.

Así, por nivel se realizan a lo sumo c operaciones, y T_ins ≤ c(H+1). En el ejemplo con dos puntos próximos se crean H niveles; cada creación cuesta al menos una constante, por lo que T_ins ≥ c'(H+1). El peor costo es Θ(H+1). Una inserción que termina antes puede costar menos. Expresar O(h) usando solo la altura previa sería incorrecto: con una raíz ocupada puede crearse una cadena profunda.

## Eliminación

El descenso sigue un solo camino hasta una hoja. Al regresar se inspeccionan cuatro hijos por ancestro. Solo se fusiona si todos son hojas y contienen como máximo un punto; recoger ese punto cuesta O(1), no se explora el subárbol completo. Sea d la profundidad alcanzada. Tenemos T(d)=T(d-1)+c, T(0)=c0; expandiendo, T(d)=cd+c0=Θ(d+1). Puesto que d≤h, la cota es O(h+1) y es ajustada en el peor caso: los puntos (0,0), (1,1) producen una eliminación que baja h niveles y fusiona h veces.

## Recorrido

Cada nodo se visita exactamente una vez. Para un interno se hacen cuatro llamadas y para una hoja se examina su punto. Por tanto T(nodo)=c+Σ T(hijo), y al sumar en todo el árbol c1 V ≤ T ≤ c2 V. El tiempo es Θ(V), más la salida de n puntos, que ya está cubierta porque n≤V. La pila recursiva ocupa O(h+1); la lista devuelta ocupa O(n).

Cada interno tiene cuatro aristas salientes y todo árbol de V nodos tiene V-1 aristas. Entonces 4I=V-1 y V=4I+1. El caso del video tiene I=8, V=33, 25 hojas y n=2. Por eso Θ(n) no describe por sí solo el recorrido de un PR quadtree no comprimido con precisión variable.

## Altura y peor caso espacial

El lado inicial es 2^b. A profundidad d, el lado es 2^(b-d). Para d=b queda una celda de lado 1 que contiene a lo sumo una coordenada entera válida. Como no almacenamos duplicados, nunca se subdivide esa celda y h≤b.

Con P=(0,0) y Q=(1,1), comparten SO hasta una región de lado 2; allí P cae en SO y Q en NE. Se necesitan b divisiones y hay 4b+1 nodos. Se alcanza h=b aun con n=2. Para coordenadas exactas de precisión no fijada puede elegirse b tan grande como se quiera; n solo no proporciona una cota de h. No se afirma que este ejemplo sea el máximo V para todo n: es un testigo de altura máxima para esta cuadrícula y de una larga cadena de fusiones.

En un árbol aproximadamente equilibrado con hojas ocupadas a profundidades comparables y ocupación no degenerada, n es comparable con 4^h; al tomar logaritmo, h=Θ(log_4 n). Esa es una hipótesis de distribución, no una garantía de esta implementación. Con b fijo, las operaciones de un camino son O(b+1); para b=8 están acotadas por ocho niveles. El almacenamiento es Θ(V), con V≤1+4nb (cota superior simple por los prefijos de los caminos de los n puntos).

## Instrumentación

`trace=True` conserva instantáneas completas para que la animación muestre exactamente el estado producido por el algoritmo. Si se generan E eventos y cada instantánea tiene a lo sumo Vmax nodos, el registro agrega O(E·Vmax) tiempo y espacio. Es un costo audiovisual, no una optimización del quadtree. Las pruebas aleatorias usan trace=False.

## Fuentes

- OpenDSA, “The PR Quadtree”: https://opendsa-server.cs.vt.edu/ODSA/Books/cnu/cpsc270/spring-2017/CPSC270SP17/html/PRquadtree.html
- Manim Community, documentación: https://docs.manim.community/en/stable/
- Enunciado CS2023 — Proyecto Final 1, proporcionado por el estudiante.

La implementación y las demostraciones de esta entrega se redactaron para este proyecto. No se reutilizó una implementación de terceros. Preparado con asistencia de ChatGPT; el grupo debe revisar, comprender y adaptar el material y documentar las contribuciones reales.

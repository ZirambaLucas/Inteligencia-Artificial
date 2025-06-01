import pygame
import sys
from queue import PriorityQueue

# Inicializar Pygame
pygame.init()

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
TURQUESA = (64, 224, 208)

# Configuración inicial
while True:
    try:
        TAMANO_TABLERO = int(input("Ingresa el tamaño del tablero (n para un tablero nxn): "))
        if TAMANO_TABLERO > 1:
            break
        else:
            print("El tamaño debe ser mayor que 1.")
    except ValueError:
        print("Por favor, ingresa un número entero válido.")

ANCHO_NODO = 60
MARGEN_BOTONES = 100
ANCHO_VENTANA = TAMANO_TABLERO * ANCHO_NODO
ALTO_VENTANA = TAMANO_TABLERO * ANCHO_NODO + MARGEN_BOTONES
VENTANA = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Algoritmo A*")

# Configuración de botones
# Botones adaptativos al ancho de la ventana
ESPACIO_ENTRE_BOTONES = ANCHO_VENTANA // 40
BOTON_ANCHO = (ANCHO_VENTANA - 4 * ESPACIO_ENTRE_BOTONES) // 3
BOTON_ALTO = 40  # Puedes ajustar este valor si quieres que sea también adaptable
POS_X_INICIAL = ESPACIO_ENTRE_BOTONES

BOTON_INICIO = pygame.Rect(POS_X_INICIAL, ALTO_VENTANA - 70, BOTON_ANCHO, BOTON_ALTO)
BOTON_META = pygame.Rect(POS_X_INICIAL + BOTON_ANCHO + ESPACIO_ENTRE_BOTONES, ALTO_VENTANA - 70, BOTON_ANCHO, BOTON_ALTO)
BOTON_COMENZAR = pygame.Rect(POS_X_INICIAL + 2 * (BOTON_ANCHO + ESPACIO_ENTRE_BOTONES), ALTO_VENTANA - 70, BOTON_ANCHO, BOTON_ALTO)

FUENTE = pygame.font.SysFont("Arial", 20)

class Nodo:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.x = fila * ANCHO_NODO
        self.y = col * ANCHO_NODO
        self.color = BLANCO
        self.vecinos = []
        self.ancho = ANCHO_NODO
        self.g = float("inf")
        self.h = float("inf")
        self.f = float("inf")

    def get_pos(self):
        return self.fila, self.col

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))
        if self.color != NEGRO:
            font = pygame.font.SysFont("Arial", 12)
            g_text = font.render(f"G:{int(self.g) if self.g != float('inf') else '-'}", True, NEGRO)
            h_text = font.render(f"H:{int(self.h) if self.h != float('inf') else '-'}", True, NEGRO)
            f_text = font.render(f"F:{int(self.f) if self.f != float('inf') else '-'}", True, NEGRO)
            ventana.blit(g_text, (self.x + 2, self.y + 2))
            ventana.blit(h_text, (self.x + 2, self.y + 15))
            ventana.blit(f_text, (self.x + 2, self.y + 28))

    def hacer_inicio(self):
        self.color = NARANJA

    def hacer_meta(self):
        self.color = PURPURA

    def hacer_pared(self):
        self.color = NEGRO

    def hacer_cerrado(self):
        self.color = ROJO

    def hacer_abierto(self):
        self.color = VERDE

    def hacer_camino(self):
        self.color = AZUL

    def restablecer(self):
        self.color = BLANCO
        self.g = float("inf")
        self.h = float("inf")
        self.f = float("inf")

    def es_pared(self):
        return self.color == NEGRO

    def es_inicio(self):
        return self.color == NARANJA

    def es_meta(self):
        return self.color == PURPURA

def crear_tablero(tamano):
    return [[Nodo(i, j) for j in range(tamano)] for i in range(tamano)]

def dibujar_tablero(ventana, tablero):
    ventana.fill(BLANCO)
    for fila in tablero:
        for nodo in fila:
            nodo.dibujar(ventana)

    for i in range(len(tablero) + 1):
        pygame.draw.line(ventana, GRIS, (0, i * ANCHO_NODO), (ANCHO_VENTANA, i * ANCHO_NODO))
        pygame.draw.line(ventana, GRIS, (i * ANCHO_NODO, 0), (i * ANCHO_NODO, ANCHO_VENTANA))

    dibujar_botones(ventana)

def dibujar_botones(ventana):
    pygame.draw.rect(ventana, NARANJA, BOTON_INICIO)
    pygame.draw.rect(ventana, PURPURA, BOTON_META)
    pygame.draw.rect(ventana, VERDE, BOTON_COMENZAR)

    texto_inicio = FUENTE.render("Inicio", True, NEGRO)
    texto_meta = FUENTE.render("Meta", True, NEGRO)
    texto_comenzar = FUENTE.render("Comenzar", True, NEGRO)

    ventana.blit(texto_inicio, (BOTON_INICIO.x + 50, BOTON_INICIO.y + 15))
    ventana.blit(texto_meta, (BOTON_META.x + 50, BOTON_META.y + 15))
    ventana.blit(texto_comenzar, (BOTON_COMENZAR.x + 30, BOTON_COMENZAR.y + 15))

def heuristica(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return 10 * (abs(x1 - x2) + abs(y1 - y2))

def algoritmo_a_estrella(tablero, inicio, meta):
    contador = 0
    open_set = PriorityQueue()
    open_set.put((0, contador, inicio))
    came_from = {}
    g_score = {nodo: float("inf") for fila in tablero for nodo in fila}
    g_score[inicio] = 0
    f_score = {nodo: float("inf") for fila in tablero for nodo in fila}
    f_score[inicio] = heuristica(inicio.get_pos(), meta.get_pos())

    inicio.g = 0
    inicio.h = f_score[inicio]
    inicio.f = f_score[inicio]

    open_set_hash = {inicio}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == meta:
            reconstruir_camino(came_from, meta, tablero)
            return True

        for vecino in obtener_vecinos(current, tablero):
            costo = 10 if (current.fila == vecino.fila or current.col == vecino.col) else 14
            tentative_g_score = g_score[current] + costo

            if tentative_g_score < g_score[vecino]:
                came_from[vecino] = current
                g_score[vecino] = tentative_g_score
                h = heuristica(vecino.get_pos(), meta.get_pos())
                f = tentative_g_score + h
                f_score[vecino] = f

                vecino.g = tentative_g_score
                vecino.h = h
                vecino.f = f

                if vecino not in open_set_hash:
                    contador += 1
                    open_set.put((f, contador, vecino))
                    open_set_hash.add(vecino)
                    vecino.hacer_abierto()

        if current != inicio:
            current.hacer_cerrado()

        dibujar_tablero(VENTANA, tablero)
        pygame.display.update()
        pygame.time.delay(50)

    return False

def obtener_vecinos(nodo, tablero):
    vecinos = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            fila, col = nodo.fila + i, nodo.col + j
            if 0 <= fila < len(tablero) and 0 <= col < len(tablero[0]):
                vecino = tablero[fila][col]
                if not vecino.es_pared():
                    vecinos.append(vecino)
    return vecinos

def reconstruir_camino(came_from, current, tablero):
    while current in came_from:
        current = came_from[current]
        if not current.es_inicio():
            current.hacer_camino()
        dibujar_tablero(VENTANA, tablero)
        pygame.display.update()
        pygame.time.delay(50)

def main():
    tablero = crear_tablero(TAMANO_TABLERO)
    inicio = None
    meta = None
    corriendo = True
    modo = None

    while corriendo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if BOTON_INICIO.collidepoint(pos):
                    modo = "inicio"
                elif BOTON_META.collidepoint(pos):
                    modo = "meta"
                elif BOTON_COMENZAR.collidepoint(pos):
                    if inicio and meta:
                        algoritmo_a_estrella(tablero, inicio, meta)
                else:
                    fila, col = pos[0] // ANCHO_NODO, pos[1] // ANCHO_NODO
                    if 0 <= fila < TAMANO_TABLERO and 0 <= col < TAMANO_TABLERO:
                        nodo = tablero[fila][col]
                        if modo == "inicio" and not nodo.es_meta() and not nodo.es_pared():
                            if inicio:
                                inicio.restablecer()
                            inicio = nodo
                            nodo.hacer_inicio()
                        elif modo == "meta" and not nodo.es_inicio() and not nodo.es_pared():
                            if meta:
                                meta.restablecer()
                            meta = nodo
                            nodo.hacer_meta()
                        elif modo is None and not nodo.es_inicio() and not nodo.es_meta():
                            if nodo.es_pared():
                                nodo.restablecer()
                            else:
                                nodo.hacer_pared()

        dibujar_tablero(VENTANA, tablero)
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

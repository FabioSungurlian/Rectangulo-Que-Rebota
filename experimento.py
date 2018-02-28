import pygame, sys, pygame.freetype
from pygame.locals import *
from random import randint, random, choice
from apscheduler.schedulers.background import BackgroundScheduler
from math import hypot
from copy import deepcopy
# Importaciones arriba

#configura apscheduler
sched = BackgroundScheduler()
sched.start()

# Variables globales
cols = {
    "fondo": pygame.Color(245, 245, 245),
    "rect": pygame.Color(105, 118, 140),
    "título": {
        "fuente": pygame.Color(50, 50, 50)
    },
    "tiempo": {
        "fuente": pygame.Color(50, 50, 50),
        "fondo": pygame.Color(200, 200, 200),
        "borde": pygame.Color(150, 150, 150)
    },
    "3D_effect": {
        "top": pygame.Color(230, 230, 230),
        "right": pygame.Color(150, 150, 150),
        "bottom": pygame.Color(20, 20, 20),
        "left": pygame.Color(150, 150, 150)
    },
    "info_text": {
        "fuente": pygame.Color(50, 50, 50),
        "fondo": pygame.Color(157, 163, 204),
        "borde": pygame.Color(100, 100, 100)
    }
}
win = [1000, 750]
lejos = 200
rectangulos_rebotones = []
info_text = [
    "                          Bienvenido a mi experimento",
    "● Puedes arrastrar a la vibora moviendo el mouse.",
    "● Puedes intentar obligarla a atravesar objetos que no debería de",
    "atravesar y observar como se niega.",
    "● ¡Observala rebotar contra la ventana y los obstaculos!",
    "● ¡Se contrae!"
]
# Clases
#------------------------------------------------------------------------------+
# Rectangulo: un rectangulo que rebota                                         |
#-----------------------------------------------------------------------------+
class Rectangulo:
    def __getitem__(self, key): return getattr(self, key)
    def __setitem__(self, key, val): setattr(self, key, val)
    def __init__(self, surfs, name, pre_follow_rect, **opciones):
        defaults = {
            "pos": [],
            "vel": 2,
            "dim": [150, 100],
            "hacia_der": choice([True, False]),
            "col": [52, 6, 73, 0],
            "rect": "rect_2",
            "max_pos": win,
            "pre_interval_secs": 0.03,
        }

        definitivo = {**defaults, **opciones}
        self.name = name
        for name, value in definitivo.items():
            setattr(self, name, value)
        self.initial_pos()
        self.max_pos = self.get_max_pos()
        self.surfs = surfs

        self.rect = pygame.Rect(
            int(self.pos[0]),
            int(self.pos[1]),
            *self.dim
        )
        self.obstaculos = [
            surfs["tiempo"],
            surfs["text"],
            surfs["text_border"]
        ]
        self.colliding_with = None
        self.surfs["rebotadores"][self.name] = self.rect
        self.pre_follow_rect = pre_follow_rect
        rectangulos_rebotones.append(self)

    # Representa unas cordenadas X y Y que no pueden ser superadas por las de pos.
    def get_max_pos(self): return [win[0] - self.dim[0], win[1] - self.dim[1]]

    # Hace que si el rectangulo vaya hacía la izquierda, vaya hacia la derecha.
    def girar(self):
        self.hacia_der = not self.hacia_der

    # Elije una posicion random en el comienzo.
    def initial_pos(self):
        self.pos = [
            randint(10, self.max_pos[0]),
            randint(10, self.max_pos[1])
        ]

    # ¿Como hago para acercarme a un punto pero solo si x es cierto?
    def acercarse(self, hacerSi, dist, job = None):
        if hacerSi:
            # Funciona porque la distancia puede ser positiva o negativa
            divisor = 400 / (self.vel * len(rectangulos_rebotones))
            negative_pos = [dist["x"] < 0, dist["y"] < 0]
            pos_alt = [
                -1 if dist["x"] < 0 else 1,
                -1 if dist["y"] < 0 else 1
            ]
            self.pos[0] -= ((dist["x"] / divisor) ** 2) * pos_alt[0]
            if dist["y"] >= lejos / 2 or dist["y"] <= -lejos / 2:
                self.pos[1] -= ((dist["y"] / divisor) ** 2) * pos_alt[1]

        elif sched.get_job(job) != None: sched.remove_job(job)

    # crea dos listas que son puntos con los que se puede corroborar si el
    # rectangulo estaría atorado si estubiese un paso a la izquierda o hacía la
    # derecha.
    def get_unreal_collider_points(self, surf):
        alts = (self.dim[0] / 5, self.dim[1] / 5)
        points = [
            [
                surf.midleft,
                surf.midright,
                surf.midtop,
                surf.midbottom,

                surf.topleft,
                surf.topright,
                surf.bottomleft,
                surf.bottomright,

                ( surf.topright[0] - alts[0], surf.topright[1] ),
                ( surf.topright[0], surf.topright[1] + alts[1]),

                ( surf.bottomleft[0] + alts[0], surf.bottomleft[1] ),
                ( surf.bottomleft[0], surf.bottomleft[1] - alts[1] ),

                ( surf.bottomright[0] - alts[0], surf.bottomright[1] ),
                ( surf.bottomright[0], surf.bottomright[1] - alts[1] ),

                ( surf.topleft[0] + alts[0], surf.topleft[1] ),
                ( surf.topleft[0], surf.topleft[1] + alts[1] ),
            ]
        ]
        points.append(points[0])

        i = 0
        for point in points[0]:
            points[0][i] = (point[0] + self.vel, point[1])
            i += 1

        i = 0
        for point in points[1]:
            points[1][i] = (point[1] - self.vel, point[1])
            i += 1
        return points

    # ¿Estoy atorado?
    def atorado(self, self_surf, obstacle):
        collide = [False, False]

        for i, pointList in enumerate(self.get_unreal_collider_points(self_surf)):
            for point in pointList:
                if obstacle.collidepoint(point):
                    collide[i] = True
                    break
        if collide[0] and collide[1]:
            self.colliding_with = obstacle
        elif self.colliding_with == obstacle:
            self.colliding_with = None
        return collide[0] and collide[1]

    # Se mueve a la izquierda o hacia la derecha.
    def moverse(self):
        if self.hacia_der and self.pos[0] <= (self.max_pos[0] - self.vel):
            self.pos[0] += self.vel
        elif not self.hacia_der and self.pos[0] >= self.vel:
            self.pos[0] -= self.vel
        else:
            self.girar()

    # La función que crea el intervalo que se acerca al centro de la pantalla
    # cuando está atorado.
    def invocador_atorado_job(self, condicional):
        job = self.interval_name("atorado_job")
        if condicional and sched.get_job(job) == None:
            sched.add_job(
                lambda: self.acercarse(
                    condicional,
                    Dist(
                        *self.rect.center,
                        win[0] - self.colliding_with.centerx,
                        win[1] - self.colliding_with.centery
                    ),
                    job
                ),
                "interval",
                seconds = self.interval_secs,
                id=job
            )
            return True
        elif (not condicional) and sched.get_job(job) != None:
            sched.remove_job(job)
        return False

    # Se asegura de acercarse a su objetivo si esta demasiado lejos y rebotar
    # cuando choca contra un obstaculo.
    def lejos_o_choque(self):

        esta_lejos = lejos < self.dist["real"]
        muy_lejos = [
            lejos < self.dist["irreal"][0],
            lejos < self.dist["irreal"][1],
        ]
        muy_lejos = muy_lejos[0] and muy_lejos[1]
        job = self.interval_name("muy_lejos_job")

        chocó = any([
            self.rect.colliderect(obstaculo) for obstaculo in self.obstaculos
        ])

        #for rebotador in self.surfs["rebotadores"].values():
        #    if self.rect.colliderect(rebotador):
        #        chocó = True
        #        break
        if chocó or esta_lejos:
            self.girar()

            if muy_lejos:
                if sched.get_job(job) == None:
                    sched.add_job(
                        lambda: self.acercarse(muy_lejos, self.dist, job),
                        "interval",
                        seconds = self.interval_secs,
                        id=job
                    )
                return True
        if ( not muy_lejos ) and sched.get_job(job) != None:
            sched.remove_job(job)
        return False

    # Crea el rectangulo, necesita estar antes de la funcion maneger.
    def pos_maneger(self):
        self.rect = pygame.Rect(
            int(self.pos[0]),
            int(self.pos[1]),
            *self.dim
        )
        return self

    # Cambía la posicion del rectangulo y crea el efecto 3D
    def maneger(self, ventana):
        surfs = self.surfs

        self.follow_rect = self.pre_follow_rect()
        self.rect = pygame.Rect(
            int(self.pos[0]),
            int(self.pos[1]),
            *self.dim
        )

        # Configua el efecto 3D
        efecto_3D(
            ventana,
            self.follow_rect,
            self.rect
        )

        surfs["rebotadores"][self.name] = self.rect

        # Configua el efecto 3D
        efecto_3D(
            ventana,
            self.follow_rect,
            self.rect
        )

        self.dist = Dist(
            *self.rect.center,
            *self.follow_rect.center,
            [self.vel, "x"]
        )

        self.surfs = surfs

        self.interval_secs = round(
            self.pre_interval_secs * len(self.surfs["rebotadores"]),
            6
        )

        # todo hasta "pygame.update()" configura el rebote
        atorado = any([
            self.atorado(self.rect, obstaculo) for obstaculo in self.obstaculos
        ])

        atorado = self.invocador_atorado_job(atorado)
        lejos_o_chocó = False if atorado else self.lejos_o_choque()

        # Hace que se mueva y rebote con la ventana
        if not (lejos_o_chocó or atorado):
            self.moverse()

    def interval_name(self, interval_name):
        return interval_name + " " + self.name

#------------------------------------------------------------------------------+
# Dist: Un objeto que tiene distintos tipos de distancias                      |
#-----------------------------------------------------------------------------+
class Dist:
    def __getitem__(self, key): return getattr(self, key)
    def __setitem__(self, key, val): setattr(self, key, val)
    def __init__(self, x1, y1, x2, y2, *modifiers):
        self.x = x1 - x2
        self.y = y1 - y2
        self.real = hypot(self.x, self.y)
        self.irreal = []
        irreal = []
        if len(modifiers) != 0:
            for mod in modifiers:
                x = mod[0] if mod[1] in ["x", "all"] else 0
                y = mod[0] if mod[1] in ["y", "all"] else 0
                irreal.append((
                    hypot(self.x + x, self.y + y),
                    hypot(self.x - x, self.y - y)
                ))
        if len(irreal) > 1: self.irreal.extend(irreal)
        elif len(irreal) == 1: self.irreal.extend(*irreal)

def efecto_3D(ventana, rect, rect_1):
    lados = {
        "bottom": (
            ( rect.bottomleft ),
            ( rect.bottomright ),
            ( rect_1.bottomright ),
            ( rect_1.bottomleft )
        ),
        "right": (
            ( rect.topright ),
            ( rect.bottomright ),
            ( rect_1.bottomright ),
            ( rect_1.topright )
        ),
        "left": (
            ( rect.topleft ),
            ( rect.bottomleft ),
            ( rect_1.bottomleft ),
            ( rect_1.topleft )
        ),
        "top": (
            ( rect.topleft ),
            ( rect.topright ),
            ( rect_1.topright),
            ( rect_1.topleft )
        ),
    }

    def compare (bigger, lower, name):
        return getattr(bigger, name) > getattr(lower, name)

    def ignore_cases (name): return [
        name in ["bottom", "right"] and compare(rect, rect_1, name),
        name in ["top", "left"] and compare(rect_1, rect, name)
    ]

    for name, item in lados.items():
        ignore = ignore_cases(name)
        if ignore[0] or ignore[1]:
            continue
        pygame.draw.polygon(ventana, (0, 0, 0), item, 4)

    for name, item in lados.items():
        ignore = ignore_cases(name)
        if ignore[0] or ignore[1]:
            continue
        pygame.draw.polygon(ventana, cols["3D_effect"][name], item)

def game():
    # Configura pygame.
    pygame.init()

    #--------------------------------------------------------------------------+
    # Configura variables locales que usan pygame.                             |
    #-------------------------------------------------------------------------+
    fuentes = {
        "open_sans_md": pygame.freetype.SysFont("Agency FB", 50, True),
        "agency_fb_sm": pygame.freetype.SysFont("Agency FB", 25, True),
        "calibri_sm": pygame.freetype.SysFont("Calibri", 16)
    }

    surfs = {
        "rect": pygame.Rect(0, 0, 100, 80),
        "rect1": pygame.Rect(100, 400, 50, 50),
        "tiempo": pygame.Rect(0, win[1] - 60, win[0], 60),
        "text": pygame.Rect(20, win[1] - 300, win[0] / 12 * 6, 300 - 60),
        "rebotadores": {}
    }
    surfs["text_border"] = pygame.Rect(
        surfs["text"].left - 5,
        surfs["text"].top - 5,
        surfs["text"].width + 10,
        surfs["text"].height + 5
    )

    textos = {
        "título": [
            fuentes["open_sans_md"].render(
                "Un rectángulo que rebota",
                cols["título"]["fuente"]
            )[0],
            (win[0] / 10, win[1] - 50)
        ],
        "tiempo": [
            None,
            (win[0] - 100, win[1] - 50)
        ],
        "titulo_de_texto": [
            fuentes["agency_fb_sm"].render(
                info_text[0],
                cols["info_text"]["fuente"]
            )[0], (
                surfs["text"].left + 20,
                surfs["text"].top + 10
            )
        ],
    }
    info_text_lines = {
        "linea" + str(i): [
            fuentes["calibri_sm"].render(
                linea,
                cols["info_text"]["fuente"]
            )[0], (
                surfs["text"].left + 20,
                surfs["text"].top + 20 * i + 40
            )
        ] for i, linea in enumerate(info_text[1:])
    }
    textos = {**textos, **info_text_lines}
    #---------------------------------------------------------------------------

    #configura la ventana.
    ventana = pygame.display.set_mode((win[0], win[1]))
    pygame.display.set_caption("Hola Mundo!!!")
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

    # Crea los objetos Rectangulos
    rect_2 = Rectangulo(surfs, "rect_2", lambda: surfs["rect"])
    rect_3 = Rectangulo(surfs, "rect_3", lambda: surfs['rebotadores']['rect_2'])
    rect_4 = Rectangulo(surfs, "rect_4", lambda: surfs['rebotadores']['rect_3'])
    # Se mantiene escuchando para ver si hay algun evento.


    while True:

        # Prepara la ventana
        ventana.fill(cols["fondo"])

        # Cronometro (resultados abajo a la derecha o en la coinsola)
        tiempo = int(pygame.time.get_ticks() // 1000)
        formatted_tiempo = (
            "0" * (4 - len( str(tiempo) ) ) if len(str(tiempo)) < 4 else ""
        ) + str(tiempo)
        textos["tiempo"][0] = fuentes["open_sans_md"].render(
            formatted_tiempo,
            cols["tiempo"]["fuente"]
        )[0]

        textos["tiempo"][1] = (
            win[0]  - 10 - len(formatted_tiempo) * 22,
            win[1] - 50
        )
        # La franja inferior
        pygame.draw.rect(ventana, cols["tiempo"]["fondo"], surfs["tiempo"])
        # Configura el texto
        pygame.draw.rect(
            ventana,
            cols["info_text"]["borde"],
            surfs["text_border"]
        )
        pygame.draw.rect(ventana, cols["info_text"]["fondo"], surfs["text"]),

        for texto in textos.values():
            ventana.blit(*texto)

        surfs["rect"].center = pygame.mouse.get_pos()
        # Configura el rectángulo rebotador.
        for rect in rectangulos_rebotones:
            rect.pos_maneger()
        for rect in reversed(rectangulos_rebotones):
            rect.maneger(ventana)

        # Configura el rectángulo que sigue al cursor.
        pygame.draw.rect(ventana, cols["rect"], surfs["rect"])

        # Escucha si el usuario cierra la ventana para detener los procesos
        for evento in pygame.event.get():
            # Cerrar ventana
            if evento.type == QUIT:
                sched.shutdown()
                pygame.quit() # Detiene modulos
                sys.exit() # Cierra ventana


        pygame.display.update()

game()

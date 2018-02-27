from time import sleep
from pprint import pprint
from functools import reduce
from copy import deepcopy
import sys
import os
# Importaciones arriba

# Funciones globales abajo
def check(cond, accion):
    if not cond:
        print("Lo sentimos mucho; Hubo un error, traté de", accion)
    return cond

def check_type(item, tipos):
    msg = "usar un objeto del tipo: " + str( type(item) ) + " como si fuese" +\
    " del tipo "
    if isinstance(tipos, tuple):
        msg += "o del tipo".join([
            str(type(tipo() if callable(tipo) else tipo)) for tipo in tipos
        ])
    else:
        msg += str(type(tipos() if callable(tipos) else tipos))

    return check(isinstance(item, tipos), msg)

def check_i(i, a_list):
    valid = False
    if check_type(i, int) and check_type(a_list, list):
        valid = (i < len(a_list) and i >= 0) or (i > -len(a_list) and i <= 0)
    return valid

# Clases abajo
class DialYRes():
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        setattr(self, key, val)

    def __init__(self, dial, ress, **options):
        self.dial = dial
        self.ress = ress
        self.input_sign = options.get("input_sign", " usuario ->>")
        self.print_sign = options.get("print_sign", " bot ->>")
        self.rewind = options.get("rewind", True)

    def run(self):
        self.options = []

        for i, res in enumerate(self.ress):
            self.options.append( "\n   {0}: {1[0]}".format( i + 1, res) )
        err_msg = "Ups! se ve que te equivocaste de numero. las opciones eran:"
        err_msg += "".join(self.options)

        msg = [self.dial]
        if len(self.options) > 1:
            msg.extend(self.options)
        print("\n", self.print_sign, "".join(msg))

        while True:
            print() # añade un espacio entre posibles respuestas y "usuario ->>"

            if len(self.options) != 1:
                user_i = input(self.input_sign)
                valid_vals = map(lambda item: str(item), range(1, 20))

                valid_type = user_i in valid_vals
                if valid_type:
                    user_i = int(user_i)
                    valid_i = len(self.ress) >= user_i
                else:
                    valid_i = False

                match = self.ress[user_i - 1] if valid_i else [None, err_msg]

                if match[1] == err_msg:
                    user_opt = " Error -"
                else:
                    user_opt = " {} {}\n".format(self.input_sign, match[0])

                sys.stdout.write("\033[F" + user_opt)
                match = match[1]
            else:
                input(self.input_sign + " " + self.ress[0][0])
                match = self.ress[0][1]

            if isinstance(match, str):
                self.output(match, "bot")
            elif isinstance(match, list):
                return match
            elif callable(match):
                match()
            else:
                print("Lo sentimos mucho, tuve un error en el que la respuesta",
                    "que te trete de dar es de un tipo invalido", type(match)
                )
            if match == err_msg:
                continue
            break

    def output(self, text, outputter):
        sign = self.print_sign if outputter == "bot" else self.input_sign
        print(sign + " " + text)

    def add_opt(self, opt, position = None):
        opts = self.ress
        pos = len(opts) if position == None else position
        if check_type(opt, list) and (not opt in opts):
            opts.insert(pos, opt)

    def del_opt(self, opt):
        opts = self.ress
        if check_type(opt, (int, str)):
            if isinstance(opt, str):
                opt_i = opts.index(list(
                    filter(lambda item: item[0] == opt, opts)
                )[0])
            elif check_i(opt, opts):
                opt_i = opt
            opt_arr = opts.pop(opt_i)
            return [opt_i, opt_arr]

    def swap_opt(self, position, opt):
        pos, deleted_opt = self.del_opt(position)
        self.add_opt(opt, pos)
        return [pos, deleted_opt]

    def change_dial(self, new_val, pos = None):
        opts = self.ress
        if check_type(pos, (list, None)):
            if isinstance(pos, list) and check_i(pos[0], opts) and \
            check_i(pos[1], opts[0]):
                old_val = opts[pos[0]][pos[1]]
                opts[pos[0]][pos[1]] = new_val
            elif isinstance(pos, None):
                old_val = self.dial
                self.dial = new_val
            return [pos, old_val]


# Un dialogo que es solamente es texto
class Dial():
    def __init__(self, text, user_talks = None):
        self.text = text
        self.señal = " usuario ->>" if user_talks == True else " bot ->>"

    def run(self):
        print(self.señal, self.text)

class Accion():
    pass
# Una lista de dialogos
class DialList():
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        setattr(self, key, val)

    def __init__(self, *dials):
        self.dials = list(dials)
        self.dial_list = self.dials
        self.create_acciones()
        self.is_temp = False

    def print_text(self, result):
        is_user = False
        if len(result) == 4:
            [action, text, is_user, cur_i] = result
        elif len(result) == 3:
            [action, text, cur_i] = result
        sign = "bot" if not is_user else "user"
        this = self.buscar_dial(0, cur_i, True)[0]
        if this: this.output(text, sign)
        sleep(self.interval)

    def create_acciones(self):
        for i, accion in self.acciones.items():
            self.acciones[i] = getattr(self, accion)
        self.set_acciones_alt()

    acciones_msg = frozenset({"print", "prints"})
    acciones_sm = frozenset({"next_dial", "prev_dial", "cur_dial"})
    acciones_tel = frozenset({"next", "back", "goto_next"})
    acciones_mega = frozenset({"add_dial", "swap_dial", "del_dial"})
    acciones_mini = frozenset({"add_opt", "del_opt", "swap_opt", "change_dial"})
    # Los valores mas alla de los descritos son añadidos automaticamente.
    def set_acciones_alt(self):
        self.acciones_alt = frozenset(
            set(self.acciones.keys()) - (
                self.acciones_msg | \
                self.acciones_sm | \
                self.acciones_tel
        ))
    acciones = {
        # Muestra un mensaje ["print", texto]
        "print": "print_text",
        # Añade un dialogo a la lista de dialogos :
        # ["add_dial", add_to_index, from_current_index?, dial]
        "add_dial": "add_dial",
        # Elimina un dialogo, misma sintaxis pero sin el dialogo.
        "del_dial": "del_dial",
        # Cambia un dialogo por otro, misma sintaxis que "add_dial"
        "swap_dial": "swap_dial",
        # Añade una respuesta a un dialogo:
        # ["add_opt", dial_index, from_current_index?, dial_answer]
        "add_opt": "add_option",
        # Elimina una respuesta, misma sintaxis pero sin la respuesta
        "del_opt": "del_option",
        # Cambia una respuesta por otra, misma sintaxis que "add_opt"
        "swap_opt": "swap_option",
        # Salta a otro dialogo: ["next", goto_index, from_current_index?]
        "next": "next",
        # Cambia un dialogo, pocision nula cuendo se quiere cambiar la pregunta
        # ["change_dial", dial_pos, from_current_index?, attr_pos, new_val]
        "change_dial": "change_dial",
        # Ejecuta un texto. ["eval", "funcion"]
        "eval": "eval",
        # Vuelve a un dialogo
        "back": "back",
        # Va al siguiente dialogo
        "goto_next": "goto_next",
        # Escribe muchos mensajes en la consola, ahorra el "print":
        #   ["prints", *prints]
        "prints": "print_block",
        # Pone la ubicación del dialogo al principio de los parametros:
        # ["in_cur_dial", action, *action_params]
        "cur_dial": "do_in_cur_dial",
        # Pone la ubicación del siguiente dialogo al principio de los parametros:
        # Misma sintaxis
        "next_dial": "do_in_next_dial",
        # Pone la ubicación del dialogo previo al principio de los parametros:
        # Misma sintaxis
        "prev_dial": "do_in_prev_dial",
        # hace cambios temporales, ["temp", args..]
        "temp": "temp"
    }
    def eval(self, result): eval(result[1])

    def run(self, interval = None):
        self.interval = 1 if interval is None else interval
        self.dial_list = self.dials[:]
        self.backup_list = deepcopy(self.dials)
        result = self.run_dials(self.dial_list)

        while not "finalizado" in result:
            self.ejecutar_accion(result)
            result = self.run_dials(self.dial_list)

        if "finalizado" != result: result[1]()

    def run_dials(self, dial_list):
        for dial in dial_list:
            self.dial = dial
            cur_i = self.dials.index(dial)
            result = dial.run()

            if isinstance(dial, Dial): sleep(self.interval)

            if isinstance(result, list):
                first = result[0]

                if isinstance(first, list):
                    in_acciones = lambda el: el[0] in self.acciones
                    valida = all(map(in_acciones, result))

                    if valida:
                        return [[*val, cur_i] for val in result]
                elif first in self.acciones:
                    return [*result, cur_i]

        return "finalizado"

    def ejecutar_accion(self, result):
        first = result[0]
        acts = self.acciones
        def ejecutar (act):
            if self.is_temp and act[0] in {"next", "back"}:
                self.dials = deepcopy(self.backup_list)
                self.is_temp = False
            acts[act[0]](act)
        # El modelo de lista es: [acción, acción_params...]
        if check_type(result, list):
            if isinstance(first, list):
                for accion in result:
                    ejecutar(accion)
                result = result[-1]
            elif first in acts:
                ejecutar(result)
            else: return None

            if not (result[0] in self.acciones_tel or result[0] == "temp"):
                getattr(self,
                    "back" if self.dial.rewind else "goto_next"
                )([None, result[-1]])

    def buscar_dial(self, position, cur_i = None, from_cur_i = None,
    dial_list = None):
        pos = position
        match = False
        dials = self.dials if dial_list == None else dial_list
        if isinstance(pos, int):
            if from_cur_i == True:
                pos += cur_i

            if check_i(pos, dials):
                match = dials[pos]

        elif isinstance(pos, str):
            matches = list(filter(lambda el: el.dial, dials))

            if len(matches) == 1:
                match = matches[0]
            else:
                print(
                    "Trate de buscar un dialogo por mi pregunta, cuando hay",
                    "varios dialogos o ningun dialogo con esa pregunta"
                )

        elif isinstance(pos, DialYRes):
            match = pos

        pos = dials.index(match)
        return [match, pos]

    def es_dial(self, dial):
        return check(
            isinstance(dial, (DialYRes, Dial)),
            "usar algo como si fuese un dialogo pero siendo:" + str(type(dial))
        )

    def next(self, result):
        [action, goto_i, from_cur_i, cur_i] = result
        dial = self.buscar_dial(goto_i, cur_i, from_cur_i)
        if dial[0]:
            self.dial_list = self.dials[dial[1]:]

    def add_option(self, result, dials = None):
        [action, pos, from_cur_i, opt, cur_i] = result
        dial = self.buscar_dial(pos, cur_i, from_cur_i, dials)[0]
        if dial: dial.add_opt(opt)

    def del_option(self, result, dials = None):
        [action, pos, from_cur_i, opt_pos, cur_i] = result

        dial = self.buscar_dial(pos, cur_i, from_cur_i, dials)
        if dial:
            return dial.del_opt(opt_pos)

    def swap_option(self, result, dials = None):
        # opt = [opt_pos, opt_content]
        [action, pos, from_cur_i, opt, cur_i] = result

        dial = self.buscar_dial(pos, cur_i, from_cur_i, dials)[0]
        if dial:
            return dial.swap_opt(*opt)

    def add_dial(self, result, dials = None):
        [action, pos, from_cur_i, dial, cur_i] = result
        dials_2 = self.dials if dials == None else dials
        dial_2 = self.buscar_dial(pos, cur_i, from_cur_i, dials)
        if dial_2[0] and self.es_dial(dial):
            dials_2.insert(dial_2[1], dial)

    def del_dial(self, result, dials = None):
        [action, pos, from_cur_i, cur_i] = result
        dial, pos = self.buscar_dial(pos, cur_i, from_cur_i, dials)
        dials_2 = self.dials if dials == None else dials
        if dial:
            dials_2.remove(dial)
            return [dial, pos]

    def swap_dial(self, result, dials = None):
        [action, pos, from_cur_i, dial, cur_i] = result
        deleted_dial = self.del_dial([action, pos, from_cur_i, cur_i], dials)
        self.add_dial(result, dials)
        return deleted_dial

    def change_dial(self, result, dials = None):
        [action, dial_pos, from_cur_i, attr_pos, new_val, cur_i] = result

        dial = self.buscar_dial(dial_pos, cur_i, from_cur_i, dials)[0]
        if dial: dial.change_dial(new_val, attr_pos)

    def back(self, result):
        [action, cur_i] = result
        self.next([None, 0, True, cur_i])

    def goto_next(self, result):
        [action, cur_i] = result
        self.next([None, 1, True, cur_i])

    def print_block(self, result):
        [action, *prints] = result
        cur_i = prints.pop(-1)
        if all( map(lambda value: check_type(value, list), prints) ):
            for value in prints:
                self.acciones["print"]([None, *value, cur_i])

    def do_in_x_dial(self, result, mod):
        [accion, accion_2, *params] = result
        cur_i = params[-1]

        if accion_2 in self.acciones_alt:
            self.acciones[accion_2]([None, cur_i + mod, False, *params])

    def do_in_cur_dial(self, result): self.do_in_x_dial(result, 0)

    def do_in_next_dial(self, result): self.do_in_x_dial(result, 1)

    def do_in_prev_dial(self, result): self.do_in_x_dial(result, -1)

    def temp(self, result):
        [accion, accion_2, *params] = result
        self.backup_list = deepcopy(self.dials)
        self.is_temp = True
        if accion_2 in (self.acciones_alt | self.acciones_sm):
            self.acciones[accion_2]([None, *params])

    def multiple_dials(self, result):
        [accion, pos, *dials] = result
        cur_i = dials.pop(-1)
        for dial in dials:
            pass

# Programas para testear y o correr programa abajo
dials = DialList(
    DialYRes("¿patata o boniato?", [
        ["patata", "¡que gran eleccion!"],
        ["boniato", [["temp", "cur_dial", "swap_opt", ["boniato", [
                "te dije que me gusta el boniato", [
                        ["temp", "next_dial", "add_dial", DialYRes("¿Encerio?",[
                                ["si", [
                                    ["prints", ["..."], ["..."]],
                                    ["next", -1, False]
                                ]], ["nope",(
                                    "sabia que era imposible que te gustase el"
                                    " boniato"
                        )]])],
                        ["goto_next"]
            ]]]],
            ["cur_dial", "change_dial", [0, 1], "Sabía que mentías"]
        ]]
    ]),
    DialYRes("¿Rock o Pop?", [
        ["Rock", "rgaaaahhhh!"],
        ["Pop", ["next_dial", "add_opt",
            ["¡El lenguaje de la musica!", "ok..."]]
    ]], rewind=False),
    DialYRes("¿espanol o ingles?", [
        ["espanol", "pregunta tonta, no?"],
        ["ingles", [["next_dial", "add_dial", DialYRes(
            "¿What is your favorite type of potato?", [
                ["¿Hay muchos tipos de patatas?", "Si, los hay"],
                ["¿Estas dejando de lado a los degustadores de patatas?", "sep"],
                ["¿Que?", [
                    ["print", "acabas de fracasar el test de ingles"],
                    ["next", 3, True]
                ]],
                ["se la respuesta pero no pienso decirla", [
                    ["print", "Claro que la sabes, dare el test por fracasado"],
                    ["next", 3, True]
                ]]
            ])],
            ["add_dial", 2, True, DialYRes(
                ("Would you put your hand inside magma for the purpouse of"
                " killing all the friends of yours?"), [
                    ["Si", [
                        ["print", ("puede que no me entiendas o puede que"
                        " seas un psicopata, pero no llamare a la policia.")],
                        ["next", 2, True]
                    ]],
                    ["No", ("Lo estas haciendo muy bien por ahora, pero el "
                    "siguiente sera muy dificil")]
            ])],
            ["add_dial", 3, True, DialYRes(
                "Potato Chips?", [
                    ["¡Potato Chips!", "¡Has completado el test!"],
                    ["¿Potato Chips?", """¿Que es ese animo? por tu actitud te \
dare un premio a la persona más aguafiestas:
        ________________________
        \                      /
         \    Premio a la     /
          \  aguafiesteria   /
           \                /
            ----------------
           /                \         ¡Felecidades!
          |   _/_/_   /|     |
          |  _/_/_     |     |
          |  / /      _|_    |
           \                /
             ______________

                    """],
                    ["Estoy a dieta", """Ahí te va un premio a la salud aburrida:
        ________________________
        \                      /
         \    Premio a la     /
          \  salud aburrida  /
           \                /
            ----------------
           /                \         ¡Felecidades!
          |   _/_/_   /|     |
          |  _/_/_     |     |
          |  / /      _|_    |
           \                /
             ______________

                    """],
                    ["¿Porque sigo jugando a esto?", ["next_dial", "add_dial",
                        DialYRes("¿Osea que no sos yo?", [
                            ["no", [
                                ["print", ("fuera ahora mismo de aca, no "
                                    "permitire que jueges a esto ni hoy ni"
                                    " nunca."
                                )],
                                ["next", -1, False]
                            ]],
                            [(
                                "si que lo soy, solo estoy testeando los "
                                "dialogos que yo hice."
                            ), "uff, que susto me di"],
                            ["¿Porque iba a serlo?", [["next_dial", "add_dial",
                                DialYRes((
                                    "porque yo debi de haber eliminado todo"
                                    " esto con el paso del tiempo y...\n\t"
                                    "no me digas que todavia no he "
                                    "eliminado esto"
                                ), [
                                    ["Aparentemente no", ("ese me sirve de "
                                    "mucho consuelo")],
                                    [(
                                        "Si que lo hiciste, solo que yo "
                                        " piratie la base de datos para "
                                        "encontrar este archivo eliminado"
                                    ), ["prints",
                                        ["¡¡Seguridad!!"],
                                        ["¡No esperen, yo simplemente..",
                                            True],
                                        ["Esto te pasa por hacker"]
                                    ]],
                                    ["Yo soy tu", ["prints",
                                        ["¿Yo soy tu o yo soy yo?"],
                                        ["Tu sos yo", True],
                                        [("¿Pero no es lo mismo que yo soy yo?")],
                                        ["no", True],
                                        ["¿Porque?"],
                                        ["porque lo digo yo", True],
                                        ["¿Y yo?"],
                                        ["tu no", True],
                                        ["¿Entonces tu tampoco?"],
                                        ["aaaahhhhhh"]
                                    ]],
                                    [(
                                        "Tu me pediste que jugase a esto "
                                        "ahora no me vengas de "
                                        "sentimentalista"
                                    ), "Lo shiento"]
                        ], rewind=False)]
                    ]]
                ], rewind=False)]
            ]], rewind=False)
        ]]
    ]], rewind=False),
    DialYRes("dejemonos de hablar y empezemos con el juego", [
        ["Ya era hora...", [
            ["print", "Alla vamos!"],
            ["cur_dial", "swap_opt", ["Ya era hora...",
                ["¿Ya era hora?", ["next", 0, False]]
            ]]
        ]]
    ]),
)

dials.run()

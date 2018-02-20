from time import sleep
from pprint import pprint
from functools import reduce
import sys
import os
# Importaciones arriba

# Funciones globales abajo
def check(cond, accion):
    if not cond:
        print(
            "Lo sentimos mucho; Hubo un error, traté de", accion
        )
    return cond

def check_type(item, tipos):
    msg = "usar un objeto del tipo: " + str( type(item) ) + " como si fuese" +\
    " del tipo "
    if isinstance(tipos, tuple):
        msg += "o del tipo".join([ str(type(tipo)) for tipo in tipos ])
    else:
        msg += str(type(tipos))

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

    def __init__(self, dial, ress, input_sign = None, print_sign = None):
        self.dial = dial
        self.ress = ress
        self.input_sign = " usuario ->>" if input_sign == None else input_sign
        self.print_sign = " bot ->>" if print_sign == None else print_sign

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
                user_i = int( input(self.input_sign) )
                valid_i = len(self.ress) >= user_i
                match = self.ress[user_i - 1] if valid_i else err_msg
                sys.stdout.write("\033[F{} {}\n".format(self.input_sign, match[0]))
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
                print(
                    "Lo sentimos mucho, tuve un error en el que la respuesta",
                    "que te trete de dar es de un tipo invalido", type(match)
                )
            if match == err_msg:
                continue
            break

    def output(self, text, outputter):
        sign = self.print_sign if outputter == "bot" else self.input_sign
        print(sign + " " + text)

    def add_opt(self, option, position = None):
        pos = position if position != None else len(self.ress)
        if check_type(option, list) and (not option in self.ress):
            self.ress.insert(pos, option)

    def del_opt(self, option):
        opciones = self.ress
        if check_type(option, (int, str)):
            if isinstance(option, str):
                option_2 = opciones.index(list(
                    filter(lambda item: item[0] == option, opciones)
                )[0])
            elif check_i(option, opciones):
                option_2 = option
            opciones.pop(option_2)
            return [option_2]

    def swap_opt(self, position, option):
        pos = self.del_opt(position)[0]
        self.add_opt(option, pos)

    def change_dial(self, new_val, pos = None):
        if isinstance(pos, list):

            if check_type(pos[0], str) and check_type(pos[1], str):

                pos_num_valid = check(
                    check_i(pos[0], self.ress) and check_i(pos[1], self.ress[0]),
                    'cambiar un valor de las opciones que se sale de los ' +
                    'posibles'
                )

                if pos_num_valid:
                    self.ress[pos[0]][pos[1]] = new_val

        elif isinstance(pos, None):
            self.dial = new_val

        else:
            print("cambiar el dialogo en una posicion del tipo: " +
            str(type(pos)))


# Un dialogo que es solamente es texto
class Dial():
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

    def print_text(self, result):
        is_user = False
        if len(result) == 4:
            [action, text, is_user, cur_i] = result
        elif len(result) == 3:
            [action, text, cur_i] = result
        sign = "bot" if not is_user else "user"
        this = self.buscar_dial(0, cur_i, True)
        if this: this.output(text, sign)
        sleep(self.interval)

    def create_acciones(self):
        for i, accion in self.acciones.items():
            self.acciones[i] = getattr(self, accion)

    acciones_de_tel = ["next", "back", "goto_next"]
    # Los valores mas alla de los descritos son añadidos automaticamente.
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
        "prev_dial": "do_in_prev_dial"
    }
    def eval(self, result): eval(result[1])

    def run(self, interval = None):
        self.interval = 1 if interval is None else interval
        self.dial_list = self.dials
        result = self.run_dials(self.dial_list)

        while not "finalizado" in result:
            self.ejecutar_accion(result)
            result = self.run_dials(self.dial_list)

        if "finalizado" != result: result[1]()

    def run_dials(self, dial_list):
        for i, dial in enumerate(dial_list):

            result = dial.run()

            if isinstance(dial, Dial): sleep(self.interval)

            if isinstance(result, list):
                first = result[0]

                if isinstance(first, list):
                    valida = True
                    for action in result:
                        if not action[0] in self.acciones:
                            valida = False
                        action.append(i)
                    if valida:
                        return result
                elif first in self.acciones and first != "print":
                    result.append(i)
                    return result

        return "finalizado"

    def ejecutar_accion(self, result):
        first = result[0]
        last = result[-1]
        # El modelo de lista es: [acción, acción_params...]
        if check_type(result, list):
            if isinstance(first, list):
                for accion in result:
                    if accion[0] in self.acciones:
                        self.acciones[accion[0]](accion)
                if not last[0] in self.acciones_de_tel:
                    self.back([None, last[-1]])

            elif first in self.acciones and first != "print":
                self.acciones[first](result)
                if not first in self.acciones_de_tel:
                    self.back([None, last])

    def buscar_dial(self, position, cur_i = None, from_cur_i = None):
        pos = position
        if from_cur_i:
            pos += cur_i

        if check_type(pos, int): num_valid = check(
                check_i(pos, self.dials),
                'buscar el elemento "numero" '+ str(pos + 1) +'de una lista...'
            )
        return self.dials[pos] if check_type(pos, int) and num_valid else False

    def es_dial(self, dial):
        return check(
            isinstance(dial, (DialYRes, Dial)),
            "usar algo como si fuese un dialogo pero siendo:" + str(type(dial))
        )

    def next(self, result):
        [action, goto_i, from_cur_i, cur_i] = result
        dial = self.buscar_dial(goto_i, cur_i, from_cur_i)

        if dial:
            self.dial_list = self.dials[goto_i:]

    def add_option(self, result):
        [action, pos, from_cur_i, opt, cur_i] = result

        dial = self.buscar_dial(pos, cur_i, from_cur_i)
        if dial: dial.add_opt(opt)

    def del_option(self, result):
        [action, pos, from_cur_i, opt_pos, cur_i] = result

        dial = self.buscar_dial(pos, cur_i, from_cur_i)
        if dial: dial.del_opt(opt_pos)

    def swap_option(self, result):
        # opt = [opt_pos, opt_content]
        [action, pos, from_cur_i, opt, cur_i] = result

        dial = self.buscar_dial(pos, cur_i, from_cur_i)
        if dial: dial.swap_opt(*opt)

    def add_dial(self, result):
        [action, pos, from_cur_i, dial, cur_i] = result

        dial_2 = self.buscar_dial(pos, cur_i, from_cur_i)
        pprint(dial_2)
        if dial_2 and self.es_dial(dial): self.dials.insert(pos, dial)

    def del_dial(self, result):
        [action, pos, from_cur_i, cur_i] = result
        dial = self.buscar_dial(pos, cur_1, from_cur_i)

        if dial: self.dials.remove(dial)

    def swap_dial(self, result):
        [action, pos, from_cur_i, dial, cur_i] = result
        self.del_dial(action, pos, from_cur_i, cur_i)
        self.add_dial(result)

    def change_dial(self, result):
        [action, dial_pos, from_cur_i, attr_pos, new_val, cur_i] = result

        dial = self.buscar_dial(dial_pos, cur_i, from_cur_i)
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
        if accion_2 in self.acciones:
            self.acciones[accion_2]([None, cur_i + mod, False, *params])

    def do_in_cur_dial(self, result): self.do_in_x_dial(result, 0)

    def do_in_next_dial(self, result): self.do_in_x_dial(result, 1)

    def do_in_prev_dial(self, result): self.do_in_x_dial(result, -1)

# Programas para testear y o correr programa abajo
dials = DialList(
    DialYRes("¿patata o boñato?", [
        ["patata", "¡que gran eleccion!"],
        ["boñato", [["cur_dial", "swap_opt", ["boñato", [
                "te dije que me gusta el boñato", [
                        ["next_dial", "add_dial", DialYRes("¿Encerio?", [
                                ["si", [
                                    ["prints", ["..."], ["..."]],
                                    ["next", -1, False]
                                ]], ["nope",
                                    "sabia que era imposible que te gustase el"+
                                    "boñato"
                                ]
                            ]
                        )],
                        ["goto_next"]
                    ]
                ]
            ]],
        ]]
    ]),
    DialYRes("¿Rock o Pop?", [
        ["Rock", "rgaaaahhhh!"],
        ["Pop", [
            ["next_dial", "add_opt", ["¡El lenguaje de la musica!", "ok..."]],
            ["goto_next"]
        ]]
    ]),
    DialYRes("¿espanol o ingles?", [
        ["espanol", "pregunta tonta, no?"],
        ["ingles", "Hello"]
    ]),
    DialYRes("dejemonos de hablar y empezemos con el juego", [
        ["Ya era hora...", "Alla vamos!"]
    ]),
)
dials.run()

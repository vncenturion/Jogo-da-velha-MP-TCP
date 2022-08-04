import tkinter as tk
from tkinter import PhotoImage
from tkinter import messagebox
import socket
from time import sleep
import threading

# TELA PRINCIPAL DO JOGO
window_main = tk.Tk()
window_main.title("JOGO DA VELHA")
top_welcome_frame= tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text = "Nome:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Entrar", command=lambda : connect())
btn_connect.pack(side=tk.LEFT)
top_welcome_frame.pack(side=tk.TOP)

top_frame = tk.Frame(window_main)


# network client
client = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8432

list_labels = []
num_cols = 3
sua_vez = False
you_started = False

meus_dados = {
    "name": "Charles",
    "symbol": "X",
    "color" : "",
    "score" : 0
}

dados_do_oponente = {
    "name": " ",
    "symbol": "O",
    "color": "",
    "score": 0
}

for x in range(3):
    for y in range(3):
        lbl = tk.Label(top_frame, text=" ", font="Helvetica 45 bold", height=2, width=5, highlightbackground="grey",
                       highlightcolor="grey", highlightthickness=1)
        lbl.bind("<Button-1>", lambda e, xy=[x, y]: get_cordinate(xy))
        lbl.grid(row=x, column=y)

        dict_labels = {"xy": [x, y], "symbol": "", "label": lbl, "ticked": False}
        list_labels.append(dict_labels)

lbl_status = tk.Label(top_frame, text="Status: Não conectado ao servidor", font="Helvetica 14 bold")
lbl_status.grid(row=3, columnspan=3)

top_frame.pack_forget()


def init(arg0, arg1):
    global list_labels, sua_vez, meus_dados, dados_do_oponente, you_started

    sleep(3)

    for i in range(len(list_labels)):
        list_labels[i]["symbol"] = ""
        list_labels[i]["ticked"] = False
        list_labels[i]["label"]["text"] = ""
        list_labels[i]["label"].config(foreground="black", highlightbackground="grey",
                                       highlightcolor="grey", highlightthickness=1)

    lbl_status.config(foreground="black")
    lbl_status["text"] = "STATUS: Carregando partida."
    sleep(1)
    lbl_status["text"] = "STATUS: Carregando partida.."
    sleep(1)
    lbl_status["text"] = "STATUS: Carregando partida..."
    sleep(1)

    if you_started:
        you_started = False
        sua_vez = False
        lbl_status["text"] = "STATUS: " + dados_do_oponente["name"] + " jogando!"
    else:
        you_started = True
        sua_vez = True
        lbl_status["text"] = "STATUS: Sua vez!"


def get_cordinate(xy):
    global client, sua_vez
    # convert 2D to 1D cordinate i.e. index = x * num_cols + y
    label_index = xy[0] * num_cols + xy[1]
    label = list_labels[label_index]

    if sua_vez:
        if label["ticked"] is False:
            label["label"].config(foreground=meus_dados["color"])
            label["label"]["text"] = meus_dados["symbol"]
            label["ticked"] = True
            label["symbol"] = meus_dados["symbol"]
            # envia coordenada para servidor
            client.send(("$xy$" + str(xy[0]) + "$" + str(xy[1])).encode())
            sua_vez = False

            # analisando resultado do jogo
            result = logica_do_jogo()
            if result[0] is True and result[1] != "":  # venceu
                meus_dados["score"] = meus_dados["score"] + 1
                lbl_status["text"] = "FIM DE JOGO, Você venceu! Você(" + str(meus_dados["score"]) + ") - " \
                    "" + dados_do_oponente["name"] + "(" + str(dados_do_oponente["score"]) + ")"
                lbl_status.config(foreground="green")
                threading._start_new_thread(init, ("", ""))

            elif result[0] is True and result[1] == "":  # empate
                lbl_status["text"] = "FIM DE JOGO, Empate! Você(" + str(meus_dados["score"]) + ") - " \
                    "" + dados_do_oponente["name"] + "(" + str(dados_do_oponente["score"]) + ")"
                lbl_status.config(foreground="blue")
                threading._start_new_thread(init, ("", ""))

            else:
                lbl_status["text"] = "STATUS: " + dados_do_oponente["name"] + " jogando!"
    else:
        lbl_status["text"] = "STATUS: Espere sua vez!"
        lbl_status.config(foreground="red")

# vitoria por completar linha
# [(0,0) -> (0,1) -> (0,2)], [(1,0) -> (1,1) -> (1,2)], [(2,0), (2,1), (2,2)]
def check_row():
    list_symbols = []
    list_labels_temp = []
    winner = False
    win_symbol = ""
    for i in range(len(list_labels)):
        list_symbols.append(list_labels[i]["symbol"])
        list_labels_temp.append(list_labels[i])
        if (i + 1) % 3 == 0:
            if (list_symbols[0] == list_symbols[1] == list_symbols[2]):
                if list_symbols[0] != "":
                    winner = True
                    win_symbol = list_symbols[0]

                    list_labels_temp[0]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)
                    list_labels_temp[1]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)
                    list_labels_temp[2]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)

            list_symbols = []
            list_labels_temp = []

    return [winner, win_symbol]

# vitoria por completar coluna
# [(0,0) -> (1,0) -> (2,0)], [(0,1) -> (1,1) -> (2,1)], [(0,2), (1,2), (2,2)]
def check_col():
    winner = False
    win_symbol = ""
    for i in range(num_cols):
        if list_labels[i]["symbol"] == list_labels[i + num_cols]["symbol"] == list_labels[i + num_cols + num_cols][
            "symbol"]:
            if list_labels[i]["symbol"] != "":
                winner = True
                win_symbol = list_labels[i]["symbol"]

                list_labels[i]["label"].config(foreground="green", highlightbackground="green",
                                               highlightcolor="green", highlightthickness=2)
                list_labels[i + num_cols]["label"].config(foreground="green", highlightbackground="green",
                                                          highlightcolor="green", highlightthickness=2)
                list_labels[i + num_cols + num_cols]["label"].config(foreground="green", highlightbackground="green",
                                                                     highlightcolor="green", highlightthickness=2)

    return [winner, win_symbol]


def check_diagonal():
    winner = False
    win_symbol = ""
    i = 0
    j = 2

    # diagonal1 (0, 0) -> (1,1) -> (2, 2)
    a = list_labels[i]["symbol"]
    b = list_labels[i + (num_cols + 1)]["symbol"]
    c = list_labels[(num_cols + num_cols) + (i + 1)]["symbol"]
    if list_labels[i]["symbol"] == list_labels[i + (num_cols + 1)]["symbol"] == \
            list_labels[(num_cols + num_cols) + (i + 2)]["symbol"]:
        if list_labels[i]["symbol"] != "":
            winner = True
            win_symbol = list_labels[i]["symbol"]

            list_labels[i]["label"].config(foreground="green", highlightbackground="green",
                                           highlightcolor="green", highlightthickness=2)

            list_labels[i + (num_cols + 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
            list_labels[(num_cols + num_cols) + (i + 2)]["label"].config(foreground="green",
                                                                         highlightbackground="green",
                                                                         highlightcolor="green", highlightthickness=2)

    # diagonal2 (0, 0) -> (1,1) -> (2, 2)
    elif list_labels[j]["symbol"] == list_labels[j + (num_cols - 1)]["symbol"] == list_labels[j + (num_cols + 1)][
        "symbol"]:
        if list_labels[j]["symbol"] != "":
            winner = True
            win_symbol = list_labels[j]["symbol"]

            list_labels[j]["label"].config(foreground="green", highlightbackground="green",
                                           highlightcolor="green", highlightthickness=2)
            list_labels[j + (num_cols - 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
            list_labels[j + (num_cols + 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
    else:
        winner = False

    return [winner, win_symbol]


# empate se o grid esta completo
def check_draw():
    for i in range(len(list_labels)):
        if list_labels[i]["ticked"] is False:
            return [False, ""]
    return [True, ""]


def logica_do_jogo():
    #verificar linhas
    result = check_row()
    if result[0]:
        return result
    # verificar colunas
    result = check_col()
    if result[0]:
        return result
    # verificar diagonais
    result = check_diagonal()
    if result[0]:
        return result
    # verificar empate
    result = check_draw()
    return result

def connect():
    global meus_dados
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="Você deve inserir seu nome <ex. Bat-leo>")
    else:
        meus_dados["name"] = ent_name.get()
        connect_to_server(ent_name.get())


def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode())  # envia nome apos conectar


        threading._start_new_thread(receive_message_from_server, (client, "m"))
        top_welcome_frame.pack_forget()
        top_frame.pack(side=tk.TOP)
        window_main.title("Jogo da velha cliente - " + name)
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Impossível conectar ao host: " + HOST_ADDR + " on port: " + str(
            HOST_PORT) + " Servidor indisponível. Tente novamente")


def receive_message_from_server(sck, m):
    global meus_dados, dados_do_oponente, sua_vez, you_started
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server: break

        if from_server.startswith("welcome"):
            if from_server == "welcome 1\n":
                meus_dados["color"] = "blue"
                dados_do_oponente["color"] = "yellow"
                lbl_status["text"] = "Server: Bem vindo " + meus_dados["name"] + "! Aguardando player 2"
            elif from_server == "welcome 2\n":
                lbl_status["text"] = "Server: Bem vindo " + meus_dados["name"] + "! Jogo logo vai começar"
                meus_dados["color"] = "yellow"
                dados_do_oponente["color"] = "blue"

        elif from_server.startswith("$opponent_name$"):
            temp = from_server.replace("$opponent_name$", "")
            temp = temp.replace("$symbol$", "")
            name_index = temp.find("$")
            symbol_index = temp.rfind("$")
            dados_do_oponente["name"] = temp[0:name_index]
            meus_dados["symbol"] = temp[symbol_index:len(temp)]

            # gravando sinal do oponente
            if meus_dados["symbol"] == "O":
                dados_do_oponente["symbol"] = "X"
            else:
                dados_do_oponente["symbol"] = "O"

            lbl_status["text"] = "STATUS: " + dados_do_oponente["name"] + " conectado!"
            sleep(3)
            # vez de jogar ou nao
            if meus_dados["symbol"] == "O":
                lbl_status["text"] = "STATUS: Sua vez!"
                sua_vez = True
                you_started = True
            else:
                lbl_status["text"] = "STATUS: " + dados_do_oponente["name"] + " jogando!"
                you_started = False
                sua_vez = False
        elif from_server.startswith("$xy$"):
            temp = from_server.replace("$xy$", "")
            _x = temp[0:temp.find("$")]
            _y = temp[temp.find("$") + 1:len(temp)]

            # update grid
            label_index = int(_x) * num_cols + int(_y)
            label = list_labels[label_index]
            label["symbol"] = dados_do_oponente["symbol"]
            label["label"]["text"] = dados_do_oponente["symbol"]
            label["label"].config(foreground=dados_do_oponente["color"])
            label["ticked"] = True

            # vitoria ou empate
            result = logica_do_jogo()
            if result[0] is True and result[1] != "":  # oponente vence
                dados_do_oponente["score"] = dados_do_oponente["score"] + 1
                if result[1] == dados_do_oponente["symbol"]:  #
                    lbl_status["text"] = "FIM DE JOGO, Você perdeu! Você(" + str(meus_dados["score"]) + ") - " \
                        "" + dados_do_oponente["name"] + "(" + str(dados_do_oponente["score"]) + ")"
                    lbl_status.config(foreground="red")
                    threading._start_new_thread(init, ("", ""))
            elif result[0] is True and result[1] == "":  # a draw
                lbl_status["text"] = "FIM DE JOGO, Empate! Você(" + str(meus_dados["score"]) + ") - " \
                    "" + dados_do_oponente["name"] + "(" + str(dados_do_oponente["score"]) + ")"
                lbl_status.config(foreground="blue")
                threading._start_new_thread(init, ("", ""))
            else:
                sua_vez = True
                lbl_status["text"] = "STATUS: Sua vez!"
                lbl_status.config(foreground="black")

    sck.close()


window_main.mainloop()

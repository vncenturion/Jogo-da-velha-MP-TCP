import tkinter as tk
import socket
import threading
from time import sleep
import random


window = tk.Tk()
window.title("JOGO DA VELHA (SERVER)")

# Frame superior (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Frame meio: rotulos
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Endereço IP: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Porta: XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# lista de jogadores
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="*** Jogadores conectados ***").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=20, width=40)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(15, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8432
client_name = " "
clients = []
clients_names = []
player_data = []


# Iniciar servidor
def start_server():
    global server, HOST_ADDR, HOST_PORT
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # servidor em listening de conexao

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Endereço IP: " + HOST_ADDR
    lblPort["text"] = "Porta: " + str(HOST_PORT)


# Parar servidor
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)


def accept_clients(the_server, y):
    while True:
        if len(clients) < 2:
            client, addr = the_server.accept()
            clients.append(client)

            # use a thread so as not to clog the gui thread
            threading._start_new_thread(send_receive_client_message, (client, addr))


# funçao que recebe dados do cliente atual e envia para os demais

def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, player_data, player0, player1

    client_msg = " "

    # envia msg de boas vindas
    client_name = client_connection.recv(4096).decode()

    if len(clients) < 2:
        client_connection.send("welcome 1\n".encode())
    else:
        client_connection.send("welcome 2\n".encode())

    clients_names.append(client_name)
    update_client_names_display(clients_names)  # update lista jogadores

    if len(clients) > 1:
        sleep(1)
        symbols = ["O", "X"]

        # envia o nome do oponente e sinal X ou O
        clients[0].send(("$opponent_name$" + clients_names[1] + "$symbol$" + symbols[0]).encode())
        clients[1].send(("$opponent_name$" + clients_names[0] + "$symbol$" + symbols[1]).encode())


    while True:

        # recupera a escolha do jogador dos dados recebidos
        data = client_connection.recv(4096).decode()
        if not data: break

        # coordenada x,y do jogador. encaminhar para o outro jogador.
        if data.startswith("$xy$"):
            # verifica a origem da msg client1 ou client2?
            if client_connection == clients[0]:
                # envia os dados da jogada para o outro jogador
                clients[1].send(data.encode())
            else:
                # envia os dados da jogada para o outro jogador
                clients[0].send(data.encode())

    # saindo do laço de execução, limpa a lista de jogadores e clientes
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.close()

    update_client_names_display(clients_names)  # update lista nomes


# Recupera o index do cliente atual na lista de clientes
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx

# Update da lista de jogadores quando um cliente novo se conecta ou desconecta
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)

window.mainloop()

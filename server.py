import socket
import threading
import sys
import json

SERVER_PORT = 22300
SERVER_ADDR = "127.0.1.1"

# list of clients and their ips
users_conn, users_usernames = [], []

# create server instance
server = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)

server.bind((SERVER_ADDR, SERVER_PORT))


def create_message(msg_type, msg_value, msg_sender):
    return json.dumps({"msg_type": msg_type, "msg_value": msg_value,
                       "msg_sender": msg_sender})


def dejosn_message(msg):
    return json.loads(msg)


def start_server():
    print("Server starting on {}".format(SERVER_ADDR))

    # start listening to connections
    server.listen()
    while(True):
        try:
            user_conn, user_addr = server.accept()
            print("user accepted: {}".format(user_addr))
            user_conn.send(create_message(
                "cmd_name", "username", "server").encode("utf-8"))
            user_username_json = user_conn.recv(1024).decode("utf-8")
            user_username = dejosn_message(user_username_json)
            if user_username == None or not user_username:
                break
            users_conn.append(user_conn)
            users_usernames.append(user_username)
            print("{} has joined chat".format(user_username["msg_value"]))

            t = threading.Thread(target=handle_connetion,
                                 args=(user_conn, user_addr))
            t.start()

            print("current activate connections {}".format(
                threading.activeCount()-1))
        except KeyboardInterrupt as e:
            # temp
            print("closing by hand")
            sys.exit()


# Logic to inform client about msg delivery
def client_inform(client, msg_status):
    msg = create_message("msg_status", msg_status, "server")
    client.send(msg.encode("utf-8"))


#handle individual current connection
def handle_connetion(user_conn, user_addr):
    user_connected = True

    while user_connected:
        msg_json = user_conn.recv(1024).decode("utf-8")
        if not msg_json:
            break

        msg = dejosn_message(msg_json)
        if not msg["msg_value"]:
            break
        else:
            if msg["msg_type"] == "user_msg":
                print("{} sent: {}".format(msg["msg_sender"],
                                           msg["msg_value"]))
                msg_broadcast("user_msg", msg["msg_value"], msg["msg_sender"])
                client_inform(user_conn, "Message sent")
            elif msg["msg_type"] == "cmd_typing":
                print(msg["msg_value"])
                msg_broadcast("cmd_typing", "None", msg["msg_sender"])
            else:
                print(msg)
                print("unknown format")

# logic to kick client when he disconnect
# TBI

def client_kick(client):
    print("I should kick this guy")
    print(client)

#broadcast msg to everyone on connection
def msg_broadcast(msg_type, value, sender):
    for client in users_conn:
        try:
            client.send(create_message(
                msg_type, value, sender).encode("utf-8"))
        except Exception as e:
            print("Failed to send to client {}".format(client))
            print("Because: {}".format(e.__class__))
            client_kick(client)


if __name__ == "__main__":
    start_server()

import socket
import threading
import sys
import json
from tkinter import *
from tkinter import font
from tkinter import ttk

# Local port and addrs
SERVER_PORT = 22300
SERVER_ADDR = "127.0.1.1"


def create_message(msg_type, msg_value, msg_sender):
    return json.dumps({"msg_type": msg_type, "msg_value": msg_value,
                       "msg_sender": msg_sender})

# fun to make json fmrt back to string
def dejosn_message(msg):
    return json.loads(msg)


try:
    client = socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM)
    client.connect((SERVER_ADDR, SERVER_PORT))
except (ConnectionRefusedError, OSError):
    print("No server found!")
    print("server off or bad server address")
    sys.exit()


# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self):

        # chat window which is currently hidden
        self.window = Tk()
        self.window.withdraw()

        # instance box to input username
        self.username_input = Toplevel()
        self.username_input.title("Login")
        self.username_input.resizable(width=False,
                                      height=False)
        self.username_input.configure(width=400,
                                      height=300)
        self.pls = Label(self.username_input,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        self.label_name = Label(self.username_input,
                                text="Name: ",
                                font="Helvetica 12")

        self.label_name.place(relheight=0.2,
                              relx=0.1,
                              rely=0.2)

        # entry username box
        self.entry_username = Entry(self.username_input,
                                    font="Helvetica 14")

        self.entry_username.place(relwidth=0.4,
                                  relheight=0.12,
                                  relx=0.35,
                                  rely=0.2)

        self.entry_username.focus()

        # create a Continue Button
        # along with action for username getting
        self.go = Button(self.username_input,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.go_next(
                             self.entry_username.get()))

        self.go.place(relx=0.4,
                      rely=0.55)
        self.window.mainloop()

    def go_next(self, username):
        self.username_input.destroy()
        self.layout(username)

        # the thread to receive messages
        rcv = threading.Thread(target=self.msg_receive)
        rcv.start()

    # The main layout of the chat
    def layout(self, username):

        self.username = username
        # to show chat window
        self.window.deiconify()
        self.window.title("CHATROOM")
        self.window.resizable(width=False,
                              height=False)
        self.window.configure(width=470,
                              height=550)
        self.label_head = Label(self.window,
                                text=self.username,
                                font="Helvetica 13 bold",
                                pady=5)

        self.label_head.place(relwidth=1)
        self.line = Label(self.window,
                          width=450)

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.text_cons = Text(self.window,
                              width=20,
                              height=2,
                              padx=5,
                              pady=5)

        self.text_cons.place(relheight=0.745,
                             relwidth=1,
                             rely=0.08)

        self.label_bottom = Label(self.window,
                                  height=80)

        self.label_bottom.place(relwidth=1,
                                rely=0.825)

        self.entry_msg = Entry(self.label_bottom,
                               font="Helvetica 13")

        self.entry_msg.bind('<KeyRelease>', self.user_typing)

        # place the given widget
        # into the gui window
        self.entry_msg.place(relwidth=0.74,
                             relheight=0.06,
                             rely=0.008,
                             relx=0.011)

        self.entry_msg.focus()

        # create a Send Button
        self.msg_button = Button(self.label_bottom,
                                 text="Send",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 command=lambda: self.sendButton(
                                    self.entry_msg.get()))

        self.msg_button.place(relx=0.77,
                              rely=0.008,
                              relheight=0.06,
                              relwidth=0.22)

        self.text_cons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.text_cons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.text_cons.yview)

        self.text_cons.config(state=DISABLED)

    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.text_cons.config(state=DISABLED)
        self.msg = msg
        self.entry_msg.delete(0, END)
        snd = threading.Thread(target=self.msg_send)
        snd.start()

    # inform server about typing
    def user_typing(self, *args):
        message = create_message(
            "cmd_typing", "{}: Typing".format(self.username), self.username)
        client.send(message.encode("utf-8"))

    def msg_receive(self):
        # start to receiving msg
        # msg from server
        while True:
            try:
                msg_json = client.recv(1024).decode("utf-8")
                msg = dejosn_message(msg_json)

                if msg["msg_type"] == "cmd_name":
                    client.send(create_message(
                        "cmd_name", self.username,
                        self.username).encode("utf-8"))
                elif msg["msg_type"] == "user_msg":
                    self.text_cons.config(state=NORMAL)
                    self.text_cons.insert(END,
                                          "{}: {}".format(msg["msg_sender"],
                                                          msg["msg_value"])+"\n\n")

                    self.text_cons.config(state=DISABLED)
                    self.text_cons.see(END)

                elif msg["msg_type"] == "cmd_typing":
                    self.text_cons.config(state=NORMAL)
                    self.text_cons.insert(END,
                                          "{} is Typing...".format(
                                              msg["msg_sender"])+"\n\n")

                    self.text_cons.config(state=DISABLED)
                    self.text_cons.see(END)
                elif msg["msg_type"] == "msg_status":
                    # display msg status
                    self.text_cons.config(state=NORMAL)
                    self.text_cons.insert(END,
                                          msg["msg_value"]+"\n\n")

                    self.text_cons.config(state=DISABLED)
                    self.text_cons.see(END)
                else:
                    print("not known format")
            except:
                print("Lost connection...")
                print("Closing chat client, because of no response")

    def msg_send(self):
        while True:
            #message_to_send = "{}: {}".format(self.name, self.msg)
            client.send(create_message(
                "user_msg", self.msg, self.username).encode("utf-8"))
            break


if __name__ == "__main__":
    print("Starting client gui...")

    application_window = GUI()

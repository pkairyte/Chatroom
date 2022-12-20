from tkinter import *
from PIL import ImageTk, Image
from chat_client_class import *

TK_ACTIVE = True
TK_INACTIVE = False

class Log_GUI(Client):
    def __init__(self, args):
        # Main window
        self.args = args
        self.name = ""

        self.mainwin = Tk()
        self.mainwin.resizable(False, False)
        self.mainwin.title('Welcome to ICS Chat!')
        self.mainwin.geometry('450x300')
        self.mainwin.configure(background='black')

        self.pic = ImageTk.PhotoImage(Image.open('nyu_logo.png'))
        self.pic = pic.resize((80, 80), Image.ANTIALIAS)
        self.pic = ImageTk.PhotoImage(pic)
        self.panel = Label(self.mainwin, image=self.pic)
        self.panel.place(x=185, y=20)
        self.user = Label(self.mainwin, text='Username:')
        self.user.place(x=80, y=150)
        self.user.configure(background = 'black', foreground = 'DarkOrchid1')
        self.user_var = StringVar()
        self.user_entry = Entry(self.mainwin, textvariable=self.user_var)
        self.user_entry.place(x=165, y=150)
        self.user_entry.configure(bbackground = 'MediumPurple2')

        self.error = Label(self.mainwin, text="")
        self.error.place(x=160, y=130)
        self.error.configure(background = 'black', foreground = 'red')

        self.logbutton = Button(self.mainwin, text='Log In', command=self.test_login)
        self.logbutton.place(x=180, y=190)
        self.logbutton.configure(background = 'black', foreground = 'DarkOrchid1')


        self.quit_button = Button(self.mainwin, text='Quit', command=self.close)
        self.quit_button.place(x=240, y=190)
        self.quit_button.configure(background = 'black', foreground = 'DarkOrchid1')

    def test_login(self):
        self.name = self.user_entry.get()
        my_msg = self.name
        dummy_client = Client(self.args)
        dummy_client.init_chat()
        if len(my_msg) > 0:
            msg = json.dumps({"action":"login", "name":self.name})
            dummy_client.send(msg)
            response = json.loads(dummy_client.recv())
            if response["status"] == 'ok':
                dummy_client.socket.close()
                self.begin_chat()
                return (True)
            elif response["status"] == 'duplicate':
                self.error["text"] = 'Duplicate username, try again'
                return False
        else:               # fix: dup is only one of the reasons
           self.error["text"] = "Username must contain at least 1 character"
           return (False)

    def startup(self):
        self.mainwin.mainloop()

    def close(self):
        self.mainwin.destroy()

    def begin_chat(self):
        self.mainwin.destroy()
        client_chat_system = Chat_GUI(self.args)
        client_chat_system.startup(self.name)


class Chat_GUI(Client):
    def __init__(self, args):
        self.name = ''
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.running = TK_ACTIVE

        self.root = Tk()
        self.root.title("ICS Chat System")
        self.root.configure(background='black')

        # frames
        self.frame = Frame(self.root)
        self.text_box = StringVar()
        self.text_box.set("")

        self.scrollbar = Scrollbar(self.frame)
        self.msgs_frame = Listbox(self.frame, width="60", height="20", yscrollcommand=self.scrollbar.set)
        self.msgs_frame.yview(END)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.msgs_frame.pack(side=LEFT, fill=BOTH)
        self.msgs_frame.configure(background='MediumPurple2', foreground = 'black')
        self.msgs_frame.pack()
        self.frame.pack()

        self.field = Entry(self.root, textvariable=self.text_box)
        self.field.bind("<Return>", self.send_text)
        self.field.configure(background='MediumPurple2', foreground='black')
        self.field.pack()
        self.send_button = Button(self.root, text="Send", command=self.send_text)
        self.send_button.configure(background='black', foreground='DarkOrchid1')
        self.send_button.pack()
        
        self.quit_button = Button(self.root, text='Quit', command=self.close)
        self.quit_button.pack()
        self.quit_button.configure(background = 'black', foreground = 'DarkOrchid1')

    # ============== GUI FUNCTIONS ==============#
    def startup(self, name):
        self.name = name
        self.run_chat()

    def send_info(self, t):
        text = t
        self.msgs_frame.insert(END, text)

    def send_text(self, event=None):
        text = self.text_box.get()
        if self.sm.get_state() != S_CHATTING:
            self.system_msg += text
            self.console_input.append(text)
        if self.sm.get_state() == S_CHATTING:
            self.console_input.append(text)
        self.output()
        self.text_box.set("")

    # ============= OVERWRITING CLIENT FUNCTIONS ==================#

    def login(self):
        my_msg, peer_msg = self.get_msgs()
        my_msg = self.name
        if len(my_msg) > 0:
            self.name = my_msg
            msg = json.dumps({"action": "login", "name": self.name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(self.name)
                self.print_instructions()
                return (True)
            elif response["status"] == 'duplicate':
                self.system_msg += 'Duplicate username, try again'
                return False
        else:  # fix: dup is only one of the reasons
            return (False)


    def quit(self):
        self.root.destroy()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    # output prints system msgs to tkinter and console
    def output(self):
        if len(self.system_msg) > 0:
            print(self.system_msg)
            lines = self.system_msg.split("\n")
            for ln in lines:
                self.send_info(ln)
            self.system_msg = ""
            return self.system_msg

    def run_chat(self):
        self.init_chat()
        self.system_msg += 'Welcome to ICS chat! \n'
        self.output()

        while self.running:
            self.root.update()
            if self.sm.get_state() != S_LOGGEDIN:
                self.login_task()
            if self.sm.get_state() == S_LOGGEDIN:
                self.proc_task()
            if self.sm.get_state() == S_OFFLINE:
                self.running = TK_INACTIVE

        self.quit()

    # ============== ABSTRACTED TASKS =============#

    def login_task(self):
        while self.login() != True:
            self.root.update()
            self.output()
        self.system_msg += 'You are registered as ' + self.get_name() + '!'
        self.output()

    def proc_task(self):
        while self.sm.get_state() != S_OFFLINE:
            self.root.update()
            self.proc()
            self.output()
            self.msgs_frame.yview_moveto(1)
            time.sleep(CHAT_WAIT)

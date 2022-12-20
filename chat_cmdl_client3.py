
from gui import *

def main():
    import argparse
    parser = argparse.ArgumentParser(description='chat client argument')
    parser.add_argument('-d', type=str, default=None, help='server IP addr')
    args = parser.parse_args()

    client_gui = Log_GUI(args)
    client_gui.startup()
    # client = Client(args)
    # client.run_chat()

main()
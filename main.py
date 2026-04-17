import argparse
from main_win import MainWindow
from api_emul.server import server_loop


parser = argparse.ArgumentParser(prog='Test com')
parser.add_argument("--server", action="store_true")


def main():
    main_win = MainWindow()
    main_win.mainloop()
    main_win.cleanup()


def main_server():
    server_loop()


if __name__ == "__main__":
    args = parser.parse_args()
    if args.server:
        main_server()
    else:
        main()

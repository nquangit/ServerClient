import threading
import time
import zmq

UPDATE_NOTIFY = "UPDATE_NOTIFY"
UPDATE_WAITING_CLIENT = "UPDATE_WAITING_CLIENT"
UPDATE_CLIENT = "UPDATE_CLIENT"
COMMAND_RESPONSED = "COMMAND_RESPONSED"


class Server_Info:
    DEBUG = True
    _HOST = '0.0.0.0'
    _PORT = 13044
    _WATING_CLIENT = []
    _CLIENT = []
    _CLIENT_INFO = []
    _SOCKET = None
    _NOTIFY = []
    _STOP = threading.Event()
    _LOCK = threading.Lock()
    _DELAY_TIME = 5
    _contactGUIApplicationAddress = "tcp://127.0.0.1:13444"

    def __init__(self) -> None:
        super().__init__()

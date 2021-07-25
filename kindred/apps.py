from django.apps import AppConfig
import sys
from threading import Thread
from socketclusterclient import Socketcluster
from kindred_backend.settings import WEBSOCKET_URL


socket_is_ready = True

def on_connect(m_socket):
    global socket_is_ready
    socket_is_ready = True
    print('Socket connection was established')

def on_disconnect(m_socket):
    print('Disconnected from socket')

def on_connect_error(m_socket, error):
    print(error)

socket = Socketcluster.socket(WEBSOCKET_URL)
socket.setBasicListener(on_connect, on_disconnect, on_connect_error)
socket.setdelay(2)
socket.setreconnection(True)


class KindredConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kindred'

    def ready(self):
        # allowed_arg = '/usr/local/bin/gunicorn'
        allowed_arg = 'runserver'
        if allowed_arg in sys.argv:
            t = Thread(target=socket.connect)
            t.daemon = True
            t.start()
            print('Please wait for the socket connection to be established...')
            while not socket_is_ready:
                pass

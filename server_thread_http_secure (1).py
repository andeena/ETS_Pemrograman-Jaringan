import os
from socket import *
import socket
import threading
import logging
import ssl
from http import HttpServer
 
httpserver = HttpServer()
 
class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address
 
    def run(self):
        rcv = ""
        while True:
            try:
                data = self.connection.recv(32)
                if data:
                    d = data.decode()
                    rcv = rcv + d
                    if rcv[-2:] == '\r\n':
                        logging.warning("data dari client: {}".format(rcv))
                        hasil = httpserver.proses(rcv)
                        hasil = hasil + "\r\n\r\n".encode()
                        logging.warning("balas ke client: {}".format(hasil))
                        self.connection.sendall(hasil)
                        rcv = ""
                        self.connection.close()
                        break
                else:
                    break
            except OSError as e:
                logging.warning(f"Error: {str(e)}")
                break
        self.connection.close()
 
class Server(threading.Thread):
    def __init__(self, hostname='testing.net'):
        threading.Thread.__init__(self)
        self.the_clients = []
        self.hostname = hostname
        cert_location = os.getcwd() + '/certs/'
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile=cert_location + 'domain.crt',
                                     keyfile=cert_location + 'domain.key')
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
    def run(self):
        self.my_socket.bind(('0.0.0.0', 8443))
        self.my_socket.listen(1)
        while True:
            connection, client_address = self.my_socket.accept()
            try:
                secure_connection = self.context.wrap_socket(connection, server_side=True)
                logging.warning("connection from {}".format(client_address))
                clt = ProcessTheClient(secure_connection, client_address)
                clt.start()
                self.the_clients.append(clt)
            except ssl.SSLError as e:
                logging.warning(f"SSL error: {str(e)}")
                connection.close()
            except Exception as e:
                logging.warning(f"Error: {str(e)}")
                connection.close()
 
def main():
    svr = Server()
    svr.start()
 
if __name__ == "__main__":
    main()
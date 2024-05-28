import socket
import threading
import logging

class HttpServer:
    def proses(self, data):
        response = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
        return response.encode()

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
                    logging.warning("Raw data received: {}".format(data))
                    try:
                        d = data.decode('utf-8')
                        rcv += d
                        logging.warning("Decoded data: {}".format(rcv))
                        if '\r\n\r\n' in rcv:
                            logging.warning("End of headers received")
                            hasil = httpserver.proses(rcv)
                            logging.warning("Sending response: {}".format(hasil))
                            self.connection.sendall(hasil)
                            break
                    except UnicodeDecodeError as e:
                        logging.error("UnicodeDecodeError: {}".format(e))
                else:
                    break
            except OSError as e:
                logging.error("OSError: {}".format(e))
                break
        self.connection.close()

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.my_socket.bind(('0.0.0.0', 8889))
        self.my_socket.listen(1)
        logging.warning("Server started on port 8889")
        while True:
            try:
                conn, addr = self.my_socket.accept()
                logging.warning("Connection from {}".format(addr))
                clt = ProcessTheClient(conn, addr)
                clt.start()
                self.the_clients.append(clt)
            except Exception as e:
                logging.error("Exception: {}".format(e))

def main():
    logging.basicConfig(level=logging.WARNING)
    svr = Server()
    svr.start()

if __name__ == "__main__":
    main()

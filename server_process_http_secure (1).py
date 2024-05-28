import os
import socket
import multiprocessing
import logging
import ssl
from http import HttpServer

httpserver = HttpServer()

class ProcessTheClient(multiprocessing.Process):
    def __init__(self, connection, address):
        super().__init__()
        self.connection = connection
        self.address = address

    def run(self):
        rcv = b""  # Initialize as bytes
        try:
            while True:
                data = self.connection.recv(32)
                if data:
                    rcv += data  # Append received bytes
                    if rcv[-4:] == b'\r\n\r\n':
                        # End of command, process bytes
                        request_str = rcv.decode()
                        logging.warning("data dari client: {}".format(request_str))
                        hasil = httpserver.proses(request_str)  # Process as string
                        if isinstance(hasil, str):
                            hasil = hasil.encode() + b"\r\n\r\n"  # Encode result to bytes
                        logging.warning("balas ke client: {}".format(hasil))
                        self.connection.sendall(hasil)  # Send bytes
                        rcv = b""  # Reset to empty bytes
                        break  # Exit loop after processing
                else:
                    break
        except OSError as e:
            logging.warning(f"Error: {str(e)}")
        finally:
            self.connection.close()

class Server(multiprocessing.Process):
    def __init__(self, hostname='testing.net'):
        super().__init__()
        self.the_clients = []
        self.hostname = hostname
        cert_location = os.getcwd() + '/certs/'
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile=cert_location + 'domain.crt',
                                     keyfile=cert_location + 'domain.key')
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.max_clients = 10  # Limit the number of concurrent clients

    def run(self):
        self.my_socket.bind(('0.0.0.0', 8443))
        self.my_socket.listen(self.max_clients)
        logging.warning("server berjalan di port 8443")

        try:
            while True:
                connection, client_address = self.my_socket.accept()
                secure_connection = self.context.wrap_socket(connection, server_side=True)
                logging.warning("connection from {}".format(client_address))
                clt = ProcessTheClient(secure_connection, client_address)
                clt.start()
                self.the_clients.append(clt)

                # Clean up finished processes
                self.the_clients = [p for p in self.the_clients if p.is_alive()]
        except Exception as e:
            logging.warning(f"Server error: {str(e)}")
        finally:
            self.my_socket.close()

def main():
    logging.basicConfig(level=logging.WARNING)
    svr = Server()
    svr.start()
    svr.join()  # Ensure the server process keeps running

if __name__ == "__main__":
    main()

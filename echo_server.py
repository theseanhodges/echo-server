import socket
import sys
import traceback


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print("making a server on {0}:{1}".format(*address), file=log_buffer)

    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)

            conn, addr = sock.accept()
            conn.settimeout(5)
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                while True:
                    data = conn.recv(16)
                    if not data:
                        break
                    print('received "{0}"'.format(data.decode('utf8')))
                    
                    conn.sendall(data)
                    print('sent "{0}"'.format(data.decode('utf8')))
            except socket.timeout:
                print('receive timed out', file=log_buffer)
            except Exception:
                traceback.print_exc()
                sys.exit(1)
            finally:
                conn.close()
                print(
                    'echo complete, client connection closed', file=log_buffer
                )

    except KeyboardInterrupt:
        sock.close()
        print('quitting echo server', file=log_buffer)


if __name__ == '__main__':
    server()
    sys.exit(0)

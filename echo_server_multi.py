import select
import socket
import sys
import traceback


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print("LISTENING ON {0}:{1}".format(*address), file=log_buffer)

    sock.bind(address)
    sock.listen(1)

    inputs = [sock]

    try:
        while inputs:
            readable, writable, exceptional = select.select(
                inputs, [], inputs, 10
            )

            for this_socket in readable:
                if this_socket is sock:
                    conn, addr = this_socket.accept()
                    conn.settimeout(5)

                    inputs.append(conn)

                    print('{0}:{1} ++ NEW CONNECTION ++'.format(*addr), file=log_buffer)
                else:
                    data = this_socket.recv(16)
                    if data:
                        print('{0}:{1} received "{2}"'.format(
                            *this_socket.getpeername(),
                            data.decode('utf8')
                        ))
                        this_socket.sendall(data)
                        print('{0}:{1} sent "{2}"'.format(
                            *this_socket.getpeername(),
                            data.decode('utf8')
                        ))
                    else:
                        inputs.remove(this_socket)
                        this_socket.close()
                        print(
                            '{0}:{1} -- CLOSED (no data) --'.format(*this_socket.getpeername()),
                            file=log_buffer
                        )
            for this_socket in exceptional:
                print(
                    '{0}:{1} -- CLOSED (socket erorr) --'.format(*this_socket.getpeername()),
                    file=log_buffer
                )
                inputs.remove(this_socket)
                this_socket.close()
            if not (readable or writable or exceptional):
                for this_socket in inputs:
                    if this_socket is sock:
                        continue
                    print(
                        '{0}:{1} -- CLOSED (wait timeout) --'.format(*this_socket.getpeername()),
                        file=log_buffer
                    )
                    inputs.remove(this_socket)
                    this_socket.close()

    except KeyboardInterrupt:
        sock.close()
        print('QUITTING ECHO SERVER', file=log_buffer)


if __name__ == '__main__':
    server()
    sys.exit(0)

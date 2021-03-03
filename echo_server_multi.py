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
            # Select sockets with new network activity
            readable, writable, exceptional = select.select(
                inputs, [], inputs, 5
            )

            for this_socket in readable:
                if this_socket is sock:
                    # This will occur if a new connection is received
                    # Process it and add it to the inputs list for r/w
                    conn, addr = this_socket.accept()
                    conn.settimeout(5)

                    inputs.append(conn)

                    print('{0}:{1} ++ NEW CONNECTION ++'.format(*addr), file=log_buffer)
                else:
                    # New data was received on an existing socket
                    # Read it and write it back
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
                        # No data received -- close the socket and remove it from the inputs list
                        inputs.remove(this_socket)
                        this_socket.close()
                        print(
                            '{0}:{1} -- CLOSED (no data) --'.format(*this_socket.getpeername()),
                            file=log_buffer
                        )
            for this_socket in exceptional:
                # Handle socket errors by closing them and removing from inputs
                print(
                    '{0}:{1} -- CLOSED (socket erorr) --'.format(*this_socket.getpeername()),
                    file=log_buffer
                )
                inputs.remove(this_socket)
                this_socket.close()
            if not (readable or writable or exceptional):
                # If nothing was received after 10 seconds, close the open sockets to prevent
                # resources from staying open and unused.
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

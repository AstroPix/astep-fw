import socket

def example_shutdown_function():
    print()
    print('***EXAMPLE***')
    print('SHUTDOWN SIGNAL RECIEVED')
    print('RAMPING HIGH VOLTAGE DOWN')
    print('CLOSING TCP/IP CONNECTION')
    print('***EXAMPLE***')
    print()

sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
PORT=1025
sock.bind(('::', PORT))

sock.listen(1)
print('Waiting for connection...')

conn, addr = sock.accept()
print(f'Connected by {addr}')

while True:
    try:
        data = conn.recv(1024)
        if not data:
            break
        print('Recieved:', data.decode('ascii'))
        if data=='shutdown'.encode('ascii'):
            example_shutdown_function()
            break
    except KeyboardInterrupt:
        print(f' KeyboardInterrupt, exiting cleanly...')
        break

conn.close()
import socket, time

def discover_cube():
    TIMEOUT=5
    PORT=23272
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    s.settimeout(TIMEOUT)
    # yes we need to staticly define a src port
    s.bind(('0.0.0.0', PORT))

    sender = None
    hexdiscover="6551334D61782A002A2A2A2A2A2A2A2A2A2A49"
    data = bytes.fromhex(hexdiscover)

    s.sendto(bytes.fromhex(hexdiscover), ("<broadcast>", PORT))

# so we have to listen on port 23272 to get a response, but we want to ignore our own response...
# so either we do recvfrom twice or until we get something (more of an ugly hack thought)
    while data==bytes.fromhex(hexdiscover):
        try:
            data, (addr, foo) = s.recvfrom(1024)
#            print('Received: %s from %s' % (data, addr))
        except socket.timeout:
            print("No cube for you")
            return sender
    s.close()
    return addr

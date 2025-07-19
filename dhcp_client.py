import socket
import struct
import random
import uuid
import time
import binascii
import argparse

MAGIC_COOKIE = b'\x63\x82\x53\x63'

def get_mac_bytes():
    mac_int = uuid.getnode()
    return binascii.unhexlify(f'{mac_int:012x}')

def build_packet(op, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr, options):
    sname = b'\x00' * 64
    file = b'\x00' * 128
    fixed = struct.pack('!BBBBIHH4s4s4s4s16s64s128s', op, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr + b'\x00' * (16 - len(chaddr)), sname, file)
    return fixed + MAGIC_COOKIE + options + b'\xff'

def parse_options(options_data):
    if options_data[:4] != MAGIC_COOKIE:
        raise ValueError("Invalid magic cookie")
    options = {}
    i = 4
    while i < len(options_data):
        code = options_data[i]
        if code == 255:
            break
        length = options_data[i + 1]
        value = options_data[i + 2:i + 2 + length]
        options[code] = value
        i += 2 + length
    return options

def parse_dhcp_packet(data):
    unpacked = struct.unpack('!BBBBIHH4s4s4s4s16s64s128s', data[:236])
    op, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr, sname, file_ = unpacked
    options_data = data[236:]
    options = parse_options(options_data)
    return {
        'op': op,
        'xid': xid,
        'yiaddr': yiaddr,
        'siaddr': siaddr,
        'options': options
    }

def dhcp_discover(mac):
    xid = random.randint(0, 0xFFFFFFFF)
    options = b'\x35\x01\x01'  # DHCP Message Type: Discover
    options += b'\x37\x04\x01\x03\x0f\x06'  # Parameter Request List: subnet, router, domain, DNS
    packet = build_packet(1, 1, 6, 0, xid, 0, 0x8000, b'\x00'*4, b'\x00'*4, b'\x00'*4, b'\x00'*4, mac, options)
    return packet, xid

def dhcp_request(mac, xid, requested_ip, server_ip):
    options = b'\x35\x01\x03'  # DHCP Message Type: Request
    options += struct.pack('!B B 4s', 50, 4, requested_ip)  # Requested IP
    options += struct.pack('!B B 4s', 54, 4, server_ip)  # Server Identifier
    options += b'\x37\x04\x01\x03\x0f\x06'  # Parameter Request List
    packet = build_packet(1, 1, 6, 0, xid, 0, 0x8000, b'\x00'*4, b'\x00'*4, b'\x00'*4, b'\x00'*4, mac, options)
    return packet

def main(interface=None):
    mac = get_mac_bytes()
    print(f"Using MAC address: {':'.join(f'{b:02x}' for b in mac)}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('0.0.0.0', 68))

    # Send DHCP Discover
    discover_packet, xid = dhcp_discover(mac)
    sock.sendto(discover_packet, ('255.255.255.255', 67))
    print("Sent DHCP Discover")

    # Receive DHCP Offer
    data, addr = sock.recvfrom(1024)
    parsed = parse_dhcp_packet(data)
    if parsed['xid'] != xid or parsed['options'].get(53, b'')[0] != 2:
        print("Invalid or mismatched DHCP Offer")
        return

    offered_ip = parsed['yiaddr']
    server_ip = parsed['options'].get(54, b'\x00'*4)
    print(f"Received DHCP Offer: IP {socket.inet_ntoa(offered_ip)} from server {socket.inet_ntoa(server_ip)}")

    # Send DHCP Request
    request_packet = dhcp_request(mac, xid, offered_ip, server_ip)
    sock.sendto(request_packet, ('255.255.255.255', 67))
    print("Sent DHCP Request")

    # Receive DHCP ACK
    data, addr = sock.recvfrom(1024)
    parsed = parse_dhcp_packet(data)
    if parsed['xid'] != xid or parsed['options'].get(53, b'')[0] != 5:
        print("Invalid or mismatched DHCP ACK")
        return

    assigned_ip = parsed['yiaddr']
    print(f"Received DHCP ACK: Assigned IP {socket.inet_ntoa(assigned_ip)}")

    # Here, in a real client, configure the interface with the IP, but that's OS-specific and requires root.
    # For demo, just print.
    if '1' in parsed['options']:  # Subnet mask
        subnet = socket.inet_ntoa(parsed['options'][1])
        print(f"Subnet Mask: {subnet}")
    if '3' in parsed['options']:  # Router
        router = socket.inet_ntoa(parsed['options'][3][:4])  # First one
        print(f"Default Gateway: {router}")
    if '6' in parsed['options']:  # DNS
        dns = ', '.join(socket.inet_ntoa(parsed['options'][6][i:i+4]) for i in range(0, len(parsed['options'][6]), 4))
        print(f"DNS Servers: {dns}")

    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple DHCP Client")
    parser.add_argument('--interface', help="Network interface (optional, not used in this basic version)")
    args = parser.parse_args()
    main(args.interface)
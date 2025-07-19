||Simple DHCP Client||

|Overview|

This is a basic Python implementation of a DHCP client using only standard libraries (no external dependencies). It performs the full DHCP handshake: sending a DISCOVER message, receiving an OFFER, sending a REQUEST, and receiving an ACK. It prints the assigned IP and other parameters but does not configure the network interface (which requires root privileges and OS-specific commands).

Ideal for testing DHCP servers or learning about the protocol. Runs on Python 3.8+.

|Features >|
Sends DHCP DISCOVER and REQUEST packets.
Parses OFFER and ACK responses.
Extracts and displays IP address, subnet mask, default gateway, and DNS servers.
Uses broadcast UDP sockets for communication.
Generates a random transaction ID (xid) and uses the system's MAC address via uuid.getnode().
Basic error checking for message types and xid matching.



|Requirements >|
Python 3.8 or higher.
Run as administrator/root (may be required for binding to port 68 and broadcasting).
A DHCP server on the network (e.g., router or test server).
No external libraries needed—all uses built-in socket, struct, random, uuid, binascii, time, and argparse.


|Installation >|
Save the script as dhcp_client.py.
No installation required—just run it.


|Usage|
Run the script from the command line:

sudo python dhcp_client.py [--interface <interface_name>]
--interface: Optional; specifies the network interface (not implemented for configuration, but can be extended).
The script will send a DHCP DISCOVER, wait for responses, and print the results.


Example output:

Using MAC address: aa:bb:cc:dd:ee:ff
Sent DHCP Discover
Received DHCP Offer: IP 192.168.1.100 from server 192.168.1.1
Sent DHCP Request
Received DHCP ACK: Assigned IP 192.168.1.100
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.1.1
DNS Servers: 8.8.8.8, 8.8.4.4
Note: This is a basic client and assumes a single OFFER/ACK. In production, handle multiple offers, timeouts, and renewals. Passwords/credentials not involved—pure network protocol.


|How It Works >|

Get MAC: Uses uuid.getnode() to get the hardware address.
Build DISCOVER: Constructs the UDP packet with fixed fields and options (message type 1, parameter request list).
Send/Receive: Broadcasts to 255.255.255.255:67, listens on port 68.
Parse OFFER: Checks for message type 2, extracts offered IP and server ID.
Build REQUEST: Includes requested IP (50) and server ID (54) options.
Parse ACK: Checks for message type 5, displays parameters.


|Customization>|
Options: Modify dhcp_discover or dhcp_request to add more options (e.g., hostname with code 12).
Timeouts: Add sock.settimeout(5) for production use.
Interface Config: Extend with subprocess to run ip addr add (Linux) or netsh (Windows) to apply the IP.
Renew/Release: Add functions for message types 3 (renew) or 7 (release).


|Troubleshooting>|
Permission Denied: Run with sudo/root.
No Response: Ensure a DHCP server is active and network allows broadcasts. Check firewall.
Invalid Magic Cookie: Server response malformed—debug with Wireshark.
MAC Issues: If uuid.getnode() fails, hardcode a MAC in get_mac_bytes().
Testing: Use a virtual network or tools like isc-dhcp-server for simulation.
For advanced features, consider libraries like scapy (not used here for purity).


|Limitations>|
Does not handle DHCP relays or multiple servers (takes first offer).
No lease management, renewals, or error retries.
Assumes Ethernet (htype=1, hlen=6).
Demo-only: Does not apply IP to interface.


|License>|
MIT License. Free to use, modify, and distribute.

|COPYRIGHT @CYBERDUDEBIVASH 2025 |
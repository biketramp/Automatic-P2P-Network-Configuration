# Automatic-P2P-Network-Configuration
Scripts and a service file for use with Sun Founder Pi Car S robots containing a RPi model 3B.
Automatically configures compatible network interfaces and adds them to the batman-adv mesh.
Uses avahi to provide unique link local addressing.
Changes the hostname to the MAC address of the interface.
Detects gateways to the internet and adds them to the batman-adv configuration.
Sets up a VPN using Openvpn to an off site VPN server for remote monitoring and configuration.
Has a GUI to change mesh settings.

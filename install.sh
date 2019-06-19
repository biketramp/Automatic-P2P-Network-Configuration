#!/bin/bash

#Update repo list + upgrade
sudo apt update && apt upgrade

#Disable dhcpcd auto config on the wireless and bat interfaces
sudo sed -i 1i"denyinterfaces wlan*\ndenyinterfaces bat*" /etc/dhcpcd.conf

#Enable SSH by creating an empty file in the boot directory
echo >> /boot/ssh

#Remove Avahi
sudo apt purge -y avahi-daemon

#Install Wireshark Filezilla and 2 packages required by batctl
sudo apt install -y wireshark filezilla libnl-3-dev libnl-genl-3-dev 

#Set permissions for Wireshark
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap
sudo chown root /usr/bin/dumpcap
sudo chmod u+s /usr/bin/dumpcap
sudo gpasswd -a pi wireshark

#Clone and install batctl
git clone https://git.open-mesh.org/batctl.git
cd batctl
sudo make install
cd /home/pi

#Add batman-adv to startup modules
sudo chmod 666 /etc/modules
echo 'batman-adv' >> /etc/modules

#Moving and changing file permissions and making executable 
sudo mv /home/pi/autop2p.service /etc/systemd/system
sudo chmod 644 /etc/systemd/system/autop2p.service
chmod +x /home/pi/autop2p.py
chmod +x /home/pi/edit_mesh_settings.py

#Reload the sytemctl daemon and enable the autop2p.service on boot
sudo systemctl enable autop2p.service
sudo systemctl daemon-reload

#Clone and install the Sun Founder Pi Car S software
git clone --recursive https://github.com/sunfounder/SunFounder_PiCar-S.git
cd SunFounder_PiCar-S/
sudo ./install_dependencies

#!/bin/bash

#Update repo list + upgrade
sudo apt update && apt -y upgrade

#Disable dhcpcd auto config on the wireless and bat interfaces
sudo sed -i 1i"denyinterfaces wlan*\ndenyinterfaces bat*" /etc/dhcpcd.conf

#Enable SSH by creating an empty file in the boot directory
echo >> /boot/ssh

#Remove Avahi
sudo apt purge -y avahi-daemon

#Install Wireshark Filezilla and other packages required by batctl
sudo apt install -y wireshark filezilla libnl-3-dev libnl-genl-3-dev build-essential python-dev python-smbus python-pip git xrdp 

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

#Clone and install Adafruit BNO055 library
git clone https://github.com/adafruit/Adafruit_Python_BNO055.git
cd Adafruit_Python_BNO055
sudo python setup.py install
cd /home/pi
sudo pip3 install Adafruit_BNO055

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

#Clone the AutoP2P files
sudo git clone https://github.com/biketramp/Automatic-P2P-Network-Configuration
cd Automatic-P2P-Network-Configuration
sudo cp * /home/pi/
cd /home/pi/
sudo rm Automatic-P2P-Network-Configuration



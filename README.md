This automatic network configuration tool is for use with Raspberry Pi based Pi Car-S robot cars, it is intended to automate network configuration and simplify updating network settings. It could be easily adapted for use with other variation of Debian or Linux.


The autop2p tool consists of the following files:
1.  autop2p.service
2.  autop2p.py
3.  ipcheck.py
4.  edit_mesh_settings.py
5.  install.sh

All files are placed in the /home/pi/ directory initially, setting the install.sh script to be executable and running it with the following 2 commands will configure everything:

sudo chmod +x install.sh

sudo bash install.sh

This has been tested on Raspbian desktop Nov 18 + Apr 19 with Raspberry Pi 3B's.

A wireless network adapter capable of an increasing its MTU to 1532 is required with batman-adv or the code can be changed for 
use with the built in wireless adapter at the cost of fragmentation.

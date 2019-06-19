"""
The purpose of this script is to carry out the following configurutation
on a Raspberry Pi 3B:
1. Set the WiFi country code to GB.
2. Start the batman-adv process.
3. Discover network interfaces.
4. Configure any wireless interfaces for use in a batman-adv mesh.
5. Check for external connectivity and set the gateway mode accordingly.
6. Change the hostname to the MAC of the mesh wireless interface.
7. If no wireless int is configured change hostname to Ethernet MAC.
8. Create and update the batlog and batips log files.
8. Carry out network IP addressing, log neighbour addresses.

It has the following limitations:
1. The OS must have the correct folder structure and the user account
   must be the default pi account stucture or the script will terminate.
   e.g /home/pi or /etc/hosts.
2. The OS must use systemd to manage its services.
3. batctl and its dependencies must be installed.
4. A wireless interface must be capable of accepting an MTU increase to 
   1532 which current RPi chips do not. The Ralink RT5370 does and comes
   with the Pi Car S kit.
5. The wireless interface must also be capable of being set to ad-hoc
6. Python 2.7 must be installed. At the time of writing this comes pre-
   installed on Raspbian (Stretch).
7. The autop2p package must be installed and configured using the
   install.sh script, see user guide and README file.
"""

import os
import commands
import subprocess
import re
import time
    
# The user editable batman-adv mesh settings. Must match on all devices
essid = "Batmesh"
channel = "1"
mode = "ad-hoc"
cell_id = "00:11:22:33:44:55"
key = "1234567890123"

# Variables used in interface configuration and change hostname phases
wireless_list = []
interface_list = []
wireless_success = False
current_hostname = ''
new_hostname = "ChangeMe"
succesful_interface = ''

# Lists for use in the addressing phase
split_mac_list = []
neighbour_list = []
forth_elements = []
fifth_elements = []
sixth_elements = []
hex_list = []
unused_hex = []

def check_files():
    """ Check the 2 host files and wpa_supplicant.conf are in the
    correct location before proceeding. If not then quit. Check the 2 
    log files are in the correct location, wipe if they are and create
    if not """
    if not os.path.exists('/etc/hosts'):
	print \
	"The hosts file is not in the etc directory\nThis could be due \
	to the operating system file structure"
	raise SystemExit
    if not os.path.exists('/etc/hostname'):
	print\
	"The hostname file is not in the etc directory\nThis could be \
	due to the operating system file structure"
	raise SystemExit
    if not os.path.exists('/etc/wpa_supplicant/wpa_supplicant.conf'):
	print\
	"The wpa_supplicant.conf file is not in the etc directory\nThis\
	 could be due to the operating system file structure"
	raise SystemExit
    if not os.path.exists('/home/pi/batlog.txt'):
	open('/home/pi/batlog.txt', 'w').close()
    else:
	open('/home/pi/batlog.txt', 'w').close()
    if not os.path.exists('/home/pi/batips.txt'):
	open('/home/pi/batips.txt', 'w').close()
    else:
	open('/home/pi/batips.txt', 'w').close()
	
def set_country_code():
    """ Check and if neccessary set the WiFi country code to GB to avoid 
    issues when attempting to connect to standard WiFi """ 
    os.system('sudo chmod 666 /etc/wpa_supplicant/wpa_supplicant.conf')
    print "Setting WiFi country code to GB"
    f = open("/etc/wpa_supplicant/wpa_supplicant.conf", 'a')
    f.write('country=GB\n')
    f.close()
    print "Country now set to GB"

def create_wireless_int_list(wireless_list):
    """ Because the wlan interfaces have been disabled in dhcpcd.conf
    they need to be discovered and brought up manually prior to the
    create_full_int_list function.
    The grep command searches though the output from iwconfig and 
    awk prints the first word on the line which should be the interface
    name. That output is captured by Popen and subprocess to make into
    the wireless_list. 
    """
    iwconfig_list = subprocess.Popen\
    ("iwconfig | grep 802.11 | awk '{ print $1}'",\
     shell=True, stdout=subprocess.PIPE)
    for line in iter(iwconfig_list.stdout.readline, ''):
	wireless_list.append(line.rstrip('\n'))
	
def create_full_int_list():
    """ The grep/Popen/subrocess combination used above gets the
    raw interface names. The colons are removed so that can be used for
    the getmac function. For each line in the output an entry is 
    appended to the initially empty interface_list. Removes bat0 and l0
    as they do not require configuration and the list is sorted in
    reverse alphabettically so the wireless interfaces are processed
    first to save unneccessary computation """
    global interface_list
    ifconfig_list = subprocess.Popen\
    ("ifconfig | grep BROADCAST | awk '{ print $1}'",\
     shell=True, stdout=subprocess.PIPE)
    for line in iter(ifconfig_list.stdout.readline, ''):
	    interface_list.append(line.rstrip('\n'))
    interface_list = map(lambda each:each.strip(":"), interface_list)
    if "bat0" in interface_list:
	interface_list.remove("bat0")
    if "lo" in interface_list:
	interface_list.remove("l0")
    interface_list.sort(reverse=True)
    print "The following interfaces were found"
    for p in interface_list: print (p)

def getmac(iface):
    """ Uses grep to parse though the ifconfig output of the interface 
    stated, awk prints the second word on the line with that matched 
    the grep string. Strip removes white space from either side of the
    mac address. The .getoutput function takes that value and stores it
    in as the ifconfig variable. Use of regular expressions to check a
    valid mac address has been found, if it is then the colons are removed
    so it can be stored as the global macaddr variable and used as the
    hostname. If statements dictate if the interface is configured as 
    wired or wireless dependant on the first letter. iface and macaddr
    variables are passed to the relevant interface configuration 
    function.
    """
    ifconfig = commands.getoutput\
    ("ifconfig " + iface + "| grep ether | awk '{ print $2 }'").strip()
    if re.match('^([a-fA-F0-9]{2}[:]?){5}[a-fA-F0-9]{2}$', ifconfig):
        macaddr = ifconfig
        macaddr = macaddr.replace(':', '')
        print "Valid " + iface + " address found"
        print macaddr
        if iface.startswith("w"):
            print "Attempting configuration of " + iface
            config_wireless_interface(iface,macaddr)
        if iface.startswith("e"):
            config_wired_interface(iface,macaddr)
    else:
        print "No valid mac address found, ifconfig output dosnt match\
         the expected output"
	raise SystemExit

def config_wireless_interface(iface,macaddr):
    """ The config_wireless_interface function makes use of ifconfig,
    iwconfig and batctl cmds to configure the passed iface value from
    the getmac function. The interface must begin with "w" """
    # Takes down the interface, attempts increasing mtu to 1532
    os.system('sudo ifconfig ' + iface + ' down')
    error_message = os.system('sudo ifconfig ' + iface + ' mtu 1532')
    # If success the error_message value will be 0, continue config
    if error_message == 0:
        os.system('sudo iwconfig ' + iface + ' mode ' + mode)
        os.system('sudo iwconfig ' + iface + ' essid ' + essid)
        os.system('sudo iwconfig ' + iface + ' ap ' + cell_id)
        os.system('sudo iwconfig ' + iface + ' channel ' + channel)
        os.system('sudo iwconfig ' + iface + ' key s:' + key)
        os.system('sleep 1s')
        os.system('sudo ifconfig ' + iface + ' up')
        os.system('sleep 1s')
        # Bridge physical interface with batman-adv virtual interface
        os.system('sudo batctl if add ' + iface)
        os.system('sleep 1s')
        print iface + " int configured with default cell settings"
        os.system('sudo ifconfig bat0 up')
        os.system('sleep 5s')
        print "bat0 is up and running"
        global new_hostname
        global wireless_success
	global succesful_interface
        new_hostname = macaddr
        wireless_success = True
	succesful_interface = iface
    else:
        print iface + " wont allow 1532 mtu"
        os.system('sudo ifconfig ' + iface + ' up')
        
def config_wired_interface(iface,macaddr):
    """ The config_wired_interface function sets the hostname to the
    Ethernet mac address should the configuration of a wireless
    interface not be successful. """
    if not wireless_success:
        global new_hostname
        new_hostname = macaddr
	
def check_hostname():
    """ Find out the current hostname using the commands.getoutput
    function """
    global current_hostname
    current_hostname = commands.getoutput("hostname")
    print "Current hostname is " +current_hostname
    print "New hostname is " +new_hostname

def change_hostname(new_hostname):
    """ First ensure that root has r + w permissions for the 2 host
    files. Then opens the files from the paths specified as readable and
    stores it in the newly created f variable. The file contents are
    then read into the filedata variable with .read and the file is
    closed. A variable called newdata is created and the the current
    hostname is replaced with the new_hostname. The file is then
    re-opened as writable and the newdata is written over the top of the
    old data. This is done on both host files and then the hostname
    command issued. """
    
    os.system('sudo chmod 666 /etc/hosts')
    os.system('sudo chmod 666 /etc/hostname')
    print "current hostname is not the batman interface, changing now"
    f = open('/etc/hostname', 'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace(current_hostname, new_hostname)
    f = open("/etc/hostname", 'w')
    f.write(newdata)
    f.close()
    f = open("/etc/hosts", 'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace(current_hostname, new_hostname)
    f = open("/etc/hosts", 'w')
    f.write(newdata)
    f.close()
    os.system('sudo hostname ' + new_hostname)
    os.system('sudo service networking restart')
    time.sleep(2)

def set_gateway_option():
    """ Checks for external connectivity by pinging Googles DNS server
    If succesful then "from" will be in output, configure as gateway server
    If not succesful but a wireless int has been successfully configured
    then configure as gateway client, else dont set gateway mode and inform
    user """
    ping_output = commands.getoutput('ping -c 2 8.8.8.8')
    if "from" in ping_output:
	if wireless_success:
	    print ping_output
	    os.system('sudo batctl gw_mode server')
	    print "External connectivity detected, gateway mode set too:"
	    os.system('sudo batctl gw_mode')
	else:
	    print "External connectivy detected, but no successful wireless \
    interface configuration\nCheck a compatible wireless interface is \
    inserted and reboot or manually start\nthe autop2p.py script"
    if "from" not in ping_output:
	if wireless_success:
	    print ping_output
	    os.system('sudo batctl gw_mode client')
	    print "No external connectivity detected, gateway mode set too:"
	    os.system('sudo batctl gw_mode')
	else:
	    print "No external connectivity or succesful wireless \
	    interface configuration detected"
	
def create_mac_lists():
    
    global split_mac_list, neighbour_list, forth_elements\
    ,fifth_elements , sixth_elements
    
    """ Get output from ifconfig of succesful_interface, print word
    2 (mac address) Check the format with re.match. Use .split to
    break the mac down into seperate elements. Set ifconfig to
    batmac. Remove colons. Delete the OUI part of the MAC."""

    ifconfig = commands.getoutput("ifconfig " +succesful_interface+\
    " | grep ether | awk '{ print $2 }'").strip()
    if re.match('^([a-fA-F0-9]{2}[:]?){5}[a-fA-F0-9]{2}$', ifconfig):
	split_mac_list = ifconfig.split(':')
	del split_mac_list[0:3]
    else:
	print "No valid MAC for " +succesful_interface+ " found"
	
    """ Create a neighbour_list of neighbouring succesful_interface MAC
    addresses for comparison to avoid duplicate addressing using
    subprocess.Popen. For each line of output add an extra element to
    the list. map and lamba to create a mini function that treats the
    elements of the list as object and gets rid of the colons.
    """
    other_batmac = subprocess.Popen\
    ("sudo batctl o | grep \* | awk '{print $2 }'",\
    shell=True, stdout=subprocess.PIPE)
    for line in iter(other_batmac.stdout.readline, ''):
	neighbour_list.append(line.rstrip('\n'))
	neighbour_list = map(lambda each:each.replace(":", "")\
		, neighbour_list)

    # Create 3 seperate lists from the neighbour_list:
    for i in neighbour_list:
	sixth_elements.append(i[-2:])
	fifth_elements.append(i[8:10])
	forth_elements.append(i[6:8])

def address_bat0():
    
    """ For every entry in sixth_elements list, convert to decimal
    and write to batips.txt to enable simple ip address record"""
    for i in sixth_elements:
	    neighbour_ip = str((int(i, 16)))
	    f = open("/home/pi/batips.txt", 'w+')
	    if ('10.100.1' +neighbour_ip) not in f:
		    f.write('10.100.1.' +neighbour_ip+'\n')
		    f.close()
	    f.close()
	    
    """ First check that the octet value isnt 00 or ff as these will
    convert to the broadcast and network addresses or the network. Then
    check if the local 6th element of the bat0 mac address is
    the same as any other 6th elements. If it isnt, convert to 
    decimal and apply IP with the decimal value as the last octet
    to interface. Append the IP address to the batlog.txt file for
    ease of identification. 
    """
    if split_mac_list[2] == '00':
	addressing_backstop()
    elif split_mac_list[2] == 'ff':
	addressing_backstop()

    if split_mac_list[2] not in sixth_elements:
	print "The 6th element of the host mac is unique"
	print "Converting to decimal and applying IP"
	batmac_to_decimal = str((int(split_mac_list[2], 16)))
	os.system\
	('sudo ifconfig bat0 10.100.1.' +batmac_to_decimal+ '/24')
	f = open("/home/pi/batlog.txt", 'w+')
	f.write\
	('On 1st attempt bat0 interface set to 10.100.1.'\
	+batmac_to_decimal+ '/24\n')
	f.close()
	print "bat0 IP set to 10.100.1." +batmac_to_decimal+ "/24"
    else:
	print "The 6th element of the host mac is not unique"
	    
	""" Check if the local 5th element of the successful_interface
	mac is the same as other 6th or 5th elements. If it isnt do the 
	same as above.
	"""
	if split_mac_list[1] == '00':
	    addressing_backstop()
	elif split_mac_list[1] == 'ff':
	    addressing_backstop()
	
	if split_mac_list[1] not in\
	    (sixth_elements, fifth_elements):
	    print "The 5th element of the host mac is unique"
	    print "Converting to decimal and applying IP"
	    batmac_to_decimal = str((int(split_mac_list[1], 16)))
	    os.system\
	    ('sudo ifconfig bat0 10.100.1.'+batmac_to_decimal+ '/24')
	    f = open("/home/pi/batlog.txt", 'w+')
	    f.write\
	    ('On second attempt bat0 interface set to 10.100.1.'\
	    +batmac_to_decimal+ '/24\n')
	    f.close()
	    print "bat0 IP set to 10.100.1."+batmac_to_decimal+"/24"
	else:
	    print "The 5th element of the host mac is not unique"
		
	    """ Check if the local 4th element of the successful_interface
	    mac address is the same as other 4th, 5th or 6th elements.
	    If not do the same as above.
	    """
	    if split_mac_list[0] == '00':
		addressing_backstop()
	    elif split_mac_list[0] == 'ff':
		addressing_backstop()
	    
	    if split_mac_list[0] not in (sixth_elements,\
		fifth_elements, forth_elements):
		print "4th element of the host mac is unique"
		print "Converting to decimal and applying IP"
		batmac_to_decimal = str((int(split_mac_list[0], 16)))
		os.system\
		('sudo ifconfig bat0 10.100.1.'+batmac_to_decimal+\
		'/24')
		f = open("/home/pi/batlog.txt", 'w+')
		f.write\
		('On 3rd attempt bat0 interface set to 10.100.1.'\
		+batmac_to_decimal+'/24\n')
		f.close()
		print "bat0 IP set to 10.100.1."+batmac_to_decimal+"/24"
	    else:
		addressing_backstop()
		
def addressing_backstop():
    """ This function is used it the address_bat0 function fails due
    to duplicate addressing. It creates a list of all possible hex
    values in hex_list , minus 00 and ff as these are the broadcast
    and network addresses. The 3 lists of neighbouring MACs are combined into
    the full_list. A new list is created called unused_hex containing all
    the unused hex values using a for loop. The first entry from the 
    unused_hex list is assigned to the interface.
    """
    for o in range(256):
	global hex_list
	if o < 16:
	    hex_list.append('0'+(str((hex(o)[2:]))))
	else:
	    hex_list.append(str((hex(o)[2:])))
    # Remove 1st and last element to avoid .255 or .0 addressing
    hex_list = hex_list[1:-1]
    global unused_hex
    full_list = forth_elements+fifth_elements+sixth_elements
    unused_hex = [x for x in hex_list if x not in full_list]
    batmac_to_decimal =\
    str((int(unused_hex[0], 16)))
    os.system\
    ('sudo ifconfig bat0 10.100.1.' +batmac_to_decimal+\
     '/24')
    f = open("/home/pi/batlog.txt", 'w+')
    f.write ('Kaaapow !!! No unique octets, had to use one from the unused list\nbat0 interface set to 10.100.1.'+batmac_to_decimal+'/24\n')
    f.close()
    print "bat0 IP set to 10.100.1." \
    +batmac_to_decimal+ "/24"

#Main body of code
check_files()
country_code = commands.getoutput\
('sudo grep GB /etc/wpa_supplicant/wpa_supplicant.conf')
if "country=GB" not in country_code:
    set_country_code()
# Start the batman-adv process and wait a second
os.system('sudo modprobe batman-adv')
time.sleep(1)
create_wireless_int_list(wireless_list)
for p in wireless_list: print p
# Bring up the wireless interfaces
for i in wireless_list:
    os.system('sudo ifconfig ' +i+ ' up')
create_full_int_list()
print "Checking for valid MAC addresses"
# A for loop that passes each entry in the interface_list to getmac
for i in interface_list:
    iface = i
    getmac(iface)
# getmac starts config_wireless_int, config_wired_int or exits on fail
check_hostname()
if current_hostname != new_hostname:
    change_hostname(new_hostname)
if current_hostname == new_hostname:
    print "Hostname is already set"
set_gateway_option()
# Only carry out addressing if bat0 is up
bats_up = commands.getoutput('sudo ifconfig | grep bat0')
if 'bat0' in bats_up:
    create_mac_lists()
    address_bat0()

else:
    f = open("/home/pi/batlog.txt", 'a')
    f.write('bat0 is down')
    f.close()
    print "bat0 is down"
    
raise SystemExit

""" The getmac function is based on the work of "Trip"
found at the following url:
https://forums.hak5.org/topic/20372-python-script-to-get-mac-address/
The config_wireless_interface function was adapted from the work of
"darknetplan" found at the following url:
https://www.reddit.com/r/darknetplan/comments/68s6jp/how_to_configure_\
batmanadv_on_the_raspberry_pi_3/
Thanks and respect to you both"""
# Word Count 2418

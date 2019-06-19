import subprocess
import commands
import re
split_mac_list = []
neighbor_list = []
forth_elements = []
fifth_elements = []
sixth_elements = []

""" Uses grep to search through the output from batctl if to
identify the interface being used with batman-adv
"""
batctl_if = commands.getoutput\
("batctl if | grep active | awk '{ print $1 }'")
batctl_if = batctl_if.replace(':', '')
print batctl_if + " is the wireless interface bridged with bat0"

""" Get output from ifconfig of bat0, print word 2 (mac address)
Check the format with re.match. Use .split to break the mac down
into seperate elements.
"""
ifconfig = commands.getoutput\
("ifconfig "+batctl_if+" | grep ether | awk '{ print $2 }'").strip()
if re.match('^([a-fA-F0-9]{2}[:]?){5}[a-fA-F0-9]{2}$', ifconfig):
	split_mac_list = ifconfig.split(':')
	
""" Discover own ip by using grep/awk with ifconfig
"""
own_ip = commands.getoutput\
("ifconfig bat0 | grep 10.100. | awk '{ print $2}'").strip()
print "The bat0 IP is " + own_ip

""" Create a neighbor_list of neighboring bat0 MAC addresses for 
comparison to avoid duplicate addressing using subprocess.Popen.
For each line of output add an extra element to the list. map 
and lamba to create a mini function that treats the elements of
the list as object and gets rid of the colons.
"""
other_batmac = subprocess.Popen\
("sudo batctl o | grep \* | awk '{print $2 }'",\
 shell=True, stdout=subprocess.PIPE)
for line in iter(other_batmac.stdout.readline, ''):
	neighbor_list.append(line.rstrip('\n'))
neighbor_list = map(lambda each:each.replace(":", "")\
, neighbor_list)

""" Create 3 seperate lists from the neighbor_list
"""
for i in neighbor_list:
	sixth_elements.append(i[-2:])
	fifth_elements.append(i[8:10])
	forth_elements.append(i[6:8])
	
""" For every entry in sixth_elements list, convert to decimal
and write to batips.txt to enable simple ip address record"""
print "Neighbouring IP addresses are:"
for i in sixth_elements:
	neighbor_ip = str((int(i, 16)))
	print '10.100.1.' +neighbor_ip

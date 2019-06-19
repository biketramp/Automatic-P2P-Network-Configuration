import re
import os
import commands
""" Check that the autop2p files are in the correct directorys before
continuing
"""
if not os.path.exists("/home/pi/autop2p.py"):
	print "The autop2p.py file is not in the /home/pi directory"
if not os.path.exists("/etc/systemd/system/autop2p.service"):
	print\
	"The autop2p.service file is not in the /etc/systemd/system directory"
	
valid_essid = False
valid_channel = False
valid_mode = False
valid_cell_id = False
valid_confirmation = False
valid_action = False
uk_channels=['1','2','3','4','5','6','7','8','9','10','11','12','13']
mesh_modes=['ad-hoc']

""" Discover and print out current settings based on the entries in
the autop2p.py file
"""
current_essid = commands.getoutput\
("sudo grep 'essid =' /home/pi/autop2p.py")
current_channel = commands.getoutput\
("sudo grep 'channel =' /home/pi/autop2p.py")
current_mode = commands.getoutput\
("sudo grep 'mode =' /home/pi/autop2p.py")
current_cell_id = commands.getoutput\
("sudo grep 'cell_id =' /home/pi/autop2p.py")

print "The current settings are:"
print current_essid
print current_channel
print current_mode
print current_cell_id

""" A user may wish to use this script to get the robots back to their
default state. At the end of a project for example. 
"""
def default_settings():
    print "Defaulting values in /home/pi/autop2p.py"
    f = open("/home/pi/autop2p.py", 'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace(current_essid, 'essid = "Batmesh"')
    newdata = newdata.replace(current_channel, 'channel = "1"')
    newdata = newdata.replace(current_mode, 'mode = "ad-hoc"')
    newdata = newdata.replace\
    (current_cell_id, 'cell_id = "00:11:22:33:44:55"')
    f = open("/home/pi/autop2p.py", 'w')
    f.write(newdata)
    f.close()
    print "System defaults have been set"
    #os.system('sudo python /home/pi/autop2p.py')
    raise SystemExit

while not valid_action:
	choice = raw_input\
	('To default the settings press D to continue updating press C:\n')
	if choice.lower() == 'd':
		print 'Updating configuration now'
		valid_action = True
		default_settings()
	elif choice.lower() == 'c':
		valid_action = True
		break
	else:
		print('Please re-enter in correct format')
	
print ('To update the mesh setting follow the instructions')

""" Prompt user for input to change essid. Check input using regular
expressions. If correct format set valid_essid to true and break out of
loop, if not try again.
"""
while not valid_essid:
	print 'A valid mesh name contains upto 32 letters and numbers only'
	essid = raw_input('Enter new mesh name:\n')
	correct_format = re.match('^([a-zA-Z0-9_ -]{1,32})$', essid)
	if correct_format:
		valid_essid = True
	else:
		print 'Please re-enter in correct format'		

""" Prompt user for input to change wireless channel. Check input is
in the correct format. If so also set a freq variable with the RF
frequency value. Same procedure as above to break the loop.
"""
while not valid_channel:
	channel = raw_input('Enter new channel between 1 to 13:\n')
	if channel in uk_channels:
		if channel == '1':
			freq = '2.412'
		elif channel == '2':
			freq = '2.417'
		elif channel == '3':
			freq = '2.422'
		elif channel == '4':
			freq = '2.427'
		elif channel == '5':
			freq = '2.432'
		elif channel == '6':
			freq = '2.437'
		elif channel == '7':
			freq = '2.442'
		elif channel == '8':
			freq = '2.447'
		elif channel == '9':
			freq = '2.452'
		elif channel == '10':
			freq = '2.457'
		elif channel == '11':
			freq = '2.462'
		elif channel == '12':
			freq = '2.467'
		elif channel == '13':
			freq = '2.472'
		valid_channel = True
	else:
		print 'Please re-enter in correct format'
	
""" Prompt user for input to change interface mode. Check input is
in the correct format. Prints out the entries in the mode list.
Same procedure as above to break the loop.
"""	
while not valid_mode:
	print 'Enter a new mesh mode from the following:'
	for p in mesh_modes: print p
	mode = raw_input()
	if mode in mesh_modes:
		valid_mode = True
	else:
		print 'Please re-enter a valid mode'
		
""" Prompt the user to enter a new cell ID. Check input is in the right
format (MAC address style). If not try again.
"""
while not valid_cell_id:
	cell_id = raw_input\
	('Enter new cell_id in the correct format e.g\n1F:42:14:GE:17:32\
	\n6 pairs of numbers or letters from A to F separated by colons:\n')
	correct_format = re.match('^([a-fA-F0-9]{2}[:]?){5}[a-fA-F0-9]{2}$'\
	, cell_id)
	if correct_format:
			valid_cell_id = True
	else:
			print 'Please re-enter in correct format'
			
""" Allow the user the chance to review the entered settings
"""
print 'New settings entered are:\n'
print 'Essid = ' +essid
print 'Channel = ' +channel
print 'Mode = ' +mode
print 'Frequency = ' +freq
print 'Cell ID = ' +cell_id

""" Prompt the user to confirm the entries before committing. If yes
change the autop2p.py startup script and run it again. If not exit.
"""
def update_settings():
	print "Updating values in /home/pi/autop2p.py"
	f = open("/home/pi/autop2p.py", 'r')
	filedata = f.read()
	f.close()
	newdata = filedata.replace(current_essid, 'essid = "'+essid+'"')
	newdata = newdata.replace(current_channel, 'channel = "'+channel+'"')
	newdata = newdata.replace(current_mode, 'mode = "'+mode+'"')
	newdata = newdata.replace(current_cell_id, 'cell_id = "'+cell_id+'"')
	f = open("/home/pi/autop2p.py", 'w')
	f.write(newdata)
	f.close()
	os.system('sudo python /home/pi/autop2p.py')
	raise SystemExit

while not valid_confirmation:
	choice = raw_input('Enter Y to confirm or N to cancel and exit:\n')
	if choice.lower() == 'y':
		print 'Updating configuration now'
		valid_confirmation = True
		update_settings()
	elif choice.lower() == 'n':
		print 'Exiting now'
		valid_confirmation = True
	else:
		print('Please re-enter in correct format')
	


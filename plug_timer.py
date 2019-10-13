'''
The following code provides a multiple event on/off timer for use with 
a Raspberry Pi and a 4 channel relay module to control 4 x 240v plug
sockets.
'''
import os
import commands
import sys
import time
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
#Use the board pin numbering system
GPIO.setmode(GPIO.BOARD)
'''
The chan_list entries and physical wiring can be adjusted as necessary.
Socket 1 = 33
Socket 2 = 35
Socket 3 = 36
Socket 4 = 37
'''
chan_list = (33,35,36,37)

#Set all the pins in the channel list to low
GPIO.setup(chan_list, GPIO.OUT, initial=GPIO.LOW)
#NEED TO CHECK THAT THE LISTS ARE CONSECUTIVE AND NOT OVERLAPPING
'''
######## THIS IS WHERE YOU SET THE ON & OFF TIMINGS ###########
######### Ensure there is an off for every on #################
'''
socket_1_on_times = ['1950', '2201']
socket_1_off_times = ['2200', '2202']

socket_2_on_times = ['2127']
socket_2_off_times = ['2244']

socket_3_on_times = ['0700']
socket_3_off_times = ['0701']

socket_4_on_times = ['0700']
socket_4_off_times = ['2300']

'''
The time_now variable needs initiating before the main loop to carry 
out the 
'''
def check_consecutive():
	i = 0
	for x in socket_1_on_times:
		print socket_1_on_list_length
		print i
		if socket_1_off_times[i] <= socket_1_on_times[i]:
			print "A timing entered for socket 1 is either a duplicate or less than the start time"
			GPIO.cleanup()
			raise SystemExit
		if socket_1_on_list_length > i:
			if socket_1_on_times[i+1] <= socket_1_off_times[i]:
				print "A timing entered for socket 1 is overlapping or non consecutive, please correct"
				GPIO.cleanup()
				raise SystemExit
		i += 1
			
		
print "Starting the timer function - Press Ctrl C to interrupt"
#NEED TO CHECK THAT THE ON AND OFF TIMES ARNT THE SAME
'''
The list length checks that there are equal amounts of on / off entries
to avoid any misconfiguration.
'''
def list_length_check():
	global socket_1_on_list_length 
	global socket_1_off_list_length
	global socket_2_on_list_length
	global socket_2_off_list_length
	global socket_3_on_list_length
	global socket_3_off_list_length
	global socket_4_on_list_length
	global socket_4_off_list_length
	socket_1_on_list_length = len(socket_1_on_times)
	socket_1_off_list_length = len(socket_1_off_times)
	if socket_1_on_list_length != socket_1_off_list_length:
		print "Theres an on or off timing missing from the socket 1 lists"
		GPIO.cleanup()
		raise SystemExit
	socket_2_on_list_length = len(socket_2_on_times)
	socket_2_off_list_length = len(socket_2_off_times)
	if socket_2_on_list_length != socket_2_off_list_length:
		print "Theres an on or off timing missing from the socket 2 lists"
		GPIO.cleanup()
		raise SystemExit
	socket_3_on_list_length = len(socket_3_on_times)
	socket_3_off_list_length = len(socket_3_off_times)
	if socket_3_on_list_length != socket_3_off_list_length:
		print "Theres an on or off timing missing from the socket 3 lists"
		GPIO.cleanup()
		raise SystemExit
	socket_4_on_list_length = len(socket_4_on_times)
	socket_4_off_list_length = len(socket_4_off_times)
	if socket_4_on_list_length != socket_4_off_list_length:
		print "Theres an on or off timing missing from the socket 4 lists"
		GPIO.cleanup()
		raise SystemExit
'''
The lists need to be checked to ensure that the on/off entries do not 
overlap for each individual socket and that they are in sequence.
'''
def same_on_off_check():
	i = 0
	for x in socket_1_on_times:
		if socket_1_on_times[i] == socket_1_off_times[i]:
			print "Socket 1 number " + str(i) + " on and off times are the same"
			GPIO.cleanup()
			raise SystemExit
		i += 1
	i = 0
	for x in socket_2_on_times:
		if socket_2_on_times[i] == socket_2_off_times[i]:
			print "Socket 2 number " + str(i) + " on and off times are the same"
			GPIO.cleanup()
			raise SystemExit
		i += 1
	i = 0
	for x in socket_3_on_times:
		if socket_3_on_times[i] == socket_3_off_times[i]:
			print "Socket 3 number " + str(i) + " on and off times are the same"
			GPIO.cleanup()
			raise SystemExit
		i += 1
	i = 0
	for x in socket_4_on_times:
		if socket_4_on_times[i] == socket_4_off_times[i]:
			print "Socket 1 number " + str(i) + " on and off times are the same"
			GPIO.cleanup()
			raise SystemExit
		i += 1
	
'''
There is a possiblity that during the initial power up or following a
system restart that the triggering of the change of power state will be
missed as the check_alarms function requires an exact match. The purpose
of this function is to check for that possibility and ensure that the
correct power state is set.
'''
def startup_status_check():
	#time_now need initialising here.
	global time_now
	time_now = commands.getoutput ("sudo date -R | awk '{print $5}'")
	time_now = time_now.replace(':', '')
	time_now = time_now[0:4]
	i = 0
	#Check if the time_now is between an on and an off time.
	for x in socket_1_on_times:
		if time_now >= socket_1_on_times[i] and time_now < socket_1_off_times[i]:
			print "Timer started during socket 1 on period"
			GPIO.output(33, 1)
			print "Socket 1 on"
		#Compare the off time with the next on time - check if there is one first.
		if i+1 < socket_1_on_list_length:
			if time_now >= socket_1_off_times[i] and time_now < socket_1_on_times[i+1]:
				print "Timer started during socket 1 off period"
				GPIO.output(33, 0)
				print "Socket 1 off"
		if socket_1_on_times[i] > socket_1_off_times[i]:
			print "This alarm goes over the midnight boundary"
			if time_now >= socket_1_on_times[i] or time_now < socket_1_off_times[i]:
				print "Timer started during socket 1 on period"
				GPIO.output(33, 1)
				print "Socket 1 on"
		i += 1
	i = 0
	for x in socket_2_on_times:
		if time_now >= socket_2_on_times[i] and time_now < socket_2_off_times[i]:
			print "Timer started during socket 2 on period"
			GPIO.output(35, 1)
			print "Socket 2 on"
		#Compare the off time with the next on time - check if there is one first.
		if i+1 < socket_2_on_list_length:
			if time_now >= socket_2_off_times[i] and time_now < socket_2_on_times[i+1]:
				print "Timer started during socket 2 off period"
				GPIO.output(35, 0)
				print "Socket 2 off"
		if socket_2_on_times[i] > socket_2_off_times[i]:
			print "This alarm goes over the midnight boundary"
			if time_now >= socket_2_on_times[i] or time_now < socket_2_off_times[i]:
				print "Timer started during socket 2 on period"
				GPIO.output(35, 1)
				print "Socket 2 on"
		i += 1
	i = 0
	for x in socket_3_on_times:
		if time_now >= socket_3_on_times[i] and time_now < socket_3_off_times[i]:
			print "Timer started during socket 3 on period"
			GPIO.output(36, 1)
			print "Socket 3 on"
		#Compare the off time with the next on time - check if there is one first.
		if i+1 < socket_3_on_list_length:
			if time_now >= socket_3_off_times[i] and time_now < socket_3_on_times[i+1]:
				print "Timer started during socket 3 off period"
				GPIO.output(36, 0)
				print "Socket 3 off"
		if socket_3_on_times[i] > socket_3_off_times[i]:
			print "This alarm goes over the midnight boundary"
			if time_now >= socket_3_on_times[i] or time_now < socket_3_off_times[i]:
				print "Timer started during socket 3 on period"
				GPIO.output(36, 1)
				print "Socket 3 on"
		i += 1
	i = 0
	for x in socket_4_on_times:
		if time_now >= socket_4_on_times[i] and time_now < socket_4_off_times[i]:
			print "Timer started during socket 4 on period"
			GPIO.output(37, 1)
			print "Socket 4 on"
		#Compare the off time with the next on time - check if there is one first.
		if i+1 < socket_4_on_list_length:
			if time_now >= socket_4_off_times[i] and time_now < socket_4_on_times[i+1]:
				print "Timer started during socket 4 off period"
				GPIO.output(37, 0)
				print "Socket 4 off"
		if socket_4_on_times[i] > socket_4_off_times[i]:
			print "This alarm goes over the midnight boundary"
			if time_now >= socket_4_on_times[i] or time_now < socket_4_off_times[i]:
				print "Timer started during socket 4 on period"
				GPIO.output(37, 1)
				print "Socket 4 on"
		i += 1
		
'''
The following function sets all the available global variables by grepping
thought the output from the date command. Not all variables are in use,
the unused ones can be commented out or removed as required or the variables
utilised for future purposes.
'''
def get_date_time():
	global day_now
	global date_now
	global month_now
	global year_now
	global offset_now
	global time_now
	day_now = date_now = commands.getoutput ("sudo date -R | awk '{print $1}'")
	day_now = day_now.replace(',', '')
	date_now = commands.getoutput ("sudo date -R | awk '{print $2}'")
	month_now = commands.getoutput ("sudo date -R | awk '{print $3}'").strip()
	year_now = commands.getoutput ("sudo date -R | awk '{print $4}'")
	time_now = commands.getoutput ("sudo date -R | awk '{print $5}'")
	time_now = time_now.replace(':', '')
	time_now = time_now[0:4]
	offset_now = commands.getoutput ("sudo date -R | awk '{print $6}'")
	print day_now + (' ') + month_now + (' ') + date_now + (' ') + year_now+ (' ') + time_now
	time.sleep(.5)

'''
The following check socket functions check all of the entries in the
on and off time lists, if a match is found the corresponding action is
taken.
'''
	
def check_socket_1():
	if time_now in socket_1_on_times:
		GPIO.output(35, 1)
		print "Socket 1 on"
	if time_now in socket_1_off_times:
		GPIO.output(35, 0)
		print "Socket 1 off"
		
def check_socket_2():
	if time_now in socket_2_on_times:
		GPIO.output(35, 1)
		print "Socket 2 on"
	if time_now in socket_2_off_times:
		GPIO.output(35, 0)
		print "Socket 2 off"
		
def check_socket_3():		
	if time_now in socket_3_on_times:
		GPIO.output(36, 1)
		print "Socket 3 on"
	if time_now in socket_3_off_times:
		GPIO.output(36, 0)
		print "Socket 3 off"
			
def check_socket_4():		
	if time_now in socket_4_on_times:
		GPIO.output(37, 1)
		print "Socket 4 on"
	if time_now in socket_4_off_times:
		GPIO.output(37, 0)
		print "Socket 4 off"

################## THIS IS THE MAIN LOOP ###############################
def main():
	while True:
		get_date_time()
		check_socket_1()
		check_socket_2()
		check_socket_3()
		check_socket_4()

if __name__ == '__main__':
    try:
		list_length_check()
		startup_status_check()
		same_on_off_check()
		check_consecutive()
		#main()
    except KeyboardInterrupt:
		GPIO.cleanup()
		print "Interrupted"
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)


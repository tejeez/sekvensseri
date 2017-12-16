#!/usr/bin/env python3
import sys, os, termios, fcntl, time

# http://love-python.blogspot.fi/2010/03/getch-in-python-get-single-character.html
fd = sys.stdin.fileno()
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

while True:
	print(sys.stdin.read(1))
	time.sleep(0.1)


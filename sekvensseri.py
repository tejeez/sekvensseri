#!/usr/bin/env python3
import sys, os, termios, fcntl, time
seqlen = 16
seqnum = 8
seq = []
for i in range(seqlen):
	seq.append([0] * seqnum)

cursorrow = 0
cursorcol = 0

# http://love-python.blogspot.fi/2010/03/getch-in-python-get-single-character.html
fd = sys.stdin.fileno()
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
#fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
oldflags &= ~os.O_NONBLOCK

# http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
key_up = "\u001b[A"
key_down = "\u001b[B"
key_right = "\u001b[C"
key_left = "\u001b[D"

print("\033[2J")
while True:
	print("\033[H")
	for rown, row in enumerate(seq):
		pline = "|"
		for coln, col in enumerate(row):
			ch = " .-"[col]*3
			if coln == cursorcol and rown == cursorrow:
				pline += "\033[43m"+ch+"\33[0m"
			else:
				pline += ch
			pline += "|"
		print(pline)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
	key = sys.stdin.read(4)
	
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
	changed = False
	if key == key_up:
		cursorrow = (cursorrow - 1) % seqlen
	elif key == key_down:
		cursorrow = (cursorrow + 1) % seqlen
	elif key == key_left:
		cursorcol = (cursorcol - 1) % seqnum
	elif key == key_right:
		cursorcol = (cursorcol + 1) % seqnum
	elif key == " ":
		seq[cursorrow][cursorcol] = 0
		changed = 1
	elif key == "-":
		seq[cursorrow][cursorcol] = 2
		changed = 1
	elif key == ".": # oispa makrot
		seq[cursorrow][cursorcol] = 1
		changed = 1
	if changed:
		cursorrow = (cursorrow + 1) % seqlen
	time.sleep(0.01)


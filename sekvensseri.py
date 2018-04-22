#!/usr/bin/env python3
import sys, os, termios, fcntl, time, pickle

dryrun = len(sys.argv)<2
if not dryrun:
	outf = open(sys.argv[1],"wb")

patnum = 64
seqlen = 16
seqnum = 6
seq = []
for i in range(seqlen):
	seq.append([0] * seqnum)

pats = []
for i in range(patnum):
	pats.append([0]*seqlen)

seqpats = [i for i in range(seqnum)]

def getcol(row, col):
	return pats[seqpats[col]][row]

def setcol(row, col, newval):
	print(seqpats[col])
	pats[seqpats[col]][row] = newval

def getrow(row):
	return [pats[seqpats[col]][row] for col in range(seqnum)]

def getwholeseq():
	return list(zip(*[pats[seqpats[col]] for col in range(seqnum)]))

inverts = [0] * seqnum

cursorrow = int(0)
cursorcol = int(0)
playrow = int(0)
playlen = seqlen
bpm = 150.0
lasttime = time.time()

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

print("\033[2J\033[Hpress i to invert output"+(" DRY RUN" if dryrun else ""))
while True:
	t = time.time()

	print("\033[H")

	pline = ":"
	for coln, col in enumerate(seqpats):
		pline += str(col).zfill(3)+":"
	print(pline + " bpm:" + str(bpm).zfill(3))

	pline = ":"
	outbyte = 0
	for coln, col in enumerate(getrow(playrow)):
		inv = inverts[coln] == 1
		#on = t - lasttime < 60.0 / (bpm*7) * col
		on = col == 2 or col == 1 and t - lasttime < 60.0 / (bpm*7) or col == 3 and t - lasttime > 60.0 / (bpm*7)

		if inv: pline += "\033[44m"
		pline += " "+str(coln)+("!" if on else " ")+"\033[0m"
		if ((not inv) and on) or (inv and (not on)):
			outbyte |= 1 << coln
		pline += ":"
	if not dryrun:
		outf.write(bytes([outbyte]))
		outf.flush()
	print(pline)

	for rown, row in enumerate(getwholeseq()):
		pline = "|"
		for coln, col in enumerate(row):
			ch = " .-,"[col]*3
			if coln == cursorcol and rown == cursorrow:
				pline += "\033[42m"+ch+"\33[0m"
			elif rown == playrow:
				pline += "\033[43m"+ch+"\33[0m"
			elif rown % 4 == 0:
				pline += "\033[46m"+ch+"\33[0m"
			else:
				pline += ch
			pline += "|"
		print(pline)

	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
	key = sys.stdin.read(3)
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
	else:
		for k in key:
			if k == " ":
				setcol(cursorrow,cursorcol,0)
				changed = 1
			elif k in ['a','-']:
				setcol(cursorrow,cursorcol,2)
				changed = 1
			elif k in ['z','x','c','v','b','n','m','.']: # oispa makrot
				setcol(cursorrow,cursorcol,1)
				changed = 1
			elif k in [',']:
				setcol(cursorrow,cursorcol,3)
				changed = 1
			elif k in ['q']:
				seqpats[cursorcol] -= 1
				if seqpats[cursorcol] < 0:
					seqpats[cursorcol] = patnum-1
			elif k in ['w']:
				seqpats[cursorcol] += 1
				if seqpats[cursorcol] >= patnum:
					seqpats[cursorcol] = 0
			elif k in ['e']:
				bpm -= 0.5
			elif k in ['r']:
				bpm += 0.5
			elif k in ['s']:
				data = {"pats": pats, "seqpats": seqpats, "bpm": bpm, "inverts": inverts}
				pickle.dump(data, open("pats.dat","wb"))
			elif k in ['l']:
				data = pickle.load(open("pats.dat","rb"))
				globals().update(data)
			elif k == "i":
				inverts[cursorcol] ^= 1
	if changed:
		cursorrow = (cursorrow + 1) % seqlen

	timestep = 60.0 / (bpm*4)
	if t - lasttime >= timestep:
		playrow = (playrow + 1) % playlen
		lasttime += timestep
	time.sleep(0.01)


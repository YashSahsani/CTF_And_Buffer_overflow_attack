#!/usr/bin/env python2
import signal, socket, pickle, zlib, os
from base64 import b64encode,b64decode
#signal.signal(signal.SIGCHLD, signal.SIG_IGN)

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 1024))
s.listen(5)

entries = {}

def rl():
	l = ""
	while not l.endswith("\n"):
		c = s.recv(1)
		c = c.decode()
		assert(c)
		l += c
	return l[:-1]

def spam_list():
	s.sendall("Listing %d passwords:\n".encode() % len(entries))
	for k, v in entries.items():
		s.sendall(str("%s: %s\n" % (k,v)).encode())
	s.sendall("---\n".encode())

def spam_add():
	s.sendall("Enter name of the site: ".encode())
	name = rl()
	s.sendall("Enter password: ".encode())
	pasw = rl()
	entries[name] = pasw
	s.sendall("Password successfully added.\n".encode())

def spam_del():
	s.sendall("Enter name of the site which should be deleted: ".encode())
	name = rl()
	if name not in entries:
		s.sendall("Entry not found.\n".encode())
	else:
		del entries[name]
		s.sendall("Entry successfully deleted.\n".encode())

def spam_backup():
	s.sendall (str("your backup is : "+ b64encode(zlib.compress(pickle.dumps(entries))).decode()+"\n").encode())

def spam_restore():
	s.sendall("Paste your backup here: ".encode())
	backup = rl()
	global entries
	entries = pickle.loads(zlib.decompress(b64decode(backup.encode())))
	s.sendall("Successfully restored %d entries\n".encode() % len(entries))

while 1:
	c, _ = s.accept()
	p = os.fork()
	if p != 0:
		c.close()
		continue
	else:
		s.close()
		break

s = c
del c

s.sendall("Welcome to Super Password Authentication Manager (SPAM)!\n".encode())

while 1:
	while 1:
		s.sendall("Menu:\n".encode())
		s.sendall("1) List Passwords\n".encode())
		s.sendall("2) Add a Password\n".encode())
		s.sendall("3) Remove a Password\n".encode())
		s.sendall("4) Backup Passwords\n".encode())
		s.sendall("5) Restore backup\n".encode())
		l = rl()
		if len(l) == 1 and l in "12345":
			[spam_list, spam_add, spam_del, spam_backup, spam_restore][int(l) - 1]()
		else:
			s.sendall("Invalid choice.\n".encode())


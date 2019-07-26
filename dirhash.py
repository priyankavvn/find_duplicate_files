#!/usr/bin/python3 
# -*- coding: utf-8 -*-
"""
Date: 26 June 2019

@author: V V N Priyanka
"""

# Usage:
#	dirhash.py [-h <hashing algorithm>] -r <root directory> [-d <database file>] [-t <text file>]
#		Only <root directory> argument is mandatory
#		All other arguments have default values:
#			-h defaults to sha256
#			-d defaults to <root directory>.db
#			-t defaults to <root directory>.txt

# Recursively traverse a directory and create an sqlite3 databse of md5/sha256/etc hashes fo each file
 

import os
import sys
import hashlib		
import sqlite3		
import signal		
import datetime		
import time		
import getopt		
import string

##hashlib.algorithms_available:
##Available algorthims  {'SHA224', 'sha224', 'DSA', 'sha256', 'MD5', 'ripemd160',
##'MD4', 'ecdsa-with-SHA1', 'SHA1', 'DSA-SHA', 'SHA256', 'SHA', 'dsaWithSHA', 'sha512
##'md5', 'sha1', 'SHA384', 'RIPEMD160', 'sha', 'SHA512', 'dsaEncryption', 'whirlpool', 'md4', 'sha384'}
##
##hashlib.algorithms_guaranteed:
##Guraranteed algorthims  {'sha224', 'sha256', 'sha512', 'md5', 'sha1', 'sha384'}
##Currently this program supports only 'guaranteed algorithms'. Full range of algorithms will be supported in future
##using hashlin.new() fuction.
# Hash algorithm: md5, sha1, etc.

hashname = ""
hash_func = hashlib.md5 

# Name of the hash database
hashdb=""

# Name of the hash text file
hashtxt=""

# Root node of the file tree for which hash db is to be created
rootdir=""

# Get command line options
# options: -r, -d, -t (all options are optional)
# -r -> rootdir (default value = current dir)
# -d -> md5 database (sqlite3) (default value = md5db.db)
# -t -> md5 text file  (default value = md5db.txt)
def get_opts():
    global hashname, hash_func, rootdir, hashdb, hashtxt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:r:d:t:", [])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        usage()
		
    for o, a in opts:
        if o == "-h":
            hashname = a
        elif o == "-r":
            rootdir = a
        elif o == "-d":
            hashdb = a
        elif o == "-t":
            hashtxt = a
        else:
            assert False, "unhandled option"

    if (rootdir == ""):
        print ("root directory not specified")
        usage()

    if (hashname == ""):
        hashname = "sha256"
        print ("Hashing algorithm not specified. Defaults to SHA256")

    if (hashdb == ""):
        hashdb =  rootdir+".db"
        print ("Hashdb file not specified. Defaults to", hashdb)
        if ((hashdb[0]=='.') or (hashdb[0]=='\\') or (hashdb[0]=='/')):
          print("Default values cannot start with a '.', '/', or '\\'. Specify it on command line")
          usage()

    if (hashtxt == ""):
        hashtxt =  rootdir + ".txt"
        print ("Hash text file not specified. Defaults to", hashtxt)
        if ((hashtxt[0]=='.') or (hashtxt[0]=='\\') or (hashtxt[0]=='/')):
          print("Default values cannot start with a '.', '/', or '\\'. Specify it on command line")
          usage()

    if hashname.lower() not in hashlib.algorithms_guaranteed:           #lower() required since the list contains lower case names only.
        print("Specified hashing algorithm ", hashname, " not supported")
        print("Specify on of the following hashing algorithms: ", hashlib.algorithms_guaranteed)
        sys.exit(2)
    hash_func = getattr(hashlib, hashname.lower())

def usage():
    print("Usage: " + os.path.basename(sys.argv[0]) + " -h <hashing algorithm> -r <root directory> -d <database file> -t <text file>")
    sys.exit(2)		

# Larger block_size for efficiency
# Open file in 'rb' mode for 'reading in binary mode'.  No translations beween "\n", "\r", "\n\r" translations.
# Returns hexdigest which is a 32-byte ascii string representing 32-hex digits of the md5 hash
def generate_file_hash(file_dir_path, file_name, block_size=2**20):
        m = hash_func()
        with open( os.path.join(file_dir_path, file_name) , "rb" ) as f:
            while True:
                buf = f.read(block_size)
                if not buf:
                    break
                m.update(buf)
        return m.hexdigest()

# Check whether the given files already exist and delete interactively
def check_file(file):
	if os.path.isfile(file):
		print("File ",file," already exists\n")
		print("Delete it and recreate a new file with the same name?\n")
		while True:
			answer=input("Enter Y/N: ")
			if answer == 'Y':
				os.remove(file)
				break
			elif answer == 'N':
				print("Delete the file manually and restart the application. Exiting")
				sys.exit(1)
		
# Catch control-c. Close db and txt files. Without this feature, control-c will just abort the program without saving any partial data that is generated so far.
def sigint_handler(signal, frame):
	print ('Control-C received')
	save_db_and_txt()
	sys.exit(0)

# Nice to see summary statistics. Especially for large file trees.
def print_stats():
	end_date = str(datetime.datetime.now())
	end_time=time.time()
	line =   ("\nStatistics:"
	+ "\nHash Algorithm:        " + hashname
	+ "\nTotal files:           " + str(file_count) 
	+ "\nTotal directories:     " + str(dir_count)
	+ "\nTotal bytes:           " + str(total_bytes)
	+ "\nStart date & time:     " + start_date
	+ "\nEnd date and time:     " + end_date
	+ "\nTime elapsed(seconds): " + str(end_time-start_time)) 
	print(line)
	hashtxtfd.write(line)

# Commit and close the md5 db and txt files.
# Called when the program terminately normally or abruptly due to keyboard interrupt
def save_db_and_txt():

        conn.commit()
        conn.close()
        print_stats()
        hashtxtfd.close()

def uniprint(s):
        printable = string.ascii_letters + string.digits + string.punctuation + ' '
        def escape(c):
                if (c in printable):
                        return c
                c = ord(c)
                if c <= 0xff:
                        return r'\x{0:02x}'.format(c)
                elif c <= 0xffff : #c <= '\uffff':
                        return r'\u{0:04x}'.format(c)
                else:
                        return r'\U{0:08x}'.format(c)
        try:
                print(s)
        except UnicodeEncodeError as e:
                s1=''.join(escape(c) for c in s)
                print(s1) 
        
get_opts()
check_file(hashdb)
check_file(hashtxt)
hashtxtfd = open(hashtxt,'w')
conn=sqlite3.connect(hashdb)
signal.signal(signal.SIGINT, sigint_handler)

c = conn.cursor()

c.execute ('''CREATE TABLE hash_table (''' + hashname + ''' text, path text)''')

file_count=0
dir_count=0
previous_dir=""
start_time=0
end_time=0
total_bytes=0
start_date = str(datetime.datetime.now())
start_time=time.time()

# Recursive traversal of the file tree, compute md5, insert the values into a db file and also write a text file
for root,dirs,files in os.walk(rootdir):
	for file in files:
		file_count += 1
		file_size = os.path.getsize(os.path.join(root,file))
		total_bytes += file_size 

		if (previous_dir != root):
			line = "\n" 
			uniprint (line) 
			hashtxtfd.write(line)
			previous_dir=root
			dir_count += 1
			
		m=generate_file_hash(root,file)
		# Insert a row of data
		c.execute("INSERT INTO hash_table VALUES (?,?)", (m, os.path.join(root, file)))

		line = '{:s} {:s}'.format(m, os.path.join(root,file))
		hashtxtfd.write(line+"\n")
		uniprint (line) #print(line, end='') 
		
save_db_and_txt()

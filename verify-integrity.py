#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""
Date: 26 June 2019
 
@author: V V N Priyanka

Usage:
	verif-integrity.py -h -d <sqlite3 db> -f <files folder>

Description:
	Check the integrity of the files against a reference hash database (sqlite3).
	Procedure:
	  1. For each record in the sqlite3 db, get the <sha256> and <file path>
	  2. Calculate sha256 of the corresponding file from the <files folder>
	  3. Verify that both sha256's match
	  4. Generate statistics and error report (if any)

The Database used here should be created by the command 'dirhash.py'

"""
import os
import re
import sys
import time
import getopt
import hashlib
import sqlite3

OUT_DIR_PREFIX = "out_dir_"
db = ""
fldr = ""
BLOCK_SIZE =  2**20 # For calculating sha256

# log file created inside out_dir_ 
log_file = "log.txt"
log_fd = ""

# Every sqlite db contains the following string as first 16 characters. (\x00 is null byte)
SQLite_MAGIC_STRING = b"SQLite format 3\x00"

########################################################################################################
# Check whether a given file a SQL Database file                                                       #
# A SQL Database file starts with the 16-byte string: "SQLite format 3\x00" (here \x00 is a null byte) #
########################################################################################################
def check_sql_db(dbfile):
  f = open(dbfile, "rb")
  magic = f.read(16)
  if (magic == SQLite_MAGIC_STRING):
    return True
  else:
    return False

########################################################
# Print the string to stdout and write to log.txt file #
########################################################
def print_and_log(*s):
  global log_fd
  for i in s:
    print(i, end='', sep='')
    log_fd.write(str(i))	

########################################################
# Print the string to stdout and write to log.txt file #
# Same as print_and_log, except that it will print a   #
# new line after all args are printed. This will avoid #
# passing "\n" for every print_and_log call            #
########################################################
def print_and_log_n(*s):
  global log_fd
  for i in s:
    print(i, end='', sep='')
    log_fd.write(str(i))	
  print("")
  log_fd.write("\n")
	
############################
# Get command line options #
############################
def get_opts():
    global db, fldr
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:f:h", [])
    except getopt.GetoptError as err:
        # print help information and exit:"
        print(err)  # will print something like "option -a not recognized"
        usage()
		
    for o, a in opts:
        if o == "-d":
            db = a
        elif o == "-f":
            fldr = a
        elif o == "-h":
          usage() 
        else:
            assert False, "unhandled option"

    if (db == ""):
      print_and_log_n("Database file not specified")
      usage()

    if (fldr == ""):
      print_and_log_n("Files folder not specified")
      usage()

    if not os.path.isdir(fldr):
      print_and_log_n("Not a directory: ", fldr)
      usage()

    if not os.path.isfile(db):
      print_and_log_n("Not a file: ", db)
      usage()

    if not check_sql_db(db):
      print_and_log_n("Not an sqlite3 database file: ", db)
      usage()

#################  
# Display Usage #
#################
def usage():
    print("Usage: " + os.path.basename(sys.argv[0]) + " -d <sqlite3 db> -f <files folder>")
    sys.exit(2)	

#########################
# Find sha256 of a file #
#########################
def find_sha256(filepath):
  hash_func = getattr(hashlib, 'sha256')
  m = hash_func()
  with open(filepath, "rb" ) as f:
    while True:
      buf = f.read(BLOCK_SIZE)
      if not buf:
        break
      m.update(buf)
  return m.hexdigest()  

########
# MAIN #
########
out_dir = OUT_DIR_PREFIX + str(time.time())
os.mkdir(out_dir)

log_fd = open (os.path.join(out_dir,log_file), "w")
get_opts()	

# Create a temp db
con = sqlite3.connect("")
cur = con.cursor()

# Attach the new db
cur.execute("ATTACH " + '"' + db + '"' + " AS db;")

sql_stmt = '''SELECT sha256, path FROM db.hash_table;'''  
cur.execute(sql_stmt)


rowcount = 0
hash_match_count = 0
hash_fail_count = 0
row = cur.fetchone()
while row:
  rowcount = rowcount + 1

  sha256_from_db = row[0]
  file_path = row[1]
  file_full_path = os.path.join(fldr, file_path)

  sha256_of_file = find_sha256(file_full_path)

  print_and_log_n("{:0>4}:".format(rowcount))
  print_and_log_n("File: ", file_full_path)
  print_and_log_n("SHA256 as in DB: ", sha256_from_db)
  print_and_log_n("SHA256 computed: ", sha256_of_file)

  if (sha256_from_db == sha256_of_file):
    print_and_log_n("SHA256 Match OK")
    hash_match_count = hash_match_count + 1
  else:
    print_and_log_n("***SHA256 MATCH FAILED ***")
    hash_fail_count = hash_fail_count + 1

  print_and_log_n("")
  row = cur.fetchone()

print_and_log_n("Satatistics:\n")
print_and_log_n("Number of files processed: ", rowcount)
print_and_log_n("Number of hash matches: ", hash_match_count) 
print_and_log_n("Number of hash fails: ", hash_fail_count)
if (hash_fail_count):
  print_and_log_n("***** Folder Integerity Check FAILED *****")
  print_and_log_n("Number of CORRUPT files: ", hash_fail_count)
else:
  print_and_log_n("***** All Files verified OK *****")


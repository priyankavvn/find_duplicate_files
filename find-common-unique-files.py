#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""
Date: 26 June 2019

@author: V V N Priyanka

File: 
	find-common-unique-files.py


Usage:
	find-common-unique-files.py [-h] db1 db2

Description:
	Find common and unique files between db1 and db2

Input:
	db1 and db2

Output:
        All output files are created in an output directory, whose name is out_dir_time, for example: out_dir_1560158423.1453307
	The following files are generated:
		unique_to_<db1>.txt
		unique_to_<db2>.txt
		common_to_<db1>_and_<db2>.txt

"""

import os
import sys
import sqlite3		# for creating sqlite3 database of md5, sha1, etc. hashes
import getopt		# command line option processing
import time		# used for creating an output dir with a unique name using time.time() which returns float representig the current time
import re

OUT_DIR_PREFIX = "out_dir_"

db1 = ''
db2 = ''
log_file = "log.txt"
log_fd = ''

# Every sqlite db contains the following string as first 16 characters. (Note: \x00 is null byte)
SQLite_MAGIC_STRING = b"SQLite format 3\x00"

########################################################
# Print the string to stdout and write to log.txt file #
########################################################
def print_and_log(*s):
  global log_fd
  for i in s:
    print(i,end='')
    log_fd.write(str(i))
  print("")
  log_fd.write("\n")

############################
# Get command line options #
############################
def get_opts():
    global db1, db2
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", [])
    except getopt.GetoptError as err:
        # print help information and exit:"
        print(err)  # will print something like "option -a not recognized"
        usage()
		
    for o, a in opts:
      if o == "-h":
        usage()
      else:
        assert False, "unhandled option"

    if len(args) != 2:
      usage()

    db1 = args[0]
    db2 = args[1]

    if not os.path.isfile (db1):
      print_and_log("No such file: ", db1)
      usage()

    if not os.path.isfile (db2):
      print_and_log("No such file: ", db2)
      usage()
     
    if not check_sql_db(db1):
      print_and_log("Not a sqlite3 db file: ", db1)
      usage()

    if not check_sql_db(db2):
      print_and_log("Not a sqlite3 db file: ", db2)
      usage()

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

#################  
# Display Usage #
#################
def usage():
    print("Usage: " + os.path.basename(sys.argv[0]) + " [-h] db1 db2")
    sys.exit(2)		

###############################
# Files common to db1 and db2 #
###############################
def common_to_db1_db2(outfile):
  sql_stmt = '''SELECT sha256, path FROM db1.hash_table 
             WHERE sha256 IN 
             (SELECT sha256 FROM db2.hash_table);'''
  cur.execute(sql_stmt)
  fl = open(out_dir + "/" + outfile, "w")

  count = 0
  row = cur.fetchone()
  while row:
    line = row[0]+'|'+row[1]+'\n'
    fl.write(line)
    row = cur.fetchone()
    count = count + 1
  fl.close()
  print_and_log("Generated '" + outfile + "'. Number of files:", count)

###############################################################
# Files unique to db1 (that is, files in db1, but not in db2) #
###############################################################
def unique_to_db1(outfile):
  sql_stmt = '''SELECT sha256, path FROM db1.hash_table 
             WHERE sha256 NOT IN 
             (SELECT sha256 FROM db2.hash_table);'''
  cur.execute(sql_stmt)
  fl = open(out_dir + "/" + outfile, "w")

  count = 0
  row = cur.fetchone()
  while row:
    line = row[0]+'|'+row[1]+'\n'
    fl.write(line)
    row = cur.fetchone()
    count = count + 1
  fl.close()
  print_and_log("Generated '" + outfile + "'. Number of files:", count)

###############################################################
# Files unique to db2 (that is, files in db2, but not in db1) #
###############################################################
def unique_to_db2(outfile):
  sql_stmt = '''SELECT sha256, path FROM db2.hash_table 
             WHERE sha256 NOT IN 
             (SELECT sha256 FROM db1.hash_table);'''
  cur.execute(sql_stmt)
  fl = open(out_dir + "/" + outfile, "w")

  count = 0
  row = cur.fetchone()
  while row:
    line = row[0]+'|'+row[1]+'\n'
    fl.write(line)
    row = cur.fetchone()
    count = count + 1
  fl.close()
  print_and_log("Generated '" + outfile + "'. Number of files:", count)


########
# Main #
########

# Keep all output files in a sigle dir, instead of creating in the current directory
# The name of the output dir is generated by concatening the OUT_DIR_PREFIX with time.time()
# A sample output of time.time() is "1559930379.3724217" (float)
# So a sample output dir name is: out_dir_1559930379.3724217
# The default mode of out dir is 777
out_dir = OUT_DIR_PREFIX + str(time.time())
os.mkdir(out_dir)

# Create a log file in out dir
log_fd = open (os.path.join(out_dir,log_file), "w")

get_opts()


con = sqlite3.connect("")
cur = con.cursor()

# Attach the new db
cur.execute("ATTACH " + '"' + db1 + '"' + " AS db1;")
cur.execute("ATTACH " + '"' + db2 + '"' + " AS db2;")

common_to_db1_db2("common_to_" + db1 + "_and_" + db2 + ".txt")
unique_to_db1("unique_to_" + db1 + ".txt")
unique_to_db2("unique_to_" + db2 + ".txt")

log_fd.close()


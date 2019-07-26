# find_duplicate_files
 Suite of utilities to find duplicate files and also check file integrity.
 
These utilities are written on python use sqlite3 database to compute and store hashes (md5/sha256/...) for each file in a directory tree.
This hash database is, then used, to find duplicate files within a folder or between two folders. Same hash database is also used by verify_integrity.py to verify the integrity of files.

**_dirhash.py_**:  
Recursively traverse a directory and create an sqlite3 database of md5/sha256/etc hashes fo each file

	Usage:
	dirhash.py [-h <hashing algorithm>] -r <root directory> [-d <database file>] [-t <text file>]
		Only <root directory> argument is mandatory
		All other arguments have default values:
			-h defaults to sha256
			-d defaults to <root directory>.db
			-t defaults to <root directory>.txt


**_find-duplicate-files-in-db**_:  
Find duplicate files within hash database. This is equivalent to finding duplicate files within the folder for which the hash database was created.

	Usage:
		find-duplicate-files.py [-h] <hash db>

**_find-duplicates.py**_:  
Find which of the files given on command line are duplicated within the hash database.
	
	Usage:
		find-duplicate-files.py hash-db file1 file2 file3 ...

**_find-common-unique-files.py**_:  
	Find list of common and unique files within the two given hash databases.  
	The output files will be created inside a directory ("out_....") within the current directory.  
	The following files are generated:  
	unique_to_<db1>.txt  
	unique_to_<db2>.txt  
	common_to_<db1>_and_<db2>.txt  

	Usage:
		find-common-unique-files.py [-h] db1 db2

**_verify-integrity.py**_:  
Verify the integrity of files within a folder with respect to the hash database.

	Usage:
		verif-integrity.py -h -d <sqlite3 db> -f <files folder>
	


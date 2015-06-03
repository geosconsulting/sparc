__author__ = 'fabio.lana'

#!python

from time import gmtime, strftime
import subprocess
import os
import glob
import time

# change these as appropriate for your platform/environment :
USER = "postgres"
PASS = "postgres"
HOST = "localhost"

BACKUP_DIR = "e:\\postgresql_backups\\"
dumper = """ "c:\\program files\\postgresql\\8.1\\bin\\pg_dump" -U %s -Z 9 -f %s -F c %s  """

def log(string):
    print time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime()) + ": " + str(string)

# Change the value in brackets to keep more/fewer files. time.time() returns seconds since 1970...
# currently set to 2 days ago from when this script starts to run.

x_days_ago = time.time() - ( 60 * 60 * 24 * 2 )

os.putenv('PGPASSWORD', PASS)

database_list = subprocess.Popen('echo "select datname from pg_database" | psql -t -U %s -h %s template1' % (USER,HOST) , shell=True, stdout=subprocess.PIPE).stdout.readlines()

# Delete old backup files first.
for database_name in database_list :
    database_name = database_name.strip()
    if database_name == '':
        continue

    glob_list = glob.glob(BACKUP_DIR + database_name + '*' + '.pgdump')
    for file in glob_list:
        file_info = os.stat(file)
        if file_info.st_ctime < x_days_ago:
            log("Unlink: %s" % file)
            os.unlink(file)
        else:
            log("Keeping : %s" % file)

log("Backup files older than %s deleted." % time.strftime('%c', time.gmtime(x_days_ago)))

# Now perform the backup.
for database_name in database_list :
    log("dump started for %s" % database_name)
    thetime = str(strftime("%Y-%m-%d-%H-%M"))
    file_name = database_name + '_' + thetime + ".sql.pgdump"
    #Run the pg_dump command to the right directory
    command = dumper % (USER,  BACKUP_DIR + file_name, database_name)
    log(command)
    subprocess.call(command,shell = True)
    log("%s dump finished" % database_name)

log("Backup job complete.")

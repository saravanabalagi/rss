#!/bin/sh
USERNAME="student"
PASSWORD="password"
SERVER="Gallinula"
# Directory where file is located
DIR="."
#  Filename of backup file to be transfered
FILE_1="toddler.py"
FILE_2="line.py"
FILE_3="find_satellite.py"
FILE_4="image_operations.py"
# login to ftp server and transfer file
cd $DIR
ftp -n -i $SERVER <<EOF
user $USERNAME $PASSWORD
binary
mput $FILE_1
mput $FILE_2
mput $FILE_3
mput $FILE_4
quit
EOF
# End of script

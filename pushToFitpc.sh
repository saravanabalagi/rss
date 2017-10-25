#!/bin/sh
USERNAME="student"
PASSWORD="password"
SERVER="Hypena"
# Directory where file is located
DIR="."
#  Filename of backup file to be transfered
FILE="toddler.py"
FILE_2="line.py"
# login to ftp server and transfer file
cd $DIR
ftp -n -i $SERVER <<EOF
user $USERNAME $PASSWORD
binary
mput $FILE
mput $FILE_2
quit
EOF
# End of script

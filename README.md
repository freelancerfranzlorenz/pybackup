# pybackup
An easy python backup script

# Requirements
The script is written and tested with python3 on windows 10.
The script does not need any additional python packages.

# Usage

## Step 1: Get the script
First of all, clone the file backup.py to your local computer.

## Step 2: Create config file
- Open a console application in the folder of backup.py
- Type in: python backup.py init
- After the script executed, a new file backup.conf will be created on the current folder

## Step 3: Edit & Save configuration file
IMPORTANT NOTE: Please use only slashes '/' and NO backslashes '\' for path/filenames.
The script does automatically changes it into the native format - if needed.

The config file is structured in sections and keys.
Sections are clasped by square brackets.
Keys are only words followed by an equal sign and a value or string.

The backup config file, has the following sections and keys:

|section|Keys|Description|
|-------|----|-----------|
|[Backup]|drive|Character of the drive, where the backup files are stored|
|[Include]|directory|One or more directories/folders, which should be backuped|
|[Exclude]|directory|One or more directories/folders, which should be excluded from the backup|
|[Exclude]|foldername|One or more foldernames, which should be excluded from the backup|
|[Prebackup]|cmdexec|executable command line commands, which will be executed BEFORE the backup starts|

NOTE: The delimiter between directories/folders is a semicolon ';'

## Step 4: Start the backup
- Open a console application in the folder of backup.py
- Type in: python backup.py backup

# Appendix
Example of a backup.config file:

```
[Backup]
drive = E

[Include]
directory = d:/

[Exclude]
directory = d:/programs;d:/github
foldername = .git;.vscode

[Prebackup]
cmdexec = del d:/gnucash/*.log
   del d:/gnucash/MyAccount.gnucash.*.gnucash
   del d:/temp/*.tmp
```

"""
Backup-script
https://docs.python.org/3/library/argparse.html
https://docs.python.org/3/library/configparser.html
"""
#-----------------------------------------------------------
# IMPORT
import os
import sys
from datetime import datetime
import argparse
import configparser
import shutil

#-----------------------------------------------------------
# CLASS
class ConsoleLine :
  nLineLen = 0
  nCols = 80
  nCols2 = 38
  fLogFile = None
  
  def __init__( self ) :
    Size = os.get_terminal_size()
    self.nCols = int( Size.columns )-4
    self.nCols2 =  int( self.nCols/2 )-4

  def setLogFile( self, sFilename ) :
    try :
      self.fLogFile = open( sFilename, "at", encoding="utf-8" )
      sDateTime = datetime.today().strftime( "%Y-%m-%d %H:%M:%S" )
      self.fLogFile.write( "\n" )
      self.fLogFile.write( "-"*60 )
      self.fLogFile.write( "\n" )
      self.fLogFile.write( "backup log of "+sDateTime+"\n" )
    except :
      self.fLogFile = None
    return

  def _limit( self, sLine ) :
    if len( sLine ) > self.nCols :
      sRet  = sLine[1:self.nCols2]
      sRet += "..."
      sRet += sLine[-self.nCols2:]
      sLine = sRet
    return sLine

  def print( self, sLine, bWriteToLog=True ) :
    if bWriteToLog :
      if self.fLogFile is not None :
        self.fLogFile.write( sLine + "\n" )
      if self.nLineLen > 0 :
        print( "" )
        self.nLineLen = 0
    print( self._limit( sLine ) )
    return

  def overwrite( self, sLine, bWriteToLog=True ) :
    if bWriteToLog :
      if self.fLogFile is not None :
          self.fLogFile.write( sLine + "\n" )
    sLine = self._limit( sLine )
    if self.nLineLen > 0 :
      print( "\b"*self.nLineLen, end='' )
      print( " "*self.nLineLen, end='' )
      print( "\b"*self.nLineLen, end='' )
    print( sLine, end='\r' )
    self.nLineLen = len( sLine )
    return

  def __del__( self ) :
    if self.fLogFile is not None :
      self.fLogFile.close()
    return
# end-of-class


class Console( ConsoleLine ):
    bLog = True
    bInf = True

    def log( self, sLine ) :
        self.print( "log : "+sLine, False )
        return

    def log_o( self, sLine ) :
        self.overwrite( "log : "+sLine, False )
        return

    def info( self, sLine ) :
        self.print( "info : "+sLine )
        return

    def error( self, sLine, nExitCode=1 ) :
        self.print( "error : "+sLine )
# end-of-class

#-----------------------------------------------------------
# CLASS
class BackupScan( Console ) :

    # list of all scanned directories
    lDirs = []
    # list of all scanned files
    lFiles = []
    # exclude directories
    lExcludeDirs = []
    # exclude dirnames
    lExcludeDirName = []
    #

    def __init__( self, classConsole ) :
        self.Out = classConsole
        return

    def setExcludeDirs( self, sDirList ) :
        bRet = False
        lDirs = sDirList.split( ";" )
        if len( lDirs ) > 0 :
            for sDir in lDirs :
                sDir = sDir.lower().strip()
                if len( sDir ) > 0 :
                    self.lExcludeDirs.append( sDir )
            bRet = True
        return bRet

    def setExcludeDirNames( self, sDirNames ) :
        bRet = False
        lDirs = sDirNames.split( ";" )
        if len( lDirs ) > 0 :
            for sDir in lDirs :
                sDir = sDir.lower().strip()
                if len( sDir ) > 0 :
                    self.lExcludeDirName.append( sDir )
            bRet = True
        return bRet

    def scanDir( self, sFolder ) :
        try :
            Entries = os.scandir( sFolder )
            for Entry in Entries :
                sItem = Entry.path.replace( "\\", "/" )
                sCurrDir = sItem.split( "/" ).pop()
                if Entry.is_dir() :
                    if "$" not in Entry.name :
                        if sItem.lower() in self.lExcludeDirs :
                            self.Out.log_o( "exclude dir '"+sItem+"'" )
                        elif sCurrDir.lower() in self.lExcludeDirName :
                            self.Out.log_o( "exclude dir '"+sItem+"'" )
                        else :
                            self.Out.log_o( "scan dir '"+sItem+"'" )
                            self.lDirs.append( sItem )
                            self.scanDir( sItem )
                elif Entry.is_file() :
                    nDate = os.stat( sItem ).st_mtime
                    nSize = os.stat( sItem ).st_size
                    self.lFiles.append( sItem )
                    self.lFiles.append( ":"+str( nDate )+":"+str( nSize)+":" )
            Entries.close()
        except :
            pass

    # This function saves all scanned files with their names
    # and additional infos in a file.
    # @param    sBackupFile     full qualified filename
    # @return   bool            True if file was saved, otherwise False
    def save( self, sBackupFile ) :
        bRet = True
        try :
            file = open( sBackupFile , "wt", encoding="utf-8" )
            for sLine in self.lFiles : 
                file.write( sLine+"\n" )
            file.close()
        except :
            bRet = False
        return bRet

    # This function loads a saved file with scanned files
    # and additional infos from an existing file.
    # @param    sBackupFile     full qualified filename
    # @return   bool            True if file was read, otherwise False
    def load( self, sBackupFile ) :
        bRet = True
        try :
            file = open( sBackupFile , "rt", encoding="utf-8" )
            self.lFiles = []
            sLine = file.readline().strip()
            while sLine :
                self.lFiles.append( sLine )
                sLine = file.readline().strip()
            file.close()
        except :
            bRet = False
        return bRet

# end-of-class

#-----------------------------------------------------------
# GLOBALS
Output = Console()
Config = configparser.ConfigParser()
PreviousScan = BackupScan( Output )
CurrentScan  = BackupScan( Output )

#-----------------------------------------------------------
# FUNCTIONS

def configInit() :
    Config = configparser.ConfigParser()
    File = open( "./backup.config", "w" ) 
    Config.add_section( "Backup" )
    Config.set( "Backup", "Drive", "E" )
    Config.add_section( "Exclude" )
    Config.set( "Exclude", "Directory", "d:/programs;d:/CardoOneDrive" )
    Config.set( "Exclude", "Foldername", ".git" )
    Config.add_section( "Include" )
    Config.set( "Include", "Directory", "d:/;C:/Users/Dell/Pictures" )
    Config.write( File )
    File.close()

def configRead( sFilename ) :
    global Config
    Config.read( sFilename )
    return

def checkDrive( sDrive ) :
    if len( sDrive ) == 1 :
        sDrive += ":/"
    return os.path.exists( sDrive )

def scanCurrent( sScanLogFile = "" ) :
    global CurrentScan
    global Config
    CurrentScan.setExcludeDirs( Config["Exclude"]["Directory"] )
    CurrentScan.setExcludeDirNames( Config["Exclude"]["Foldername"] )
    for sScanDir in Config["Include"]["Directory"].split( ";" ) :
        Output.log_o( "scan directory '"+sScanDir+"'" )
        CurrentScan.scanDir( sScanDir )
    if len( sScanLogFile ) > 0 :
        CurrentScan.save( sScanLogFile )
    return

def createBackupFilename( sSrcFilename, sDstDrive ) :
    sSrcDir = os.path.dirname( sSrcFilename )
    sSrcFil = os.path.basename( sSrcFilename )
    sDrive = sSrcDir.split( ":/" )[0]
    sDir   = sSrcDir.split( ":/" )[1]
    sNewDir = sDstDrive+":/drive_"+sDrive
    if len( sDir ) > 0 :
        sNewDir += "/"+sDir
    return { "file":sNewDir+"/"+sSrcFil, "dir":sNewDir } 

def copyFile( sSrcFile, sDstFile, sDstDir ) :
    if not os.path.exists( sDstDir ) :
        os.makedirs( sDstDir )
    try :
        shutil.copy( sSrcFile, sDstFile )
    except :
        Output.info( "copy '"+sSrcFile+"' is not allowed" )

def getBackupDrive() :
    global Config
    return Config["Backup"]["Drive"][0]

def getBackupFilename() :
    return getBackupDrive()+"://backup.files"

def getBackupLogFilename() :
    return getBackupDrive()+"://backup.log"

#   This function does the backup
def runBackup() :
    configRead( Args.config )
    Output.info( "run backup" )
    sDrive = getBackupDrive()
    if checkDrive( sDrive ) :
        Output.info( "backup drive '"+sDrive+"' is available" )
        sFile = getBackupFilename()
        Output.info( "load backup file '"+sFile+"'" )
        PreviousScan.load( sFile )
        Output.info( "scan sources" )
        scanCurrent()
        # now, CurrentScan and PreviousScan have files
        Output.info( "write backup file '"+sFile+"'" )
    else :
        Output.error( "connect backup drive '"+sDrive+"' to your computer and restart script" )
    #
    return

# This function executes the command line commands
# that are set in the config file in section "Prebackup"
# item "cmdexec".
def runPrebackupCmds() :
    global Config
    try :
        lCmds = Config["Prebackup"]["cmdexec"].split( "\n" )
        for sCmd in lCmds :
            sCmd = sCmd.strip()
            if len( sCmd ) > 1 :
                Output.info( "prebackup cmdexec '"+sCmd+"'" )
                sCmd = sCmd.replace( "/", "\\" )
                os.system( sCmd )
        # for
    except :
        pass
    return 

#   This function will run the copy of the files,
#   which are changed or new.
#   NOTE: CurrentScan and PreviousScan must contain
#   files. CurrentScan contains files from the current
#   drive and PreviousScan contains files from the
#   medium, where the files are backuped.
def runBackupCopy() :
    for nIdx in range( 0, len( CurrentScan.lFiles ), 2 ) :      #scan all files on the source media
        #                                                       # then...
        sFile = CurrentScan.lFiles[nIdx+0]                      # get filename from the list
        sInfo = CurrentScan.lFiles[nIdx+1]                      # get fileattributes from the list
        try :
            nFound = PreviousScan.lFiles.index( sFile )         # try to find file on the backup media list
            sPrevInfo = PreviousScan.lFiles[nFound+1]           # get the fileattributes of the file on the backup media list
            if sPrevInfo != sInfo :                             # anything changed of the fileattributes?
                DstFile = createBackupFilename( sFile, Config["Backup"]["Drive"] )
                Output.info( "copy changed file '"+sFile+"' to '"+DstFile["file"]+"'" )
                copyFile( sFile, DstFile["file"], DstFile["dir"] )
            del PreviousScan.lFiles[nFound]                     # delete filename and fileattributes from
            del PreviousScan.lFiles[nFound]                     # the backup media list to speed-up the search/find
            # print( "check info of '"+sFile+"'" )
        except ValueError :                                     # if the file NOT found in the backup media list
            DstFile = createBackupFilename( sFile, Config["Backup"]["Drive"] )
            Output.info( "copy new file '"+sFile+"' to '"+DstFile["file"]+"'" )
            copyFile( sFile, DstFile["file"], DstFile["dir"] )
    return


#-----------------------------------------------------------
# MAIN

# only for debug sys.argv.append( "check" )

Parser = argparse.ArgumentParser()
Parser.add_argument( "-c", "--config", help="configuration file", default="backup.config" )
Parser.add_argument( "command", help="command string", default="quit" )
Args = Parser.parse_args()

if Args.command == "init" :
    Output.setLogFile( getBackupLogFilename() )
    Output.info( "write initial backup configuration file" )
    configInit()
    #
else :
    #
    configRead( Args.config )
    #
    if Args.command == "check" :
        Output.info( "check config settings" )
        sDrive = Config["Backup"]["Drive"]
        Output.info( "check drive '"+sDrive+"' is '"+str( checkDrive( sDrive ) )+"'" )
        sFile = getBackupFilename()
        if os.path.exists( sFile ) :
            Output.info( "check backup file '"+sFile+"' is available" )
        else :
            Output.info( "backup file '"+sFile+"' not created." )
            Output.info( " call script with command 'firstbackup' to get this file." )
        #
    elif Args.command == "scanonly" :
        Output.info( "scan only the sources" )
        scanCurrent( "" )
        #
    elif Args.command == "firstbackup" :
        Output.info( "scan all files" )
        sDrive = getBackupDrive()
        if checkDrive( sDrive ) :
            Output.setLogFile( getBackupLogFilename() )
            Output.info( "backup drive '"+sDrive+"' is available" )
            runPrebackupCmds()
            sFile = getBackupFilename()
            scanCurrent( sFile )
            Output.info( "write backup file '"+sFile+"'" )
        else :
            Output.error( "connect backup drive '"+sDrive+"' to your computer and restart script" )
        #
    elif Args.command == "backup" :
        Output.info( "start backup..." )
        sDrive = getBackupDrive()
        if checkDrive( sDrive ) :
            Output.info( "backup drive '"+sDrive+"' is available" )
            Output.setLogFile( getBackupLogFilename() )
            runPrebackupCmds()
            sFile = getBackupFilename()
            Output.info( "load backup file '"+sFile+"'" )
            PreviousScan.load( sFile )
            Output.info( "scan sources" )
            scanCurrent()
            # CurrentScan.save( "d://test.backup.files" )
            runBackupCopy()
            Output.info( "write backup file '"+sFile+"'" )
            CurrentScan.save( getBackupFilename() )
            Output.info( "backup finished" )
        else :
            Output.error( "connect backup drive '"+sDrive+"' to your computer and restart script" )
        #
    else :
        Output.error( "command '"+Args.command+"' unknown" )

del Output

#!/usr/bin/python

import sys
import getopt
import signal
#import traceback
from datetime import datetime
from os import getpid

from HerokuAutoscale import HerokuAutoscale
from logger import Logger
from pyUnixDaemon import pyUnixDaemon

def singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


@singleton
class HerokuAutoscaleDeamon(pyUnixDaemon):    
    def __init__(self, options):
        self._uid = options['uid']
        self._gid = options['gid']
        self._lockpidfile = options['lockpidfile']
        self._outputfile = options['outputfile']
        self._errorfile = options['errorfile']
        self._configfile = options['configfile']
        self._status_file = options['status_file']
        pyUnixDaemon.__init__(self, self._lockpidfile, (self._uid, self._gid))
        self.setOutput(Logger(self._outputfile), Logger(self._errorfile))
        self._oldTime = datetime.now()
        self.processes = []
        
    def _run(self):
        self._app_pid = getpid()
        print "** Starting Heroku Autoscale daemon... PID: {0} **".format(self._app_pid)
        
        # Catch the SIGHUP signal
        # This signal will be used to reload the configuration file
        signal.signal(signal.SIGHUP, self.reloadConfiguration)
        try:
            #self._oldTime = datetime(1970, 1, 1, 0, 0)
            #print "** Parsing conf file : {0} **".format(self._configfile)
            #self._backupSet = parser.parse(self._configfile)
            #elf._mainLoop()
            #server = Server(("", 8080))
            #server.serve_forever()
            ha = HerokuAutoscale(self._configfile)
            ha.autoscale_forever()
            
        #except ValueError:
        #    print >> sys.stderr, traceback.format_exc()
        #    print >> sys.stderr, "Error in timing description. Stopping daemon..."
        #    return
        finally:
            if getpid() == self._app_pid:
                print "** Stoping Heroku Autoscale daemon... PID: {0} **".format(getpid())
            
    
    def reloadConfiguration(self, sig=None, frame=None):
        """Reload the configuration."""
        #parser.parse(self._backupSet._configPath, self._backupSet)

def processArgs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:g:o:e:c:s:", ["help", "uid=", "gid=", "outputfile=", "errorfile=", "config=", "lockpidfile=", "status-file="])
    except getopt.GetoptError, err:
        print >> sys.stderr, "%s" % (str(err))
        usage()
        sys.exit(2)
    
    options = {
        'uid': 0,
        'gid': 0,
        'lockpidfile': '/var/run/heroku-autoscale.pid',
        'outputfile': '/var/log/heroku-autoscale.log',
        'errorfile': '/var/log/heroku-autoscale_error.log',
        'configfile': '/etc/heroku-autoscale/config.ini',
        'status_file': '/tmp/heroku-autoscale.status',
    }
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-u", "--uid"):
            options['uid'] = int(a)
        elif o in ("-g", "--gid"):
            options['gid'] = int(a)
        elif o in ("-o", "--outputfile"):
            options['outputfile'] = a
        elif o in ("-e", "--errorfile"):
            options['errorfile'] = a
        elif o in ("-c", "--config"):
            options['configfile'] = a
        elif o == "--lockpidfile":
            options['lockpidfile'] = a
        elif o in ("-s", "--status-file"):
            options['status_file'] = a
        else:
            print >> sys.stderr, "Unhandled option : \"%s\"" % (o)
    return options

def usage():
    print """
    Usage: HerokuAutoscaleDeamon [OPTIONS]
         -h, --help                          Display this usage message
         -u, --uid=userid                    User id to bind daemon to (default: 1002).
         -g, --gid=groupid                   Group id to bind daemon to (default: 1002).
         -o, --outputfile=path_to_log        Path to log file (default: "/var/run/heroku-autoscale.log")
         -e, --errorfile=path_to_error_log   Path to error log file (default: "/var/log/heroku-autoscale_error.log")
         -c, --config=config_file            Path to config file (default: "/etc/heroku-autoscale/config.ini")
         --lockpidfile=groupid               Lock file (PID) of daemon (default: "/var/run/heroku-autoscale.pid")
    """

if __name__ == "__main__":
    options = processArgs()
    daemon = HerokuAutoscaleDeamon(options)
    daemon.launch()

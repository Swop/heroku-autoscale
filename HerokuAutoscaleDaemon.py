#!/usr/bin/python

"""This module define the HerokuAutoscaleDaemon class 
"""

import sys
import getopt
import signal
from datetime import datetime
from os import getpid

from HerokuAutoscale import HerokuAutoscale
from logger import Logger
from pyUnixDaemon import pyUnixDaemon

def singleton(cls):
    """Return a singleton of the HerokuAutoscaleDaemon class
    """
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


@singleton
class HerokuAutoscaleDaemon(pyUnixDaemon):
    """The Heroku Autoscale engine's daemon
    This class manage the launch and the stop of the daemon.
    """    
    def __init__(self, options):
        """Initilaize the daemon.
        
        Argument:
        - options : a dictionary composed with these required elements:
            - uid: the linux UID used by the daemon
            - gid: the linux GID used by the daemon
            - lockpidfile: the PID lock file path to store the PID of the running daemon
            - outputfile: the info log file path to use
            - errorfile: the error log file path to use
            - configfile: the config file to use to tweek the engine's behaviour (see the HAConf class)
            - status_file: (Currently unused) the status file to use to store some info about the running daemon
        """
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
        """Start the daemon
        
        The demon will start the HerokuAutoscale engine's mail loop
        """
        self._app_pid = getpid()
        print "** Starting Heroku Autoscale daemon... PID: {0} **".format(self._app_pid)
        
        # Catch the SIGHUP signal
        # This signal will be used to reload the configuration file
        signal.signal(signal.SIGHUP, self.reloadConfiguration)
        try:
            ha = HerokuAutoscale(self._configfile)
            ha.autoscale_forever()
        finally:
            if getpid() == self._app_pid:
                print "** Stoping Heroku Autoscale daemon... PID: {0} **".format(getpid())
            
    
    def reloadConfiguration(self, sig=None, frame=None):
        """Reload the configuration."""
        #TODO
        pass

def processArgs():
    """Process the input CLI args"""
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
    """Print the usage of the daemon CLI launcher"""
     
    print """
    Usage: HerokuAutoscaleDaemon [OPTIONS]
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
    daemon = HerokuAutoscaleDaemon(options)
    daemon.launch()

#!/usr/bin/python
# AVERTISSEMENTS:
# Cette classe ne peut en aucun cas etre utilise a des fins lucratives
# (sauf autorisation ecrite).
# Je me degage de toute responsabilite quant aux consequences liees a
# l'utilisation du contenu de ce fichier.
# Tous droits reserves - Steve MULLER 2007
import signal
import os
import sys

class pyUnixDaemon:
    """ This class implements a UNIX daemon. You can derived from it to build
        your own daemon.
    """
    def __init__(self, lockFilename = "/var/run/pyUnixDaemon.pid", user = (0, 0)):
        """ This method initializes some internal variables and instancies an
            object.
        """
        self._user = user
        self._lockFilename = lockFilename
    def _daemonExists(self):
        """ This method checks if the lock file exists.
        """
        return os.path.exists(self._lockFilename)
    def _lock(self):
        """ This method creates the lock file and write the daemon pid.
        """
        self._lockFile = open(self._lockFilename, "w")
        self._lockFile.write("%d" % (os.getpid()))
        self._lockFile.flush()
    def _unlock(self):
        """ This method closes and removes the lock file.
        """
        self._lockFile.close()
        os.unlink(self._lockFilename)
    def _fork(self):
        """ This method forks the daemon using the unix way.
        """
        if (self._daemonExists()):
            print "[Error] Could not be daemonized: already in memory"
            sys.exit(1)
        try:
            pid = os.fork()
            if (pid > 0):
                sys.exit(0)
        except OSError, e:
            print "[Error] Fork #1 failed: %s (%d)" % (e.strerror, e.errno)
            sys.exit(1)
        os.chdir("/")
        os.setsid()
        os.umask(0)
        try:
            pid = os.fork()
            if (pid > 0):
                sys.exit(0)
        except OSError, e:
            print "[Error] Fork #2 failed: %s (%d)" % (e.strerror, e.errno)
            sys.exit(1)
    def _run(self):
        """ This method must be derivated to do something.
        """
        while(self._loop):
            pass
    def __signalHandler(self, signalNumber, frame):
        """ This method sets an internal flag that permits to break the forever
            loop.
        """
        self._loop = False
    def setOutput(self, output, error = None):
        """ This method redirects stdout and stderr flows.
        """
        self._stdout = sys.stdout
        self._output = output
        self._stderr = sys.stderr
        if (error is not None):
            self._error = error
        else:
            self._error = output
    def launch(self):
        """ This method prepares all required actions before lauching the background method '_run'.
        """
        self._fork()
        self._lock()
        os.setegid(self._user[1])
        os.seteuid(self._user[0])
        self._loop = True
        signal.signal(signal.SIGTERM, self.__signalHandler)
        sys.stdout = self._output
        sys.stderr = self._error
        self._run()
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        os.setegid(0)
        os.seteuid(0)
        self._unlock()

"""
EXEMPLE

if (__name__ == "__main__"):
    from datetime import datetime
    from os import getpid
    from time import sleep
    import sys

    class pyTest(pyUnixDaemon):
        def __init__(self, lockFilename):
            pyUnixDaemon.__init__(self, lockFilename)
        def _run(self):
            while(self._loop):
                print "%s - %s" % (datetime.now(), getpid())
                sys.stdout.flush()
                sleep(5)

    daemon = pyTest("/var/run/pyTest.pid")
    daemon.setOutput(open("/var/log/pyTest.log", "a"))
    daemon.launch()
"""

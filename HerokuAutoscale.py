"""
Define the Main class of the Heroku Autoscale engine.
By Sylvain MAUDUIT (Swop)
"""

from __future__ import print_function

import heroku
import signal, sys, time
from Plot import Plot
from HAConfigParser import HAConfigParser
from pingdom.pingdomapi import PingdomAPIWrapper
from datetime import datetime, timedelta
from measurementtools import *

def log(msg):
    """Log something into the logger "info" channel
    
    Argument:
    - msg: Message to log
    """
    print(msg)
    sys.stdout.flush()
    
def logerr(msg):
    """Log something into the logger "error" channel
    
    Argument:
    - msg: Message to log
    """
    print(msg, file=sys.stderr)
    sys.stderr.flush()

class HerokuAutoscale:
    """Main class of the Heroku Autoscale engine. Manage the dyno scaling during time.
    
    Parse the config file and manage the number of dynos through time with regular checks using Pingdom API.
    """
    def __init__(self, config_file = "config.ini"):
        """Initialise the daemon with the given config file.
        
        Argument:
        - config_file: (optional, default = "config.ini") The configuration file to use.
        """
        self._conf = HAConfigParser.loadConf(config_file)
        self._pd_wrapper = PingdomAPIWrapper(self._conf.getPingdomAPIKey(),
                                             self._conf.getPingdomLogin(),
                                             self._conf.getPingdomPassword())
        
        hrk_cloud = heroku.from_key(self._conf.getHerokuAPIKey())
        self._heroku_app = hrk_cloud.apps[self._conf.getHerokuAppName()]
    
    def autoscale(self):
        """Autoscale now the Heroku App.
        
        This method gonna check the response time through Pingdom API, and adapt the number of dynos according to it.
        If the measured response time is below the response time low score defined in the HAConf object, the Heroku app will be scaled up.
        If the measured response time is over the response time high score defined in the HAConf object, the Heroku app will be scaled down.
        
        If the measured response time is between the response time low score and the response time high score :
        - If the tendency of the response times is strongly rising:  the Heroku app will be scaled up
        - If the tendency of the response times is strongly down:  the Heroku app will be scaled down
        """
        self._log("----> Start autoscale...")
        end = datetime.utcnow()
        end_time = int(time.mktime(end.timetuple()))
        begin = end - timedelta(minutes = self._conf.getPingdomCheckPeriod())
        begin_time =  int(time.mktime(begin.timetuple()))
        self._log("Pingdom period to request: Begin: {0}, End: {1}".format(begin.isoformat(), end.isoformat()))
        checks = self._pd_wrapper.getChecks(self._conf.getPingdomCheckId(), begin_time, end_time)
        
        rep_time_avg = getResponseTimeAvg(checks)
        self._log("Avg resp time: {0}".format(rep_time_avg))
        
        t = datetime.now()
        
        reg_coef = computeLinearRegressionModel(checks)
        self._log("Linear regression: y' = a * x + b with a = {0}, b = {1}".format(reg_coef[0], reg_coef[1]))
        
        if(rep_time_avg < self._conf.getResponseTimeLow()):
            if(reg_coef[0] < 0):
                self._removeDyno()
                settlement = "Revove dyno"
            else:
                self._log("===> Do nothing...")
                settlement = "Do nothing"
        elif(rep_time_avg >= self._conf.getResponseTimeLow() and 
             rep_time_avg < self._conf.getResponseTimeHigh()):
            
            if(reg_coef[0] > self._conf.getResponseTimeTrendHigh()):
                self._addDyno()
                settlement = "Add dyno"
            elif(reg_coef[0] < self._conf.getResponseTimeTrendLow()):
                self._removeDyno()
                settlement = "Revove dyno"
            else:
                self._log("===> Do nothing...")
                settlement = "Do nothing"
        else:
            if(reg_coef[0] > 0):
                self._addDyno()
                settlement = "Add dyno"
            else:
                self._log("===> Do nothing...")
                settlement = "Do nothing"
        
        if(self._conf.isPlotting()):
            Plot.plot(checks, rep_time_avg, reg_coef, self._conf.getResponseTimeLow(), self._conf.getResponseTimeHigh(), settlement, self._conf.getGraphsFolder() + '/' + t.strftime("%d-%m-%Y_%H-%M-%S") + "_out.pdf", "pdf")
            
    def autoscale_forever(self):
        """Start the infinite loop to automatically scale the Heroku app.
        
        The Heroku app will be scaled according to the response time, every time defined by the check frequency inside the HAConf object. 
        """
        self._register_signal(signal.SIGHUP)
        self._register_signal(signal.SIGINT)
        self._register_signal(signal.SIGTERM)
        
        self._log("Check frequency: %s" % str(int(self._conf.getCheckFrequency()) * 60))
        while(True):
            self.autoscale()
            time.sleep(self._conf.getCheckFrequency() * 60)
            
    def _register_signal(self, signum):
        """Register a system SIG number to catch in the program
        """
        signal.signal(signum, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle a system signal to shutdown properly the daemon 
        """
        logerr("Caught signal {0}. Shutdown server...".format(signum))
        raise SystemExit()
            
    def _addDyno(self, count=1):
        """Scale up the Heroku app
        
        Argument:
        - count: (optional, default = 1) Number of dynos to add
        """
        self._log("===>  Add {0} dyno(s)".format(count))
        current_dynos = self._getCurrentDynos()
        self._log("===> Current dynos: {0}".format(current_dynos))
        new_scale = current_dynos + count
        if(new_scale > self._conf.getMaxDynos()):
            self._log("===> New scale ({0}) > Max dyno ({1}) --> New scale = {1}".format(new_scale, self._conf.getMaxDynos()))
            new_scale = self._conf.getMaxDynos()
        
        if(new_scale != current_dynos):
            self._log("====> New scale ({0}) != current dyno ({1}) --> Scale to New scale ({0})".format(new_scale, current_dynos))
            if(not self._conf.isInDebugMode()):
                self._heroku_app.processes['web'].scale(new_scale)
            return
        self._log("===> Do nothing...")
        
    def _removeDyno(self, count=1):
        """Scale down the Heroku app
        
        Argument:
        - count: (optional, default = 1) Number of dynos to remove
        """
        self._log("===>  Remove {0} dyno(s)".format(count))
        current_dynos = self._getCurrentDynos()
        self._log("===> Current dynos: {0}".format(current_dynos))
        new_scale = current_dynos - count
        if(new_scale < self._conf.getMinDynos()):
            self._log("===> New scale ({0}) < Min dyno ({1}) --> New scale = {1}".format(new_scale, self._conf.getMinDynos()))
            new_scale = self._conf.getMinDynos()
        
        if(new_scale != current_dynos):
            self._log("===> New scale ({0}) != current syno ({1}) --> Scale to New scale ({0})".format(new_scale, current_dynos))
            if(not self._conf.isInDebugMode()):
                self._heroku_app.processes['web'].scale(new_scale)
            return
        self._log("===> Do nothing...")
    
    def _getCurrentDynos(self):
        """Return the current Heroku app dyno number
        """
        web_proc = self._heroku_app.processes['web']
        cpt = 0
        for proc in web_proc:
            cpt += 1
        return cpt
    
    def _log(self, msg):
        """Log something into the logger "info" channel
        
        Argument:
        - msg: Message to log
        """
        print(msg)
        sys.stdout.flush()
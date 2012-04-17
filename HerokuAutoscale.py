from __future__ import print_function

import heroku
import signal, sys, time
from HAConfigParser import HAConfigParser
from pingdom.pingdomapi import PingdomAPIWrapper
from datetime import datetime, timedelta

def log(msg):
    """Log something into the logger "info" channel
    """
    print(msg)
    sys.stdout.flush()
    
def logerr(msg):
    """Log something into the logger "error" channel
    """
    print(msg, file=sys.stderr)
    sys.stderr.flush()

class HerokuAutoscale:
    """Main class of the Heroku Atoscale engine. Manage the dyno scaling during time.
    
    Parse the config file and manage the number of dynos through time with regular checks using Pingdom API.
    """
    def __init__(self, config_file = "config.ini"):
        """Initialise the daemon with the given config file.
        
        Argument:
        - config_file: (optional, default = "config.ini") The configuration file to use.
        """
        self._conf = HAConfigParser.loadConf(config_file)
        self._pd_wrapper = PingdomAPIWrapper(self._conf.getPingdomAPIKey(), self._conf.getPingdomCheckId())
        
        hrk_cloud = heroku.from_key(self._conf.getHerokuAPIKey())
        self._heroku_app = hrk_cloud.apps[self._conf.getHerokuAppName()]
    
    def autoscale(self):
        """Autoscale now the Heroku App.
        
        This method gonna check the response time through Pingdom API, and adapt the number of dynos according to it.
        If the measured response time is below the response time low score defined in the HAConf object, the Heroku app will be scaled up.
        If the measured response time is over the response time high score defined in the HAConf object, the Heroku app will be scaled down.
        """
        self._log("Start autoscale...")
        end = datetime.utcnow()
        end_time = int(time.mktime((datetime.now()).timetuple()))
        begin = end - timedelta(minutes = self._conf.getPingdomCheckPeriod())
        begin_time =  int(time.mktime(begin.timetuple()))
        self._log("begin: {0}, end: {1}".format(begin.isoformat(), end.isoformat()))
        checks = self._pd_wrapper.getChecks(self._conf.getPingdomCheckId(), begin_time, end_time)
        
        rep_time_avg = self._getResponseTimeAvg(checks)
        self._log("avg resp time: {0}".format(rep_time_avg))
        rep_time_trend = self._getResponseTimeTrend(checks)
        self._log("resp time trend: {0}".format(rep_time_trend))
        
        if(rep_time_avg < self._conf.getResponseTimeLow()):
            if(rep_time_trend < 0):
                self._removeDyno()
            else:
                self._log("Do nothing...")
        elif(rep_time_avg >= self._conf.getResponseTimeLow() and 
             rep_time_avg < self._conf.getResponseTimeHigh()):
            if(rep_time_trend > self._conf.getResponseTimeTrendHigh()):
                self._addDyno()
            elif(rep_time_trend < self._conf.getResponseTimeTrendLow()):
                self._removeDyno()
            else:
                self._log("Do nothing...")
        else:
            if(rep_time_trend > 0):
                self._addDyno()
            else:
                self._log("Do nothing...")
            
    def autoscale_forever(self):
        """Start the infinite loop to automatically scale the Heroku app.
        
        The Heroku app will be scaled according to the response time, every time defined by the check frequency inside the HAConf object. 
        """
        self._register_signal(signal.SIGHUP)
        self._register_signal(signal.SIGINT)
        self._register_signal(signal.SIGTERM)
        
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
        """
        self._log("Add dyno")
        current_dynos = self._getCurrentDynos()
        self._log("Current dynos: {0}".format(current_dynos))
        new_scale = current_dynos + count
        if(new_scale > self._conf.getMaxDynos()):
            self._log("New scale ({0}) > Max dyno ({1}) --> New scale = {1}".format(new_scale, self._conf.getMaxDynos()))
            new_scale = self._conf.getMaxDynos()
        
        if(new_scale != current_dynos):
            self._log("New scale ({0}) != current syno ({1}) --> Scale to New scale ({0})".format(new_scale, current_dynos))
            #self._heroku_app.processes['web'].scale(current_dynos)
        
    def _removeDyno(self, count=1):
        """Scale down the Heroku app
        """
        self._log("Remove dyno")
        current_dynos = self._getCurrentDynos()
        self._log("Current dynos: {0}".format(current_dynos))
        new_scale = current_dynos - count
        if(new_scale < self._conf.getMinDynos()):
            self._log("New scale ({0}) < Min dyno ({1}) --> New scale = {1}".format(new_scale, self._conf.getMinDynos()))
            new_scale = self._conf.getMinDynos()
        
        if(new_scale != current_dynos):
            self._log("New scale ({0}) != current syno ({1}) --> Scale to New scale ({0})".format(new_scale, current_dynos))
            #self._heroku_app.processes['web'].scale(current_dynos)
            
    def _getResponseTimeAvg(self, checks):
        """Return the average of the response times
        
        Arguments:
        - checks: A dictionary (key: check time) of pingdomcheck.PingdomCheck objects
        """
        times = checks.keys()
        times.sort()
        
        avg = 0
        for time in times:
            check = checks[time]
            avg += check.get_response_time()
        avg /= len(checks.keys)
        return avg
        
    def _getResponseTimeTrend(self, checks):
        """Return the global leading coefficient of the response time graph.
        
        Arguments:
        - checks: A dictionary (key: check time) of pingdomcheck.PingdomCheck objects
        """
        times = checks.keys()
        times.sort()
        
        check_count = len(checks.keys)
        
        global_coef = 0
        for i in range(check_count-1):
            current_check = checks[times[i]]
            next_check = checks[times[i+1]]
            
            global_coef += (next_check.get_response_time() - current_check.get_response_time()) / (next_check.get_time() - current_check.get_time())
        
        return global_coef
    
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
        """
        #print(datetime.now().isoformat(" ")+" "+msg)
        print(msg)
        sys.stdout.flush()
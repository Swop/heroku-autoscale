from __future__ import print_function

import heroku
import signal, sys, time
from HAConfigParser import HAConfigParser
from newrelic.NewRelicAPIWrapper import NewRelicAPIWrapper
from datetime import datetime, timedelta

def log(msg):
    print(msg)
    sys.stdout.flush()
    
def logerr(msg):
    print(msg, file=sys.stderr)
    sys.stderr.flush()

class HerokuAutoscale:

    def __init__(self, config_file = "config.ini"):
        self._conf = HAConfigParser.loadConf(config_file)
        self._nr_wrapper = NewRelicAPIWrapper(self._conf.getNewRelicAPIKey(), self._conf.getNewRelicAccountId(), self._conf.getNewRelicAppId())
        
        hrk_cloud = heroku.from_key(self._conf.getHerokuAPIKey())
        self._heroku_app = hrk_cloud.apps[self._conf.getHerokuAppName()]
    
    def autoscale(self):
        self._log("Start autoscale...")
        end = datetime.utcnow()
        begin = end - timedelta(minutes = self._conf.getCheckFrequency())
        self._log("begin: {0}, end: {1}".format(begin.isoformat(), end.isoformat()))
        apdex_score = self._nr_wrapper.getApdex(begin, end)
        self._log("apdex: {0}".format(apdex_score))
        
        if(apdex_score < self._conf.getApdexLowScore()):
            self._addDyno()
        elif(apdex_score >= self._conf.getApdexLowScore() and apdex_score < self._conf.getApdexHighScore()):
            self._log("Do nothing...")
            pass
        else:
            self._removeDyno()
            
    def autoscale_forever(self):
        self._register_signal(signal.SIGHUP)
        self._register_signal(signal.SIGINT)
        self._register_signal(signal.SIGTERM)
        
        while(True):
            self.autoscale()
            time.sleep(self._conf.getCheckFrequency() * 60)
        
    def _register_signal(self, signum):
        signal.signal(signum, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logerr("Caught signal {0}. Shutdown server...".format(signum))
        raise SystemExit()
            
    def _addDyno(self):
        self._log("Add dyno")
        current_dynos = self._getCurrentDynos()
        self._log("Current dynos: {0}".format(current_dynos))
        new_scale = current_dynos + 1
        if(new_scale > self._conf.getMaxDynos()):
            self._log("New scale ({0}) > Max dyno ({1}) --> New scale = {1}".format(new_scale, self._conf.getMaxDynos()))
            new_scale = self._conf.getMaxDynos()
        
        if(new_scale != current_dynos):
            self._log("New scale ({0}) != current syno ({1}) --> Scale to New scale ({0})".format(new_scale, current_dynos))
            #self._heroku_app.processes['web'].scale(current_dynos)
        
    def _removeDyno(self):
        self._log("Remove dyno")
        current_dynos = self._getCurrentDynos()
        self._log("Current dynos: {0}".format(current_dynos))
        new_scale = current_dynos - 1
        if(new_scale < self._conf.getMinDynos()):
            self._log("New scale ({0}) < Min dyno ({1}) --> New scale = {1}".format(new_scale, self._conf.getMinDynos()))
            new_scale = self._conf.getMinDynos()
        
        if(new_scale != current_dynos):
            self._log("New scale ({0}) != current syno ({1}) --> Scale to New scale ({0})".format(new_scale, current_dynos))
            #self._heroku_app.processes['web'].scale(current_dynos)
    
    def _getCurrentDynos(self):
        web_proc = self._heroku_app.processes['web']
        cpt = 0
        for proc in web_proc:
            cpt += 1
        return cpt
    
    def _log(self, msg):
        #print(datetime.now().isoformat(" ")+" "+msg)
        print(msg)
        sys.stdout.flush()
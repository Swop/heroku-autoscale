from ConfigException import ConfigException

class HAConf:
    
    def __init__(self):
        self._heroku = {'api_key': '',
                       'app_name': ''
        }
        self._newrelic = {'api_key': '',
                          'account_id': '',
                         'app_id': ''
        }
        self._autoscale_settings = {'min_dynos': 1,
                                   'max_dynos': 10,
                                   'apdex_low': 0.5,
                                   'apdex_high': 0.8,
                                   'check_frequency': 5
        }
    
    def setHerokuAPIKey(self, heroku_api_key):
        self._heroku['api_key'] = heroku_api_key
        
    def getHerokuAPIKey(self):
        return self._heroku['api_key']
    
    def setHerokuAppName(self, heroku_app_name):
        self._heroku['app_name'] = heroku_app_name
        
    def getHerokuAppName(self):
        return self._heroku['app_name']
    
    def setNewRelicAPIKey(self, newrelic_api_key):
        self._newrelic['api_key'] = newrelic_api_key
    
    def getNewRelicAPIKey(self):
        return self._newrelic['api_key']
    
    def setNewRelicAccountId(self, newrelic_account_id):
        self._newrelic['account_id'] = newrelic_account_id
    
    def getNewRelicAccountId(self):
        return self._newrelic['account_id']
    
    def setNewRelicAppId(self, newrelic_app_id):
        self._newrelic['app_id'] = newrelic_app_id
        
    def getNewRelicAppId(self):
        return self._newrelic['app_id']
    
    def setMinDynos(self, min_dynos):
        if(min_dynos < 1):
            raise ConfigException("You have to set at least 1 dyno minimum (you indicate {0})".format(min_dynos))
        self._autoscale_settings['min_dynos'] = min_dynos
    
    def getMinDynos(self):
        return self._autoscale_settings['min_dynos']
    
    def setMaxDynos(self, max_dynos):
        self._autoscale_settings['max_dynos'] = max_dynos
        
    def getMaxDynos(self):
        return self._autoscale_settings['max_dynos']
    
    def setApdexLowScore(self, apdex_low_score):
        if(isinstance(apdex_low_score, float) and apdex_low_score >= 0 and apdex_low_score <= 1):
            self._autoscale_settings['apdex_low'] = apdex_low_score
        else:
            raise ConfigException("Apdex low score must be a float value, between 0 and 1 (you indicate {0})".format(apdex_low_score))
    
    def getApdexLowScore(self):
        return self._autoscale_settings['apdex_low']
        
    def setApdexHighScore(self, apdex_high_score):
        if(isinstance(apdex_high_score, float) and apdex_high_score >= 0 and apdex_high_score <= 1):
            self._autoscale_settings['apdex_high'] = apdex_high_score
        else:
            raise ConfigException("Apdex high score must be a float value, between 0 and 1 (you indicate {0})".format(apdex_high_score))
    
    def getApdexHighScore(self):
        return self._autoscale_settings['apdex_high']
    
    def setCheckFrequency(self, check_frequency):
        if(check_frequency < 1):
            raise ConfigException("The check frequency must be at least 1 minute (you indicate {0})".format(check_frequency))
        self._autoscale_settings['check_frequency'] = check_frequency
        
    def getCheckFrequency(self):
        return self._autoscale_settings['check_frequency']
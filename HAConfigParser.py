import ConfigParser
from ConfigException import ConfigException
from HAConf import HAConf

class HAConfigParser:
    
    @staticmethod
    def loadConf(config_file = "config.ini"):
        config = ConfigParser.RawConfigParser()
        config.readfp(open(config_file))
                
        ha_conf = HAConf()
        
        HAConfigParser._loadHerokuConf(config, ha_conf)
        HAConfigParser._loadNewRelicConf(config, ha_conf)
        HAConfigParser._loadAutoscaleSettings(config, ha_conf)
        
        return ha_conf
    
    @staticmethod
    def _loadHerokuConf(config, ha_conf):
        if(not config.has_section('HEROKU_INFOS')):
            raise ConfigException('Config file must have a HEROKU_INFOS section')
        
        if(config.has_option('HEROKU_INFOS', 'api_key')):
            ha_conf.setHerokuAPIKey(config.get('HEROKU_INFOS', 'api_key'))
        else:
            raise ConfigException("You must provide a Heroku API Key (section 'HEROKU_INFOS', key 'api_key')")
        
        if(config.has_option('HEROKU_INFOS', 'app_name')):
            ha_conf.setHerokuAppName(config.get('HEROKU_INFOS', 'app_name'))
        else:
            raise ConfigException("You must provide a Heroku App name (section 'HEROKU_INFOS', key 'app_name')")
        
    @staticmethod
    def _loadNewRelicConf(config, ha_conf):
        if(not config.has_section('NEWRELIC_INFOS')):
            raise ConfigException('Config file must have a NEWRELIC_INFOS section')
        
        if(config.has_option('NEWRELIC_INFOS', 'api_key')):
            ha_conf.setNewRelicAPIKey(config.get('NEWRELIC_INFOS', 'api_key'))
        else:
            raise ConfigException("You must provide a New Relic API Key (section 'NEWRELIC_INFOS', key 'api_key')")
        
        if(config.has_option('NEWRELIC_INFOS', 'account_id')):
            ha_conf.setNewRelicAccountId(config.get('NEWRELIC_INFOS', 'account_id'))
        else:
            raise ConfigException("You must provide a New Relic Account ID (section 'NEWRELIC_INFOS', key 'account_id')")
        
        if(config.has_option('NEWRELIC_INFOS', 'app_id')):
            ha_conf.setNewRelicAppId(config.get('NEWRELIC_INFOS', 'app_id'))
        else:
            raise ConfigException("You must provide a New Relic App ID (section 'NEWRELIC_INFOS', key 'app_id')")
    
    @staticmethod
    def _loadAutoscaleSettings(config, ha_conf):
        if(config.has_section("AUTOSCALE_SETTINGS")):
            if(config.has_option('AUTOSCALE_SETTINGS', 'min_dynos')):
                ha_conf.setMinDynos(config.getint('AUTOSCALE_SETTINGS', 'min_dynos'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'max_dynos')):
                ha_conf.setMaxDynos(config.getint('AUTOSCALE_SETTINGS', 'max_dynos'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'apdex_low')):
                ha_conf.setApdexLowScore(config.getfloat('AUTOSCALE_SETTINGS', 'apdex_low'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'apdex_high')):
                ha_conf.setApdexHighScore(config.getfloat('AUTOSCALE_SETTINGS', 'apdex_high'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'check_frequency')):
                ha_conf.setCheckFrequency(config.getfloat('AUTOSCALE_SETTINGS', 'check_frequency'))
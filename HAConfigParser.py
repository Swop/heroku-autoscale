import ConfigParser
from ConfigException import ConfigException
from HAConf import HAConf

class HAConfigParser:
    """This class is used to parse the config file and create an HAConf object
    
    The HAConf object is created and reflects the parameters used into the config file
    """
    @staticmethod
    def loadConf(config_file = "config.ini"):
        """Load and parse the given config file.
        
        Argument:
        - config_file: (optional, default: config.ini) The config file's path to parse
        
        Return: An HAConf obejct (see HAConf.py)
        """
        config = ConfigParser.RawConfigParser()
        config.readfp(open(config_file))
                
        ha_conf = HAConf()
        
        HAConfigParser._loadHerokuConf(config, ha_conf)
        HAConfigParser._loadPingdomConf(config, ha_conf)
        HAConfigParser._loadAutoscaleSettings(config, ha_conf)
        
        return ha_conf
    
    @staticmethod
    def _loadHerokuConf(config, ha_conf):
        """Load scpecific infos about Heroku settings
        
        Arguments:
        - config: the config file, allready opened by a ConfigParser.RawConfigParser
        - ha_conf: An intanciated HAConf object to write infos into
        """
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
    def _loadPingdomConf(config, ha_conf):
        """Load scpecific infos about Pingdom settings
        
        Arguments:
        - config: the config file, allready opened by a ConfigParser.RawConfigParser
        - ha_conf: An intanciated HAConf object to write infos into
        """
        if(not config.has_section('PINGDOM_INFOS')):
            raise ConfigException('Config file must have a PINGDOM_INFOS section')
        
        if(config.has_option('PINGDOM_INFOS', 'api_key')):
            ha_conf.setPingdomAPIKey(config.get('PINGDOM_INFOS', 'api_key'))
        else:
            raise ConfigException("You must provide a Pingdom API Key (section 'PINGDOM_INFOS', key 'api_key')")
        
        if(config.has_option('PINGDOM_INFOS', 'login')):
            ha_conf.setPingdomLogin(config.get('PINGDOM_INFOS', 'login'))
        else:
            raise ConfigException("You must provide a Pingdom login (section 'PINGDOM_INFOS', key 'login')")
        
        if(config.has_option('PINGDOM_INFOS', 'password')):
            ha_conf.setPingdomPassword(config.get('PINGDOM_INFOS', 'password'))
        else:
            raise ConfigException("You must provide a Pingdom password (section 'PINGDOM_INFOS', key 'password')")
        
        if(config.has_option('PINGDOM_INFOS', 'check_id')):
            ha_conf.setPingdomCheckId(config.get('PINGDOM_INFOS', 'check_id'))
        else:
            raise ConfigException("You must provide a Pingdom check ID (section 'PINGDOM_INFOS', key 'check_id')")
    
    @staticmethod
    def _loadAutoscaleSettings(config, ha_conf):
        """Load scpecific infos about Autoscale settings
        
        Arguments:
        - config: the config file, allready opened by a ConfigParser.RawConfigParser
        - ha_conf: An intanciated HAConf object to write infos into
        """
        if(config.has_section("AUTOSCALE_SETTINGS")):
            if(config.has_option('AUTOSCALE_SETTINGS', 'min_dynos')):
                ha_conf.setMinDynos(config.getint('AUTOSCALE_SETTINGS', 'min_dynos'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'max_dynos')):
                ha_conf.setMaxDynos(config.getint('AUTOSCALE_SETTINGS', 'max_dynos'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'response_time_low')):
                ha_conf.setResponseTimeLow(config.getint('AUTOSCALE_SETTINGS', 'response_time_low'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'response_time_high')):
                ha_conf.setResponseTimeHigh(config.getint('AUTOSCALE_SETTINGS', 'response_time_high'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'check_frequency')):
                ha_conf.setCheckFrequency(config.getint('AUTOSCALE_SETTINGS', 'check_frequency'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'pingdom_check_period')):
                ha_conf.setPingdomCheckPeriod(config.getint('AUTOSCALE_SETTINGS', 'pingdom_check_period'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'response_time_trend_low')):
                ha_conf.setResponseTimeTrendLow(config.getfloat('AUTOSCALE_SETTINGS', 'response_time_trend_low'))
            if(config.has_option('AUTOSCALE_SETTINGS', 'response_time_trend_high')):
                ha_conf.setResponseTimeTrendHigh(config.getfloat('AUTOSCALE_SETTINGS', 'response_time_trend_high'))
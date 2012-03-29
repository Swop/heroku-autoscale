class ConfigException(Exception):
    """Exception raised when a syntax error is detected inside a config file
    """ 
    def __init__(self, msg):
        Exception.__init__(self, msg)
        
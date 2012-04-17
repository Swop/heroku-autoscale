"""Define the class representing a Pingdom check result object.
"""

class PingdomCheck:
    """This class represent a Pingdom API check result.
    """

    def __init__(self, probe_id, time, probe_status, response_time, status_desc, status_long_desc):
        """Initialize the PingDom API Check object.
        
        Arguments:
        - probe_id : the id of the probe
        - time : time of the check
        - probe_status : The status (up/down) of the probe
        - response_time : The measured response time
        - status_desc : A short description of the result check (OK, NOK ...)
        - status_long_desc : Long description of the result of the check
        """
        self._probe_id = probe_id
        self._time = time
        self._probe_status = probe_status
        self._response_time = response_time
        self._status_desc = status_desc
        self._status_desc_long = status_long_desc
        
    def get_probe_id(self):
        """Return the ID of the probe"""
        return self._probe_id
        
    def get_time(self):
        """Return the time of the check"""
        return self._time
    
    def get_probe_status(self):
        """Return the status (up/down) of the probe"""
        return self._probe_status
    
    def get_response_time(self):
        """Return the measured response time"""
        return self._response_time
    
    def get_status_desc(self):
        """Return a short description of the result check (OK, NOK ...)"""
        return self._status_desc
    
    def get_status_desc_long(self):
        """Return a long description of the result of the check"""
        return self._status_desc_long
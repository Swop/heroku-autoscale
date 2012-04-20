"""
Define a light wrapper class for the Pingdom API.
By Sylvain MAUDUIT (Swop)
"""

import httplib, base64
import simplejson as json
from pingdomcheck import PingdomCheck

class PingdomAPIWrapper:
    """Wrapper to use the Pingdom API to bring back the checks results"""
    
    def __init__(self, pingdom_api_key, pingdom_login, pingdom_password):
        """Initialize the PingDom API wrapper
        
        Arguments:
        - pingdom_api_key: The Pingdom API key
        - pingdom_login: The login to use (aka the account email)
        - pingdom_password: The associated password
        """
        self._api_key = pingdom_api_key
        self._login = pingdom_login
        self._password = pingdom_password

    def getChecks(self, check_id, from_date=None, to_date=None):
        """Return the check results from PingDom engine ("Get Raw Check Results" API method)
        
        Arguments:
        - check_id: The ID of the Pingdom check which monitor your application
        - from_date: Begin of the period (UNIX time)
        - to_date: End of the period (UNIX time)
        
        Returns: Dictionary 'time => PingdomCheck'
        """
        uri = "/api/2.0/results/" + check_id

        first_arg = True
        
        if from_date or to_date:
            uri = uri + "?"

        if from_date:
            uri = uri + "from=" + str(from_date)
            first_arg = False
        if to_date:
            if not first_arg:
                uri = uri + "&"
            uri = uri + "to=" + str(to_date)

        json_response = self._contactApi('api.pingdom.com', uri)
        response_object = json.loads(json_response)
        
        checks = {}
        for check in response_object["results"]:
            try:
                if(check["status"] == 'up'):
                    checks[check["time"]] = PingdomCheck(check["probeid"], 
                                               check["time"], 
                                               check["status"], 
                                               check["responsetime"], 
                                               check["statusdesc"], 
                                               check["statusdesclong"])
            except KeyError:
                pass
        
        return checks

    def _contactApi(self, host, uri, data = "", method = "GET"):
        """Contact a specific method of the Pingdom API
        
        Arguments:
        - host: The API host
        - uri: The specific method URI
        - data: Additional data to place into the body of the request
        - method: HTTP method to use
        
        Returns: The body of the response
        """ 
        base64string = base64.encodestring('%s:%s' % (self._login, self._password))[:-1]
        headers = {"App-Key": self._api_key, "Authorization": "Basic %s" % base64string}

        conn = httplib.HTTPSConnection(host)
        conn.request(method, uri, data, headers)
        response = conn.getresponse()

        data = response.read()
        conn.close()

        if(response.status != 200):
            raise Exception(data)

        return data

    def _getNodelistText(self, nodelist):
        """Return the text string of DOM node list
        
        Arguments:
        - nodeList: List of nodes
        
        Returns: The compiled text string
        """
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

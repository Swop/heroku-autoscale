import httplib, base64
import simplejson as json
from pingdomcheck import PingdomCheck


# local to unix UTC :  int(time.mktime((datetime.datetime.now()).timetuple()))

"""Define a light wrapper class for the Pingdom API. 
"""
class PingdomAPIWrapper:
    """Initialize the PingDom API wrapper"""
    def __init__(self, pingdom_api_key, pingdom_login, pingdom_password):
        self._api_key = pingdom_api_key
        self._login = pingdom_login
        self._password = pingdom_password

    """Return the check results from PingDom engine ("Get Raw Check Results" API method)
    
    Arguments:
    - pingdom_api_key : The Pingdom API key
    """
    def getChecks(self, check_id, from_date=None, to_date=None):
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
        #print(json_response)
        #exit(1)
        response_object = json.loads(json_response)
        
        checks = {}
        for check in response_object["results"]:
            #print(check)
            #exit(1)
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
        #host = "localhost"
       
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
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

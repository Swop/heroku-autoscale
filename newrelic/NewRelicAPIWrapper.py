import httplib
import xml.dom.minidom
from NewRelicApiException import NewRelicApiException

class NewRelicAPIWrapper:
    """Handle the communication with the NewRelic REST API
    
    Manage the HTTP request to the API. Usefull to get the Apdex score for a given period.
    """
    def __init__(self, api_key, account_id, app_id):
        """Initialise the NewRelic API wrapper
        
        Arguments:
        - NewRelic API Key
        - NewRelic Accounf ID
        - NewRelic App ID
        """
        self._api_key = api_key
        self._account_id = account_id
        self._app_id = app_id
        
    def getApdex(self, begin, end, summary = True):
        """Get the Apdex score of the application for a given period.
        Arguments:
        - begin date (datetime)
        - end date (datetime)
        - summary (boolean): Specify if the result mus be a global score or each score in the period (default: True)
        
        Returns: The Apdex score(s).
        """
        host = "api.newrelic.com"
        uri = "/api/v1/accounts/{0}/applications/{1}/data.xml?metrics[]=Apdex&field=score&begin={2}&end={3}".format(self._account_id, self._app_id, begin.isoformat(), end.isoformat())
        
        xml_response = self._contactApi(host, uri)#, data)
        dom = xml.dom.minidom.parseString(xml_response)
        
        apdex_field = dom.getElementsByTagName("field")[0]
        return float(self._getNodelistText(apdex_field.childNodes))
        
    def _contactApi(self, host, uri, data = {}, method = "GET"):
        """Request a specific action of the NewRelic API
        
        Contacts a given NewRelic URI with specified data and return the XML response.
        
        Arguments:
        - host: the NewRelic hostname (like "api.newrelic.com")
        - uri: the action to request (like "api/v1/account/...")
        - data: (optional) a dictionary of the data to embed in the request
        - method: (optional, default: GET) method to use in the HTTP request
        
        Return: the XML response
        """
        headers = {"Content-type": "application/xml", "x-api-key": self._api_key}
        
        conn = httplib.HTTPSConnection(host)
        conn.request(method, uri, data, headers)
        response = conn.getresponse()
        
        data = response.read()
        conn.close()
        
        if(response.status != 200):
            raise NewRelicApiException(data)
        
        return data
    
    def _getNodelistText(self, nodelist):
        """Return the concatened string of nodelist's textnodes
        """
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)
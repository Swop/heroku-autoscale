import httplib
import xml.dom.minidom
from NewRelicApiException import NewRelicApiException

class NewRelicAPIWrapper:

    def __init__(self, api_key, account_id, app_id):
        self._api_key = api_key
        self._account_id = account_id
        self._app_id = app_id
        
    def getApdex(self, begin, end, summary = True):
        host = "api.newrelic.com"
        uri = "/api/v1/accounts/{0}/applications/{1}/data.xml?metrics[]=Apdex&field=score&begin={2}&end={3}".format(self._account_id, self._app_id, begin.isoformat(), end.isoformat())
        
        xml_response = self._contactApi(host, uri)#, data)
        dom = xml.dom.minidom.parseString(xml_response)
        
        apdex_field = dom.getElementsByTagName("field")[0]
        return float(self._getNodelistText(apdex_field.childNodes))
        
    def _contactApi(self, host, uri, data = {}, method = "GET"):
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
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)
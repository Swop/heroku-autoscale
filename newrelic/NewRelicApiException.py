import xml.dom.minidom

class NewRelicApiException(Exception):
    """Exception raised when an error occurs during the communication with the New Relic REST API.
    """ 
    def __init__(self, xml_response):
        all_errors = ""
        dom = xml.dom.minidom.parseString(xml_response)
        
        errors = dom.getElementsByTagName("error")
        for error in errors:
            all_errors += self._getNodelistText(error.childNodes)
        
        print(all_errors)
        Exception.__init__(self, all_errors)
        
    def _getNodelistText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ' - '.join(rc)
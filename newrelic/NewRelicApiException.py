import xml.dom.minidom

class NewRelicApiException(Exception):

    def __init__(self, xml_response):
        all_errors = ""
        dom = xml.dom.minidom.parseString(xml_response)
        
        errors = dom.getElementsByTagName("error")
        for error in errors:
            all_errors += error
                
        Exception.__init__(self, all_errors)
# *****************************************************
# Util.py
# Created by: k.timtim
# 
# Contains helper methods for mitmproxy addon scripts
# *****************************************************
import json

class Util:

    # Constant for mapping file name
    MAPPING_FILE = "mappings.json"

    # Empty constructor
    def __init__(self):
        pass

    # Loads request_url:response_file mapping from mappings.json.
    # Returns JSON object of mapping
    def loadReqResMappingFromFile(self):
        print("Mapping File: %s" % self.MAPPING_FILE)
        with open(self.MAPPING_FILE) as mapping_file:
            mapping_json = json.load(mapping_file)
        return mapping_json


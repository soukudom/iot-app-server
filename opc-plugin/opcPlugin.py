#!/usr/bin/env python3
#import config
import configparser

from opcua import Client
from opcua import ua

import sys

## TODO: Add Sphinx
## TODO: Create opc-au moduel diagrams
## TODO: How to solve connection handling

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def event_notification(self, event):
        print("New event recived: ", event)


class OpcClient:
    def __init__(self, opc_url, variables):
        self.opc_url = opc_url
        self.variables = variables
    
    def readData(self):
        data = {}
        try:
            client = Client(self.opc_url) 
            client.connect()
            for key, val in self.variables.items():
                node = client.get_node(val) 
                data[key] = node.get_value()
            #msclt = SubHandler()
            #sub = client.create_subscription(100, msclt)
            #handle = sub.subscribe_events()
            print(data)
            client.disconnect()
            return data

        except Exception as e:
            print("\033[31mError\033[0m: Unable to read OPC/UA server data -> '{}'".format(e))
            sys.exit(1)
    
        
class Config:
    def __init__(self,filename):
        self.config = configparser.ConfigParser()

#    def parse(self, filename):
        self.config.read(filename)
        
        #sections = config.sections()
        #for i in sections:
        #    print("section ", i)
        #    for j in config[i]:
        #        print(" key: ",j, "value:", config[i][j])

    def getGeneral(self):
        return self.config["general"]

    def getOpcVariables(self):
        variables = {}
        for key, val in self.config["variables"].items():
            # Skip all non-opc variables
            if val == "register":
                continue
            variables[key] = val 

        return variables


if __name__ == "__main__":
    params = Config("package_config.ini")

    url = params.getGeneral()["opc_client"]
    variables = params.getOpcVariables()

    opc = OpcClient(url,variables)
    print(opc.readData())


    


    
    #OpcClient("")
    



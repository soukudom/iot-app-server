#!/usr/bin/env python3
#import config
import configparser

from opcua import Client
from opcua import ua

import sys

## TODO: Add Sphinx
## TODO: Create opc-au moduel diagrams
## TODO: How to solve connection handling + subscription
## TODO: Check input parameters
## TODOL Add secure login methods

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)


class OpcClient:
    def __init__(self, opc_url, variables, settings):
        self.opc_url = opc_url
        self.variables = variables
        self.settings = settings
        self.handlers = {}
        self.subscritption = None
    
    def readData(self):
        data = {}
        try:
            client = Client(self.opc_url) 
            client.connect()
            for key, val in self.variables.items():
                node = client.get_node(val) 
                data[key] = node.get_value()
            
            print(data)
            #client.disconnect()
            #return data

        except Exception as e:
            print("\033[31mError\033[0m: Unable to read OPC/UA server data -> '{}'".format(e))
            sys.exit(1)

    # Create a subscription and store the connection handle
    def createSubscription(self, address):
        handler = SubHandler()
        self.subcription = client.create_subscription(500, handler)
        handle = self.subscription.subscribe_data_change(client.get_node(address))
        self.handlers[address] = handle

    def unsubscribeSubscriptions(self, address=None):
        # Unsubscribe all connection handlers
        if address is None:
            self.subscription.unsubscribe(self.handlers[address])
        # Unsubscribe defined connection handlers
        else:
            for handler in self.handlers:
                self.subcription.unsubscribe(handler)
            self.subscription.delete()

        # Check handler count
        if len(self.handlers) == 0:
            # Close subscription
            self.subscription.delete()
    
        
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
            variables[key] = val 
        return variables

    def getOpcVariablesSettings(self):
        settings = {}
        sections = self.config.sections()
        # Remote global sections
        sections.remove("general")
        sections.remove("variables")

        for section in sections:
            for key,val in self.config[section].items():
                try:    
                    settings[section][key] = val #self.config[section]
                # Create a first record
                except Exception as e:
                    settings[section] = {}
                    settings[section][key] = val #self.config[section]
        return settings


if __name__ == "__main__":
    params = Config("package_config.ini")

    # PLC url address
    url = params.getGeneral()["opc_client"]
    # Get OPC variable to readm
    variables = params.getOpcVariables()
    # Get reading settings for variables
    settings = params.getOpcVariablesSettings()
    

    opc = OpcClient(url,variables,settings)
    print(opc.readData())


    

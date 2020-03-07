#!/usr/bin/env python3
#import config
import configparser

from opcua import Client
from opcua import ua

import sys
import time

## TODO: Add Sphinx
## TODO: Create opc-au moduel diagrams
## TODO: How to solve connection handling + subscription
## TODO: Check input parameters
## TODO: Add secure login methods
## TODO: Add mqtt connection 

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("OPC/UA: New data change event", node, val)
        # TODO: change polling period till another event

    #def event_notification(self, event):
    #    print("OPC/UA: New event", event)


class OpcClient:
    def __init__(self, opc_url, variables, settings):
        self.opc_url = opc_url
        self.variables = variables
        self.settings = settings
        self.handlers = {}
        self.subscritption = None

    def login(self):
        pass
    
    def logout(self):
        pass
    
    def readData(self):
        data = {}
        try:
            client = Client(self.opc_url) 
            client.connect()
            for key, val in self.variables.items():
                node = client.get_node(val) 
                data[key] = node.get_value()
            
            print(data)
            client.disconnect()
            return data

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

class MqttClient:
    def __init__(self):
        pass

    def sendData(self):
        pass

    def receivedData(self):
        pass
    
        
class Config:
    def __init__(self,filename):
        self.config = configparser.ConfigParser()
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

class Control:
    def __init__(self, poll_interval, opc_client):
        self.poll_interval = poll_interval 
        self.ready_flag = True
        self.opc_client = opc_client

    def start(self):
        #login
        self.ready_flag = True
    
    def run(self):
        while self.ready_flag:
            #read OPC data
            # send them via MQTT
            time.sleep(self.poll_interval)
    
    def stop(self):
        self.ready_flag = False
        # logout

if __name__ == "__main__":
    params = Config("package_config.ini")

    # PLC url address
    url = params.getGeneral()["opc_client"]
    # Get OPC variable to readm
    variables = params.getOpcVariables()
    # Get reading settings for variables
    settings = params.getOpcVariablesSettings()
   
    opc_client = OpcClient(url,variables,settings)
    print(opc.readData())
    ctl = Control(2,opc_client) 
    ctl.start()
    ctl.run()
        
    #sleep = 2
    # login to OPC server
    #while True:
        # read OPC data
        # send them via MQTT
        # check status register -> change reading period
    #    time.sleep(sleep)
        



    

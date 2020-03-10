#!/usr/bin/env python3
import configparser

from opcua import Client
from opcua import ua
import paho.mqtt.client as mqtt

import sys
import time

## TODO: Add Sphinx
## TODO: How to solve connection handling + subscription
## TODO: Check input parameters
## TODO: Expcetion handling
## TODO: Add secure login methods
## TODO: Add mqtt reverse connection 
## TODO: Add verbose mode
## TODO: Local storage

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        if int(val)%5 == 0:
            print("OPC/UA: New data change event", node, val,type(data),data)
        # TODO: change polling period till another event

    # Event notification callback
    #def event_notification(self, event):
    #    print("OPC/UA: New event", event)


class OpcClient:
    def __init__(self, opc_url, variables, settings):
        # OPC/UA server url
        self.opc_url = opc_url
        # OPC/UA variables addresses
        self.variables = variables
        # OPC/UA variables config parameters
        self.settings = settings
        # subscription objects
        self.handlers = {}
        self.subscription = None
        # OPC/UA connection from client to a server
        self.client = None
        # Local registers
        self.registers = {}
        # State flag
        self.init = True

    def login(self):
        # Init local registers
        for key, val in self.variables.items():
            self.registers[key] = {}
            self.registers[key]["min"] = None
            self.registers[key]["max"] = None

        
        self.client = Client(self.opc_url) 
        self.client.connect()
    
    def logout(self):
        self.client.disconnect()

    def pollData(self):
        data = {}
        for key, val in self.variables.items():
            node = self.client.get_node(val) 
            data[key] = {}
            data[key]["value"] = node.get_value()
            data[key]["role"] = "normal"
            data[key]["register_min"] = "n/a"
            data[key]["register_max"] = "n/a"
            # Custom configuration parameters
            try:
                for param_key, param_val in self.settings[key].items():
                    # Add settings parameters to the data structure
                    if param_key == "register":
                        config = param_val.split(",")
                        for config_param in config:
                            if config_param == "min":
                                # Check and init the first value
                                if self.registers[key]["min"] == None:
                                    self.registers[key]["min"] = data[key]["value"]
                                elif int(self.registers[key]["min"]) > int(data[key]["value"]):
                                    self.registers[key]["min"] = data[key]["value"]
                                data[key]["register_min"] = self.registers[key]["min"]
                            elif config_param == "max":
                                # Check and init the first value
                                if self.registers[key]["max"] == None:
                                    self.registers[key]["max"] = data[key]["value"]
                                elif int(self.registers[key]["max"]) < int(data[key]["value"]):
                                    self.registers[key]["max"] = data[key]["value"]
                                data[key]["register_max"] = self.registers[key]["max"]
                            else:
                                print("\033[31mError\033[0m: Invalid option for register parameter in the configuration file")
                    if param_key == "state" and self.init:
                        # Create subription
                        self.createSubscription(val)
                        self.init = False
                    if param_key == "state":
                        data[key]["role"] = "status"
            # Key for specific configuration does not exist
            except Exception as e:
                pass

        return data
         
    def readData(self):
        data = {}
        try:
            client = Client(self.opc_url) 
            client.connect()
            for key, val in self.variables.items():
                node = client.get_node(val) 
                data[key] = node.get_value()
            
            client.disconnect()
            return data

        except Exception as e:
            print("\033[31mError\033[0m: Unable to read OPC/UA server data -> '{}'".format(e))
            sys.exit(1)

    # Create a subscription and store the connection handle
    def createSubscription(self, address):
        handler = SubHandler()
        self.subscription = self.client.create_subscription(500, handler)
        handle = self.subscription.subscribe_data_change(self.client.get_node(address))
        self.handlers[address] = handle
        # Verbose
        #print("Subscription created for address ",address)

    def unsubscribeSubscriptions(self, address=None):
        # Unsubscribe all connection handlers
        if address is None:
            self.subscription.unsubscribe(self.handlers[address])
        # Unsubscribe defined connection handlers
        else:
            for handler in self.handlers:
                self.subscription.unsubscribe(handler)
            self.subscription.delete()

        # Check handler count
        if len(self.handlers) == 0:
            # Close subscription
            self.subscription.delete()

class MqttClient:
    def __init__(self, broker,topic):
        self.broker = broker
        self.topic = topic
        self.mqtt_client = mqtt.Client(client_id="iox-app", clean_session=False)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    def login(self):
        self.mqtt_client.connect(host=self.broker,port=1883,keepalive=60)
        #self.mqtt_client.loop_forever()
    
    def logout(self):
        self.mqtt_client.disconnect()

    def on_connect(self,client, data, flags, rc):
        client.subscribe(self.topic)

    def on_message(self,client, data, msg):
        print("MQTT Data:",msg.topic+" "+str(msg.payload))

    def sendData(self,data):
        for record_key, record_val in data.items():
            ret = self.mqtt_client.publish(self.topic+record_key,payload=str(record_val), qos=0, retain=False)

    def receiveData(self):
        pass
    
        
class Config:
    def __init__(self,filename):
        self.config = configparser.ConfigParser()
        self.config.read(filename)
        
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
    def __init__(self, poll_interval, opc_client, mqtt_client):
        self.poll_interval = poll_interval 
        self.ready_flag = True
        self.opc_client = opc_client
        self.mqtt_client = mqtt_client

    def start(self):
        #login
        self.opc_client.login()
        self.mqtt_client.login()
        self.ready_flag = True
    
    def run(self):
        data = {}
        while self.ready_flag:
            #read OPC data
            data = self.opc_client.pollData()
            # send them via MQTT
            self.mqtt_client.sendData(data)
            # Sleep before the next poll
            time.sleep(int(self.poll_interval))
    
    def stop(self):
        self.ready_flag = False
        # logout
        self.opc_client.logout()

if __name__ == "__main__":
    params = Config("package_config.ini")

    # General configuration parameters
    general = params.getGeneral()
    # Get OPC variable to readm
    variables = params.getOpcVariables()
    # Get reading settings for variables
    settings = params.getOpcVariablesSettings()
   
    opc_client = OpcClient(general["opc_server"],variables,settings)
    mqtt_client = MqttClient(general["mqtt_broker"],general["topic_name"])
    #print(opc.readData())

   # print(variables)
   # print(settings)
    ctl = Control(general["polling"],opc_client,mqtt_client) 
    ctl.start()
    ctl.run()
        

    

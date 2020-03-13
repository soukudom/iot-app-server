#!/usr/bin/env python3
import configparser

from opcua import Client
from opcua import ua
import paho.mqtt.client as mqtt
import json

import sys
import time

## TODO: Add Sphinx
## TODO: Add secure login methods
## TODO: Local storage, try opc history read feature

VERBOSE=1

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def __init__(self):
        self.control = Control()
        self.nodes = {}

    def checkProcess(self,node,val):
        if val == 0:
            # Process have stopped => read slower
            #print("Process stop")
            pass
        else:
            # Process have started => read faster
            #print("Process start")
            pass

    def datachange_notification(self, node, val, data):
        #print("OPC/UA: New data change event", node, val,type(data),data)

        if node in self.nodes:
            # Check control value
            self.checkProcess(node,val)
        else:
            # Create a first node
            self.nodes[node] = val
            self.checkProcess(node,val)
            
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

        try:
            self.client = Client(self.opc_url) 
            self.client.connect()
        except Exception as e:
            raise Exception("OPC/UA server is not available. Please check connectivity by cmd tools")
        if VERBOSE:
            print("NOTE: client connected to a OPC/UA server",self.opc_url)
        
    def logout(self):
        try:
            self.client.disconnect()
        except Exception as e:
            raise Exception("OPC/UA server is not available for logout command. Please check connectivity by cmd tools")
        if VERBOSE:
            print("NOTE: logout form OPC/UA server")

    # TODO: Create support for more status variable -> right now the self.init flag is a limitation
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
        try:
            handler = SubHandler()
            self.subscription = self.client.create_subscription(500, handler)
            handle = self.subscription.subscribe_data_change(self.client.get_node(address))
            self.handlers[address] = handle
        except Exception as e:
            raise Exception("Unable to create subscription to OPC/UA server address", address)

        if VERBOSE:
            print("NOTE: Subscription created for address ",address)

    def unsubscribeSubscriptions(self, address=None):
        if len(self.handlers) == 0:
            return True

        # Unsubscribe defined connection handlers
        if address is not None:
            self.subscription.unsubscribe(self.handlers[address])
        # Unsubscribe all connection handlers
        else:
            for handler in self.handlers:
                self.subscription.unsubscribe(handler)
            self.subscription.delete()

        # Check handler count
        if len(self.handlers) == 0:
            # Close subscription
            self.subscription.delete()

class MqttClient:
    def __init__(self, broker,port,topic):
        self.broker = broker
        self.topic = topic
        self.port = port
        self.mqtt_client = mqtt.Client(client_id="iox-app", clean_session=False)
        #self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.control = None

    def login(self):
        try:
            self.mqtt_client.connect(host=self.broker,port=self.port,keepalive=60)
            self.control = Control()
        except Exception as e:
            raise Exception("MQTT broker is not available. Please check connectivity by cmd tools")
        if VERBOSE:
            print("NOTE: MQTT client is connected to the broker",self.broker)
    
    def logout(self):
        self.mqtt_client.disconnect()
        if VERBOSE:
            print("NOTE: MQTT client is disconnected from the broker", self.broker)

    def on_message(self,client, data, msg):
        if VERBOSE: 
            print("NOTE: MQTT data have been received:",msg.topic+" "+str(msg.payload))

        payload_data = json.loads(str(msg.payload.decode()))
        for cmd_key, cmd_val in payload_data.items():
            if cmd_key == "poll":
                self.control.poll_interval = cmd_val
            elif cmd_key == "clear":
                pass
            else:
                print("\033[31mError\033[0m: Unknown command")
                

        #print("val is",val["comm"])

    def sendData(self,data):
        for record_key, record_val in data.items():
            ret = self.mqtt_client.publish(self.topic+record_key,payload=str(record_val), qos=0, retain=False)

    def subscribe(self):
        try:
            self.mqtt_client.subscribe(self.topic+"command")
            self.mqtt_client.loop_start()
        except Exception as e:
            raise Exception("Unable to subscribe topic",self.topic+"command")

        if VERBOSE:
            print("NOTE MQTT topic '",self.topic+"commnad","' has been subscribed")
   
 
# Class to parse configuration data        
class Config:
    def __init__(self,filename):
        self.config = configparser.ConfigParser()
        self.config.read(filename)
        
    # Get the general section
    def getGeneral(self):
        try:
            general = self.config["general"]
            # Test polling to int
            tmp = general["polling"]
            int(tmp)
            
            # Test polling to int
            tmp = general["polling_change"]
            int(tmp)

            # Simple test to ip address
            tmp = general["mqtt_broker"]
            if len(tmp.split(".")) != 4:
                raise Exception("IP adrress of MQTT broker is not formated correctly")
           
            # Simple test to port 
            tmp = general["mqtt_port"]
            int(tmp)
            
            # Simple test to opc server format
            tmp = general["opc_server"]
            if tmp.split("@")[0] != "opc.tcp://":
                raise Exception("OPC server address must start with 'opc.tcp://'")
                
            # Simple test to a mqtt format 
            tmp = general["topic_name"]
            if tmp[-1] != "/":
                raise Exception("Topic name must end with '/'")
            
        except Exception as e:
            print("\033[31mError\033[0m: Missing mandatory General section or General parameters in the configuration file or parameters are not formated well -> ", e)
    
            
        #return self.config["general"]
        return general
   
    # TODO: Test that string are without quotes 
    # Get the variables section
    def getOpcVariables(self):
        variables = {}
        for key, val in self.config["variables"].items():
            variables[key] = val 
        return variables
    
    # Get custom variables settings section
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

# Metaclass for singleton pattern
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# The main class to control the whole flow
class Control(metaclass=Singleton):
    def __init__(self, poll_interval=5, opc_client=None, mqtt_client=None):
        self.poll_interval = int(poll_interval) 
        self.ready_flag = True
        self.opc_client = opc_client
        self.mqtt_client = mqtt_client

    # Start remote connections 
    def start(self):
        try:
            # Login
            self.opc_client.login()
            self.mqtt_client.login()
            self.ready_flag = True
            if VERBOSE:
                print("NOTE: MQTT and OPC connections have been established")
        except Exception as e:
            print("\033[31mError\033[0m: Unable to login to a remote server -> ", e)
            sys.exit(1)
        try:
            self.mqtt_client.subscribe()
        except Exception as e:
            print("\033[31mError\033[0m: Unable to subscribe to a remote server -> ", e)
            sys.exit(1)

    
    def run(self):
        data = {}
        try:
            while self.ready_flag:
                # Read OPC data
                data = self.opc_client.pollData()
                # Send them via MQTT
                self.mqtt_client.sendData(data)
                if VERBOSE > 1:
                    print("NOTE: MQTT data have been send:",data)
                # Sleep before the next poll
                time.sleep(int(self.poll_interval))
        except Exception as e:
            print("\033[31mError\033[0m: Unable to receive/send data from a remote server -> ", e)
            sys.exit(1)
            
            
    # Stop all remote connections
    def stop(self):
        self.ready_flag = False
        try:
            # Logout
            self.opc_client.logout()
            self.mqtt_client.logout()
            if VERBOSE:
                print("NOTE: MQTT and OPC connection have been closed")

        except Exception as e:
            print("\033[31mError\033[0m: Unable to logout from a remote server -> ", e)
            sys.exit(1)
            

if __name__ == "__main__":
    # Get configuration object
    params = Config("package_config.ini")
    # General configuration parameters
    general = params.getGeneral()
    # Get OPC variables to read
    variables = params.getOpcVariables()
    # Get reading settings for variables
    settings = params.getOpcVariablesSettings()
    
    if VERBOSE:
        print("NOTE: Configuration has been loaded")

    # Create opc and mqtt client objects 
    opc_client = OpcClient(general["opc_server"],variables,settings)
    mqtt_client = MqttClient(general["mqtt_broker"],general["mqtt_port"],general["topic_name"])

    # Create control object and start process
    ctl = Control(general["polling"],opc_client,mqtt_client) 
    ctl.start()
    ctl.run()
        

    

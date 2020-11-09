import socket
import time					
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import datetime


class DataReader:
    def __init__(self):
        # camera UDP
        self.camera_ip = '0.0.0.0'
        self.camera_port = 20021
        self.addr = (self.camera_ip, self.camera_port)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.s.bind(self.addr)
        self.stopped = False

        # bees data  # $dataset,$type,$act,$datex,$min,$sec,$hive,$bee_type,$dbx,$location
        self.beesin = []
        self.beesout = []

        # AWS
        myMQTTClient = AWSIoTMQTTClient("ClientID")
        myMQTTClient.configureEndpoint("a1ocikpeg4zf0y-ats.iot.us-east-2.amazonaws.com", 8883)
        myMQTTClient.configureCredentials("./AmazonRootCA1.pem", "./781f626098-private.pem.key", "781f626098-certificate.pem.crt")
        myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        self.mqttClient = myMQTTClient
        self.channel = 'Nantou/bee_inout'

    # receive the UDP packages and send it back to AWS every minute.
    def run(self):
        while self.stopped:
            data, addr =self.s.recvfrom(512)
            if data:
                print(data)
            # TODO : parse data after printed.
        self.s.close()

    # count bees in this minute and format json to AWS
    def parse2json(self) -> str: # return string of json
        timestamp = datetime.datetime.now()
        # json = '{ "timestamp": "'+ str(timestamp) + '",   \
        #           "weight": "' + str(1) +  '",     \
        #           "temp": "' + str(shtd[0]) + '",  \
        #           "hum": "'  + str(shtd[1]) + '"}' 
        
        #  json = f'"timestamp": "{timestamp}", "weight": "{scaled}", "temp": "{shtd[0]}", "hum": "{shtd[1]}"'
        # json = "{" + json + "}"
        # return json

    # send to AWS   ####### TODO: no connection. what is shadow and green grass, insert datas 
    def toAWS(self, msg:str):
        if not self.mqttClient.connect():
            return
        #msg = "{ \"timestamp\": {t}, \"weight\": {w}}".format(t=timestamp, w=weight)
        # msg = f'{ "timestamp": {timestamp}, "weight": {weight}}'
        # msg= '{ "timestamp": "'+ str(timestamp) + '", "weight": ' + str(1) + ' }'
        self.mqttClient.publish(self.channel, msg, 1)
        print(msg)
        self.mqttClient.disconnect()

    def stop(self):
        self.stopped = True


if __name__ == '__main__':
    reader = DataReader()
    reader.run()

import socket
import time					
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import datetime


class DataReader:
    def __init__(self):
        # UDP setting, check QT for these settings
        self.camera_ip = '127.0.0.1'
        self.camera_port = 20022
        self.addr = (self.camera_ip, self.camera_port)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.s.bind(self.addr)
        self.stopped = False

        # bees data buffer # $dataset,$type,$act,$datex,$min,$sec,$hive,$bee_type,$dbx,$location
        self.buff = []
        self.maxbuff = 3000

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
        self.send_data_interval = 3 * 60 # 3min
        self.retry_interval = 1 * 60  # 1 min 
        self.last_sendtime = time.time()

    # receive the UDP packages and buffer or send it back to AWS
    def run(self):
        while not self.stopped:
            print('in run loop')
            data, addr =self.s.recvfrom(512)
            if data:
                # read from QT program
                data = data.decode("utf-8")
                data = data.split(':')
                print(data[2], data[-1])
                data = self.parse2json(data[2], data[-1])

                # check the length of buff
                if len(self.buff) >= self.maxbuff:
                    self.buff.pop(0)
                self.buff.append(data)
                print('buffer len: ', len(self.buff), 'data: ', data)

                # send to AWS
                interval = time.time() - self.last_sendtime
                if interval >= self.send_data_interval:
                    success = self.toAWS()
                    print('sending success', success)
                    # if sending failed, resend in self.retry_interval
                    self.send_data_interval = lambda success: self.send_data_interval if success else self.retry_interval
                    self.last_sendtime = time.time()

        self.s.close()
        print('run f')

    # parse data from reader to json format
    def parse2json(self, act, ispollen) -> str: # return string of json
        timestamp = datetime.datetime.now()
        json = f'"timestamp": "{timestamp}", "act": "{act}", "ispollen": {ispollen}'
        json = "{" + json + "}"
        return json

    # send all buffer to AWS & clean the buffer if sent. 
    # return True for successfully sent all buffer, otherwise False
    def toAWS(self):
        try:
            self.mqttClient.connect(timeout=1000)
        except:
            return False

        # send all buffer
        while len(self.buff) > 0:
            try:
                success = self.mqttClient.publish(self.channel, self.buff[0], 1)
                if success:
                    self.buff.pop(0)
                else:
                    raise Exception('Publish failed')
            except:
                self.mqttClient.disconnect()
                return False
                
        self.mqttClient.disconnect()
        return True

    # stop run() loop
    def stop(self):
        self.stopped = True


if __name__ == '__main__':
    reader = DataReader()
    reader.run()

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
        self.record_data_interval = datetime.timedelta(minutes=1)

        # AWS
        myMQTTClient = AWSIoTMQTTClient("ClientID")
        myMQTTClient.configureEndpoint("a1ocikpeg4zf0y-ats.iot.us-east-2.amazonaws.com", 8883)
        myMQTTClient.configureCredentials("/home/nvidia/Documents/Nantou_bee_rpiTX2/AmazonRootCA1.pem", "/home/nvidia/Documents/Nantou_bee_rpiTX2/781f626098-private.pem.key", "/home/nvidia/Documents/Nantou_bee_rpiTX2/781f626098-certificate.pem.crt")
        myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        self.mqttClient = myMQTTClient
        self.channel = 'Nantou/bee_inout'
        self.send_data_interval = 1.5 *60 # 3min
        self.default_send_interval = 1.5 * 60
        self.retry_interval = 1 * 60  # 1 min 
        self.last_sendtime = time.time()

    # receive the UDP packages and buffer or send it back to AWS
    def run(self):
        inbee, outbee, inpollen, outpollen = 0, 0, 0, 0
        now_time_section = datetime.datetime.now()
        while not self.stopped:
            print('in run loop')
            data, addr =self.s.recvfrom(512)
            if data:
                # read from QT program
                data = data.decode("utf-8")
                data = data.split(':')
                act, ispollen = data[2], data[-1]
                print('act: ', act, 'ispollen: ', ispollen)  # act, ispollen

                # sum up per minute in(include pollenin)/out(include pollenout)/pollenin/pollenout
                if act == 'IN':
                    inbee +=1
                    if ispollen == '1':
                        inpollen += 1
                elif act == 'OUT':
                    outbee += 1
                    if ispollen == '1':
                        outpollen += 1

                # send one json per section_interval
                print(f'Bee added. inbee{inbee}, outbee{outbee}, inpollen{inpollen}, outpollen{outpollen}', '\n')
                now_t = datetime.datetime.now()
                if now_t - now_time_section > self.record_data_interval :
                    now_time_section = now_t
                    # check the length of buff
                    if len(self.buff) >= self.maxbuff:
                        self.buff.pop(0)
                    data = self.parse2json(inbee, outbee, inpollen, outpollen)
                    self.buff.append(data)
                    inbee, outbee, inpollen, outpollen = 0, 0, 0, 0
                    print('to json. buffer len: ', len(self.buff), 'data: ', data)

                # send to AWS
                interval = time.time() - self.last_sendtime
                if interval >= self.send_data_interval:
                    success = self.toAWS()
                    print('sending success', success)
                    # if sending failed, resend in self.retry_interval
                    if success:
                        self.send_data_interval = self.default_send_interval
                    else:
                        self.send_data_interval = self.retry_interval
                    # self.send_data_interval = lambda success: self.send_data_interval if success else self.retry_interval
                    self.last_sendtime = time.time()
        self.s.close()
        print('run f')
    
    def parse2json(self, inbee, outbee, inpollen, outpollen) -> str: # return string of json
        dt = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(dt)
        json = f'"timestamp": {timestamp}, "dt": "{dt}", "inbee": {inbee}, "outbee": {outbee}, "inpollen": {inpollen}, "outpollen": {outpollen}, "interval": "{self.record_data_interval}"'
        json = "{" + json + "}"
        return json

    '''
    # parse data from reader to json format
    def parse2json(self, act, ispollen) -> str: # return string of json
        dt = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(dt)
        json = f'"timestamp": {timestamp}, "dt": "{dt}", "act": "{act}", "ispollen": {ispollen}'
        json = "{" + json + "}"
        return json
    '''

    # send all buffer to AWS & clean the buffer if sent. 
    # return True for successfully sent all buffer, otherwise False
    def toAWS(self):
        print('to AWSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
        try:
            self.mqttClient.connect()
        except:
            print('mqtt connect failed')
            return False

        # send all buffer
        while len(self.buff) > 0:
            # print('in to AWS loop')
            try:
                success = False
                for i in range(3):
                    success = self.mqttClient.publish(self.channel, self.buff[0], 1)
                    if success:
                        break
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

    def sendtestdata(self):
        data = self.parse2json(0,0,0,0)
        self.buff.append(data)
        self.toAWS()

if __name__ == '__main__':
    reader = DataReader()
    reader.sendtestdata()
    reader.run()

import socket
import time					
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import datetime
from sht20 import SHT20
import pyaudio

class DataReader:
    def __init__(self):
        # scale 
        self.scale_ip = '192.168.85.210'
        self.scale_port = 59367
        self.addr = (self.scale_ip, self.scale_port)

        # AWS
        myMQTTClient = AWSIoTMQTTClient("ClientID")
        myMQTTClient.configureEndpoint("a1ocikpeg4zf0y-ats.iot.us-east-2.amazonaws.com", 8883)
        myMQTTClient.configureCredentials("./AmazonRootCA1.pem", "./781f626098-private.pem.key", "781f626098-certificate.pem.crt")
        myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        self.mqttClient = myMQTTClient
        self.channel = 'Nantou/test'

        # temperature and humid
        self.sht = SHT20(1, resolution=SHT20.TEMP_RES_14bit)

        # audio
        form_1 = pyaudio.paInt16 # 16-bit resolution
        chans = 1 # 1 channel
        samp_rate = 44100 # 44.1kHz sampling rate
        chunk = 512 # 2^12 samples for buffer
        dev_index = 0 # device index found by p.get_device_info_by_index(ii)
        self.audio = pyaudio.PyAudio() # create pyaudio instantiation
        # create pyaudio stream
        #self.stream = self.audio.open(format = form_1,rate = samp_rate,channels = chans, \
        #                input_device_index = dev_index,input = True, \
        #                frames_per_buffer=chunk)
        self.stream= 1

    # collect datas
    def read(self) -> str: # return string of json
        shtd = self.readSHT()
        scaled = self.TCPsend('ACK\r\n')
        scaled = float(scaled.split(',')[0])
 
        timestamp = datetime.datetime.now()
        json = f'"timestamp": "{timestamp}", "weight": {scaled}, "temp": {shtd[0]}, "hum": {shtd[1]}'
        json = "{" + json + "}"
        return json

    # send to AWS
    def toAWS(self, msg:str):
        try:
            if not self.mqttClient.connect():
                return False
            self.mqttClient.publish(self.channel, msg, 1)
            print(msg)
            self.mqttClient.disconnect()
            return True

        except:
            return False

    # send all buffer to AWS & clean the buffer if sent. 
    # return True for successfully sent all buffer, otherwise False
    def send_buffer(self, buff):
        try:
            self.mqttClient.connect(timeout=1000)
        except:
            return False

        # send all buffer
        while len(buff) > 0:
            try:
                success = self.mqttClient.publish(self.channel, buff[0], 1)
                if success:
                    buff.pop(0)
                else:
                    raise Exception('Publish failed')
            except:
                self.mqttClient.disconnect()
                return False
                
        self.mqttClient.disconnect()
        return True

    # read scale
    def TCPsend(self, msg:str) -> str:  # eg TCPsend("ACK[0D 0A]")
        clientsock = socket.socket()
        clientsock.connect(self.addr)
        clientsock.send(bytes(msg,encoding='gbk'))
        recvdata = clientsock.recv(1024)
        res = str(recvdata,encoding='gbk')
        clientsock.close()
        return res

    # read in-hive temp and humidity
    def readSHT(self):
        return self.sht.read_all()   #[temp, humid]

    def readMic(self, port:int):
        # sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
        # sudo pip3 install pyaudio
        # sudo apt-get install python3-dev
        # https://www.raspberrypi.org/forums/viewtopic.php?t=25173
        1
        # TODO: contineously recordinf and info extraction. 



if __name__ == '__main__':
    reader = DataReader()
    interval = 3 * 60 # 15 min
    max_buffer = 2000  # store at most 2000 node when wifi disconnected. About 20 days
    buff = []  # buffer list for data sending failed.
    
    while 1:
        data = reader.read()
        success = reader.toAWS(data)

        # if internet connected
        if success:
            # check and send the buffer
            while len(buff) != 0:
                reader.send_buffer(buff)
        # if not connected, save to buffer
        else:
            if len(buff) >= max_buffer:
                buff.pop(0)
            buff.append(data)
            
                
        print(success)
        sleep(interval)

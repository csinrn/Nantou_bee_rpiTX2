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
        # json = '{ "timestamp": "'+ str(timestamp) + '",   \
        #           "weight": "' + str(1) +  '",     \
        #           "temp": "' + str(shtd[0]) + '",  \
        #           "hum": "'  + str(shtd[1]) + '"}' 
        json = f'"timestamp": "{timestamp}", "weight": {scaled}, "temp": {shtd[0]}, "hum": {shtd[1]}'
        json = "{" + json + "}"
        return json

    # send to AWS   ####### TODO: no connection. what is shadow and green grass, insert datas 
    def toAWS(self, msg:str):
        if not self.mqttClient.connect():
            return False
        #msg = "{ \"timestamp\": {t}, \"weight\": {w}}".format(t=timestamp, w=weight)
        # msg = f'{ "timestamp": {timestamp}, "weight": {weight}}'
        # msg= '{ "timestamp": "'+ str(timestamp) + '", "weight": ' + str(1) + ' }'
        self.mqttClient.publish(self.channel, msg, 1)
        print(msg)
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
    # test scale
    while 1:
    	#print(reader.TCPsend('ACK\r\n'))
    
    # test temp
        #print(reader.readSHT())

    # test AWS
        datas = reader.read()
        stat = reader.toAWS(datas)
        print(stat)
        sleep(2)

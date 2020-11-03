import RPi.GPIO as GPIO                   #Import GPIO library
import time					              #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import datetime
# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering
GPIO.cleanup()

# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("ClientID")
# myMQTTClient.configureEndpoint("a1ocikpeg4zf0y-ats.iot.us-east-2.amazonaws.com", 8883)
myMQTTClient.configureEndpoint("a1ocikpeg4zf0y-ats.iot.us-east-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials("./AmazonRootCA1.pem", "./781f626098-private.pem.key", "781f626098-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

#connect and publish
myMQTTClient.connect()
#myMQTTClient.publish("xxxx/info", "connected", 0)
TRIG = 23                                  	#Associate pin 23 to TRIG
ECHO = 24                                  	#Associate pin 24 to ECHO

while 1:
    weight = 1
    timestamp = datetime.datetime.now()
    b="\""
    #msg = "{ \"timestamp\": {t}, \"weight\": {w}}".format(t=timestamp, w=weight)
    #msg = f'{ "timestamp": {timestamp}, "weight": {weight}}'
    msg= '{ "timestamp": "'+ str(timestamp) + '", "weight": ' + str(weight) + ' }'
    myMQTTClient.publish("weightData", msg, 1)
    print(msg)
    sleep(4)
'''
GPIO.setup(TRIG,GPIO.OUT)                 #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)                  #Set pin as GPIO in
while 1:

  GPIO.output(TRIG, False)                 #Set TRIG as LOW
  time.sleep(2)                            		#Delay of 2 seconds

  GPIO.output(TRIG, True)                  #Set TRIG as HIGH
  time.sleep(0.00001)                      	#Delay of 0.00001 seconds
  GPIO.output(TRIG, False)                 #Set TRIG as LOW

  while GPIO.input(ECHO)==0:           #Check whether the ECHO is LOW
    pulse_start = time.time()              	#Saves the last known time of LOW pulse
  while GPIO.input(ECHO)==1:           #Check whether the ECHO is HIGH
    pulse_end = time.time()                	#Saves the last known time of HIGH pulse

  #Get pulse duration to a variable
  pulse_duration = pulse_end - pulse_start
  distance = pulse_duration * 17150          #Multiply pulse duration by 17150 to get distance
  distance = round(distance, 2)              #Round to two decimal points
  if distance > 2 and distance < 400:
    payload = '{"Distance":'+ str(distance) +'}'
    print payload
    myMQTTClient.publish("makerdemy/data", payload, 0)
  sleep(4)
'''

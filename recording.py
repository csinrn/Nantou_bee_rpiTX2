import boto3
import pyaudio
import wave
from botocore.exceptions import ClientError
import datetime
import os
from time import sleep

chunk = 512   
format_ = pyaudio.paInt16     # 16bit 採樣
channels = 1
rate = 44100 # 16000 
time = 1* 60     # length of one record in seconds
record_interval = 1 *60* 60 - time       # interval between two records in seconds

def list_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'),  p.get_device_info_by_host_api_device_index(0, i).get('defaultSampleRate'))
    p.terminate()

def record(time=5*60, device_index=0):
    audio = pyaudio.PyAudio()
    print('Record start')
    wavstream = audio.open(format=format_,
                            channels=channels,
                            rate=rate,
                            input=True,
                            frames_per_buffer=chunk, 
                            input_device_index=device_index)
    count = 0
    buff = []
    while count < int(rate / chunk * time):
        t = wavstream.read(chunk, exception_on_overflow=False)
        buff.append(t)
        count += 1

    samplesize = audio.get_sample_size(format_)
    wavstream.stop_stream()
    wavstream.close()
    audio.terminate()

    return buff, samplesize

def savewav(buff, samplesize, filename):
    wavfile = wave.open(filename, 'wb')
    wavfile.setnchannels(channels)
    wavfile.setsampwidth(samplesize)
    wavfile.setframerate(rate)
    wavfile.writeframes(b''.join(buff))
    wavfile.close()

def upload_file(file_name, bucket='bee2audio', object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        e = s3_client.upload_file(file_name, bucket, object_name)
    except Exception as e:
        print(e)
        return False
    return True

#time = 1 * 60
#record_interval = 15 * 60
if __name__ == '__main__':
    last_record = datetime.datetime.now() - datetime.timedelta(seconds=time)
    fail_sent_file_list = []
    print('Start')
    list_devices()
    while 1:
        sleep(1)
        delta = datetime.datetime.now() - last_record 
        if delta.seconds%(60*10)==0:
            print('time delta:', delta)
        if delta.seconds >= record_interval:
            # record and save wav
            filename = 'bee2-1/' + datetime.datetime.now().strftime("bee2-1-%Y-%m-%d_%H-%M-%S") + '.wav'
            print(filename)
            buf, samplesize = record(time=time, device_index=2)
            savewav(buf, samplesize, filename)
            # update time
            last_record = datetime.datetime.now()

            # send to aws s3 (credientaion placed at ~/.aws/credientials, transmitted by scp)
            success = upload_file(filename)
            if success:
                # delete file
                print('Send success ' + filename) 
                # os.remove(filename)
                # resend files
                for f in fail_sent_file_list:
                    s = upload_file(f)
                    if s:
                        print('Successfuly resend file ' + f)
                        fail_sent_file_list.remove(f)
                        # os.remove(filename)
                    else:
                        print('Resend ' + f + ' failed')
                        break

            else:
                fail_sent_file_list.append(filename)
                print('Send failed ' + filename + ', resend list len: ', len(fail_sent_file_list) )
                # buffered, and send later

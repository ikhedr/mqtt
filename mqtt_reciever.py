import time
import paho.mqtt.client as paho

broker = "192.168.1.6"
columns = ['Stationid,', 'binid,', 'partno,', 'distance']
summerized_data = {}


# define callback
def on_message(client, userdata, message):
    time.sleep(1)
    instance_data = {}
    if message:
        message = str(message.payload.decode("utf-8")).split()
        if len(message) == 4:
            for i in range(0, len(columns)):
                instance_data[columns[i]] = message[i]
                i = i + 1
        else:
            print("data missing from the payload. Checkout the sensor output.")
            return 1
    else:
        print("Didn't recieve message. Checkout the sensor output.")
        return 1
    print("received message = {0}".format(instance_data))


client = paho.Client(
    "client-001")  # create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
######Bind function to callback
client.on_message = on_message
#####
print("connecting to broker ", broker)
client.connect(broker, 1883)  # connect
client.loop_start()  # start loop to process received messages
print("subscribing ")
client.subscribe("test/message")  # subscribe
time.sleep(6)
client.disconnect()  # disconnect
client.loop_stop()  # loop_forever()

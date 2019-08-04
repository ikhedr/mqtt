#!/usr/bin/env python3

import socket
import uuid
import paho.mqtt.client as mqtt
import asyncio
import time

client_id = 'paho-mqtt-python'
topic = "test/message"
print("Using client_id: {0} \n topic: {1} ".format(client_id, topic))


class AsyncioHelper:
    def __init__(self, loop, client):
        self.loop = loop
        self.client = client
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):
        print("Socket opened")

        def cb():
            print("Socket is readable, calling loop_read")
            client.loop_read()

        self.loop.add_reader(sock, cb)
        self.misc = self.loop.create_task(self.misc_loop())

    def on_socket_close(self, client, userdata, sock):
        print("Socket closed")
        self.loop.remove_reader(sock)
        self.misc.cancel()

    def on_socket_register_write(self, client, userdata, sock):
        print("Watching socket for writability.")

        def cb():
            print("Socket is writable, calling loop_write")
            client.loop_write()

        self.loop.add_writer(sock, cb)

    def on_socket_unregister_write(self, client, userdata, sock):
        print("Stop watching socket for writability.")
        self.loop.remove_writer(sock)

    async def misc_loop(self):
        print("misc_loop started")
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
        print("misc_loop finished")


class AsyncMqttExample:
    def __init__(self, loop):
        self.loop = loop

    def on_connect(self, client, userdata, flags, rc):
        print("Subscribing")
        client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        print("Got message: {}".format(msg.decode("utf-8")))
        if not self.got_message:
            print("Got unexpected message: {}".format(msg.decode()))
        else:
            self.got_message.set_result(msg.payload)

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def main(self):
        self.disconnected = self.loop.create_future()
        self.got_message = None

        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        aioh = AsyncioHelper(self.loop, self.client)

        self.client.connect('192.168.1.6', 1883)
        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
        await asyncio.sleep(5)

        self.client.disconnect()
        print("Disconnected: {}".format(await self.disconnected))


print("Starting")
loop = asyncio.get_event_loop()
loop.run_until_complete(AsyncMqttExample(loop).main())
loop.close()
print("Finished")

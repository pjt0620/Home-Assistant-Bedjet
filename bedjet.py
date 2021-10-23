import pygatt
from binascii import hexlify
import paho.mqtt.client as mqtt 
import time
import sys
import math
import datetime

mqttBroker = "homeassistant.local" 
mqttUser = "homeassistant"
mqttPassword = ""
mqttPort = 1883
bedjetMac = ''

client = mqtt.Client()			
client.username_pw_set(username=mqttUser,password=mqttPassword)
client.connect(mqttBroker, mqttPort, 60)
client.subscribe("bedjet/#")

class mode:
	off = 0x01
	cool = 0x02
	heat = 0x03
	turbo = 0x04
	dry = 0x05
	ext_ht = 0x06
	
class control:
	fan_up = 0x10
	fan_down = 0x11
	temp_up = 0x12
	temp_down = 0x13
	
class preset:
	m1 = 0x20
	m2 = 0x21
	m3 = 0x22

class bedjet:
	global client
	def __init__(self):
		self.adapter = pygatt.backends.GATTToolBackend()
		self.temp_actual = None
		self.temp_setpoint = None
		self.time = None
		self.timestring = None
		self.fan = None
		self.mode = None
		self.devname = None
		try:
			self.adapter.stop()
		except:
			pass
		self.adapter.start()
		trycount = 0
		while trycount < 4:
			try:
				self.device = self.adapter.connect(bedjetMac)
				break
			except pygatt.exceptions.NotConnectedError:
				print('Failed to connect to ' + bedjetMac + ' try ' + str(trycount + 1) + ' of 4' )
				trycount = trycount + 1
		if trycount == 4:
			print('Failed to connect to ' + bedjetMac + ' Aborting ')
			sys.exit(0)
			
		self.devname = self.device.char_read("00002001-bed0-0080-aa55-4265644a6574").decode()
		self.device.subscribe("00002000-bed0-0080-aa55-4265644a6574", callback=self.handle_data)
				
	def handle_data(self, handle, value):
		self.temp_actual = round(((int(value[7]) - 0x26) + 66) - ((int(value[7]) - 0x26) / 9))
		self.temp_setpoint = round(((int(value[8]) - 0x26) + 66) - ((int(value[8]) - 0x26) / 9))
		self.time = (int(value[4]) * 60 *60) + (int(value[5]) * 60) + int(value[6])
		self.timestring = str(int(value[4])) + ":" + str(int(value[5])) + ":" + str(int(value[6]))
		self.fan = int(value[10]) * 5
		if value[14] == 0x50 and value[13] == 0x14:
			self.mode = "off"
		if value[14] == 0x34:
			self.mode = "cool"
		if value[14] == 0x56:
			self.mode = "turbo"
		if value[14] == 0x50 and value[13] == 0x2d:
			self.mode = "heat"
		if value[14] == 0x3e:
			self.mode = "dry"
		if value[14] == 0x43:
			self.mode = "ext ht"
		client.publish("bedjet/" + self.devname + "/temp_actual", self.temp_actual)
		client.publish("bedjet/" + self.devname + "/temp_setpoint", self.temp_setpoint)
		client.publish("bedjet/" + self.devname + "/time", self.time)
		client.publish("bedjet/" + self.devname + "/timestring", self.timestring)
		client.publish("bedjet/" + self.devname + "/fan", self.fan)
		client.publish("bedjet/" + self.devname + "/mode", self.mode)
	
	def set_mode(self, mode):
		self.device.char_write( '00002004-bed0-0080-aa55-4265644a6574', [0x01,mode])
		
	def press_control(self, control):
		self.device.char_write( '00002004-bed0-0080-aa55-4265644a6574', [0x01,control])
		
	def press_preset(self, preset):
		self.device.char_write( '00002004-bed0-0080-aa55-4265644a6574', [0x01,preset])

	def set_fan(self, fanPercent):
		if fanPercent >= 5 and fanPercent <= 100:
			self.device.char_write( '00002004-bed0-0080-aa55-4265644a6574', [0x07,round(fanPercent/5)-1])
		
	def set_temp(self, temp):
		if temp >= 66 and temp <= 104:
			temp_byte = ( int((temp - 60) / 9) + (temp - 66))  + 0x26
			self.device.char_write( '00002004-bed0-0080-aa55-4265644a6574', [0x03,temp_byte])
		
	def set_time(self, minutes):
		self.device.char_write( '00002004-bed0-0080-aa55-4265644a6574', [0x02, minutes // 60, minutes % 60])
		
		
		
bjet = bedjet()

def on_message(client, userdata, message):
	splttopic = message.topic.split('/')
	command = splttopic[2]
	if splttopic[1] == bjet.devname:
		if command == 'setmode':
			if message.payload == b'off':
				bjet.set_mode(mode.off)
			if message.payload == b'cool':
				bjet.set_mode(mode.cool)
			if message.payload == b'heat':
				bjet.set_mode(mode.heat)
			if message.payload == b'turbo':
				bjet.set_mode(mode.turbo)
			if message.payload == b'dry':
				bjet.set_mode(mode.dry)
			if message.payload == b'ext_ht':
				bjet.set_mode(mode.ext_ht)
				
		if command == 'control':
			if message.payload == b'fan_up':
				bjet.set_mode(control.fan_up)
			if message.payload == b'fan_down':
				bjet.set_mode(control.fan_down)
			if message.payload == b'temp_up':
				bjet.set_mode(control.temp_up)
			if message.payload == b'temp_down':
				bjet.set_mode(control.temp_down)

		if command == 'preset':
			if message.payload == b'm1':
				bjet.set_mode(preset.m1)
			if message.payload == b'm2':
				bjet.set_mode(preset.m2)
			if message.payload == b'm3':
				bjet.set_mode(preset.m3)
				
		if command == 'set_temp':
			bjet.set_temp(int(message.payload))
			
		if command == 'set_fan':
			bjet.set_fan(int(message.payload))

		if command == 'set_time':
			bjet.set_time(int(message.payload))

client.on_message=on_message 
    
print('Start')
try:
	client.loop_forever()	
except KeyboardInterrupt:
	bjet.adapter.stop()
	sys.exit(0)

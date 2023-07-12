import json
import math
import threading

from inputs import get_gamepad

PATH = "C:\\tmp\\xRCsim\\"

X,Y,Z = 0,1,2

class BoneID:
	INFO = 0
	BODY = 1
	LIFT = 3
	SLIDE1 = 4
	SLIDE2 = 5

class Time:
	GAME = 2.5 * 60 * 1000
	AUTO = 15 * 1000
	TELEOP = (2.5 * 60 - 15) * 1000

class GameHandler():
	def __init__(self):
		self.buttons = {
			"a": 0,
			"b": 0,
			"x": 0,
			"y": 0,
			"dpad_down": 0,
			"dpad_up": 0,
			"dpad_left": 0,
			"dpad_right": 0,
			"bumper_l": 0,
			"bumper_r": 0,
			"stop": 0,
			"restart": 0,
			"right_y": 0,
			"right_x": 0,
			"left_y": 0,
			"left_x": 0,
			"trigger_l": 0,
			"trigger_r": 0,
		}

		self.time_left_ms = 0
		self.robot = {}
		self.game_elements = []

	def Reset(self):
		self.buttons = {
			"a": 0,
			"b": 0,
			"x": 0,
			"y": 0,
			"dpad_down": 0,
			"dpad_up": 0,
			"dpad_left": 0,
			"dpad_right": 0,
			"bumper_l": 0,
			"bumper_r": 0,
			"stop": 0,
			"restart": 0,
			"right_y": 0,
			"right_x": 0,
			"left_y": 0,
			"left_x": 0,
			"trigger_l": 0,
			"trigger_r": 0,
		}

	def Format(self):
		return "\n".join(f"{key}={value}" for key,value in self.buttons.items())

	def Write(self):
		with open(PATH + "Controls.txt","w+") as file:
			file.write(self.Format())

	def ReadAll(self):
		return self.ReadTime(), self.ReadRobot(), self.ReadElements()

	def ReadTime(self):
		try:
			with open(PATH + "GAME_STATE.txt","r") as file:
				self.time_left_ms = float(file.read().split("Time Left (ms) =")[-1].split("\n")[0])
		except:
			pass

		return self.time_left_ms

	def ReadRobot(self):
		try:
			with open(PATH + "myRobot.txt","r") as file:
				self.robot = json.load(file)
		except json.JSONDecodeError:
			pass

		return self.robot

	def ReadElements(self):
		try:
			with open(PATH + "GameElements.txt","r") as file:
				self.game_elements = json.load(file)
		except json.JSONDecodeError:
			pass

		return self.game_elements

class XboxController(object):
	MAX_TRIG_VAL = math.pow(2, 8)
	MAX_JOY_VAL = 32768

	def __init__(self):

		self.LeftJoystickY = 0
		self.LeftJoystickX = 0
		self.RightJoystickY = 0
		self.RightJoystickX = 0
		self.LeftTrigger = 0
		self.RightTrigger = 0
		self.LeftBumper = 0
		self.RightBumper = 0
		self.A = 0
		self.X = 0
		self.Y = 0
		self.B = 0
		self.LeftThumb = 0
		self.RightThumb = 0
		self.Back = 0
		self.Start = 0
		self.LeftDPad = 0
		self.RightDPad = 0
		self.UpDPad = 0
		self.DownDPad = 0

		self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
		self._monitor_thread.daemon = True
		self._monitor_thread.start()


	def read(self): # return the buttons/triggers that you care about in this methode
		return {
			"a": self.A,
			"b": self.B,
			"x": self.X,
			"y": self.Y,
			"dpad_down": 0,
			"dpad_up": 0,
			"dpad_left": 0,
			"dpad_right": 0,
			"bumper_l": 0,
			"bumper_r": 0,
			"stop": self.Back,
			"restart": self.Start,
			"right_y": self.RightJoystickY,
			"right_x": self.RightJoystickX,
			"left_y": -self.LeftJoystickY,
			"left_x": self.LeftJoystickX,
			"trigger_l": self.LeftTrigger,
			"trigger_r": self.RightTrigger,
			"auto_score": self.RightBumper,
			"auto_aim": self.LeftBumper,
			"scoring_up": self.UpDPad,
			"scoring_down": self.DownDPad,
			"scoring_left": self.LeftDPad,
			"scoring_right": self.RightDPad,
		}

	def _monitor_controller(self):
		while True:
			events = get_gamepad()
			for event in events:
				if event.code == 'ABS_Y':
					self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
				elif event.code == 'ABS_X':
					self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
				elif event.code == 'ABS_RY':
					self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
				elif event.code == 'ABS_RX':
					self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
				elif event.code == 'ABS_Z':
					self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
				elif event.code == 'ABS_RZ':
					self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
				elif event.code == 'BTN_TL':
					self.LeftBumper = event.state
				elif event.code == 'BTN_TR':
					self.RightBumper = event.state
				elif event.code == 'BTN_SOUTH':
					self.A = event.state
				elif event.code == 'BTN_NORTH':
					self.Y = event.state #previously switched with X
				elif event.code == 'BTN_WEST':
					self.X = event.state #previously switched with Y
				elif event.code == 'BTN_EAST':
					self.B = event.state
				elif event.code == 'BTN_THUMBL':
					self.LeftThumb = event.state
				elif event.code == 'BTN_THUMBR':
					self.RightThumb = event.state
				elif event.code == 'BTN_SELECT':
					self.Back = event.state
				elif event.code == 'BTN_START':
					self.Start = event.state
				elif event.code == 'ABS_HAT0X':
					self.LeftDPad = int(event.state < 0)
					self.RightDPad = int(event.state > 0)
				elif event.code == 'ABS_HAT0Y':
					self.UpDPad = int(event.state < 0)
					self.DownDPad = int(event.state > 0)
				# print(event.code, event.state)
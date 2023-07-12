from handler import *

import GameMaker as gm
from GameMaker.Assets import *

SCORING = [
	[0.91, 0.41, -0.19, -0.73, -1.29, -1.88, -2.42, -2.96, -3.55],
	[-7.2, -7.6, -8],
	-6.5,
]

class Node:
	LOW = 0
	MID = 1
	HIGH = 2

class RobotController():
	def __init__(self,blue = False):
		self.pos = [0,0,0]
		self.vel = [0,0,0]

		self.rot = [0,0,0]
		self.rot_vel = [0,0,0]

		self.blue = blue
	
		self.scale = -1 if self.blue else 1

	def Update(self,robot):
		self.pos = robot["myrobot"][BoneID.BODY]["global pos"]
		self.vel = robot["myrobot"][BoneID.BODY]["velocity"]

		self.rot = robot["myrobot"][BoneID.BODY]["global rot"]
		self.rot_vel = robot["myrobot"][BoneID.BODY]["rot velocity"]

	def MoveTo(self,target):
		# Go to Target

		return {
			"left_y": -(target[Z] - self.pos[Z] - self.vel[Z] / 6) * 3 * self.scale,
			"left_x": (target[X] - self.pos[X] - self.vel[X] / 6) * 3 * self.scale,
		}

	def TurnTo(self,rot_target):
		rot_move = rot_target - (self.rot[Y] + self.rot_vel[Y] * 10) 

		return {
			"right_x": rot_move / 10
		}

	def AngleTo(self,x,y):
		ang = 360 - math.degrees(math.atan2( y - self.pos[Z], x - self.pos[X] ))

		while ang > 360: ang -= 360
		while ang < 0: ang += 360

		return ang

	def Distance(self,target):
		return math.sqrt( pow(target[X] - self.pos[X],2) + pow(target[Z] - self.pos[Z],2) )

	def AtTarget(self,target,rot_target=None,tolerance=1):
		if rot_target == None: rot_target = self.rot[Y]
		return self.Distance(target) < 0.06 and abs(rot_target - self.rot[Y]) < tolerance

class UI():
	def __init__(self):
		self.button_size = 50

		self.window = gm.Window([self.button_size * 9, self.button_size * 3],"xRC Auto Scorer")
		self.buttons = [Button([self.button_size * (i % 9), self.button_size * (i // 9), self.button_size, self.button_size],outline=0,text=self.text(i),foreground_color=self.color(i),hovered_color=self.darken(i)) for i in range(9 * 3)]

		self.selected_node = 8 # Left to Right -> 0 to 8
		self.height = Node.HIGH

	def text(self,i):
		if i // 9 == 0:
			return "H"
		elif i // 9 == 1:
			return "M"

		return "L"

	def color(self,i):
		if self.ConeNode(i):
			return (252, 186, 3)
		return (130, 7, 186)

	def darken(self,i):
		if self.ConeNode(i):
			return (232, 166, 0)
		return (110, 0, 166)

	def selected(self,i):
		if self.ConeNode(i):
			return (172, 106, 0)
		return (70, 0, 126)

	def ConeNode(self,i):
		return i % 9 in [0,2,3,5,6,8] and (i // 9) < 2

	def run(self):
		while self.window.RUNNING:
			for i in range(len(self.buttons)):
				if self.buttons[i].status == gm.PRESSED:
					self.selected_node = 8 - (i % 9)
					self.height = 2 - (i // 9)

				if (8 - self.selected_node) + (2 - self.height) * 9 == i:
					self.buttons[i].foreground_color = self.selected(i)
					self.buttons[i].outline = 2
				else:
					self.buttons[i].foreground_color = self.color(i)
					self.buttons[i].outline = 0

			self.window.draw(self.buttons)
			self.window.update()

game = GameHandler()
robot_controller = RobotController()

controller = XboxController()

ui = UI()

def main():
	game.Reset()
	game.Write()

	target = [0,0,0]
	rot_target = 0

	tolerance = 0.1

	scoring_changer = {
		"scoring_up": 0,
		"scoring_down": 0,
		"scoring_left": 0,
		"scoring_right": 0,
	}

	try:
		while ui.window.RUNNING:
			try:
				game.ReadRobot()
			except PermissionError:
				continue

			buttons = controller.read()

			for key in scoring_changer:
				if buttons[key]:
					scoring_changer[key] += 1
				else:
					scoring_changer[key] = 0

			if scoring_changer["scoring_up"] == 1 and ui.height < 2:
				ui.height += 1
			if scoring_changer["scoring_down"] == 1 and ui.height > 0:
				ui.height -= 1
			if scoring_changer["scoring_right"] == 1 and ui.selected_node > 0:
				ui.selected_node -= 1
			if scoring_changer["scoring_left"] == 1 and ui.selected_node < 8:
				ui.selected_node += 1

			for key in ["right_x","right_y","left_x","left_y"]:
				if -tolerance < buttons[key] < tolerance:
					buttons[key] = 0

			target = [
				SCORING[0][ui.selected_node], 	# X
				0,								# Y
				SCORING[2], 					# Z
			]

			rot_target = robot_controller.AngleTo(
				SCORING[0][ui.selected_node],
				SCORING[1][ui.height]
			)

			robot_controller.Update(game.robot)

			if buttons["auto_score"]:
				buttons["left_x"] /= 1.5
				buttons["left_y"] /= 1.5

				buttons["right_x"] /= 2

				buttons[["dpad_down","dpad_left","dpad_right"][ui.height]] = 1

				cone_mode = ui.ConeNode((2 - ui.height) * 9 + ui.selected_node)

				if robot_controller.AtTarget(target,rot_target,1 if cone_mode else 3):
					if cone_mode:
						buttons["trigger_l"] = 1
					else:
						buttons["a"] = 1

				buttons |= {button: buttons[button] + value for button, value in robot_controller.MoveTo(target).items()}
				buttons |= {button: buttons[button] + value for button, value in robot_controller.TurnTo(rot_target).items()}

			elif buttons["auto_aim"]:
				buttons["right_x"] /= 1.5

				buttons["dpad_up"] = 1

				buttons |= {button: buttons[button] + value for button, value in robot_controller.TurnTo(270).items()}


			game.buttons = buttons
	
			game.Write()

	except KeyboardInterrupt:
		pass

	game.Reset()
	game.Write()
	

if __name__ == '__main__':
	thread = threading.Thread(target=main)
	thread.start()

	ui.run()

	thread.join()
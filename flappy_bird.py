#importing all the required libraries
import pygame
import neat
import time
import os
import random

#Set the Screen Width

WIN_WIDHT = 600
WIN_HEIGHT = 800

#Importing all the Required Images

Bird_Image = [pygame.transform.scale2x(pygame.image.load(os.path("images","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path("images","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path("images","bird3.png")))]
Pipe_Image = [pygame.transform.scale2x(pygame.image.load(os.path("images","pipe.png")))]
Base_Image = [pygame.transform.scale2x(pygame.image.load(os.path("images","base.png")))]
BG_Image = [pygame.transform.scale2x(pygame.image.load(os.path("images","bg.png")))]

#Class Bird to handle all the operation of Bird
class Bird:
	Images = Bird_Image		#Make a copy of bird Images
	Max_Rotation = 25		#Maximum angle to tilt bird upward or downward
	Rot_Vel = 20			#How much we rorate the bird at each frame or at each time we move the bird
	Animation_Time = 5		#How long an each bird animation will be shown

	def __init__(self,x,y):
		self.x = x					#Starting position of bird
		self.y = y
		self.tilt = 0				#How much an image will be tilted
		self.tick_count = 0			#How Many times we have jumped from last time
		self.vel = 0				#Speed of bird 
		self.height = self.y		#Origin of the bird from where bird is start moving
		self.img_count = 0			#Keep track of the current showing Image
		self.img = self.Images[0]	#Initialize first bird

	def jump(self):
		self.vel = -10.5			#Starting with going Upward i.e -ve direction
		self.tick_count = 0			
		self.height = self.y		

	def move(self):
		self.tick_count +=1			#How Many times we have jumped from last time

		#How many pixel we are moving Up and Down based on the current bird velocity of the bird
		#Intially (-10.5*1 + 1.5*1**2 = -9 )  which results the bird going upward from -10.5 to -9
		displcmnt = self.Rot_Vel*self.tick_count + 1.5*self.tick_count**2
		#Terminal Velocity from which we are not accepting to accelarate any more
		if displcmnt > 16:
			d = 16
		if displcmnt <= 0:		#If you are moving upward just move little more
			d -= 2

		self.y = self.y + displcmnt		#Whatever the Displacement is calculated add to the current position of the bird
		

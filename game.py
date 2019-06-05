# PyGame template.
 
# Import standard modules.
import sys

import random
# Import non-standard modules.
import pygame
from pygame.locals import *

class Object:
	
	def __init__(self, name, size, is_holdable, is_container, is_exit, exit_destination, description, current_coordinates, capacity, portrait="empty.png", room_image="empty.png"):
		self.name = name
		self.image = pygame.image.load(portrait)
		self.room_image = pygame.image.load(room_image)
		self.hold = is_holdable
		self.container = is_container
		self.exit = is_exit
		self.dest = exit_destination
		self.desc = description
		self.coord = current_coordinates
		self.select = False
		self.use = False
		self.size = Rect((current_coordinates), size)
		self.center = self.size.center
		self.contents = []
		self.cap = capacity
		self.open = False
	
	def addToContents(self, item):
		item.size = Rect((self.size[0] + 110*len(self.contents), self.size[1]), (100, 100))
		item.select = False
		item.use = False
		self.contents = self.contents + [item]
	
	def removeFromContents(self, item):
		self.contents.remove(item)
		for x in range(len(self.contents)):
				self.contents[x].size = Rect((self.size[0] + 110*x, self.size[1]), (100, 100))

class Room:
	
	def __init__(self, room_name, room_objects, room_image):
		self.name = room_name
		self.objects = room_objects
		self.image = pygame.image.load(room_image)
		self.select = False



class Game:
	
	def __init__(self, all_rooms):
		self.width = 1600
		self.height = 900
		self.inventory = []
		self.cap = 7
		self.current_room =  all_rooms["outside"]
		self.rooms = all_rooms
		self.second_object = self.rooms["resources"].objects[0]
		self.infobar = Rect(0, self.height-170, self.width, 50)
		self.inventorybar = Rect(0, self.height-120, 860, 120)
		
	def addToInventory(self, item):
		if len(self.inventory) < self.cap:
			item.size = Rect(((20 + 110*len(self.inventory), self.height-110)), (100, 100))
			item.use = False
			self.inventory = self.inventory + [item]
			return(True)
		else:
			return(False)	
			

	def removeFromInventory(self, item):
		self.inventory.remove(item)
		for inv in range(len(self.inventory)):
				self.inventory[inv].size = Rect(((20 + 110*inv, self.height-110)), (100, 100))
			
	def findObjectByName(self, object_name, room):
		for i in room.objects:
			if i.name == object_name:
				return(i)
		
	
	def clickonBoard(self, click):
		#This checks for click, selection, and use effects in the inventory and current room
		print(click)
		for obj in self.inventory + self.current_room.objects:
			if obj.select:
				self.second_object = obj
				if obj.container:
					for content in obj.contents:
						if content.size.collidepoint(click):
							if content.select:
								content.use = True
							else:
								content.select = True
								content.use = False
						else:
							content.select = False
							content.use = False
			if obj.size.collidepoint(click):
				if obj.select:
					obj.use = True
				else:
					obj.select = True
					obj.use = False
					
			else:
				obj.select = False

		print(self.second_object.use)
		print(self.second_object.name)
		
	
	def checkForEffects(self):
		#Apply changes to objects and inventory based on combinations
		for obj in self.current_room.objects + self.inventory:
			if obj.select:
				
				#This is to pick up an item from the room
				if obj.use & obj.hold & (obj in self.current_room.objects):
					if self.addToInventory(obj):
						self.current_room.objects.remove(obj)
						self.second_object = self.rooms["resources"].objects[0]
				
				#This is to check for an exit
				if obj.exit:
					obj.select = False
					self.current_room = self.rooms[obj.dest]
				
				#CABIN - This is to check for effects in the cabin room
				if self.current_room.name == "Cabin":
					
					#CABIN This is to check the effects of the on the fireplace
					if (obj.name == "fireplace"):
						if (self.second_object.desc == "A lit match.") & any(x.name == "bookLovecraft" for x in obj.contents) & (obj.dest=="hell"):
							self.second_object.desc == "A burning match."
							self.removeFromInventory(self.second_object)
							for burn_object in obj.contents:
								if burn_object.name == "bookLovecraft":
									obj.removeFromContents(burn_object)
									obj.room_image = pygame.image.load("cabinFireplaceFire.png")
									obj.desc = "A roaring hearth."
						if (obj.desc == "A roaring hearth.") & any(x.name == "flesh" for x in obj.contents) & any(y.desc == "A bucket filled with water." for y in obj.contents):
							for burn_object in obj.contents:
								if burn_object.name == "flesh":
									obj.removeFromContents(burn_object)
								if burn_object.name == "bucket":
									burn_object.image = pygame.image.load("bucketglue.png")
									burn_object.desc = "A bucket of rawhide glue."
					
					#CABIN This is to move the chair
					if (self.second_object.name == "chair") & self.second_object.use:
						
						#CABIN to underneath the attic entrance
						if (obj.name == "cabinToAttic"):
							obj.exit = True
							self.second_object.room_image = pygame.image.load("cabinChairAttic.png")
							self.second_object.size = Rect((86, 357), (130, 253))
						#CABIN back to the table
						if (obj.name == "table"):
							self.findObjectByName("cabinToAttic", self.current_room).exit = False
							self.second_object.room_image = pygame.image.load("cabinChairTable.png")
							self.second_object.size = Rect((1029, 520), (250, 160))
				
				#BEHIND - This is to check for effects in the behind room
				if self.current_room.name == "Out back":
										
					#BEHIND This is to check if the goat runs away
					if (obj.name=="goat"):
						if any(x.name == "rope" for x in self.current_room.objects):
							pass
						else:
							self.current_room.objects.remove(obj)										
					#BEHIND This is to fix the broken wagon
					if (self.second_object.name == "wheel") & self.second_object.use & (obj.name == "wagon"):
						self.removeFromInventory(self.second_object)
						obj.desc = "A functional wagon."
						obj.container = True
						obj.cap = 2
						obj.room_image = pygame.image.load("behindWagonFixed.png")
					
					#BEHIND This is to push the wagon and create the loose dirt.
					if (obj.name == "wagon") & obj.use & (obj.desc == "A functional wagon."):
						obj.desc = "A wagon."
						obj.size[0] = 0
						self.current_room.objects = self.current_room.objects + [self.rooms["resources"].objects[2]]
					#BEHIND This is to use the shovel to uncover the underground entrance
					if (self.second_object.name == "shovel") & self.second_object.use:
						if obj.name == "loosedirt":
							obj.select = False
							self.second_object = self.rooms["resources"].objects[0]
							obj.name = "behindToDungeon"
							obj.exit = True
							obj.dest = "dungeon"
							obj.room_image = pygame.image.load("behindLoosedirt.png")
						if obj.desc == "A locked chicken coop. It needs a key.":
							obj.desc = "A chicken coop."
					
					#This is to get a chicken from the unlocked chicken coop
					if (obj.desc == "A chicken coop.") & (obj.cap > 0) & obj.use:
						 if (self.addToInventory(self.rooms["resources"].objects[5])):
							 obj.cap -= 1
						
				#SIDE - This is to check for effects on the side of the house
				if self.current_room.name == "Side":
					
					#SIDE Use the ladder to get to the ROOF
					if (obj.name=="ladder") & obj.use:
						obj.select = False
						obj.use = False
						self.current_room = self.rooms["roof"]
				
				#ROOF - This is to check for effects on the roof
				if self.current_room.name == "Roof":
					
					#ROOF Use the ladder to get to the SIDE
					if (obj.name=="ladder") & obj.use:
						obj.select = False
						obj.use = False
						self.current_room = self.rooms["side"]
						self.second_object = self.rooms["resources"].objects[0]
					
					#ROOF Remove lid if elastic is gone
					if (obj.name=="chimneylid"):
						if any(x.name == "elastic" for x in self.current_room.objects):
							pass
						else:
							self.current_room.objects.remove(obj)	
					
					#ROOF This is to use the combined rope and icehook to unclog the bats from the chimney
					if (obj.name=="chimney") & (self.second_object.name=="ropeicehook") & self.second_object.use:
							self.findObjectByName("fireplace", self.rooms["cabin"]).dest = "hell"
							
				#UNIVERSAL SPECIAL EFFECTS
						
				#This is to check if the bucket is going to be used
				if self.second_object.use & (self.second_object.name == "bucket") & (self.second_object.desc == "A bucket filled with water.") & (obj.container == False) & (obj != self.second_object):
					self.second_object.desc = "An empty bucket."
					self.second_object.image = pygame.image.load("bucketempty.png")
					if (obj.name=="drain") & (self.current_room.name=="Roof"):
						self.findObjectByName("barrel", self.rooms["outside"]).addToContents(self.rooms["resources"].objects[6])
					
				#This is to combine the icehook and the rope
				if (self.second_object.name == "rope") & self.second_object.use & (obj.name == "icehook") & obj.select & (obj in self.inventory):
					self.removeFromInventory(self.second_object)
					self.removeFromInventory(obj)
					self.addToInventory(self.rooms["resources"].objects[4])
				
			#This is to get flesh and hair from the swamp hide
			if (self.second_object.name == "knife") & self.second_object.use & (obj.name == "hide") & (obj.desc == "A tanning hide.") & obj.select:
				if (self.addToInventory(self.rooms["resources"].objects[3])):
					obj.desc = "A tanning hide, crudely scraped."
				
			#This is to make the match and elastic lighter
			if (self.second_object.name == "elastic") & self.second_object.use & (obj.name == "match") & obj.select & (obj in self.inventory):
				self.removeFromInventory(self.second_object)
				self.removeFromInventory(obj)
				self.addToInventory(self.rooms["resources"].objects[1])
				
			#This is to light a match
			if (self.second_object.name == "elasticmatch") & self.second_object.use & (obj.desc == "An unlit match.") & obj.select & (obj in self.inventory):
				obj.desc = "A lit match."
				obj.image = pygame.image.load("match.png")
				obj.use = True
				
			#This is to discard a burnt match and generate a new one at a random location
			if (obj.desc == "A burnt match.") & obj.use:
				obj.desc = "An unlit match."
				obj.image = pygame.image.load("match.png")
				obj.size = Rect((10,3), (150, 170))
				self.removeFromInventory(obj)
				random_room = random.choice(list(self.rooms.keys()))
				if random_room == "resources":
					random_room = "cabin"					
				self.rooms[random_room].objects = self.rooms[random_room].objects + [obj]
				
			#This is to extinguish matches if they're not being used
			if (obj.desc == "A lit match.") & (obj.use == False) and (obj in self.inventory):
				obj.desc = "A burnt match."
				
			#This is to check for effects on containers
			if obj.container:
				print(obj.cap > len(obj.contents))
				if obj.cap > len(obj.contents):
					print(obj.select & self.second_object.use & (self.second_object in self.inventory))
					if obj.select & self.second_object.use & (self.second_object in self.inventory):
						self.removeFromInventory(self.second_object)
						obj.addToContents(self.second_object)
				for content in obj.contents:
					if content.use:
						if (self.addToInventory(content)):
							obj.removeFromContents(content)
				

		pygame.mouse.get_rel()

		
			

g = Game({
  
"cabin" : 
	Room(
	"Cabin",
	[
	Object("cabinToAttic", (90,60), False, False, False, "attic", "To the attic.", (108, 64), 0, room_image="cabinAttic.png"),
	Object("chair", (250,160), False, False, False, "nowhere", "A chair.", (1029, 520), 0, room_image="cabinChairTable.png"),
	Object("cabinToDoor", (1600,30), False, False, True, "door", "To the cabin door.", (0, 700),0), 
	Object("wheel", (213,150), True, False, False, "nowhere", "A spinning wheel.", (129, 546),0, portrait="wheel.png", room_image="cabinWheel.png"),
	Object("match", (44,14), True, False, False, "nowhere", "An unlit match.", (1377, 216),0, portrait="match.png",room_image="anywhereMatch.png"),
	Object("fireplace", (400, 245), False, True, False, "nowhere", "A fireplace.", (526, 345), 3, room_image="cabinFireplace.png"),
	Object("cabinet", (210,375), False, True, False, "nowhere", "A simple cabinet.", (1220, 224), 1, room_image="cabinCabinet.png"),
	Object("table", (610,50), False, True, False, "nowhere", "A table.", (877, 650), 2),
	Object("knife", (40,203), True, False, False, "nowhere", "A small blade. Crude, yet sharp.", (1324, 519), 0, portrait="knife.png", room_image="cabinKnife.png")
	], 
	"cabin.png"
),

"door" : 
	Room(
	"Cabin door",
	[
	Object("doorToCabin", (640,30), False, False, True, "cabin", "To the hearth.", (0, 450), 0),
	Object("doorToOutside", (100,220), False, False, True, "outside", "To outside.", (144, 80), 0), 
	Object("bookLovecraft", (100,100), True, False, False, "nowhere", "A book of Lovecraft stories.", (1000, 300), 0, portrait="book.png", room_image="book.png")
	], 
	"door.jpg"
),

"attic" : 
	Room(
	"Attic",
	[
	Object("atticToCabin", (1600,30), False, False, True, "cabin", "To the ground floor of the cabin.", (0, 700), 0), 
	Object("match", (44,14), True, False, False, "nowhere", "An unlit match.", (150, 170), 0, portrait="match.png",room_image="anywhereMatch.png")
	], 
	"attic.jpg"
),

"outside" : 
	Room(
	"Outside",
	[
	Object("outsideToCabin", (105,200), False, False, True, "cabin", "To the ground floor of the cabin.", (820, 367), 0),
	Object("outsideToBehind", (590,200), False, False, True, "behind", "To behind the cabin.", (1039, 350), 0),
	Object("outsideToSwamp", (1600,30), False, False, True, "swamp", "To the swamp.", (0, 700),0),
	Object("outsideToSide", (300,200), False, False, True, "side", "To the side of the cabin.", (400, 370),0),
	Object("icehook", (100,80), True, False, False, "nowhere", "An ice hook.", (1158, 658),0, portrait="icehook.png", room_image="outsideIcehook.png"),
	Object("drain", (26,354), False, False, False, "nowhere", "A drain.", (714, 114), 0, room_image="outsideDrain.png"),
	Object("barrel", (84,144), False, True, False, "nowhere", "A barrel.", (700, 468), 1, room_image="outsideBarrel.png"),
	], 
	"outside.png"
),

"behind" : 
	Room(
	"Out back",
	[
	Object("behindToOutside", (400,180), False, False, True, "outside", "To the front of the cabin.", (0, 120), 0),
	Object("wagon", (350,200), False, False, False, "nowhere", "A broken wagon.", (182, 346), 0, room_image="behindWagonBroken.png"),
	Object("goat", (136,143), False, False, False, "nowhere", "A goat.", (1024, 286), 0, room_image="behindGoat.png"),
	Object("chickencoop", (210,200), False, False, False, "nowhere", "A locked chicken coop. It needs a key.", (1328, 303), 1, room_image="behindChickencoop.png"),
	Object("deadhorse", (230,150), False, False, False, "nowhere", "A skinned horse.", (656, 356), 0, room_image="behindDeadhorse.png"),
	Object("rope", (60,20), True, False, False, "nowhere", "Rope.", (984, 331), 0, room_image="behindRope.png", portrait="rope.png")	
	], 
	"behind.png"
),

"side" : 
	Room(
	"Side",
	[
	Object("sideToOutside", (1600,30), False, False, True, "outside", "To the front of the cabin.", (0, 700),0),
	Object("ladder", (186,433), False, False, False, "nowhere", "A ladder to the roof.", (814, 0), 0, room_image="sideLadder.png"),
	], 
	"side.png"
),

"roof" : 
	Room(
	"Roof",
	[
	Object("ladder", (570,175), False, False, False, "nowhere", "A ladder.", (72, 387), 0, room_image="roofLadder.png"),
	Object("drain", (140,468), False, False, False, "nowhere", "A drain.", (1413, 429), 0, room_image="roofDrain.png"),
	Object("roofwindow", (407,165), False, False, False, "nowhere", "A window.", (108, 565), 0, room_image="roofWindow.png"),
	Object("chimneylid", (500,70), False, False, False, "nowhere", "A cover for the chimney. It's stuck.", (730, 24), 0, room_image="roofChimneylid.png"),
	Object("chimney", (410,800), False, False, False, "nowhere", "A chimney.", (770, 90), 0, room_image="roofChimney.png"),
	Object("elastic", (51,62), True, False, False, "nowhere", "An elastic band.", (960, 68), 0, portrait="elastic.png", room_image="roofElastic.png")
	], 
	"roof.png"
),

"dungeon" : 
	Room(
	"Dungeon",
	[
	Object("dungeonToBehind", (237,723), False, False, True, "behind", "To behind the cabin.", (1197, 0), 0, room_image="dungeonLadder.png"),
	Object("dungeonToStudy", (30,60), False, False, False, "study", "A door.", (300, 225), 0),
	Object("bucket", (86,114), True, False, False, "nowhere", "A bucket filled with water.", (517, 480), 0, portrait="bucketwater.png", room_image="dungeonBucket.png"),
	Object("drip", (111,400), False, False, False, "nowhere", "A drip from the ceiling.", (520, 73), 0, room_image="dungeonDrip.png")
	], 
	"dungeon.png"
),

"swamp" : 
	Room(
	"Swamp",
	[
	Object("swampToOutside", (1600,30), False, False, True, "outside", "To the front of the cabin.", (0, 700),0),
	Object("shovel", (130,240), True, False, False, "nowhere", "A shovel.", (823, 282), 0, portrait="shovel.png", room_image="swampShovel.png"),
	Object("boat", (712, 224), False, False, False, "nowhere", "A rowboat.", (130,240), 0),
	Object("swamp", (338, 114), False, False, False, "nowhere", "The swamp.", (0,276), 0),
	Object("hide", (376,365), False, False, False, "nowhere", "A tanning hide.", (1065, 255), 0, room_image="swampHide.png")
	], 
	"swamp.png"
),

"resources" : 
	Room(
	"Spare resources",
	[
	Object("Nothing", (0,0), False, False, False, "nowhere", "This resource is a prop.", (0, 0), 0),
	Object("elasticmatch", (40,470), True, False, False, "nowhere", "An elastic band fastened to a match.", (10, 20), 0, portrait="elasticmatch.png"),
	Object("loosedirt", (202,73), False, False, False, "dungeon", "Some loose dirt.", (350, 479), 0),
	Object("flesh", (0,0), True, False, False, "nowhere", "Some hair a bits of flesh.", (0, 0), 0, portrait="flesh.png"),
	Object("ropeicehook", (0,0), True, False, False, "nowhere", "An icehook attached to some rope.", (0, 0), 0, portrait="ropeicehook.png"),
	Object("chicken", (0,0), True, False, False, "nowhere", "A chicken.", (0, 0), 0, portrait="chicken.png"),
	Object("key", (0,0), True, False, False, "nowhere", "A key.", (0, 0), 0, portrait="key.png")
	],
	"behind.jpg"
)

})

def update(dt):
	"""
	Update game. Called once per frame.
	dt is the amount of time passed since last frame.
	If you want to have constant apparent movement no matter your framerate,
	what you can do is something like
	
	x += v * dt
	
	and this will scale your velocity based on time. Extend as necessary."""
	# Go through events that are passed to the script by the window.
	
	for event in pygame.event.get():
		# We need to handle these events. Initially the only one you'll want to care
		# about is the QUIT event, because if you don't handle it, your game will crash
		# whenever someone tries to exit.
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit() # Not including this line crashes the script on Windows. Possibly
			# on other operating systems too, but I don't know for sure.
			# Handle other events as you wish.
		elif event.type == MOUSEBUTTONDOWN and event.button == 1:
			g.clickonBoard(event.pos)
			g.checkForEffects()
		elif event.type == MOUSEBUTTONUP and event.button == 1:
			click = False

def draw(screen):
	"""
	Draw things to the window. Called once per frame.
	"""
	screen.fill((0, 0, 0)) # Fill the screen with black.

	# Redraw screen here.
	#Draw the room
	label = ""
	screen.blit(g.current_room.image,(0,0))
	#Draw the objects
	for obj in g.current_room.objects:
		screen.blit(obj.room_image,(obj.size))
		#pygame.draw.rect(screen, pygame.Color("red"), obj.size, 1)
		if obj.select:
			label = obj.desc
			if obj.use:
				pass
				pygame.draw.rect(screen, pygame.Color("yellow"), obj.size, 3)	
			else:
				pass
				pygame.draw.rect(screen, pygame.Color("blue"), obj.size, 3)
		if obj.container & obj.select:
			#pygame.draw.rect(screen, pygame.Color("black"), Rect((obj.size[0], obj.size[1]), (len(obj.contents)*120, 120)), 1)
			for content in obj.contents:
				screen.blit(content.image,(content.size))
				if content.select:
					label = content.desc
					pygame.draw.rect(screen, pygame.Color("blue"), content.size, 3)
				if content.use:
					pass
					pygame.draw.rect(screen, pygame.Color("yellow"), content.size, 3)

	pygame.draw.rect(screen, pygame.Color("gray"), g.inventorybar, 0)
	
	for obj in g.inventory:
			
		screen.blit(obj.image,(obj.size))
		if obj.select == True:
			label = obj.desc
			if obj.use == True:
				pygame.draw.rect(screen, pygame.Color("yellow"), obj.size, 3)	
			else:
				pass
				#pygame.draw.rect(screen, pygame.Color("blue"), obj.size, 3)
			
	font = pygame.font.SysFont('timesnewroman', 30)
	pygame.draw.rect(screen, pygame.Color("black"), g.infobar, 0)
	
	infobar_text = font.render(label, True, pygame.Color("white"))
	screen.blit(infobar_text, (20, g.height-160))	
	# Flip the display so that the things we drew actually show up.
	pygame.display.flip()
 
def runPyGame():
  # Initialise PyGame.
  pygame.init()
  
  # Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
  fps = 60.0
  fpsClock = pygame.time.Clock()
  
  # Set up the window.
  screen = pygame.display.set_mode((g.width, g.height))
  
  # screen is the surface representing the window.
  # PyGame surfaces can be thought of as screen sections that you can draw onto.
  # You can also draw surfaces onto other surfaces, rotate surfaces, and transform surfaces.
  
  # Main game loop.
  dt = 1/fps # dt is the time since last frame.
  while True: # Loop forever!
    update(dt) # You can update/draw here, I've just moved the code for neatness.
    draw(screen)
    
    dt = fpsClock.tick(fps)




runPyGame()

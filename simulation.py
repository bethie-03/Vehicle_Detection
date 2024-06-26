import random
import time
import threading
import pygame
import sys
import math


#TEST SMART TRAFFIC LIGHT SYSTEM
# RIGHT-LEFT / DOWN / LEFT-RIGHT / UP
number_vehices_right_total = {'car':0, 'bus':0, 'truck':0, 'bike':0, 'container':0 , 'firetruck':0, 'van':0, 'bicycle':0, 'total':0}
number_vehices_down_total = {'car':0, 'bus':0, 'truck':0, 'bike':0, 'container':0 , 'firetruck':0, 'van':0, 'bicycle':0, 'total':0}
number_vehices_left_total = {'car':0, 'bus':0, 'truck':0, 'bike':0, 'container':0 , 'firetruck':0, 'van':0, 'bicycle':0, 'total':0}
number_vehices_up_total = {'car':0, 'bus':0, 'truck':0, 'bike':0, 'container':0 , 'firetruck':0, 'van':0, 'bicycle':0, 'total':0}
number_vehices_total = [number_vehices_right_total,number_vehices_down_total, number_vehices_left_total, number_vehices_up_total]

number_vehices_right_inZone = {'car':0, 'bus':0, 'truck':0, 'bike':0, 'container':0 , 'firetruck':0, 'van':0, 'bicycle':0, 'total':0}
number_vehices_down_inZone = {'car':0, 'bus':0, 'truck':0, 'bike':0, 'container':0 , 'firetruck':0, 'van':0, 'bicycle':0, 'total':0}
number_vehices_left_inZone = {'car':0, 'bus':0, 'truck':0, 'bike':0, 'container':0 , 'firetruck':0, 'van':0, 'bicycle':0, 'total':0}
number_vehices_up_inZone = {'car':0, 'bus':0, 'truck':0, 'bike':0, 'container':0 , 'firetruck':0, 'van':0, 'bicycle':0, 'total':0}
number_vehices_inZone = [number_vehices_right_inZone, number_vehices_down_inZone, number_vehices_left_inZone, number_vehices_up_inZone]

queue_right = []
queue_down = []
queue_left = []
queue_up = []
queue = [queue_right, queue_down, queue_left, queue_up]
# Default values of signal timers
# defaultGreen = {0:10, 1:15, 2:20, 3:25}
defaultGreen = {0:10, 1:15}
defaultRed = 150
defaultYellow = 5

signals = []
noOfSignals = 2
currentGreen = 0   # Indicates which signal is green currently
nextGreen = (currentGreen+1)%noOfSignals    # Indicates which signal will turn green next
currentYellow = 0   # Indicates whether yellow signal is on or off 


# Coordinates of vehicles' start
x = {'right':[0,0], 'down':[655,616], 'left':[1400,1400], 'up':[702,740]}    
y = {'right':[468,510], 'down':[10,10], 'left':[422,385], 'up':[920,920]}

x_motor = {'right':[0,0,0,0], 'down':[673,653,631,616], 'left':[1400,1400,1400,1400], 'up':[698,712,737,752]}    
y_motor = {'right':[465,480,502,517], 'down':[10,10,10,10], 'left':[435,420,397,382], 'up':[920,920,920,920]}


vehicles = {
    'right': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}, 
    'down': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}, 
    'left': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}, 
    'up': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}
        }
vehicles_Name = {
    'right': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}, 
    'down': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}, 
    'left': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}, 
    'up': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}
        }

vehicleSizes = {0:[62,25], 1:[88,30], 2:[81,33], 3:[28,8],4:[176,37],5:[115,35],6:[60,33],7:[23,13]}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike',4:'container',5:'firetruck',6:'van',7:'bicycle'}
# speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'bike':2.5, 'container':1.7 , 'firetruck':2.4, 'van':2.2, 'bicycle':1}  # average speeds of vehicles
speeds = {'car':4, 'bus':4, 'truck':4, 'bike':4, 'container':14, 'firetruck':4, 'van':4, 'bicycle':1}  # average speeds of vehicles

directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(455,562),(560,152),(920,270),(786,673)]
signalTimerCoods = [(435,562),(540,152),(900,270),(816,673)]

# Coordinates of stop lines
stopLines = {'right': 490, 'down': 245, 'left': 900, 'up': 670}
defaultStop = {'right': 475, 'down': 235, 'left': 925, 'up': 690}

# stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

# Gap between vehicles
stoppingGap = 15    # stopping gap
movingGap = 15   # moving gap

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""

#######################

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, angle, vehiclesize):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction

        self.crossed = 0
        self.stopped = False  

        if vehicleClass != 'bike' and vehicleClass != 'bicycle':

            # self.x = x[direction][lane]
            # self.y = y[direction][lane]

            if lane == 0:
                self.lane_1 = 0
                self.lane_2 = 1
            elif lane == 1:
                self.lane_1 = 2
                self.lane_2 = 3
            if direction == 'right':
                self.x = min(x_motor[direction][self.lane_1], x_motor[direction][self.lane_2])
                self.y = y_motor[direction][self.lane_1]
            elif direction == 'down':
                self.x = x_motor[direction][self.lane_2]
                self.y = min(y_motor[direction][self.lane_1], y_motor[direction][self.lane_2])
            elif direction == 'left':
                self.x = max(x_motor[direction][self.lane_1], x_motor[direction][self.lane_2])
                self.y = y_motor[direction][self.lane_1]
            elif direction == 'up':
                self.x = x_motor[direction][self.lane_1]
                self.y = max(y_motor[direction][self.lane_1], y_motor[direction][self.lane_2])

            vehicles[direction][self.lane_1].append(self)
            self.index_1 = len(vehicles[direction][self.lane_1]) - 1
            vehicles[direction][self.lane_2].append(self)
            self.index_2 = len(vehicles[direction][self.lane_2]) - 1

            self.angle = angle
            path = "images/" + vehicleClass + ".png"

            self.image = pygame.transform.rotate(
                pygame.transform.scale(pygame.image.load(path), (vehiclesize[0], vehiclesize[1])),
                self.angle
            )

            if ((len(vehicles[direction][self.lane_1]) > 1 and  (vehicles[direction][self.lane_1][self.index_1 - 1].crossed == 0)) and (
                len(vehicles[direction][self.lane_2]) > 1 and  (vehicles[direction][self.lane_2][self.index_2 - 1].crossed == 0)
            )):
                if (direction == 'right'):
                    a = vehicles[direction][self.lane_1][self.index_1 - 1].stop - \
                                vehicles[direction][self.lane_1][self.index_1 - 1].image.get_rect().width - stoppingGap
                    b = vehicles[direction][self.lane_2][self.index_2 - 1].stop - \
                                vehicles[direction][self.lane_2][self.index_2 - 1].image.get_rect().width - stoppingGap
                    self.stop = min(a,b)
                elif (direction == 'left'):
                    a = vehicles[direction][self.lane_1][self.index_1 - 1].stop + \
                                vehicles[direction][self.lane_1][self.index_1 - 1].image.get_rect().width + stoppingGap
                    b = vehicles[direction][self.lane_2][self.index_2 - 1].stop + \
                                vehicles[direction][self.lane_2][self.index_2 - 1].image.get_rect().width + stoppingGap                
                    self.stop = max(a,b)

                elif (direction == 'down'):
                    a = vehicles[direction][self.lane_1][self.index_1 - 1].stop - \
                                vehicles[direction][self.lane_1][self.index_1 - 1].image.get_rect().height - stoppingGap
                    b = vehicles[direction][self.lane_2][self.index_2 - 1].stop - \
                                vehicles[direction][self.lane_2][self.index_2 - 1].image.get_rect().height - stoppingGap
                    self.stop = min(a,b)
                
                elif (direction == 'up'):
                    a = vehicles[direction][self.lane_1][self.index_1 - 1].stop + \
                                vehicles[direction][self.lane_1][self.index_1 - 1].image.get_rect().height + stoppingGap
                    b = vehicles[direction][self.lane_2][self.index_2 - 1].stop + \
                                vehicles[direction][self.lane_2][self.index_2 - 1].image.get_rect().height + stoppingGap
                    self.stop = max(a,b)
                    
            else:
                self.stop = defaultStop[direction]

            # if (direction == 'right'):
            #     temp = self.image.get_rect().width + stoppingGap
            #     x[direction][self.lane_1] -= temp
            #     x[direction][self.lane_2] -= temp
            # elif (direction == 'left'):
            #     temp = self.image.get_rect().width + stoppingGap
            #     x[direction][self.lane_1] += temp
            #     x[direction][self.lane_2] += temp

            # elif (direction == 'down'):
            #     temp = self.image.get_rect().height + stoppingGap
            #     y[direction][self.lane_1] -= temp
            #     y[direction][self.lane_2] -= temp

            # elif (direction == 'up'):
            #     temp = self.image.get_rect().height + stoppingGap
            #     y[direction][self.lane_1] += temp
            #     y[direction][self.lane_2] += temp

            if (direction == 'right'):
                temp = self.image.get_rect().width + stoppingGap
                x[direction][lane] -= temp
            elif (direction == 'left'):
                temp = self.image.get_rect().width + stoppingGap
                x[direction][lane] += temp
            elif (direction == 'down'):
                temp = self.image.get_rect().height + stoppingGap
                y[direction][lane] -= temp
            elif (direction == 'up'):
                temp = self.image.get_rect().height + stoppingGap
                y[direction][lane] += temp


            simulation.add(self)



        else:
            self.x = x_motor[direction][lane]
            self.y = y_motor[direction][lane]
            vehicles[direction][lane].append(self)
            self.index = len(vehicles[direction][lane]) - 1
            self.angle = angle
            path = "images/" + vehicleClass + ".png"
            self.image = pygame.transform.rotate(
                pygame.transform.scale(pygame.image.load(path), (vehiclesize[0], vehiclesize[1])),
                self.angle
            )
             
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
                if (direction == 'right'):
                    self.stop = vehicles[direction][lane][self.index - 1].stop - \
                                vehicles[direction][lane][self.index - 1].image.get_rect().width - stoppingGap
                elif (direction == 'left'):
                    self.stop = vehicles[direction][lane][self.index - 1].stop + \
                                vehicles[direction][lane][self.index - 1].image.get_rect().width + stoppingGap
                elif (direction == 'down'):
                    self.stop = vehicles[direction][lane][self.index - 1].stop - \
                                vehicles[direction][lane][self.index - 1].image.get_rect().height - stoppingGap
                elif (direction == 'up'):
                    self.stop = vehicles[direction][lane][self.index - 1].stop + \
                                vehicles[direction][lane][self.index - 1].image.get_rect().height + stoppingGap
            else:
                self.stop = defaultStop[direction]

            if (direction == 'right'):
                temp = self.image.get_rect().width + stoppingGap
                x_motor[direction][lane] -= temp
            elif (direction == 'left'):
                temp = self.image.get_rect().width + stoppingGap
                x_motor[direction][lane] += temp
            elif (direction == 'down'):
                temp = self.image.get_rect().height + stoppingGap
                y_motor[direction][lane] -= temp
            elif (direction == 'up'):
                temp = self.image.get_rect().height + stoppingGap
                y_motor[direction][lane] += temp
            simulation.add(self)
            
# New attribute to track if the vehicle has stopped
    def render(self, screen):
        # if self.vehicleClass != 'bike' and self.vehicleClass != 'bicycle':
        #     screen.blit(self.image, (self.x_spwan, self.y_spawn))
        # else:
            screen.blit(self.image, (self.x, self.y))

    def move(self):
        if self.vehicleClass != 'bike' and self.vehicleClass != 'bicycle':
            if currentYellow == 1 and not self.stopped:  # Check if yellow signal is on and vehicle hasn't stopped yet
                self.stopped = True
                self.stop = defaultStop[self.direction]  # Adjust stop position to default stop line
            if self.direction == 'right':
                if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                    self.crossed = 1
                if (self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (
                    currentGreen == 0 and currentYellow == 0)) and ((
                    self.index_1 == 0 or self.x + self.image.get_rect().width < (
                    vehicles[self.direction][self.lane_1][self.index_1 - 1].x - movingGap)) and ( 
                    self.index_2 == 0 or self.x + self.image.get_rect().width < (
                    vehicles[self.direction][self.lane_2][self.index_2 - 1].x - movingGap)
                    )):    
                    self.x += self.speed
            elif self.direction == 'down':
                if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                    self.crossed = 1
                if (self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (
                    currentGreen == 1 and currentYellow == 0)) and ((
                    self.index_1 == 0 or self.y + self.image.get_rect().height < (
                    vehicles[self.direction][self.lane_1][self.index_1 - 1].y - movingGap)) and ( 
                    self.index_2 == 0 or self.y + self.image.get_rect().height < (
                    vehicles[self.direction][self.lane_2][self.index_2 - 1].y - movingGap)
                    )):    
                    self.y += self.speed
            elif self.direction == 'left':
                if self.crossed == 0 and self.x < stopLines[self.direction]:
                    self.crossed = 1
                if (self.x >= self.stop or self.crossed == 1 or (
                        currentGreen == 0 and currentYellow == 0)) and ((
                        self.index_1 == 0 or self.x > (
                        vehicles[self.direction][self.lane_1][self.index_1 - 1].x +
                        vehicles[self.direction][self.lane_1][self.index_1 - 1].image.get_rect().width + movingGap)) and (
                        self.index_2 == 0 or self.x > (
                        vehicles[self.direction][self.lane_2][self.index_2 - 1].x +
                        vehicles[self.direction][self.lane_2][self.index_2 - 1].image.get_rect().width + movingGap)) and (       
                        )):
                    self.x -= self.speed
            elif self.direction == 'up':
                if self.crossed == 0 and self.y < stopLines[self.direction]:
                    self.crossed = 1
                if (self.y >= self.stop or self.crossed == 1 or (
                        currentGreen == 1 and currentYellow == 0)) and ((
                        self.index_1 == 0 or self.y > (
                        vehicles[self.direction][self.lane_1][self.index_1 - 1].y +
                        vehicles[self.direction][self.lane_1][self.index_1 - 1].image.get_rect().height + movingGap)) and (
                        self.index_2 == 0 or self.y > (
                        vehicles[self.direction][self.lane_2][self.index_2 - 1].y +
                        vehicles[self.direction][self.lane_2][self.index_2 - 1].image.get_rect().height + movingGap)) and (       
                        )):
                    self.y -= self.speed
        else:
            if currentYellow == 1 and not self.stopped:  # Check if yellow signal is on and vehicle hasn't stopped yet
                self.stopped = True
                self.stop = defaultStop[self.direction]  # Adjust stop position to default stop line

            if self.direction == 'right':
                if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                    self.crossed = 1
                if (self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (
                        currentGreen == 0 and currentYellow == 0)) and (
                        self.index == 0 or self.x + self.image.get_rect().width < (
                        vehicles[self.direction][self.lane][self.index - 1].x - movingGap)):
                    self.x += self.speed
            elif self.direction == 'down':
                if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                    self.crossed = 1
                if (self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (
                        currentGreen == 1 and currentYellow == 0)) and (
                        self.index == 0 or self.y + self.image.get_rect().height < (
                        vehicles[self.direction][self.lane][self.index - 1].y - movingGap)):
                    self.y += self.speed
            elif self.direction == 'left':
                if self.crossed == 0 and self.x < stopLines[self.direction]:
                    self.crossed = 1
                if (self.x >= self.stop or self.crossed == 1 or (
                        currentGreen == 0 and currentYellow == 0)) and (
                        self.index == 0 or self.x > (
                        vehicles[self.direction][self.lane][self.index - 1].x +
                        vehicles[self.direction][self.lane][self.index - 1].image.get_rect().width + movingGap)):
                    self.x -= self.speed
            elif self.direction == 'up':
                if self.crossed == 0 and self.y < stopLines[self.direction]:
                    self.crossed = 1
                if (self.y >= self.stop or self.crossed == 1 or (
                        currentGreen == 1 and currentYellow == 0)) and (
                        self.index == 0 or self.y > (
                        vehicles[self.direction][self.lane][self.index - 1].y +
                        vehicles[self.direction][self.lane][self.index - 1].image.get_rect().height + movingGap)):
                    self.y -= self.speed
        
            
#######################





# Initialization of signals with default values
def initialize():
    
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    # ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
    # signals.append(ts3)
    # ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
    # signals.append(ts4)

    repeat()

def repeat():
    global currentGreen, currentYellow, nextGreen
    while(signals[currentGreen].green>0):   # while the timer of current green signal is not zero
        updateValues()
        time.sleep(1)
    currentYellow = 1   # set yellow signal on
    # reset stop coordinates of lanes and vehicles 
    for i in range(0,1):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while(signals[currentGreen].yellow>0):  # while the timer of current yellow signal is not zero
        updateValues()
        time.sleep(1)
    currentYellow = 0   # set yellow signal off

     # reset all signal times of current signal to default times
    signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen # set next signal as green signal
    nextGreen = (currentGreen+1)%noOfSignals    # set next green signal
    signals[nextGreen].red = signals[currentGreen].yellow+signals[currentGreen].green    # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()  

# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

# Generating vehicles in the simulation
def generateVehicles():
    while(True):
        angle = 0
        
        # lane_number = random.randint(0,1)
        # lane_number_motor = random.randint(0,2)
        randNum_direction = random.randint(0,99)
        direction_number = 0
        dist_direction = [25,50,75,100]

        if(randNum_direction<dist_direction[0]):
            direction_number = 0
            angle = 0
            numberVehicle_total = number_vehices_total[0]
            numberVehicle_inZone = number_vehices_inZone[0]
            queue_number = queue[0]

        elif(randNum_direction<dist_direction[1]):
            direction_number = 1
            angle = 270
            numberVehicle_total = number_vehices_total[1]
            numberVehicle_inZone = number_vehices_inZone[1]
            queue_number = queue[1]

        elif(randNum_direction<dist_direction[2]):
            direction_number = 2
            angle = 180
            numberVehicle_total = number_vehices_total[2]
            numberVehicle_inZone = number_vehices_inZone[2]
            queue_number = queue[2]

        elif(randNum_direction<dist_direction[3]):
            direction_number = 3
            angle = 90
            numberVehicle_total = number_vehices_total[3]
            numberVehicle_inZone = number_vehices_inZone[3]
            queue_number = queue[3]



        # vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike',4:'container',5:'firetruck',6:'van',7:'bicycle'}
        # distributed_of_vehicle = [50,70,100,150,160,165,195,200] # default distribution of vehicles
        dist_vehicle_car = 113
        dist_vehicle_bus = 17
        dist_vehicle_truck = 60
        dist_vehicle_motorbike = 893
        dist_vehicle_container = 0
        dist_vehicle_firetruck = 0
        dist_vehicle_van = 0
        dist_vehicle_bicycle = 0

        distance_increments = [
            dist_vehicle_car,
            dist_vehicle_bus,
            dist_vehicle_truck,
            dist_vehicle_motorbike,
            dist_vehicle_container,
            dist_vehicle_firetruck,            
            dist_vehicle_van,
            dist_vehicle_bicycle,        
            ]

        distributed_of_vehicle = []

        for i in range(len(distance_increments)):
            if i == 0:
                distributed_of_vehicle.append(distance_increments[i])
            else:
                distributed_of_vehicle.append(distributed_of_vehicle[-1] + distance_increments[i])



        randNum_vehicle = random.randint(0,(distributed_of_vehicle[-1]-1))
    
        if (randNum_vehicle < distributed_of_vehicle[0]):
            vehicletype = vehicleTypes[0]
            vehiclesize = vehicleSizes[0]
            numberVehicle_total[vehicleTypes[0]] += 1
            numberVehicle_total['total'] += 1
            numberVehicle_inZone[vehicleTypes[0]] += 1
            numberVehicle_inZone['total'] += 1
            lane_number = random.randint(0,1)
            if len(queue_number) <= 9:
                queue_number.append(vehicleTypes[0])

        elif (randNum_vehicle < distributed_of_vehicle[1]):
            vehicletype = vehicleTypes[1]
            vehiclesize = vehicleSizes[1]
            numberVehicle_total[vehicleTypes[1]] += 1
            numberVehicle_total['total'] += 1
            numberVehicle_inZone[vehicleTypes[1]] += 1
            numberVehicle_inZone['total'] += 1
            lane_number = random.randint(0,1)
            if len(queue_number) <= 9:
                queue_number.append(vehicleTypes[1])

        elif (randNum_vehicle < distributed_of_vehicle[2]):
            vehicletype = vehicleTypes[2]
            vehiclesize = vehicleSizes[2]
            numberVehicle_total[vehicleTypes[2]] += 1
            numberVehicle_total['total'] += 1
            numberVehicle_inZone[vehicleTypes[2]] += 1
            numberVehicle_inZone['total'] += 1
            lane_number = random.randint(0,1)
            if len(queue_number) <= 9:
                queue_number.append(vehicleTypes[2])



        elif (randNum_vehicle < distributed_of_vehicle[3]):
            vehicletype = vehicleTypes[3]
            vehiclesize = vehicleSizes[3]
            numberVehicle_total[vehicleTypes[3]] += 1
            numberVehicle_total['total'] += 1
            numberVehicle_inZone[vehicleTypes[3]] += 1
            numberVehicle_inZone['total'] += 1
            lane_number = random.randint(0,3)
            if len(queue_number) <= 10:    
                queue_number.append(vehicleTypes[3])



        elif (randNum_vehicle < distributed_of_vehicle[4]):
            vehicletype = vehicleTypes[4]
            vehiclesize = vehicleSizes[4]
            numberVehicle_total[vehicleTypes[4]] += 1
            numberVehicle_total['total'] += 1
            numberVehicle_inZone[vehicleTypes[4]] += 1
            numberVehicle_inZone['total'] += 1
            lane_number = random.randint(0,1)
            if len(queue_number) <= 9:
                queue_number.append(vehicleTypes[4])



        elif (randNum_vehicle < distributed_of_vehicle[5]):
            vehicletype = vehicleTypes[5]
            vehiclesize = vehicleSizes[5]
            numberVehicle_total[vehicleTypes[5]] += 1
            numberVehicle_total['total'] += 1
            numberVehicle_inZone[vehicleTypes[5]] += 1
            numberVehicle_inZone['total'] += 1
            lane_number = random.randint(0,1)
            if len(queue_number) <= 9:
                queue_number.append(vehicleTypes[5])



        elif (randNum_vehicle < distributed_of_vehicle[6]):
            vehicletype = vehicleTypes[6]
            vehiclesize = vehicleSizes[6]
            numberVehicle_total[vehicleTypes[6]] += 1
            numberVehicle_total['total'] += 1
            numberVehicle_inZone[vehicleTypes[6]] += 1
            numberVehicle_inZone['total'] += 1
            lane_number = random.randint(0,1)
            if len(queue_number) <= 9:
                queue_number.append(vehicleTypes[6])



        elif (randNum_vehicle < distributed_of_vehicle[7]):
            vehicletype = vehicleTypes[7]
            vehiclesize = vehicleSizes[7]
            numberVehicle_total[vehicleTypes[7]] += 1
            numberVehicle_total['total'] += 1
            numberVehicle_inZone[vehicleTypes[7]] += 1
            numberVehicle_inZone['total'] += 1
            lane_number = random.randint(0,3)
            if len(queue_number) <= 9:
                queue_number.append(vehicleTypes[7])


        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~START PHRASE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # print("Total number of vehicles in each lane:")
        # print(f"  Lane left to right: {number_vehices_total[0]} vehicles")
        # print(f"  Lane right to left: {number_vehices_total[1]} vehicles")
        # print(f"  Lane down to up: {number_vehices_total[2]} vehicles")
        # print(f"  Lane up to down: {number_vehices_total[3]} vehicles")

        # print("Inzone number of vehicles in each lane:")
        # print(f"  Lane left to right: {number_vehices_inZone[0]} vehicles")
        # print(f"  Lane right to left: {number_vehices_inZone[1]} vehicles")
        # print(f"  Lane down to up: {number_vehices_inZone[2]} vehicles")
        # print(f"  Lane up to down: {number_vehices_inZone[3]} vehicles")

        # print("Queue of vehicles in each lane:")
        # print(f"  Lane left to right: {queue[0]} ")
        # print(f"  Lane right to left: {queue[1]} ")
        # print(f"  Lane down to up: {queue[2]} ")
        # print(f"  Lane up to down: {queue[3]} ")

        print(vehicles)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~END PHRASE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


        Vehicle(lane_number, vehicletype, direction_number, directionNumbers[direction_number], angle,vehiclesize)


        defaultGreen[0] = math.ceil((len(queue_left) + len(queue_right))/2)
        # print("DEFAULT GREEN 0", defaultGreen[0])
        defaultGreen[1] = math.ceil((len(queue_down) + len(queue_up))/2)
        # print("DEFAULT GREEN 1", defaultGreen[1])
        time.sleep(0.1)

class Main:
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/best_cr.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread2.daemon = True
    thread2.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background,(0,0))   # display background in simulation
        for i in range(0,noOfSignals):  # display signal and set timer according to current status: green, yello, or red
            if(i==currentGreen):
                if(currentYellow==1):
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                    screen.blit(yellowSignal, signalCoods[i+2])

                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
                    screen.blit(greenSignal, signalCoods[i+2])

            else:
                if(signals[i].red<=10):
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
                screen.blit(redSignal, signalCoods[i+2])

        signalTexts = ["","","",""]

        # display signal timer
        for i in range(0,noOfSignals):  
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i],signalTimerCoods[i])
            screen.blit(signalTexts[i],signalTimerCoods[i+2])


        # display the vehicles
        for vehicle in simulation:  
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()


Main()
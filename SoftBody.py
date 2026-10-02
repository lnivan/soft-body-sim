import pygame
import random
import math
import time

gameLength = 1400
gameWidth = 800

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

deltaTime = 0
lastFrameTime = time.time()

pygame.init()
screen = pygame.display.set_mode([gameLength, gameWidth])


def segmentCollideSemirrect(P1, P2, P3):
    if P1.y < P2.y:
        P1, P2 = P2, P1
    slope = (P1.y - P2.y) / (P1.x - P2.x)
    if slope == 0:
        slope = 0.00001
    indTerm = P1.y - slope * P1.x
    collisionX = (P3.y - indTerm) / slope
    if collisionX > P3.x and P1.y > P3.y and P3.y > P2.y:
        return(True)
    else:
        return(False)


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.module = math.sqrt(x**2 + y**2)
    
    def __add__(self, other):
        return(Vector2(self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return(Vector2(self.x - other.x, self.y - other.y))

    def __mul__(self, other):
        return(Vector2(self.x * other, self.y * other))

    def EM(self, other):
        return(self.x * other.x + self.y * other.y)

    def normalize(self):
        return(Vector2(self.x / self.module, self.y / self.module))

    def turn(self, radian):
        newRadian = math.atan2(self.y, self.x) + radian
        self.x = math.cos(newRadian) * self.module
        self.y = math.sin (newRadian) * self.module


class massPoint:
    def __init__(self, position, mass):
        self.mass = mass
        self.position = position
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.addedForces = []

    def update(self):
        totalAddedForces = Vector2(0, 0)
        totalAddedForces = totalAddedForces + Vector2(0, -9.8 * self.mass)
        for force in self.addedForces:
            totalAddedForces = totalAddedForces + force
        self.acceleration = totalAddedForces
        self.velocity = self.velocity + self.acceleration * deltaTime
        self.position = self.position + self.velocity * deltaTime

        if self.position.y < 10:
            self.position.y = 10
            self.velocity.y *= 0

        self.addedForces = []
    
    def draw(self):
        pygame.draw.circle(screen, white, [self.position.x, gameWidth - self.position.y], 2, 0)

class springJoint:
    def __init__(self, point1, point2, springConstant, dampening):
        self.normalDistance = (point1.position - point2.position).module
        self.springConstant = springConstant
        self.dampening = dampening
        self.point1 = point1
        self.point2 = point2

    def update(self):
        springForce1 = (self.point1.position - self.point2.position).normalize() * (self.normalDistance - (self.point1.position - self.point2.position).module) * self.springConstant
        springForce2 = springForce1 * (-1)
        dampening1 = (self.point1.position - self.point2.position).normalize() * self.dampening * (self.point1.position - self.point2.position).EM(self.point1.velocity - self.point2.velocity)
        dampening2 = (self.point2.position - self.point1.position).normalize() * self.dampening * (self.point2.position - self.point1.position).EM(self.point2.velocity - self.point1.velocity)
        self.point1.addedForces.append(springForce1 - dampening1)
        self.point2.addedForces.append(springForce2 - dampening2)
        

    def draw(self, color):
        pygame.draw.line(screen, color, [self.point1.position.x, gameWidth - self.point1.position.y], [self.point2.position.x, gameWidth - self.point2.position.y], 1)


class softBody:
    softBodyArray = []
    def __init__(self, position, springConstant, dampening, pointMass, pointPositionArray):
        self.softBodyArray.append(self)

        self.position = position

        self.pointArray = []
        for pointPosition in pointPositionArray:
            self.pointArray.append(massPoint(self.position + pointPosition, pointMass))

        self.springArray = []
        for n in range(len(self.pointArray) - 1):
            point1 = self.pointArray[n]
            for point2 in self.pointArray[n + 1:len(self.pointArray)]:
                self.springArray.append(springJoint(point1, point2, springConstant, dampening))

    def update(self):
        for point in self.pointArray:
            point.update()
        
        for spring in self.springArray:
            spring.update()

        for softBody in self.softBodyArray:
            if softBody != self:
                for point3 in softBody.pointArray:
                    collisions = 0
                    for spring in self.springArray:
                        if self.pointArray[self.pointArray.index(spring.point1) + 1] == spring.point2 or (self.pointArray.index(spring.point1) == 0 and self.pointArray.index(spring.point2) == len(self.pointArray) - 1):
                            if segmentCollideSemirrect(spring.point1.position, spring.point2.position, point3.position):
                                collisions = collisions + 1
                    

    def draw(self):
        for point in self.pointArray:
            point.draw()
        
        mouseX, mouseY = pygame.mouse.get_pos()
        mouseY = gameWidth - mouseY
        mousePos = Vector2(mouseX, mouseY)
        for spring in self.springArray:
            if self.pointArray[self.pointArray.index(spring.point1) + 1] == spring.point2 or (self.pointArray.index(spring.point1) == 0 and self.pointArray.index(spring.point2) == len(self.pointArray) - 1):
                if segmentCollideSemirrect(spring.point1.position, spring.point2.position, mousePos):
                    spring.draw(red)
                else:
                    spring.draw(white)


class softBodyPolar:
    def __init__(self, position, springConstant, dampening, pointMass, pointPositionArray):
        self.pointArray = []
        for point in pointPositionArray:
            self.pointArray.append(Vector2(point.y * math.cos(point.x), point.y * math.sin(point.x)))
        self.body = softBody(position, springConstant, dampening, pointMass, self.pointArray)
    
    def update(self):
        self.body.update()

    def draw(self):
        self.body.draw()


pointArray = []
a = 30
for i in range(a):
    pointArray.append(Vector2(math.pi*i*2/a, 100))

caca = softBodyPolar(Vector2(700, 400), 1, 0.01, 10, pointArray)

running = True
while running == True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    deltaTime = time.time() - lastFrameTime
    lastFrameTime = time.time()


    screen.fill(black)
    for object in softBody.softBodyArray:
        object.update()
        object.draw()

    caca.draw()
    pygame.display.flip()
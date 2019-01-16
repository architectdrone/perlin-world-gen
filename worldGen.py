#worldGen.py
import perlin
import sys, pygame, math, copy

#Settings
PIX_PER_SQUARE = 200 #Used for mapping an (x, y) coordinate in the screen to a decimal coordinate in the perlin-world. For lack of a better term, greater values of this lead to larger land-masses. 
SCREEN_SIZE = 1000 #Size, in pixels, of the screen. Greater values take longer.
TOP_LEFT = (50, 50)
OCTAVES = 3
PERSISTANCE = 2
SCALE = 4 #Size of each individual coordinate. As you might expect, a larger scale means less pixels to render, and thus lower processing times.
SEA_LEVEL = 130 #How high the sea is
SAND_DELTA = 10 #How far above sea level sand extends
TREE_LEVEL = 200 #How high vegetation can grow
SHADOWS = False #Whether shadows are enabled. This has a computational cost.
SUN_ANGLE = 45 #The angle that the sun is in the sky relative to the ground. Must be between 0 and 90! The sun is to the left of the world.
SHADOW_OPACITY = 50 #How dark the shadows are.
TOPOGRAPHIC_LINES = False #Whether topographic lines are shown.
TOPOGRAPHIC_DIVISIONS = 50 #What each topology line represents an increment of.
PRECIP_SCALE = 4 #Size of precipitation patterns.
PRECIP_OFFSET = 100 #Offset from main perlin coordinates.
NEW_BIOME_SYSTEM = True #Whether internal grass coloration is allowed.

gridSize = int(SCREEN_SIZE/SCALE)
pygame.init()

size = width, height = SCREEN_SIZE, SCREEN_SIZE
screen = pygame.display.set_mode(size)

print(size)

def gridWrite(drawOn, x, y, color, upper_x, upper_y, scale):
    '''Writes a single square to the screen.'''
    true_x = scale*x-upper_x
    true_y = scale*y-upper_y
    if true_x > SCREEN_SIZE or true_y > SCREEN_SIZE:
        return
    if true_x < 0 or true_y < 0:
        return
    pygame.draw.rect(drawOn, color, pygame.Rect(true_x, true_y, true_x+scale, true_y+scale))

def get2DArray(size, thing):
    '''Gets a 2D array of some item.'''
    x_axis = [thing]*int(size)
    toReturn = []
    for i in range(int(size)):
        toReturn.append(x_axis.copy())
    return toReturn

def setCoord(toSet, x, y, newValue):
    '''Sets a coordinate in a 2D array.'''
    toSet[y][x] = newValue

def getCoord(toLookupIn, x, y):
    '''Gets a coordinate in a 2D array.'''
    return toLookupIn[y][x]

def printScreenArray(screenArray):
    '''Prints the given screen array to the pygame window.'''
    global SCALE
    for y_i, y in enumerate(screenArray):
        for x_i, x in enumerate(y):
            #print(x_i, y_i, x)
            gridWrite(screen, x_i, y_i, x, 0, 0, SCALE)
    pygame.display.flip()

def perlinScreenArray(normFactor = 255):
    '''Gets a grayscale simple perlin noise screen array.'''
    global OCTAVES, PERSISTANCE, gridSize
    perlinArray = get2DArray(gridSize, 0)
    for x in range(gridSize):
        for y in range(gridSize):
            xp = x/PIX_PER_SQUARE
            yp = y/PIX_PER_SQUARE
            perl = perlin.octavePerlin(xp, yp, OCTAVES, PERSISTANCE)
            normPerl = perl*normFactor
            #print(x, y, perl, normPerl)
            setCoord(perlinArray, x, y, normPerl)
    return perlinArray

def topologyScreenArray():
    '''Creates a screen array showing topological patterns. Trippy!'''
    global gridSize
    screenArray = get2DArray(gridSize, (0, 0, 0))
    for x in range(gridSize):
        for y in range(gridSize):
            setCoord(screenArray, x, y, getTopologyColor(x, y))
    return screenArray

##def worldScreenArray():
##    '''Creates a screen array showing a world, using perlin noise.'''
##    global gridSize
##    screenArray = get2DArray(gridSize, (0,0,0))
##    for x in range(gridSize):
##        for y in range(gridSize):
##            p = getNormPerlin(x, y)
##            baseColor = (0, 0, 0)
##            if p < SEA_LEVEL:
##                baseColor = (0, 0, 255)
##            elif p < SEA_LEVEL+SAND_DELTA:
##                baseColor = (255, 255, 102)
##            elif p < TREE_LEVEL:
##                baseColor = getBiomeColor(x, y)
##            else:
##                baseColor = (150, 150, 150)
##            newColor = colorAdd(baseColor, getShading(x, y))
##            newColor = colorAdd(newColor, getTopologyColor(x, y))
##            setCoord(screenArray, x, y, newColor)
##    return screenArray         

def worldScreenArray():
    '''Creates a screen array showing a world, using perlin noise.'''
    global gridSize
    screenArray = get2DArray(gridSize, (0,0,0))
    for xu in range(gridSize):
        for yu in range(gridSize):
            x = xu+TOP_LEFT[0]
            y = yu+TOP_LEFT[1]
            p = getNormPerlin(x, y)
            baseColor = (0, 0, 0)
            if p < SEA_LEVEL:
                baseColor = (0, 0, 255)
            elif p < SEA_LEVEL+SAND_DELTA:
                baseColor = (255, 255, 102)
            elif p < TREE_LEVEL:
                baseColor = getBiomeColor(x, y)
            else:
                baseColor = (150, 150, 150)
            newColor = colorAdd(baseColor, getShading(x, y))
            newColor = colorAdd(newColor, getTopologyColor(x, y))
            setCoord(screenArray, xu, yu, newColor)
    return screenArray         


def colorAdd(t1, t2):
    '''Adds two colors together, element by element.'''
    r = t1[0]+t2[0]
    g = t1[1]+t2[1]
    b = t1[2]+t2[2]
    if r > 255:
        r = 255
    if g > 255:
        g = 255
    if b > 255:
        b = 255
    if r < 0:
        r = 0
    if g < 0:
        g = 0
    if b < 0:
        b = 0
    return (r, g, b)

def getIsShaded(x, y):
    '''Returns whether or not the given coordinate is shaded.'''
    theta_degrees = SUN_ANGLE
    theta_radians = (180-theta_degrees)*(3.1415/180)
    p = getNormPerlin(x, y)
    max_height_delta = 255-p #The maximum positive delta between this coordinate and any other coordinate.
    meaningful_range = abs((max_height_delta)/(math.tan(theta_radians))) #How far we can go before it is impossible for the sun to get blocked out.
    #print(f"Getting shading for {x}, {y}. p = {p}, Max Delta = {max_height_delta}, Meaningful Range = {meaningful_range}, Radians = {theta_radians}")
    for i in range(int(meaningful_range)):
        cur_x = x-(i+1)
        if cur_x < 0:
            break
        cur_p = getNormPerlin(cur_x, y)
        to_beat = abs(math.tan(theta_radians)*(i+1))
        delta = cur_p-p
        #print(f"-Testing {cur_x}, {y}. cur_p = {cur_p}, to_beat = {to_beat}, delta = {delta}")
        if delta >= to_beat:
            return True
    return False

def getShading(x, y):
    '''Returns a color associated with the shading at a given point.'''
    if not SHADOWS:
        return (0,0,0)
    darkness = SHADOW_OPACITY
    if getIsShaded(x, y):
        return (-darkness, -darkness, -darkness)
    else:
        return (0, 0, 0)
                                
def getNormPerlin(x, y, normFactor = 255):
    '''Get normalized perlin noise at the given point.'''
    xp = x/PIX_PER_SQUARE
    yp = y/PIX_PER_SQUARE
    return perlin.octavePerlin(xp, yp, OCTAVES, PERSISTANCE)*normFactor

def getTopologyColor(x, y):
    '''Returns a color associated with the topology.'''
    if TOPOGRAPHIC_LINES == False:
        return (0, 0, 0)
    
    xp = x/PIX_PER_SQUARE
    yp = y/PIX_PER_SQUARE
    p = perlin.octavePerlin(xp, yp, OCTAVES, PERSISTANCE)
    #print(f"x = {x}, y = {y}, xp = {xp}, yp = {yp}, p = {p*255}")
    if math.floor(p*255)%TOPOGRAPHIC_DIVISIONS == 0:
        return (255, 255, 255)
    elif math.floor(p*255)%TOPOGRAPHIC_DIVISIONS == 1:
        return (255, 255, 255)
    elif math.floor(p*255)%TOPOGRAPHIC_DIVISIONS == (TOPOGRAPHIC_DIVISIONS-1):
        return (255, 255, 255)
    else:
        return (0,0,0)

def getPrecipitation(x, y):
    '''Returns a normalized perlin value, on the same map, but stretched to a certain value, and offset by a certain value, to be interpreted as precipitation.'''
    global gridSize
    p = perlin.perlin(PRECIP_OFFSET+(2*(x/gridSize)), PRECIP_OFFSET+(2*(y/gridSize)))*255
    #print(p)
    return p

def getBiomeColor(x, y):
    '''Returns the color of grass at the given point.'''
    if not NEW_BIOME_SYSTEM:
        return (62, 207, 52)
    MAX_DARKNESS = 20
    max_temp = 255-SEA_LEVEL
    temperature = 255-getNormPerlin(x, y)
    precipitation = getPrecipitation(x, y)
    yellow_coloration = (temperature/max_temp)*255
    darkness = (precipitation/255)*MAX_DARKNESS
    color = (yellow_coloration-darkness, 255-darkness, 0)
    return color
    
    
printScreenArray(worldScreenArray())

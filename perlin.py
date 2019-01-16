#Perlin.py
import random
import math
MAX = 255
PROVIDED_HASH = [151,160,137,91,90,15,
    131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
    190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
    88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
    77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
    102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
    135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
    5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
    223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
    129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
    251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
    49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
    138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180] #Provide your own hash here.

def generateHash(MAX):
    '''Create a hash table of MAX random values, between 0 and MAX'''
    toReturn = []
    for i in range(MAX):
        toReturn.append(random.randint(0, MAX))
    return toReturn

if PROVIDED_HASH == []: 
    hashT = generateHash(MAX)
else:
    hashT = PROVIDED_HASH
    MAX = len(hashT)

def fade(t):
    '''I got this from a tutorial. I have no idea why it is what it is...'''
    return t*t*t*(t*(t*6.0 - 15.0) + 10.0)

def lerp(a, b, x):
    '''Linear Interpolation.'''
    return a+x*(b-a)

def getUnitVector(x, y):
    '''The name is a misnomer. It retrieves the psuedorandom vector for the given point of a unit square.'''

    global hashT, MAX
    try:
        hashValue = hashT[(hashT[(x%MAX)]+(y))%MAX] #Get a hash value. This will determine which vector is returned.
    except:
        print(f"HASH ERROR FOUND at {x},{y}. hashT[x&MAX] = {hashT[x&MAX]}. Add {y%MAX} to get {hashT[(x%MAX)]+(y%MAX)}.")
        hashValue = 1 #I know, cheating. Sue me.

    sel = hashValue%4
    if sel == 0:
        return (1, 1)
    elif sel == 1:
        return (-1, 1)
    elif sel == 2:
        return (1, -1)
    elif sel == 3:
        return (-1, -1)

def getDDVector(x1, y1, x2, y2):
    '''Returns a directed distance vector.'''
    return (x2-x1, y2-y1)

def dot(v1, v2):
    '''Dots two vectors together.'''
    total = 0
    for a, b in zip(v1, v2): #So pretty
        total+=(a*b)
    return total

def getInfluence(x, y, xu, yu):
    '''Gets the influence value for the coordinates x and y relative to the unit coordinates xu and yu.'''
    d = getDDVector(xu, yu, x, y)
    u = getUnitVector(xu, yu)
    influence = dot(d, u)

    return influence

def getWAvg(a, b, c, d, u, v):
    '''Returns weighted avg between a, b, c, d, where u and v are the weights.'''
    
    x1 = lerp(a, b, u)
    x2 = lerp(c, d, u)
    return lerp(x1, x2, v)

def perlin(x, y):
    '''Gets perlin noise at given point.'''

    #Get origin
    xi = math.floor(x)
    yi = math.floor(y)

    #Get influencers
    upper_left = getInfluence(x, y, xi, yi) #Internal coordinates of (0,0)
    upper_right = getInfluence(x, y, xi+1, yi) #Internal coordinates of (1, 0)
    lower_left = getInfluence(x, y, xi, yi+1) #Internal coordinates of (0, 1)
    lower_right = getInfluence(x, y, xi+1, yi+1) #Internal coordinates of (1, 1)

    #Get avg
    u = fade(x-int(x))
    v = fade(y-int(y))
    a = getWAvg(upper_left, upper_right, lower_left, lower_right, u, v)

    ##    print(f"PERLIN FOR {x}, {y}:")
    ##    print(f" upper_left = {upper_left}")
    ##    print(f" upper_right = {upper_right}")
    ##    print(f" lower_left = {lower_left}")
    ##    print(f" lower_right = {lower_right}")
    ##    print(f" u = {u}")
    ##    print(f" v = {v}")
    ##    print(f" RETURNED = {a}")
    n_a = ((a+1)/2)
    if n_a < 0:
        n_a = 0
    elif n_a > 1:
        n_a = 1
    return n_a

def octavePerlin(x, y, octaves, persistence):
    total = 0
    frequency = 1
    amplitude = 1
    maxValue = 0
    for i in range(octaves):
        total+=perlin(x*frequency, y*frequency)*amplitude
        maxValue+=amplitude
        amplitude*=persistence
        frequency*=2
    return total/maxValue

print(perlin(1.99, 4.1))
print(perlin(2, 4.1))
print(perlin(2.01, 4.1))

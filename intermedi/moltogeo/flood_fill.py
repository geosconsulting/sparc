__author__ = 'fabio.lana'

def floodfill( x,y,array, pixels_x, pixels_y):

    if x < 0 or x > len(array)-1:
        return
    if y < 0 or y > len(array[x])-1:
        return
    if array[x][y] == 1:
        return

    for i in range(0,len(pixels_x)):
        if  pixels_x[i] == x and pixels_y[i] == y :
            return

    pixels_x.append(x)
    pixels_y.append(y)
    floodfill(x+1,y,array,pixels_x,pixels_y)
    floodfill(x-1,y,array,pixels_x,pixels_y)
    floodfill(x,y+1,array,pixels_x,pixels_y)
    floodfill(x,y-1,array,pixels_x,pixels_y)
    return

pixels_x = []
pixels_y = []

array = [[0,0,0,0,0,0,0],
         [0,0,0,1,0,0,0],
         [0,0,1,0,1,0,0],
         [0,1,0,0,0,1,0],
         [1,0,0,0,1,0,0],
         [0,1,0,0,0,1,0],
         [0,0,1,0,1,0,0],
         [0,0,0,1,0,0,0]]

floodfill(3, 3, array, pixels_x, pixels_y)
for i in range(0,len(pixels_x)):
    print "Pixel: " + str(pixels_x[i]) + "," + str(pixels_y[i])

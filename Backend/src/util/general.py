import cv2



def bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)

    return min(x_coordinates), min(y_coordinates),max(x_coordinates), max(y_coordinates)



def get_filter_region(ymin,ymax):
    height = ymax - ymin
    ystart = ymin + height/3
    yend = ymin + 2*height/3
    return ystart,yend


def check_point_in_area(point,area):
    pass
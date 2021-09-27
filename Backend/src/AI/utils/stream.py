
import cv2
from threading import Thread
from src.const import *
import time


class VideoStream:
    """Camera object that controls video streaming"""
    def __init__(self,stream_url,resolution=(1280,720),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.vid_writer = None
        self.stream = cv2.VideoCapture(stream_url)
        # self.stream = cv2.VideoCapture(self.format_cam_rtsp(stream_url),cv2.CAP_GSTREAMER)
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()
        # self.k = self.stream.getRTPTimeStampSeconds()
        # self.l = self.stream.getRTPTimeStampFraction()
	# Variable to control when the camera is stopped
        self.stopped = False
        self.isOpened = True

    def format_cam_rtsp(self,uri,width=1280,height=720,latency=1000):
        get_str = ('rtspsrc location={} ! application/x-rtp,'
                    'media=video,encoding-name=H264 ! rtpjitterbuffer latency={} '
                    '! rtph264depay ! h264parse ! nvv4l2decoder ! nvvidconv ! video/x-raw, width=(int){},height=(int){},'
                    'format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1 ').format(uri,latency,width,height)
        return get_str
    def record(self,path,name):
        fps = self.stream.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        w = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("width:{}-height:{} - fps:{}".format(w,h,fps))
        self.vid_writer = cv2.VideoWriter(path+'/{}.avi'.format(name), fourcc, fps, (1280, 720))

    def start(self):
	# Start the thread that reads frames from the video stream
        self.thread = Thread(target=self.update,args=())
        self.thread.setDaemon(True)
        self.thread.start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                if isinstance(self.vid_writer, cv2.VideoWriter):
                    self.vid_writer.release()  # release previous video writer
                # self.thread.join()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            # self.k = self.stream.getRTPTimeStampSeconds()
            # self.l = self.stream.getRTPTimeStampFraction()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True
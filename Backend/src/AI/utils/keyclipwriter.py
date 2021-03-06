from collections import deque
from threading import Thread
from queue import Queue
import time
import cv2
from datetime import datetime

from src.migrate.video import  Video
from src import db

class KeyClipWriter:
    def __init__(self, bufSize=64, timeout=1.0,resolution=(1280,720)):
        # store the maximum buffer size of frames to be kept
        # in memory along with the sleep timeout during threading
        self.bufSize = bufSize
        self.timeout = timeout
        self.resolution = resolution
        # initialize the buffer of frames, queue of frames that
        # need to be written to file, video writer, writer thread,
        # and boolean indicating whether recording has started or not
        self.frames = deque(maxlen=bufSize)
        self.Q = None
        self.writer = None
        self.thread = None
        self.recording = False
        self.video_id = None

    def update(self, frame):
        # update the frames buffer
        self.frames.appendleft(frame)
        # if we are recording, update the queue as well
        if self.recording:
            self.Q.put(frame)

    def start(self, outputPath, fourcc, fps,device_id,log):
        # indicate that we are recording, start the video writer,
        # and initialize the queue of frames that need to be written
        # to the video file
        self.recording = True
        self.writer = cv2.VideoWriter(outputPath, fourcc, fps,
            self.resolution, True)
        self.Q = Queue()
        current_time = datetime.now()
        record = Video(device_id,outputPath,current_time,None)
        record.add(log)
        self.video_id = record.id
        # loop over the frames in the deque structure and add them
        # to the queue
        for i in range(len(self.frames), 0, -1):
            self.Q.put(self.frames[i - 1])
        # start a thread write frames to the video file
        self.thread = Thread(target=self.write, args=())
        self.thread.daemon = True
        self.thread.start()

    def write(self):
        # keep looping
        while True:
            # if we are done recording, exit the thread
            if not self.recording:
                return
            # check to see if there are entries in the queue
            if not self.Q.empty():
                # grab the next frame in the queue and write it
                # to the video file
                frame = self.Q.get()
                frame = cv2.resize(frame,self.resolution)
                self.writer.write(frame)
            # otherwise, the queue is empty, so sleep for a bit
            # so we don't waste CPU cycles
            else:
                time.sleep(self.timeout)

    def flush(self):
        # empty the queue by flushing all remaining frames to file
        while not self.Q.empty():
            frame = self.Q.get()
            self.writer.write(frame)

    def finish(self):
        # indicate that we are done recording, join the thread,
        # flush all remaining frames in the queue to file, and
        # release the writer pointer
        self.recording = False
        video_id =  self.video_id
        self.thread.join()
        self.flush()
        self.writer.release()
        
        data = db.session.query(Video).filter(Video.id == video_id).first()
        if data:
            data.end_time = datetime.now()
        else:
            print(video_id)
        db.session.commit()
        self.video_id = None

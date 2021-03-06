import cv2
import os
import time
from datetime import datetime
from queue import Queue
import numpy as np
import asyncio
import websockets
import json
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
import tracemalloc

from src.const import *
from src.AI.utils.stream import VideoStream
from src.AI.utils.keyclipwriter import KeyClipWriter
from src.AI.utils.plots import plot_one_box
from src.AI.yolov5 import LisencePlate
from src.AI.vehicle.ResNet import Car_Classifier

from src.migrate.detection import Detection
from src.migrate.vehicle import Vehicle
from src.migrate.video import Video
from src.migrate.recognize import Recognize
from src.migrate.vehicle_management import VM
from src.migrate.classification import Classification


from src.AI.utils.check_direction import *
from src.AI.utils.violate import *

import src.handler.track as t
import  src.handler.vehicle as v
import src.handler.classification as c
import src.handler.vehicle_management as mg






# logging.getLogger('apscheduler').setLevel(logging.WARNING)

q = Queue()
tracking_data = Queue()

lane_lst = {}
memory = {}
tracking = {}
pts = [(593, 709), (9, 555), (503, 269), (695, 240), (794, 308), (595, 705)]

def get_list_of_points(image):
    global lane_lst
    pass

def get_lane_properties(lanes,log):
    global lane_lst
    lane_lst = lanes
    log.info('pass value success')

def gen_frame(device,model,stream_config,video_config,log):
    fps = video_config['fps']
    dbe = video_config['dbe']
    kcw = KeyClipWriter(bufSize=fps*dbe,resolution=(video_config['resolution']['width'],video_config['resolution']['height']))
    mlp = LisencePlate(weights='./src/AI/models/lpr-spcs.pt',imgsz=416)
    vr = Car_Classifier(num_cls=19, model_path='./src/AI/models/epoch_39.pth', device='cuda')
    freq = cv2.getTickFrequency()
    frame_rate_calc  = 25
    deepsort = model.deepsort
    meta_data = device['meta_data']
    # stream_url = "rtsp://{}:{}@{}:{}/{}".format(meta_data['user'],
    #                 meta_data['password'],meta_data['ip'],meta_data['rtsp_port'],stream_config['channel'])
    stream_url = "rtsp://222.235.247.91:554/profile2/media.smp"
    # videostream  = VideoStream(device.stream_url,resolution=(1280,720),framerate=60)
    # videostream.start()
    # time.sleep(1)
    # if not videostream:
    #     log.error("!!! Failed VideoCapture: invalid parameter!")
    try:
        # schedulers = BackgroundScheduler()
        # schedulers.add_job(process_data,  trigger='interval',args=(device,log), seconds=1)
        # schedulers.start()
        thread = Thread(target=process_data,args=(device,deepsort,kcw,mlp,vr,log))
        thread.setDaemon(True)
        thread.start()
        consecFrames = 0
        while True:
            videostream  = VideoStream(stream_url,resolution=(stream_config['resolution']['width'],stream_config['resolution']['height']),framerate=60)
            videostream.start()
            time.sleep(1)
            if not videostream:
                log.error("!!! Failed VideoCapture: invalid parameter!")
            while videostream.stream.isOpened():
                # Capture frame-by-frame
                t1 = cv2.getTickCount()
                updateConsecFrames = True
                current_frame = videostream.read()
                if type(current_frame) == type(None):
                    log.error("!!! Couldn't read frame!")
                    log.info("Try to reconnect!")
                    break
                current_frame = cv2.resize(current_frame, (stream_config['resolution']['width'],stream_config['resolution']['height'] ))
                mask = np.zeros(current_frame.shape, np.uint8)
                for lane in lane_lst:
                    pts = lane['points']
                    points = np.array(pts, np.int32)
                    points = points.reshape((-1, 1, 2))
                    mask = cv2.polylines(mask, [points], True, (255, 255, 255), 2)
                    mask2 = cv2.fillPoly(mask.copy(), [points], (255, 255, 255))
                    mask3 = cv2.fillPoly(mask.copy(), [points], (0, 255, 0))
                # mask = np.zeros(current_frame.shape, np.uint8)
                # points = np.array(pts, np.int32)
                # points = points.reshape((-1, 1, 2))
                # mask = cv2.polylines(mask, [points], True, (255, 255, 255), 2)
                # mask2 = cv2.fillPoly(mask.copy(), [points], (255, 255, 255))  # ????????? ROI
                # mask3 = cv2.fillPoly(mask.copy(), [points], (0, 255, 0))
                show_image = cv2.addWeighted(src1=current_frame, alpha=0.8, src2=mask3, beta=0.2, gamma=0)
                roi = cv2.bitwise_and(mask2, current_frame)
                model.start(roi,show_image,current_frame)
                
                cv2.putText(model.show_image,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
                _, buffer = cv2.imencode('.jpg', model.show_image)
                current_frame = buffer.tobytes()
                q.put(current_frame)
                data = {}
                updateConsecFrames = len(model.bounding_box) == 0
                if len(model.bounding_box) > 0:
                    data = {
                        "xywhs" : model.xywhs,
                        "confs" : model.confs,
                        "clss" : model.clss,
                        "img" : model.current_frame,
                        # "bb" : model.bounding_box,
                        "names" : model.names,
                        "event_time" :  model.event_time
                    }
                    consecFrames = 0
                    tracking_data.put(data)
                    if not kcw.recording:
                        try:
                            log.info("is  recording: {} - video_id:{}".format(kcw.recording,kcw.video_id))
                            timestamp = datetime.now()
                            video_path = os.path.join(STORAGE,'video')
                            p = "{}/{}.webm".format(video_path,
                                timestamp.strftime("%Y%m%d-%H%M%S"))
                            kcw.start(p, cv2.VideoWriter_fourcc(*'vp80'),
                                fps,device['id'],log)
                        except  Exception as e:
                            log.info(e)
                if updateConsecFrames:
                    # log.info("Current consecFrames: {}".format(consecFrames))
                    consecFrames += 1
                kcw.update(model.show_image)
                if kcw.recording and consecFrames == 100:
                    log.info("Finished record!!!")
                    kcw.finish()
                
                # Calculate framerate
                t2 = cv2.getTickCount()
                time1 = (t2-t1)/freq
                frame_rate_calc= 1/time1
            time.sleep(5)
    except (KeyboardInterrupt,SystemExit):
        log.info("Finished the stream")
        model.stop()
        # videostream.stop()
        # schedulers.shutdown()


def gen_vid(path,model,log):
    INPUT= ROOTDIR + '/inputs'
    OUTPUT= ROOTDIR + '/outputs'
    src = os.path.join(INPUT,path)
    freq = cv2.getTickFrequency()
    frame_rate_calc  = 25
    videostream  = VideoStream(src,resolution=(1280,720),framerate=60).start()
    time.sleep(1)
    if not videostream:
        log.error("!!! Failed VideoCapture: invalid parameter!")
    basename = os.path.splitext(path)[0]
    # count =0
    log.info('This is test!!!!')
    videostream.record(OUTPUT,basename)
    while (videostream.stream.isOpened()):
        # time.sleep(0.3)
        # Capture frame-by-frame
        t1 = cv2.getTickCount()
        current_frame = videostream.read()
        if type(current_frame) == type(None):
            log.error("!!! Couldn't read frame!")
            break
        current_frame = cv2.resize(current_frame, (1280,720 ))


        model.start(current_frame)
        videostream.vid_writer.write(model.current_frame)
        cv2.putText(model.current_frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
        ret, buffer = cv2.imencode('.jpg', model.current_frame)
        current_frame = buffer.tobytes()
        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2-t1)/freq
        frame_rate_calc= 1/time1
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
    videostream.stop()

def setup_cameras(log):
    while True:
        frame = q.get()
        if frame is None:
            log.info("Data is empty")
            continue
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def process_data(device,deepsort,kcw,mlp,vr,log):
    global memory,lane_lst
    while True:
        timeout_start = time.time()
        response = []
        while time.time() < timeout_start + 0.2:
            tracking = tracking_data.get()
            if tracking is None:
                continue
            track_output = deepsort.update(tracking['xywhs'].cpu(), tracking['confs'].cpu(), 
                            tracking['clss'], tracking['img'])
            if len(track_output) > 0:
                for j, (output, conf) in enumerate(zip(track_output, tracking['confs'])):
                    id = output[4]
                    cls = output[5]
                    bbox_left = output[0]
                    bbox_top = output[1]
                    centerx = bbox_left + (output[2] - output[0])//2
                    centery = bbox_top + (output[2] - output[0])//2
                    midpoint = (centerx,centery)
                    if id not in memory:
                        new_track = VehiclePos()
                        new_track.add_position(midpoint)
                        memory[id] = new_track
                    memory[id].add_position(midpoint)
                    previous_midpoint = memory[id].positions[0]
                    c = int(cls)  # integer class
                    direction = ''
                    if midpoint[1] < previous_midpoint[1]:
                            direction = 'Up'
                    elif midpoint[1] >= previous_midpoint[1]:
                            direction = 'Down'
                    vehicle_pos = {
                        "direction" : direction,
                        "point" : midpoint
                    }
                    memory[id].is_wrong_direction = wrong_direction(vehicle_pos,lane_lst,log)
                    for i in memory.values():
                        i.frames_since_seen += 1
                    track_result = {
                        "video_id": kcw.video_id,
                        "tracking_number": int(id.item()),
                        "start_time": datetime.now(),
                        "end_time": datetime.now()
                    }
                    tracking = t.create_or_update(track_result, log)
        data = tracking_data.get()
        if data is None:
            continue
        data_time = datetime.now().strftime("%m:%d:%Y_%H_%M_%S.%f")
        full_path = os.path.join(STORAGE, 'full_image', data_time+'.jpg')
        outputs = deepsort.update(data['xywhs'].cpu(), data['confs'].cpu(),
                                  data['clss'], data['img'])

        if len(outputs) > 0:
            count = 0
            response = []
            for j, (output, conf) in enumerate(zip(outputs, data['confs'])):
                bboxes = output[0:4]
                id = output[4]
                cls = output[5]

                c = int(cls)  # integer class
                name = data['names'][c]

                bbox_left = output[0]
                bbox_top = output[1]
                bbox_w = output[2] - output[0]
                bbox_h = output[3] - output[1]
                centerx = bbox_left + (output[2] - output[0])//2
                centery = bbox_top + (output[2] - output[0])//2
                midpoint = (centerx,centery)
                if id not in memory:
                    new_track = VehiclePos()
                    new_track.add_position(midpoint)
                    memory[id] = new_track
                memory[id].add_position(midpoint)
                previous_midpoint = memory[id].positions[0]
                c = int(cls)  # integer class
                direction = ''
                if midpoint[1] < previous_midpoint[1]:
                        direction = 'Up'
                elif midpoint[1] >= previous_midpoint[1]:
                        direction = 'Down'
                vehicle_pos = {
                    "direction" : direction,
                    "point" : midpoint
                }
                memory[id].is_wrong_direction = wrong_direction(vehicle_pos,lane_lst,log)
                for i in memory.values():
                    i.frames_since_seen += 1


                count += 1
                track_result = {
                    "video_id": kcw.video_id,
                    "tracking_number": int(id.item()),
                    "start_time": datetime.now(),
                    "end_time": datetime.now()
                }
                tracking = t.create_or_update(track_result, log)
                boundingbox = {
                    'x' : int(bbox_left),
                    'y' : int(bbox_top),
                    'w' : int(bbox_w),
                    'h' : int(bbox_h)
                }
                detect = Detection(tracking.id,name,full_path,boundingbox,data['event_time'])
                detect.add(log)
                vehicle_coord = data['img'][int(output[1]):int(output[3]),int(output[0]):int(output[2])]
                vehicle_coord = cv2.resize(vehicle_coord, (416, 416), interpolation=cv2.INTER_CUBIC)
                crop_image = recognize_lp(vehicle_coord,mlp,count, detect.id,log)
                m = recognize_vehicle(data['img'],vr,detect.id,log)
                plot_one_box(bboxes, data['img'], label=name, color=(
                    255, 0, 0), line_thickness=2)
                response.append({
                    'data_key' : 'GB_20210001_LPR',
                    'device_id' : device['id'],
                    'tracking_id' : tracking.id,
                    'type' : detect.type,
                    'attribute' : m,
                    'region' : device['region'],
                    'full_image': detect.full_image,
                    'crop_image' : crop_image,
                    'bounding_box' : detect.bounding_box,
                    'event_time' : data['event_time'].strftime("%m:%d:%Y_%H_%M_%S.%f")
                })
            cv2.imwrite(full_path,data['img'])
            memory = {i:memory[i] for i in memory if not memory[i].frames_since_seen>= MAX_UNSEND_FRAMES}
            log.info("Send data:{}".format(response))
            try:
                if len(response) > 0:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(handle_message(response,log))
                    loop.stop()
                    loop.close()
                    log.info("Sent data!!!")
            except Exception as e:
                log.error(e)
                continue


def recognize_vehicle(frame,vr,detect_id,log):
    data = c.get_classify_by_track_id(detect_id,log)
    if data.code is not CODE_EMPTY:
        return data.data['meta_data']
    img = vr.pre_process(frame)
    color,direction,type = vr.predict(img)
    m = {
        'color': color,
        'direction' : direction,
        'type' : type
    }
    classify = Classification(detect_id,m)
    classify.add(log)
    return m

def recognize_lp(frame,mlp,count,detect_id,log):
    crop_time = datetime.now().strftime("%m:%d:%Y_%H_%M_%S.%f")
    # crop_image = cv2.resize(frame, (416, 416), interpolation=cv2.INTER_CUBIC)
    crop_image = mlp.lp_image(frame)
    if crop_image is not None:
        crop_path = os.path.join(STORAGE,'crop_image',str(count) + crop_time+'.jpg')
        cv2.imwrite(crop_path,crop_image)
        recognize = Recognize(detect_id,crop_path)
        recognize.add(log)
        return crop_path
    return None


async def handle_message(data,log):
    uri = "ws://192.168.0.179:8000"
    async with websockets.connect(uri) as websocket:
        for d in data :
            await websocket.send(json.dumps(d))
            log.info('Sent data!!!')

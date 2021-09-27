import cv2
import os
import time
from datetime import datetime
from queue import Queue
import logging
import numpy as np
import asyncio
import websockets
import json
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler 

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

import src.handler.track as t
import  src.handler.vehicle as v
import src.handler.classification as c
import src.handler.vehicle_management as mg


# logging.getLogger('apscheduler').setLevel(logging.WARNING)

ROOTDIR = '/usr/src/Backend/src/AI'
STORAGE = '/usr/src/Backend/src/AI/storage'
q = Queue()
tracking_data = Queue()

# data = None
# image = None
# event_time = None
pts = [(593, 709), (9, 555), (503, 269), (695, 240), (794, 308), (595, 705)]


def gen_frame(device,model,log):
    kcw = KeyClipWriter(bufSize=100)
    mlp = LisencePlate(weights='./src/AI/models/lpr-spcs.pt')
    vr = Car_Classifier(num_cls=19, model_path='./src/AI/models/epoch_39.pth', device='cuda')
    freq = cv2.getTickFrequency()
    frame_rate_calc  = 25
    deepsort = model.deepsort
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
            videostream  = VideoStream(device.stream_url,resolution=(1280,720),framerate=60)
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
                current_frame = cv2.resize(current_frame, (1280,720 ))
                mask = np.zeros(current_frame.shape, np.uint8)
                points = np.array(pts, np.int32)
                points = points.reshape((-1, 1, 2))
                mask = cv2.polylines(mask, [points], True, (255, 255, 255), 2)
                mask2 = cv2.fillPoly(mask.copy(), [points], (255, 255, 255))  # 用于求 ROI
                mask3 = cv2.fillPoly(mask.copy(), [points], (0, 255, 0))
                show_image = cv2.addWeighted(src1=current_frame, alpha=0.8, src2=mask3, beta=0.2, gamma=0)
                roi = cv2.bitwise_and(mask2, current_frame)
                model.start(roi,show_image,current_frame)

                cv2.putText(model.show_image,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
                ret, buffer = cv2.imencode('.jpg', model.show_image)
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
                                20,device.id,log)
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
    while True:
        # timeout_start = time.time()
        response = []
        # while time.time() < timeout_start + 0.2:
        #     tracking = tracking_data.get()
        #     if tracking is None:
        #         continue
        #     track_output = deepsort.update(tracking['xywhs'].cpu(), tracking['confs'].cpu(), 
        #                     tracking['clss'], tracking['img'])
        #     if len(track_output) > 0:
        #         for j, (output, conf) in enumerate(zip(track_output, tracking['confs'])):
        #             id = output[4]
        #             cls = output[5]

        #             c = int(cls)  # integer class
        #             track_result = {
        #                     "device_id" : device.id,
        #                     "video_id" : kcw.video_id,
        #                     "tracking_number" : int(id.item()),
        #                     "vehicle_id" : None,
        #                     "start_time" : datetime.now(),
        #                     "end_time" : datetime.now()
        #                 }
        #             tracking = create_or_update(track_result,log)
        data = tracking_data.get()
        if data is None:
            continue
        data_time = datetime.now().strftime("%m:%d:%Y_%H_%M_%S.%f")
        full_path = os.path.join(STORAGE,'full_image',data_time+'.jpg')
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
                # crop_time = datetime.now().strftime("%m:%d:%Y_%H_%M_%S.%f")
                # crop_image = data['img'][int(output[1]):int(output[3]), int(output[0]):int(output[2])]
                # crop_image = cv2.resize(crop_image, (416, 416), interpolation=cv2.INTER_CUBIC)
                # licenseplate = mlp.recog_lpr(data['img'])
                # crop_path = os.path.join(STORAGE,'crop_image',str(count) + crop_time+'.jpg')
                # cv2.imwrite(crop_path,crop_image)
                licenseplate , crop_image,vehicle_id = recognize_lp(data['img'],mlp,count, device.id,log)
                if licenseplate == 'unknonwn':
                    plot_one_box(bboxes, data['img'], label=name, color=(255, 0, 0), line_thickness=2)
                    track_result = {
                        "video_id" : kcw.video_id,
                        "tracking_number" : int(id.item()),
                        "vehicle_id" : vehicle_id,
                        "start_time" : datetime.now(),
                        "end_time" : datetime.now()
                    }
                    tracking = t.create_or_update(track_result,log)
                    boundingbox = {
                        'x' : int(bbox_left),
                        'y' : int(bbox_top),
                        'w' : int(bbox_w),
                        'h' : int(bbox_h)
                    }
                    detect = Detection(tracking.id,name,full_path,boundingbox,data['event_time'])
                    detect.add(log)
                    response.append({
                        'data_key' : 'GB_20210001_LPR',
                        'device_id' : device.id,
                        'tracking_id' : tracking.id,
                        'vehicle_id' : vehicle_id,
                        'license _plate' : licenseplate,
                        'type' : detect.type,
                        'attribute' : None,
                        'region' : device.region,
                        'full_image': detect.full_image,
                        'crop_image' : crop_image,
                        'bounding_box' : detect.bounding_box,
                        'event_time' : data['event_time'].strftime("%m:%d:%Y_%H_%M_%S.%f")
                    })
                else:
                    m = recognize_vehicle(data['img'],vr,vehicle_id,log)
                    plot_one_box(bboxes, data['img'], label=name, color=(255, 0, 0), line_thickness=2)
                    count += 1
                    track_result = {
                        "video_id" : kcw.video_id,
                        "tracking_number" : int(id.item()),
                        "vehicle_id" : vehicle_id,
                        "start_time" : datetime.now(),
                        "end_time" : datetime.now()
                    }
                    tracking = t.create_or_update(track_result,log)
                    boundingbox = {
                        'x' : int(bbox_left),
                        'y' : int(bbox_top),
                        'w' : int(bbox_w),
                        'h' : int(bbox_h)
                    }
                    detect = Detection(tracking.id,name,full_path,boundingbox,data['event_time'])
                    detect.add(log)
                    response.append({
                        'data_key' : 'GB_20210001_LPR',
                        'device_id' : device.id,
                        'tracking_id' : tracking.id,
                        'vehicle_id' : vehicle_id,
                        'license _plate' : licenseplate,
                        'type' : detect.type,
                        'attribute' : m,
                        'region' : device.region,
                        'full_image': detect.full_image,
                        'crop_image' : crop_image,
                        'bounding_box' : detect.bounding_box,
                        'event_time' : data['event_time'].strftime("%m:%d:%Y_%H_%M_%S.%f")
                    })
            cv2.imwrite(full_path,data['img'])
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


def recognize_vehicle(frame,vr,vehicle_id,log):
    data = c.get_classify_by_vehicle_id(vehicle_id,log)
    if data.code is not CODE_EMPTY:
        return data.data['meta_data']
    img = vr.pre_process(frame)
    color,direction,type = vr.predict(img)
    m = {
        'color': color,
        'direction' : direction,
        'type' : type
    }
    classify = Classification(vehicle_id,m)
    classify.add(log)
    return m

def recognize_lp(frame,mlp,count,device_id,log):
    crop_time = datetime.now().strftime("%m:%d:%Y_%H_%M_%S.%f")
    # crop_image = cv2.resize(frame, (416, 416), interpolation=cv2.INTER_CUBIC)
    lp, crop_image = mlp.recog_lpr(frame)
    if lp == 'unknonwn':
        return lp,None,None
    crop_path = os.path.join(STORAGE,'crop_image',str(count) + crop_time+'.jpg')
    cv2.imwrite(crop_path,crop_image)
    vehicle = v.create_or_update(lp,log)
    m = mg.create(vehicle.id,device_id,log)
    recognize = Recognize(vehicle.id,lp,crop_path)
    recognize.add(log)
    return lp, crop_path, vehicle.id


async def handle_message(data,log):
    uri = "ws://192.168.0.5:8000"
    async with websockets.connect(uri) as websocket:
        for d in data :
            await websocket.send(json.dumps(d))
            log.info('Sent data!!!')
import os
import logging
import sys
import base64
import json

import time
from threading import Thread
from werkzeug.utils import secure_filename

log = logging.getLogger()
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

from flask import  request,render_template,Response , send_file, make_response,send_from_directory
from flask_api import status
sys.path.append('/usr/src/Backend')
# sys.path.append('/home/goback-research/LPR/TVSLS/Backend')
print(sys.path)
from src import app
from src.service.response import *
from src.const import *
from src.AI.process import gen_frame, gen_vid, setup_cameras
from src.AI.yolov5 import  LisencePlate
from src.migrate.device import Device
from src.handler.search import *
from src.handler.validate import validate_id, validate_vehicle_id

from src.handler.video import *
from src.handler.track import *
import src.handler.vehicle as v
from src.handler.upload import *
model = None

@app.route('/stream_feed')
def stream_feed():
    return Response(setup_cameras(log), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed/<video_name>')
def video_feed(video_name):
    return Response(gen_vid(video_name,model,log), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/stream')
def stream():
    return render_template('index.html')

@app.route('/video/<video_name>')
def video(video_name):
    return render_template('video.html',vid_name=video_name)


@app.route('/search', methods=["POST"])
def search_in_range():
    log.info('Starting Process....')
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        start_time = json_reg['start_time']
        end_time = json_reg['end_time']
        valid = ValidateData(start_time=start_time,end_time=end_time)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        res = search_by_time(start_time,end_time,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if res.data is None :
            return ApiResponse(message=res.message,data= None), status.HTTP_404_NOT_FOUND
        return ApiResponse(message=res.message,data=res.data,success= True), status.HTTP_200_OK

@app.route('/device/<device_id>/vehicle',methods=["GET"])
def search_by_id(device_id):
    log.info('Starting Process....')
    if request.method == "GET":
        if device_id is None:
            return ApiResponse(message="Invalid device id"), status.HTTP_400_BAD_REQUEST
        valid = validate_id(device_id,log)
        if valid.code is not CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST
        res = search_vehicle_by_id(device_id,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if res.data is None :
            return ApiResponse(message=res.message,data= None), status.HTTP_404_NOT_FOUND
        return ApiResponse(message=res.message,data=res.data,success= True), status.HTTP_200_OK

@app.route('/device/<device_id>/video',methods=["GET"])
def get_video_list(device_id):
    log.info('Starting Process....')
    if request.method == "GET":
        if device_id is None:
            return ApiResponse(message="Invalid device id"), status.HTTP_400_BAD_REQUEST
        valid = validate_id(device_id,log)
        if valid.code is not CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST         
        res = get_list_video_by_device_id(device_id,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if res.data is None :
            return ApiResponse(message=res.message,data= None), status.HTTP_404_NOT_FOUND
        return ApiResponse(message=res.message,data=res.data,success= True), status.HTTP_200_OK

@app.route('/device/<device_id>/video/<video_id>',methods=["GET"])
def get_video(device_id,video_id):
    log.info('Starting Process....')
    if request.method == "GET":
        if device_id is None:
            return ApiResponse(message="Invalid device id"), status.HTTP_400_BAD_REQUEST
        valid = validate_id(device_id,log)
        if valid.code is not CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST
        res = search_video_by_id(video_id,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if res.data is None :
            return ApiResponse(message=res.message,data= None), status.HTTP_404_NOT_FOUND
        if res.data['end_time'] is None:
            return ApiResponse(message="The video is processing",data=res.data,code=CODE_PROCESSING), status.HTTP_200_OK
        return ApiResponse(message=res.message,data=res.data,success= True), status.HTTP_200_OK

@app.route('/device/<device_id>/video/<tracking_id>',methods=["GET"])
def get_video_by_tracking(device_id,tracking_id):
    log.info('Starting Process....')
    if request.method == "GET":
        if device_id is None:
            return ApiResponse(message="Invalid device id"), status.HTTP_400_BAD_REQUEST
        valid = validate_id(device_id,log)
        if valid.code is not CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST
        res = get_video_by_tracking_id(tracking_id,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if res.data is None :
            return ApiResponse(message=res.message,data= None), status.HTTP_404_NOT_FOUND
        if res.data['end_time'] is None:
            return ApiResponse(message="The video is processing",data=res.data,code=CODE_PROCESSING), status.HTTP_200_OK
        return ApiResponse(message=res.message,data=res.data,success= True), status.HTTP_200_OK

@app.route('/device/<device_id>/detect/<tracking_id>',methods=["GET"])
def get_detect_by_tracking_id(device_id,tracking_id):
    log.info('Starting Process....')
    if request.method == "GET":
        if device_id is None:
            log.info("Device is invalid!!")
            return ApiResponse(message="Invalid device id"), status.HTTP_400_BAD_REQUEST
        valid = validate_id(device_id,log)
        if valid.code is not CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST
        res = get_detect_result_by_tracking(tracking_id,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if res.data is None :
            return ApiResponse(message=res.message,data= None), status.HTTP_404_NOT_FOUND
        return ApiResponse(message=res.message,data=res.data,success= True), status.HTTP_200_OK

@app.route('/vehicle/<vehicle_id>/detect',methods=["GET"])
def get_detect_by_vehicle_id(vehicle_id):
    log.info('Starting Process....')
    if request.method == "GET":
        if vehicle_id is None:
            log.info("Device is invalid!!")
            return ApiResponse(message="Invalid device id"), status.HTTP_400_BAD_REQUEST
        valid = validate_vehicle_id(vehicle_id,log)
        if valid.code is not CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The vehicle id not valid'), status.HTTP_400_BAD_REQUEST
        res = v.get_detect_result_by_vehicle_id(vehicle_id,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if res.data is None :
            return ApiResponse(message=res.message,data= None), status.HTTP_404_NOT_FOUND
        return ApiResponse(message=res.message,data=res.data,success= True), status.HTTP_200_OK

@app.route('/vehicle/<vehicle_id>/info',methods=["GET"])
def get_vehicle_info_by_lp(vehicle_id):
    log.info('Starting Process....')
    if request.method == "GET":
        if vehicle_id is None:
            log.info("Device is invalid!!")
            return ApiResponse(message="Invalid device id"), status.HTTP_400_BAD_REQUEST
        valid = validate_vehicle_id(vehicle_id,log)
        if valid.code is not CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The vehicle id not valid'), status.HTTP_400_BAD_REQUEST
        license_plate = request.args.get("lp")
        if license_plate is None:
            return ApiResponse(message='The license plate not valid'), status.HTTP_412_PRECONDITION_FAILED
        res = v.get_vehicle_information_by_license_plate(license_plate,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if res.data is None :
            return ApiResponse(message=res.message,data= None), status.HTTP_404_NOT_FOUND
        if res.data is CODE_EMPTY:
            return ApiResponse(message=res.message,data= res.data,code=CODE_EMPTY), status.HTTP_206_PARTIAL_CONTENT
        return ApiResponse(message=res.message,data=res.data,success= True), status.HTTP_200_OK

@app.route('/watch', methods=['POST','GET'])
def serve_video():
    log.info('Starting Process....')
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        vid_path = json_reg['video_id']
        # vid_path = request.args.get("p")
        log.info('vid path: {}'.format(vid_path))
        resp = make_response(send_file(vid_path, 'video/x-msvideo'))
        resp.headers['Content-Disposition'] = 'inline'
        return resp
    if request.method == 'GET':
        # vid_path = json_reg['vid_path']
        video_id = request.args.get("v")
        res = search_video_by_id(video_id,log)
        rec_path = res.data['video_path']
        log.info('vid path: {}'.format(rec_path))
        resp = make_response(send_file(rec_path, 'video/webm'))
        resp.headers['Content-Disposition'] = 'inline'
        return resp

@app.route('/uploads/<video_id>', methods=['POST'])
def upload_files(video_id):
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        saved_file = json_reg['save_path']
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                    file_ext != validate_video(uploaded_file.stream):
                return "Invalid Video", 400
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return '', 204

@app.route('/download/<video_id>')
def downoad(video_id):
    return render_template('download.html',video_id=video_id)

@app.route('/download_video/<video_id>')
def downoad_video(video_id):
     if request.method == "GET":
        res = download_file(video_id,log)
        if res.code is not CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        video_path = res.data 
        log.info(video_path)
        return send_file(video_path, as_attachment= True)

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413
### Config APIs
@app.route('/configs/update')
def config_update():
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        speed_cofig = json_reg['speed']
        lane_config = json_reg['lane']
        direct_config = json_reg['direction']
        storage_config = json_reg['storage']
        video_config = json_reg['video']
        valid = ValidateConfig(speed_conf=speed_cofig,lane_conf=lane_config,
                            direct_conf=direct_config,storage_config=storage_config,video_conf=video_config)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST

@app.route('/configs/init')
def config_init():
    # if request.method == "GET":

    pass


if __name__ == '__main__':
    model = LisencePlate()
    with open('./src/config.json') as f:
        data = json.load(f)
    devices = data['Device']
    
    for device in devices:
        # log.info("passss hereee1")
        d = Device(device['type'],device['group'],device['location'],device['region'],device['url'])
        d.add(log)
        thread = Thread(target=gen_frame,args=(d,model,log))
        thread.setDaemon(True)
        thread.start()
    log.info("passss hereee1:{}".format(len(devices)))
    app.run(host="0.0.0.0", port=80, use_reloader=False)

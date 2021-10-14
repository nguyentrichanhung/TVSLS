import os
import logging
import sys
import base64
import json

from datetime import datetime, timedelta
from threading import Thread
from werkzeug.utils import secure_filename
from  werkzeug.security import generate_password_hash, check_password_hash




log = logging.getLogger()
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


# flask imports
from flask import  request,render_template,Response , send_file, make_response,send_from_directory
from flask_api import status
sys.path.append('/usr/src/Backend')

from src import app
from src.service.response import *
from src.const import *
from src.AI.process import gen_frame, gen_vid, setup_cameras,get_lane_properties
from src.AI.yolov5 import  LisencePlate
from src.migrate.device import Device
from src.handler.search import *
from src.handler.validate import validate_id, validate_vehicle_id

from src.handler.video import *
from src.handler.track import *
from src.handler.upload import *
from src.handler.health_check import *

import src.handler.vehicle as v
import src.handler.lanes as l
import src.handler.config as c
import src.handler.device as d
import src.handler.users as u

from src.util.valid import *
from src.util.auth import *

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


### START SYSTEM
@app.route('/start/<device_id>', methods=["GET"])
@token_required
def start(user_info,device_id):
    if request.method == "GET":
        lanes = l.get_config_lst(log)
        if lanes.code == CODE_EMPTY:
            return ApiResponse(message=lanes.message,success=False), status.HTTP_400_BAD_REQUEST
        if lanes.code != CODE_DONE:
            return ApiResponse(message=lanes.message,success=False), status.HTTP_500_INTERNAL_SERVER_ERROR
        get_lane_properties(lanes.data,log)
        device = d.get_device_by_id(device_id,log)
        if device.code ==CODE_EMPTY:
            return ApiResponse(message=device.message,success=False), status.HTTP_400_BAD_REQUEST
        if device.code != CODE_DONE:
            return ApiResponse(message=device.message,success=False), status.HTTP_500_INTERNAL_SERVER_ERROR
        if device.data['type'] != 'camera':
            return ApiResponse(message='Device must be camera',success=False), status.HTTP_400_BAD_REQUEST
        config = c.get_config(log)
        if config.code ==CODE_EMPTY:
            return ApiResponse(message=config.message,success=False), status.HTTP_400_BAD_REQUEST
        if config.code != CODE_DONE:
            return ApiResponse(message=config.message,success=False), status.HTTP_500_INTERNAL_SERVER_ERROR
        log.info(config.data)
        # data =json.loads(config.data['config_data'])
        stream_config = config.data['config_data']['stream']
        if len(stream_config.keys()) == 0:
            return ApiResponse(message='Need to update the stream config',success=False), status.HTTP_400_BAD_REQUEST
        video_config = config.data['config_data']['videos']
        if len(video_config.keys()) == 0:
            return ApiResponse(message='Need to update the video config',success=False), status.HTTP_400_BAD_REQUEST
        model = LisencePlate()
        thread = Thread(target=gen_frame,args=(device.data,model,stream_config,video_config,log))
        thread.setDaemon(True)
        thread.start()
        return ApiResponse(message="Internal process is running",success=True), status.HTTP_200_OK

### HEALTH CHECK
@app.route('/system/cpu', methods=["GET"])
@token_required
def cpu_info(user_info):
    if request.method == "GET":
        res = cpu_check(log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,data=res.data,success=True), status.HTTP_200_OK

@app.route('/system/gpu', methods=["GET"])
@token_required
def gpu_info(user_info):
    if request.method == "GET":
        res = gpu_check(log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,data=res.data,success=True), status.HTTP_200_OK

### DEVICE MANAGEMENT MODULE
@app.route('/device', methods=["POST"])
@token_required
def add_devices(user_info):
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        device = json_reg['device']
        valid = ValidateDevce(device)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        res = d.creates(device,log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,data=res.data,success=True), status.HTTP_201_CREATED


@app.route('/device/<device_id>', methods=["GET"])
@token_required
def get_devices(user_info,device_id):
    if request.method == "GET":
        if not device_id:
            return ApiResponse(message="device id cannot empty!!"), status.HTTP_400_BAD_REQUEST
        res = d.get_device(device_id,log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,data=res.data,success=True), status.HTTP_200_OK

@app.route('/device/<device_id>', methods=["PATCH"])
@token_required
def update_device(user_info,device_id):
    if request.method == "PATCH":
        if not device_id:
            return ApiResponse(message="device id cannot empty!!"), status.HTTP_400_BAD_REQUES
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        device_info = json_reg['device']
        res = d.edit_device(device_id,device_info,log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,data=res.data,success=True), status.HTTP_200_OK

### CONFIG MANAGEMENT MODULE

@app.route('/configs/common', methods=["POST"])
@token_required
def add_config(user_info):
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        data_stream = json_reg['stream']
        data_video = json_reg['videos']
        device_id = json_reg['device_id']
        valid = ValidateConfig(data_stream,data_video,device_id)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        res = c.creates(device_id,data_video,data_stream,log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,success=True), status.HTTP_201_CREATED

@app.route('/configs/common', methods=["GET"])
@token_required
def get_config(user_info):
    if request.method == "GET":
        res = c.get_config(log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False),status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,data=res),status.HTTP_200_OK

@app.route('/configs/common', methods=["PATCH"])
@token_required
def update_config(user_info):
    if request.method == "PATCH":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        data_stream = json_reg['stream']
        data_video = json_reg['videos']
        device_id = json_reg['device_id']
        config_id = json_reg['config_id']
        valid = ValidateConfig(data_stream,data_video,device_id)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        res = c.updates(config_id,device_id,data_video,data_stream,log)
        if res != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,success=True), status.HTTP_200_OK        


@app.route('/configs/lanes', methods=["POST"])
@token_required
def create_lanes(user_info):
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        lanes = json_reg['lanes']
        device_id = json_reg['device_id']
        valid = ValidateLanes(lanes,device_id)
        ok,msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        device = d.get_device_by_id(device_id,log)
        if device.code == CODE_EMPTY:
            return ApiResponse(message=device.message), status.HTTP_400_BAD_REQUEST
        if device.code != CODE_DONE:
            return ApiResponse(message=device.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        res = l.creates(lanes,device_id,log)
        if res != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,success=True), status.HTTP_201_CREATED

@app.route('/configs/lanes', methods=["GET"])
@token_required
def get_lanes(user_info):
    if request.method == "GET":
        res = l.get_config_lst(log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False),status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,data=res),status.HTTP_200_OK

@app.route('/configs/lanes', methods=["PATCH"])
@token_required
def update_lanes(user_info):
    if request.method == "PATCH":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        lanes = json_reg['lanes']
        device_id = json_reg['device_id']
        valid = ValidateLanes(lanes,device_id)
        ok,msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        res = l.updates(lanes,device_id,log)
        if res != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,success=True), status.HTTP_200_OK

@app.route('/configs/lanes/<lane_id>', methods=["DELETE"])
@token_required
def delete_lane(user_info,lane_id):
    if request.method == "GET":
        if lane_id is None:
            return ApiResponse(message="lane id cannot Null"), status.HTTP_400_BAD_REQUEST
        res = l.delete(lane_id)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,success=False), status.HTTP_400_BAD_REQUEST
        return ApiResponse(message=res.message,success=True), status.HTTP_200_OK

### USER MANAGEMNT MODULE
@app.route('/login', methods =['POST'])
def login():
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        name = json_reg['name']
        password = json_reg['password']
        valid = ValidateLogin(name=name,password=password)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        user = u.get_user_by_name(name,log)
        if user.code == CODE_EMPTY:
            return ApiResponse(message=user.message,data = None), status.HTTP_401_UNAUTHORIZED
        if user.code != CODE_DONE:
            return ApiResponse(message=user.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        # role = u.get_user_roles(user['id'],log)
        payload = {
            "role": user.data['role'],
            "user_id" : user.data['id'],
            "exp" :datetime.now() + timedelta(seconds = int(os.environ['ACCESS_TOKEN_TTL']))
            }
        pass_check = compare_password(user.data['hash_password'],password,log)
        if pass_check.code == CODE_FAIL:
            return ApiResponse(message=user.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        if pass_check.code == CODE_UNAUTHORIZE:
            return ApiResponse(message=user.message,data = None), status.HTTP_401_UNAUTHORIZED
        ok,token = generate_jwt_token(payload,app.config['JWT_SECRET'],log)
        if not ok:
            return ApiResponse(message="Cannot generate token",data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        return ApiResponse(message="Login successful",data=token,success= True), status.HTTP_200_OK

@app.route('/user/update_role', methods =['POST'])
@token_required
def update_user_role(user_info):
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        user_id = json_reg['user_id']
        role = json_reg['role']
        valid = ValidateRoleInfo(user_id=user_id,role=role)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        res = u.update_user_role(user_id,role,log)
        if res.code == CODE_EMPTY:
            return ApiResponse(message=res.message,data = None), status.HTTP_404_NOT_FOUND
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        return ApiResponse(message=res.message), status.HTTP_200_OK

@app.route('/user/update_password', methods =['POST'])
@token_required
def update_user_password(user_info):
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        log.info(user_info)
        user = u.get_user_by_id(user_info['user_id'],log)
        user_id = None
        if user.data['role'] == ADMIN_ROLE:
            user_id = json_reg['user_id']
            password  = json_reg['password']
        else:
            password  = json_reg['password']
            user_id = user.data['id']
        valid = ValidateLogin(name=user_id,password=password)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        ok,err = validate_password(password,log)
        if not ok:
            return ApiResponse(message=err), status.HTTP_400_BAD_REQUEST
        res = u.update_user_password(user_id,password,log)
        if res.code ==CODE_EMPTY:
            return ApiResponse(message=res.message,data = None), status.HTTP_404_NOT_FOUND
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        return ApiResponse(message=res.message), status.HTTP_200_OK

@app.route('/user/add_user', methods =['POST'])
@token_required
def add_user(user_info):
    if request.method == "POST":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        user_name = json_reg['name']
        user_role = json_reg['role']
        password  = json_reg['password']
        valid = ValidateRegister(username=user_name,password=password,role = user_role)
        ok, msg = valid.validate()
        if not ok:
            return ApiResponse(message=msg), status.HTTP_400_BAD_REQUEST
        ok,err = validate_password(password,log)
        if not ok:
            return ApiResponse(message=err), status.HTTP_401_UNAUTHORIZED
        res = u.add_new_user(user_name,password,user_role,log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        return ApiResponse(message=res.message), status.HTTP_200_OK

@app.route('/user/get_users', methods =['POST'])
@token_required
def get_users(user_info):
    if request.method == "GET":
        json_reg = request.get_json(force=True,silent=True)
        if not json_reg:
            return ApiResponse(message="Invalid json type"), status.HTTP_400_BAD_REQUEST
        user = u.get_user_by_id(user_info['user_id'],log)
        if user.data['role'] != ADMIN_ROLE:
            return ApiResponse(message='Dont have permission'), status.HTTP_406_NOT_ACCEPTABLE
        res = u.get_users(log)
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        return ApiResponse(message=res.message,data=res.data), status.HTTP_200_OK

### SEARCH MODULE
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
        if res.code != CODE_DONE:
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
        if valid.code != CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST
        res = search_vehicle_by_id(device_id,log)
        if res.code != CODE_DONE:
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
        if valid.code != CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST         
        res = get_list_video_by_device_id(device_id,log)
        if res.code != CODE_DONE:
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
        if valid.code != CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST
        res = search_video_by_id(video_id,log)
        if res.code != CODE_DONE:
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
        if valid.code != CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST
        res = get_video_by_tracking_id(tracking_id,log)
        if res.code != CODE_DONE:
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
        if valid.code != CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The device id not valid'), status.HTTP_400_BAD_REQUEST
        res = get_detect_result_by_tracking(tracking_id,log)
        if res.code != CODE_DONE:
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
        if valid.code != CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The vehicle id not valid'), status.HTTP_400_BAD_REQUEST
        res = v.get_detect_result_by_vehicle_id(vehicle_id,log)
        if res.code != CODE_DONE:
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
        if valid.code != CODE_DONE:
            return  ApiResponse(message=valid.message), status.HTTP_500_INTERNAL_SERVER_ERROR
        if valid.data is None:
            return ApiResponse(message='The vehicle id not valid'), status.HTTP_400_BAD_REQUEST
        license_plate = request.args.get("lp")
        if license_plate is None:
            return ApiResponse(message='The license plate not valid'), status.HTTP_412_PRECONDITION_FAILED
        res = v.get_vehicle_information_by_license_plate(license_plate,log)
        if res.code != CODE_DONE:
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
        if res.code != CODE_DONE:
            return ApiResponse(message=res.message,data = None), status.HTTP_500_INTERNAL_SERVER_ERROR
        video_path = res.data 
        log.info(video_path)
        return send_file(video_path, as_attachment= True)

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

if __name__ == '__main__':
    # model = LisencePlate()
    # with open('./src/config.json') as f:
    #     data = json.load(f)
    # devices = data['Device']
    
    # for device in devices:
    #     # log.info("passss hereee1")
    #     d = Device(device['type'],device['group'],device['location'],device['region'],device['url'])
    #     d.add(log)
    #     thread = Thread(target=gen_frame,args=(d,model,log))
    #     thread.setDaemon(True)
    #     thread.start()
    # log.info("passss hereee1:{}".format(len(devices)))
    app.run(host="0.0.0.0", port=80, use_reloader=False)

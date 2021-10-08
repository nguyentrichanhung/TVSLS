import sys
import os
import traceback
from threading import Thread
import time
from datetime import datetime
from pathlib import Path
# sys.path.insert(0, '/home/goback-research/LPR/yolov5')
import cv2
import torch
import torch.backends.cudnn as cudnn
import numpy as np
from numpy import random

from src.AI.models.experimental import attempt_load
from src.AI.utils.datasets import LoadStreams, LoadImages,letterbox
from src.AI.utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging
from src.AI.utils.plots import plot_one_box
from src.AI.utils.torch_utils import select_device
from src.AI.deep_sort_pytorch.utils.parser import get_config
from src.AI.deep_sort_pytorch.deep_sort import DeepSort

DEEPSORT_CONFIG = './src/AI/deep_sort_pytorch/configs/deep_sort.yaml'

class LisencePlate:
    """Detect object that tracking frame from camera"""
    def __init__(self,weights='./src/AI/models/yolov5s.pt',opt_device='',imgsz=416):
        # Initialize the labels and tflite model
        set_logging()
        self.save_img = True
        self.count = 0
        self.event_time = None
        self.pframe  = None
        self.bounding_box = []
        self.imgsz = imgsz
        print('Loading model...', end='')
        start_time = time.time()
        self.device = select_device(opt_device)
        self.model = attempt_load(weights, map_location=self.device)
        self.stride = int(self.model.stride.max())
        self.half = self.device.type != 'cpu'
        if self.half:
            self.model.half()
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('Done! Took {} seconds'.format(elapsed_time))
        print('Load Tracking method ...')
        cfg = get_config()
        cfg.merge_from_file(DEEPSORT_CONFIG)
        self.deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT,
                    max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                    nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                    max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                    use_cuda=True)
	    # Variable to control when the camera is stopped
        self.stopped = False


    def start(self,frame,show_img,current_frame):
	# Start the thread that reads frames from the video stream
        # frame = frame.copy()
        # self.detect(frame)
        self.recog(frame,show_img,current_frame)
        return self

    def lp_image(self,frame):
        lp_img = None
        img = letterbox(frame, self.imgsz, stride=self.stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        pred = self.model(img, augment=True)[0]
        pred = non_max_suppression(pred, 0.3, 0.55, classes=[0], agnostic=True)
        
        for i, det in enumerate(pred):
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
                for *xyxy, conf, cls in reversed(det):
                    ci = frame[int(xyxy[1]):int(xyxy[3]),int(xyxy[0]):int(xyxy[2])]
                    ci = cv2.resize(ci, (416, 416), interpolation=cv2.INTER_CUBIC)
                    lp_img = ci.copy()
        return lp_img

    def recog_lpr(self,frame):
        lp_img = None
        img = letterbox(frame, self.imgsz, stride=self.stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        final_str = ''
        pred = self.model(img, augment=True)[0]
        pred = non_max_suppression(pred, 0.3, 0.55, classes=[0], agnostic=True)
        
        for i, det in enumerate(pred):
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
                for *xyxy, conf, cls in reversed(det):
                    ci = frame[int(xyxy[1]):int(xyxy[3]),int(xyxy[0]):int(xyxy[2])]
                    ci = cv2.resize(ci, (416, 416), interpolation=cv2.INTER_CUBIC)
                    lp_img = ci.copy()
                    nci = letterbox(ci,self.imgsz,self.stride)[0]

                    nci = nci[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
                    nci = np.ascontiguousarray(nci)
                    
                    nci = torch.from_numpy(nci).to(self.device)
                    nci = nci.half() if self.half else nci.float()  # uint8 to fp16/32
                    nci /= 255.0  # 0 - 255 to 0.0 - 1.0
                    if nci.ndimension() == 3:
                        nci = nci.unsqueeze(0)

                    
                    pred_dg = self.model(nci, augment=True)[0]
                    pred_dg = non_max_suppression(pred_dg, 0.35, 0.45, classes=[22,23,24,25,26,27,28,29,30,31], agnostic=True)
                    
                    for j, det_dg in enumerate(pred_dg):
                        if len(det_dg):
                            bboxs = []
                            lpboxs = []
                            
                            det_dg[:, :4] = scale_coords(nci.shape[2:], det_dg[:, :4], ci.shape).round()
                            for *box, conf, cls1 in reversed(det_dg):
                                if self.names[int(cls1)] == 'lp':
                                    continue
                                dw = box[2].item() - box[0].item()
                                dh = box[3].item() - box[1].item()
                                lpboxs.append( [ int(cls1),(box[0].item()+dw/2)/ci.shape[1],(box[1].item()+dh/2)/ci.shape[0],dw/ci.shape[1],dh/ci.shape[0] ] )
                                bboxs.append([box[0],box[1],box[2],box[3],self.names[int(cls1)]])
                            if len(bboxs):
                                bboxs.sort(key=lambda x:x[1])
                                l1 = [x for x in bboxs if x[1]<bboxs[0][3]]
                                l2 = [x for x in bboxs if x[1]>bboxs[0][3]]
                                l1.sort(key=lambda x:x[0])
                                l2.sort(key=lambda x:x[0])
                                if len(l2):
                                    final_str = "".join([x[4] for x in l1]) + "\n" + "".join([x[4] for x in l2])
                                else:
                                    final_str = "".join([x[4] for x in l1])
        if len(final_str) > 3:
            return final_str, lp_img
        return 'unknonwn', lp_img



    def recog(self,frame,show_img,current_frame):
        self.bounding_box = []
        self.event_time = None
        self.current_frame = None
        self.show_image  = None
        self.xywhs = None
        self.confs = None
        self.clss = None
        cframe = current_frame.copy()
        img = letterbox(frame, self.imgsz, stride=self.stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        pred = self.model(img, augment=True)[0]
        pred = non_max_suppression(pred, 0.3, 0.55, classes=[2,3,5,7], agnostic=True)
        
        for i, det in enumerate(pred):
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
                area_boxs = []
                self.event_time = datetime.now()
                for *xyxy, conf, cls in reversed(det):
                    # if self.names[int(cls)]  != 'lp':
                    #     continue
                    # plot_one_box(xyxy, cframe, label=self.names[int(cls)], color=self.colors[int(cls)], line_thickness=2)
                    plot_one_box(xyxy, show_img, label=self.names[int(cls)], color=self.colors[int(cls)], line_thickness=2)
                    h = xyxy[3].item() - xyxy[1].item()
                    w = xyxy[2].item() - xyxy[0].item()
                    area_boxs.append( [ self.names[int(cls)],int(xyxy[0]),int(xyxy[1]),w,h ] )

                self.xywhs = xyxy2xywh(det[:, 0:4])
                self.confs = det[:, 4]
                self.clss = det[:, 5]
                self.bounding_box = area_boxs
            else:
                self.deepsort.increment_ages()
        self.current_frame = cframe
        self.show_image = show_img


    def stop(self):
	    # Indicate that the camera and thread should be stopped
        self.stopped = True
        self.current_frame = None
        # frame = None
        # self.thread.join()
        return False

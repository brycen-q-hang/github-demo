import time
import threading
from threading import Thread, Lock
import urllib.request
import cv2
import re
import array
import numpy as np

import os
import platform
import psutil
import subprocess

from ToFMode import ToFMode
from ToFPlatform import ToFPlatform
from ToFImageRendering import ToFImageRendering
from hwmonitoring import HardwareMonitoring

import socket
import msvcrt as m
import struct 
import sys

# from PIL import Image


class CameraStream(object):
    #const
    TOF_CTRL_TEMP_WIN = '\\tofctrl\\tof_ctrl_temp.exe'
    TOF_CTRL_PARAMS_WIN = '\\tofctrl\\tof_ctrl_params.exe'
    TOF_CTRL_ENUM_WIN = '\\tofctrl\\tof_ctrl_enum.exe'

    #singleton const
    __instance = None

    #tof mode & data
    mode = ToFMode.DEPTH
    
    #buffer_ir_jpeg = None #d_vu - disable - 20191018
    buffer_jpeg = None
    #codeColorMap = 4

    #video vars & const    
    src = -1
    CONST_MAX_DEVICE = 2

    #device vars
    limitfps = 30.0
    #limitfps = 10.0 #d_vu - for demo: reduce fps for network bandwidth optimization - 20191021

    time_LastRead = -1000

    @staticmethod
    def getInstance():
        if CameraStream.__instance == None:            
            CameraStream()            
                    
        return CameraStream.__instance
    
    read_lock = None
    read_lock2 = None
    thread2 = None

    #d_vu - add global: socket obj - 20191018
    sk = None
    sk2 = None

    #buff = None

    def __init__(self):
        self.vn = None
        self.buff = None
        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None


        self.sk2 = None

        #d_vu - AttributeError: 'CameraStream' object has no attribute 'frame' - 201901017
        #self.frame = None
        #self.buffer_ir_jpeg = None
        #self.buffer_depth_jpeg = None

        #d_vu - add - 20191018
        self.buffer_jpeg = None

        if self.src == -1:
            #d_vu - TODO: camera id should be detected automatically - 20190916
            if self._myPlatform() == ToFPlatform.Windows:
                self.src = 1
            else:
                self.src = 0
        
        #d_vu - add - 20190917
        if self.thread2 is None:
            self.thread2 = Thread(target=self.tofEnum, args=())
            self.thread2.start()

        self.fReady = False
        
        #d_vu - disable - 2191015, night
        '''
        self.stream = cv2.VideoCapture(self.src)
        (self.grabbed, self.frame) = self.stream.read()
        self.fReady = self.grabbed
        '''
        self.started = False
        self.fReady = True        

        if self.read_lock == None:
            self.read_lock = Lock()

        if self.read_lock2 == None:
            self.read_lock2 = Lock()
        
        CameraStream.__instance = self        
    
    def start(self):
        if self.started:
            print("started! return")

            return None
        
        print("not started! continue")
        self.started = True
        #self.fReady = True #d_vu - remove - dont do this - 20190923

        self.thread = Thread(target=self.update, args=())
        self.thread.start()

        self.thread3 = Thread(target=self.hwUsage, args=())
        self.thread3.start()        

        return self
    
    def getMinBetweenRead(self):
        min_ms = 1.0 / self.limitfps
        #min_ms /= 2.0 #d_vu - add - fixbug: after submit, the video image not update - 20190906
        return min_ms

    #d_vu - add - 20191015
    # The server's hostname or IP address
    HOST = '127.0.0.1'
    PORT = 82

    def read_jpeg(self):
        #print(">> read_jpeg....... mode ", self.mode)
        global codeColorMap_cmd

        #print("\tcode ")
        
        bt = b'1'
        
        if codeColorMap_cmd == 1:
            #print("\t\t1")
            
            bt = b'1'
        elif codeColorMap_cmd == 2:
            #print("\t\t2")

            bt = b'2'
        elif codeColorMap_cmd == 3:
            #print("\t\t3")

            bt = b'3'
        elif codeColorMap_cmd == 9:
            #print("\t\t9")

            bt = b'9'
        elif codeColorMap_cmd == 4:
            #print("\t\t4")
            
            bt = b'4'

        self.buff = None #local variable 'buff' referenced before assignment
        if self.sk == None:
            try:
                #print("send all (1)...")
                self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


                ###
                # self.sk.setsockopt(socket.SOL_SOCKET, socket.TCP_MAXSEG, True)  # must equal size of Recv
                # MAXSEG = self.sk.getsockopt(socket.SOL_SOCKET, socket.TCP_MAXSEG)
                # print("VALUE OFF MAXSEG  ---------- :::::: ---------->>>>>         ",MAXSEG)

                self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,1048576)
                SNDBUFF = self.sk.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
                print("VALUE OFF SND BUFF---------- :::::: ---------->>>>>         ",SNDBUFF)

                self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,1048576)#576)
                RCVBUFF = self.sk.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
                print("VALUE OFF RCV BUFF---------- :::::: ---------->>>>>         ",RCVBUFF)
                #timeval = struct.pack('LL', 0, 34567)
                #self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO,timeval) #SO_RCVLOWAT
                # self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE ,10) #SO_KEEPALIVE 
                # self.sk.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE )


                # timeval = struct.pack('LL', 0, 200000)
                # self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
                # SO_RCVTIMEO = self.sk.getsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO)
                # print("SO_RCVTIMEOs---------- :::::: ---------->>>>>         ",SO_RCVTIMEO)
                #self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,65536 )
               


                ###
                #print("send all (2)...")
                self.sk.connect((self.HOST, self.PORT))
                #print("send all (3)...")
                #self.sk.sendall(bt) # enable jpeg mode
                self.fReady = True
            except Exception as identifier:
                #print("send all (4)...")
                self.sk = None
                self.fReady = False

                print('camera.py - read_jpeg() - EXCPETION MSG ', str(identifier))

                #time.sleep(10)
                #camera.py - EXCEPTION IR - self.read_jpeg()  'NoneType' object has no attribute 'sendall'
                return None #d_vu - return - 20191021 (must)
        try:
            while True:   ######### v_loc 
                if self.isPrevCtrl:
                    cnt = 0

                    t1 = time.perf_counter()
                    while True:
                        #print('helo1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111')
                        try:
                            self.sk.sendall(bt) # ask for next frame
                            self.buff = self.sk.recv(1048576)
                        except Exception as identifier:
                            self.sk = None
                            self.fReady = False

                            pass                         

                        t2 = time.perf_counter()
                        diff = t2 - t1
                        if diff > 1:
                            break
                else:
                    #print("send all (5)...")
                    self.sk.sendall(bt) # ask for next frame

                   
                    self.buff = self.sk.recv(1048576)  
                   

                     
                    # self.read_lock.acquire()            # v_loc_test  
                    # try:
                    #     self.buff1 = self.sk.recv(95536)  
                    #     #print("BUFFFFF                           -->",len(buff1))
                    #     if self.buff1 == b'' :
                    #         self.buff = None
                    #         return buff 
                    # except Exception :
                    #     print("Camepra.py - EXCEPTION : Server Close")

                    #     self.buff1 = b'' 
                    #     self.sk = None
                    #     self.fReady = False

                    # if self.buff1[:2] == b'\xff\xd8' :
                    #     self.buff =self.buff1  
                    # else:
                    #     print("LENGTH ERROR     ") #          ",len(buff1))
                    #     print("VALUE  ERROR     ") #          ",buff1[:2])
                    #     self.buff = None
                    #     pass  
                    # self.read_lock.release()            # v_loc_test 


                self.isPrevCtrl = False

                #print("rev len() ", len(buff))
                #print("is control ", str(self.isCtrl))
                #print("---")

                self.fReady = True
                #print(type(self.buff))
                return self.buff
        except Exception as identifier:
            print("camera.py - EXCEPTION (CATCHED)", str(identifier))
            self.sk = None
            self.fReady = False

            pass
        
        return None  #d_vu - return - 20191021
    
    isCtrl = False    
    imgCtrl = None

    isPrevCtrl = False
    
    cntLowFps = 0
    #buffer_depth_jpeg = None #d_vu - add - 20191015
    #buffer_ir_jpeg = None #d_vu - add - 20191015 - night

    def update(self):
        min_ms_between_read = self.getMinBetweenRead()        
        while True:            
            time_start = time.perf_counter()
            if self.fReady == False:
                print('camera.py - update loop() - CAMERA NOT READY')
                
                time.sleep(0.5)

            if self.isCtrl:
                print('camera.py - update loop() - IN CONTROL MODE...')

                if self.imgCtrl == None:
                    try:
                        self.imgCtrl = open('static/inctrl.jpg', 'rb').read()
                        pass
                    except Exception as identifier:
                        print("camera.py - update loop() - EXCEPTION MSG: ", str(identifier))
                        pass

                time.sleep(0.1)
                continue
                        
            self.buffer_jpeg = self.read_jpeg()            
            
            time_end = time.perf_counter()
            diff = time_end - time_start
            if diff < min_ms_between_read:
                time_sleep = min_ms_between_read - diff

                #print("camera.py - update(): sleep a bit ", str(time_sleep))
                time.sleep(time_sleep)

    #d_vu - add - an optimized version for the camera read() returning cached image encoded in jpeg - 20190906    
    webp_count = 0
    webp_size = 0
    avg_webp = 0
    jpeg_count = 0
    jpeg_size = 0
    avg_jpeg = 0
    avg_rate_wsbp_per_jpeg = 0
    
    sl = 0
    sc = 0
    fReady = False
    def isReady(self):
        #print("is prev ctrl ", str(self.isPrevCtrl))
        if self.isPrevCtrl:
            return False

        return self.fReady
        #return True
    
    sk = None    
    def nextImage(self):
        #d_vu - add - 20191015
        # if self.buffer_jpeg == None:
        #     print('camera.py: Data buffer_jpeg none')
        time.sleep(0.003)
        return self.buffer_jpeg

        '''if self.buffer_depth_jpeg != None:
            return self.buffer_depth_jpeg
            
        
        if self.buffer_ir_jpeg != None:
            return self.buffer_ir_jpeg
        '''

        if self.isReady == False:
            print("return none ready000000000")

            return None
        
        #d_vu - disable - 20191015, night
        '''        
        if self.frame is None:
            # print("return none frame!!!!!!!!!!")
            return None
        
        if self.buffer_ir_jpeg != None:
            print("return data2222222222222")
            #self.read_lock.release() #unlock lock obj
            return self.buffer_ir_jpeg
        '''

        # d_vu - disable frame.copy(): no need to clone this frame object - 20190912
        # => disable copy() to reduce execution time and memory a bit
        #t1 = time.perf_counter()
        #frame = self.frame.copy()
        #t2 = time.perf_counter()
        #tdiff = t2 - t1
        #print("time diff ", tdiff)        #0.0001-0.0005 seconds (~ nano-seconds)

        #self.read_lock2.acquire()

        '''
        frame = self.frame
        frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        brightness_level = 1
        if self.mode == ToFMode.DEPTH:
            #d_vu - TODO: need review - bad code, temporary code: switch blevel to 21 if tof-cam detected - 20190916
            if self.tofCount != 0:
                brightness_level = 21
                                
            frameGrayBrighness = cv2.addWeighted(frameGray, brightness_level, np.zeros(frameGray.shape, frameGray.dtype),0, 0)
            framePColor = cv2.applyColorMap(frameGrayBrighness, self.codeColorMap)

            _frameDEPTHJPeg20 = None
            if self.IM_QUALITY== ToFImageRendering.WEBP:
                _frameDEPTHJPeg20 = cv2.imencode(".webp", framePColor,[cv2.IMWRITE_WEBP_QUALITY, 60])[1]
            else:
                _frameDEPTHJPeg20 = cv2.imencode(".jpg", framePColor,[cv2.IMWRITE_JPEG_QUALITY, 20])[1]
                        
            self.data = _frameDEPTHJPeg20.tobytes()
        else:
            frame = self.frame
            frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            #d_vu - TODO: need review - bad code, temporary code: switch blevel to 21 if tof-cam detected - 20190916
            if self.tofCount != 0:
                brightness_level = 19
            
            frameGrayBrighness = cv2.addWeighted(frameGray, brightness_level, np.zeros(frameGray.shape, frameGray.dtype),0, 0)

            _frameIRGrayJPG20 = None
            if self.IM_QUALITY== ToFImageRendering.WEBP:
                _frameIRGrayJPG20 = cv2.imencode('.webp', frameGrayBrighness, [cv2.IMWRITE_WEBP_QUALITY, 60])[1]
            else:
                _frameIRGrayJPG20 = cv2.imencode('.jpg', frameGrayBrighness, [cv2.IMWRITE_JPEG_QUALITY, 20])[1]

            self.buffer_ir_jpeg = _frameIRGrayJPG20.tobytes()
        '''

        _len = 0
        if self.buffer_ir_jpeg != None:
            _len = len(self.buffer_ir_jpeg)
        
        if self.buffer_depth_jpeg != None:
            _len = len(self.buffer_depth_jpeg)
                    
        if self.IM_QUALITY== ToFImageRendering.WEBP:
            if self.webp_count < 1000000:
                self.webp_size = self.webp_size + _len
                self.webp_count = self.webp_count + 1
                self.avg_webp = 1.0 * self.webp_size / self.webp_count
        elif self.IM_QUALITY== ToFImageRendering.JPEG:
            if self.jpeg_count < 1000000:
                self.jpeg_size = self.jpeg_size + _len
                self.jpeg_count = self.jpeg_count + 1                
                self.avg_jpeg = 1.0 * self.jpeg_size / self.jpeg_count
        
        # update rate
        if self.avg_jpeg != 0:
            self.avg_rate_wsbp_per_jpeg = self.avg_webp / self.avg_jpeg
            print("camera.py - [INFO] average rate size webp/jpeg ", self.avg_rate_wsbp_per_jpeg)
                
        #self.read_lock2.release()

        print("return 3")
        return self.buffer_ir_jpeg
    
    #d_vu - add - 20190924
    # if not in DEPTH mode, return None
    # else return 
    def nextDepthFrame(self):        
        if self.mode != ToFMode.DEPTH:
            return None
        
        return self.frame
    
    def stop(self):        
        self.started = False
        self.thread.join()

    def release(self):
        #d_vu - disable - 2191015, night
        #self.stream.release()
        
        self.started = False

        __instance = None
        self.thread.join()
        
    #trying = False
    prevTry = -1
    def tryNextDevice(self):

        #d_vu - skip if retry too fast - 20190923    
        if self.prevTry == -1:
            self.prevTry = time.perf_counter()
        else:
            now = time.perf_counter()
            diff = now - self.prevTry            
            if diff < 1:
                return
            
            self.prevTry = now

        #if self.trying:
        #    return
                
        #trying = True

        self.src = self.src + 1
        if self.src > self.CONST_MAX_DEVICE:
            self.src = 0
        
        ####################
        self.webp_count = 0
        self.webp_size = 0
        self.avg_webp = 0
        self.jpeg_count = 0
        self.jpeg_size = 0
        self.avg_jpeg = 0
        self.avg_rate_wsbp_per_jpeg = 0
        
        #self.read_lock.acquire()
        #self.frame = None
        #self.read_lock.release()
        
        
        #if self.started:
        #    try:
        #        self.stop()
        #    except Exception as identifier:
        #        pass

        try:
            self.__init__() # re-init device
        except Exception as identifier:
            pass

        if self.started==False:
            self.start()
        
        #trying = False
    
    def capid(self):
        return self.src
    
    heatcache = None
    #d_vu - add - 20190907
    #cap, capid, K_Mo, K_L_D1, K_L_D2, K_L_D3, K_L_D4, K_PULSE, K_GAIN, K_RANGE, K_NR_FI, K_Threthold)
    def applyToFParam(self, capid, K_Mo, K_L_D1, K_L_D2, K_L_D3, K_L_D4, K_PULSE, K_GAIN, K_RANGE, K_NR_FI, K_Threthold, color, fromHome):
        print("camera.py - applyToFParam...")

        #apply in control thread
        #self.threadCtr = Thread(target=self.ctrl, args=(capid, K_Mo, K_L_D1, K_L_D2, K_L_D3, K_L_D4, K_PULSE, K_GAIN, K_RANGE, K_NR_FI, K_Threthold, color))
        #self.threadCtr.start()
        
        if fromHome == False:
            self.ctrl(capid, K_Mo, K_L_D1, K_L_D2, K_L_D3, K_L_D4, K_PULSE, K_GAIN, K_RANGE, K_NR_FI, K_Threthold, color)
    
    # d_vu - add - 20190912
    platform = None
    def _myPlatform(self):
        if self.platform != None:
            return self.platform

        splatform = platform.system()
        if splatform == "Linux":
            self.platform = ToFPlatform.Linux
        elif splatform == "Windows":
            self.platform = ToFPlatform.Windows
        else:
            self.platform = ToFPlatform.OTHER

        return self.platform
    
    #d_vu - add - 20191017
    def _sendCommand(self, bt):
        if self.sk2 == None:
            try:                
                self.sk2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sk2.connect((self.HOST, self.PORT))
            except Exception as identifier:                
                print('camera.py - _sendCommand EXCEPTION - ', str(identifier))
                self.sk2 = None

                return False
        
        try:
            print("\tpause1|", str(bt))
            self.sk2.sendall(bt)
            
            print("\tpause2|", str(bt))
            buff = self.sk2.recv(100000000) #100000000
            print("\tpause3")
            len_buff = len(buff)
            print("\tpause4")
            print("response length = ", len_buff)

            return True

            #if len_buff == 5:
            #    print("\tpause4-1")
            #    return True            
            print("\tpause4-2")
        except Exception as identifier:
            print('camera.py - EXCEPTION - ', str(identifier))
            self.sk2 = None

            return False
        
        print("\tpause4-2")

        return False

    #d_vu - add - 20190911
    CMD_PAUSE = b'8'
    CMD_RESUME = b'7'
    def ctrl(self, capid, K_Mo, K_L_D1, K_L_D2, K_L_D3, K_L_D4, K_PULSE, K_GAIN, K_RANGE, K_NR_FI, K_Threthold, color):        
        print("in camera.py - controling...")

        self.isCtrl = True
        self.buffer_jpeg = None        

        #d_vu - add: pause streaming - 20191017        
        print("\tpause streaming...")

        #name = input("press and enter 1")
        self._sendCommand(self.CMD_PAUSE)
        #name = input("press and enter 2")
        print("\tapply new params...")

        #time.sleep(0.1)
        try:
            capid = self.capid()
            #splatform = platform.system()
            if self._myPlatform() == ToFPlatform.Linux:
                print("app.py - MSG: Linux detected...")
                
                # prepare command-line and control argurments
                bcmd='LD_LIBRARY_PATH=/home/root/btof/lib /home/root/btof/btof_ss/build/btof_ctrl /dev/video%s %s %s %s %s %s %s %s %s %s %s'%(capid, K_Mo,K_L_D1,K_L_D2,K_L_D3,K_L_D4,K_PULSE,K_GAIN,K_RANGE,K_NR_FI,K_Threthold)

                # execute controller
                os.system(bcmd)
            elif self._myPlatform() == ToFPlatform.Windows:
                print("app.py - MSG: Windows detected...")

                #d_vu - add: check result.txt must exist for each call to 'Windows version of ToF controller' - 20191022, 8:56PM VNT
                # this is to fix bug: sometime the controller crash without any noticeable reason 
                # if the controller not crash, it will create result.txt even when it can not access ToF camera 
                retry = 0
                while True:
                    # prepare command-line and control argurments
                    pathPy = self._getCurrentPyPath()
                    #pathToFCtrl = pathPy + '\\tofctrl\\btof_ctrl.exe %s %s %s %s %s %s %s %s %s %s %s'%(capid, K_Mo,K_L_D1,K_L_D2,K_L_D3,K_L_D4,K_PULSE,K_GAIN,K_RANGE,K_NR_FI,K_Threthold)
                    pathToFCtrl = pathPy + self.TOF_CTRL_PARAMS_WIN
                    print("camera.py - ctrl")
                    print("\t", pathToFCtrl)

                    try:
                        # execute controller and wait until it will finished
                        cline = pathToFCtrl                
                        p = subprocess.Popen([cline,
                                                    str(capid),             #1 - in Windows version, this capid is ignored
                                                    str(K_Mo),              #2
                                                    str(K_L_D1),            #3
                                                    str(K_L_D2),            #4
                                                    str(K_L_D3),            #5
                                                    str(K_L_D4),            #6
                                                    str(K_PULSE),           #7
                                                    str(K_GAIN),            #8
                                                    str(K_RANGE),           #9
                                                    str(K_NR_FI),           #10
                                                    str(K_Threthold)])      #11
                        p.wait()                
                    except Exception as exi:
                        print("camera.py - EXCEPTION:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ", str(exi))

                        pass

                    # d_vu - add: check result.txt must exist for each call to 'Windows version of ToF controller' - 20191022, 8:56PM VNT
                    # this is to fix bug: sometime the controller crash without any noticeable reason 
                    # if the controller not crash, it will create result.txt even when it can not access ToF camera    
                    # d_vu - code20191129temp: disable for test FAKE_TOF, turn it on for real device
                    '''
                    if os.path.exists('result.txt') == False:
                        retry = retry + 1
                        print("camera.py - result.txt not created yet, the ctrl may be crashed - Retry ", str(retry))                        
                        time.sleep(0.1)

                        continue
                    '''
                    break
            else:
                print("app.py - MSG: Unsupported platform ", self.myPlatform())
                pass
        except Exception as identifier:
            print('camera.py - EXCEPTION MSG ', str(identifier))
            pass

        #d_vu - add: pause streaming - 20191017        
        print("\tresume streaming...")
        #name = input("press and enter 3")
        self._sendCommand(self.CMD_RESUME)
        #name = input("press and enter 4")

        self.isCtrl = False
        self.isPrevCtrl = True
        #time.sleep(0.1)

        print("\tDONE")
    

    def _getCurrentPyPath(self):
        modpath = os.path.dirname(os.path.abspath(__file__)) # /a/b/c/d/e

        return modpath

    def __exit__(self, exc_type, exc_value, traceback):
        #d_vu - disable - 2191015, night
        #self.stream.release()
        return
    
    #d_vu - add - 20190913
    def _parseTemp(self, temp):
        tokens = ["NONE", "NONE"]

        try:
            num = re.findall(r'\d+\.\d+', temp) #use regex to extract all number from string
            tokens[0] = str(num[0])
            tokens[1] = str(num[1])

            print("app.py - parsed temp1: ", tokens[0])
            print("app.py - parsed temp2: ", tokens[1])
        except Exception as ep:
            print("app.py - _parseTemp EXCEPTION ", str(ep))

            pass
        return tokens
    
    prevTemp = None
    time_lastTemp = 0
    # d_vu - add - 20190913
    def getTemperature(self):
        #d_vu - disable getTemperature temporary - 20191022
        # getTemperature() affect page load => make it slow
        # getTemperature() affect depth server => conflict ToF handler (RED frame on DEPTH RAINBOW, BLACK frame on IR)
        if True:
            return

        lines = ["NONE", "NONE", "NONE"]
        lines[0] = "LT: ERR*C / IM: ERR*C"
        lines[1] = "ERR"
        lines[2] = "ERR"
        
        #d_vu - no need to re-query temp. too frequent - 20190913
        diff = time.perf_counter() - self.time_lastTemp
        if diff < 5:
            if self.prevTemp != None:
                print("app.py - getTemperature: return prevTemp (no need to re-query too frequent)")
                lines[0] = self.prevTemp

                temp = self._parseTemp(lines[0])
                lines[1] = temp[0]
                lines[2] = temp[1]

                return lines
        
        self.isCtrl = True
        time.sleep(0.2)
        capid = self.capid()

        if self._myPlatform() == ToFPlatform.Linux:
            print("app.py - getTemperature MSG: Linux detected...")

            #TODO - cần viết hàm gọi module lấy nhiệt/Linux và lưu vào lines[0]
            lines[0] = "LT: 90.000*C / IM: 300.9521*C"

            '''
            # prepare command-line and control argurments
            bcmd='LD_LIBRARY_PATH=/home/root/btof/lib /home/root/btof/btof_ss/build/btof_ctrl /dev/video%s %s %s %s %s %s %s %s %s %s %s'%(capid, K_Mo,K_L_D1,K_L_D2,K_L_D3,K_L_D4,K_PULSE,K_GAIN,K_RANGE,K_NR_FI,K_Threthold)
            # execute controller
            os.system(bcmd)
            '''

            #TODO - d_vu - add: assign prevTemp - 20190913
            self.time_lastTemp = time.perf_counter()
        elif self._myPlatform() == ToFPlatform.Windows:
            print("app.py - getTemperature MSG: Windows detected...")

            # prepare command-line and control argurments
            pathPy = self._getCurrentPyPath()
            pathToFCtrl = pathPy + self.TOF_CTRL_TEMP_WIN
            print("camera.py - getTemperature")
            print("\t", pathToFCtrl)
            
            try:
                p = subprocess.Popen(pathToFCtrl, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)                
                stdout_text, stderr_text = p.communicate()

                #print("STDOUT TEXT>>>>", stdout_text)

                # parsing
                tk = stdout_text.splitlines()
                for i in range (len(tk)):
                    txt = tk[i]

                    if txt.find('LT') >= 0:
                        if txt == "LT:-1":
                            lines[0] = "not available -1"
                        elif txt == "LT:-9":
                            lines[0] = "not available -2"
                        elif txt =="LT:-3":
                            lines[0] = "not available -3"
                        else:
                            lines[0] = tk[i]

                        self.prevTemp = lines[0]

                        break
            except Exception as exi:
                lines[0] = "try again"
                print("camera.py - EXCEPTION, getTemperature: ", str(exi))

                pass
            self.time_lastTemp = time.perf_counter()
        else:
            print("app.py - MSG: Unsupported platform ", self.myPlatform())
        
        temp = self._parseTemp(lines[0])
        lines[1] = temp[0]
        lines[2] = temp[1]

        self.isCtrl = False
        return lines
    
    #d_vu - add - 20190916
    tofCount = 1
    prevTofCount = -1
    def tofEnum(self):        
        tofCount = 1
        
        if True:
            return
        
        #d_vu - temporary ignore the bellow - 20191022
        print("app.py - detec tof-plugged after each interval")
        if self._myPlatform() == ToFPlatform.Windows:
            pathPy = self._getCurrentPyPath()
            pathToFCtrl = pathPy + self.TOF_CTRL_ENUM_WIN        

            try:
                p = subprocess.Popen(pathToFCtrl, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                stdout_text, stderr_text = p.communicate()

                try:
                    self.tofCount = int(stdout_text, 10)
                    if self.prevTofCount != self.tofCount:
                        print("camera.py - tofenum(), number-of-tof ", self.tofCount)
                    
                    self.prevTofCount = self.tofCount
                except ValueError as eve:
                    print("app.py - Exception ValueError ", str(eve))
            except Exception as epenum:
                print("app.py - tofenum EXCEPTION ", str(epenum))
            
            time.sleep(1)
        elif self._myPlatform() == ToFPlatform.Linux:
            while self.started: #d_vu - TODO: synclinux - implement tofEnumLinux - 201916
                self.tofCount = 1
                pass
                time.sleep(1)
        else:
            while self.started: #d_vu - TODO: syncother - implement tofEnumLinux - 201916
                self.tofCount = 1
                pass
                time.sleep(1)

        return
    
    '''
    d_vu - network bandwidth monitoring related's stuff - 20190918
    '''
    jpeg_size = 0
    jpeg_count = 0

    webp_size = 0
    webp_count = 0

    avg_webp = 0
    avg_jpeg = 0
    avg_rate_wsbp_per_jpeg = 0
    
    hwUsage_inteval = 1
    def hwUsage(self):
        self.IM_QUALITY = ToFImageRendering.WEBP

        prev_data_size_sr = 0 #previous data size sent + received

        mbps_cnt_jpeg = 0
        mbps_cnt_webp = 0
        mbps_cnt_retrybusylevel_ = 3
        mbps_busy_threshold_pc = 80 #percent value

        cpu_cnt_retrybusylevel = 0
        cpu_retrybusylevel_max = 5
        cpu_busy_level = 90

        while True:
            if self.isReady:
                time.sleep(self.hwUsage_inteval)
                
                continue

            cpu_p = HardwareMonitoring.getInstance().cpu_p
            if cpu_p > cpu_busy_level:
                cpu_cnt_retrybusylevel = cpu_cnt_retrybusylevel + 1

                if cpu_cnt_retrybusylevel > cpu_retrybusylevel_max:
                    if self.IM_QUALITY != ToFImageRendering.JPEG:
                        print("camera.py - [INFO] - switching to JPEG to reduce cpu usage")                        
                        self.IM_QUALITY = ToFImageRendering.JPEG

                    cpu_cnt_retrybusylevel = 0
            else:
                cpu_cnt_retrybusylevel = cpu_cnt_retrybusylevel - 1
                if cpu_cnt_retrybusylevel < 0:
                    cpu_cnt_retrybusylevel = 0

                new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
                if prev_data_size_sr:
                    bw_mbps = HardwareMonitoring.getInstance().bw_mbps
                    bw_network_usage = HardwareMonitoring.getInstance().bw_network_usage                    

                    if bw_network_usage >= mbps_busy_threshold_pc:
                        mbps_cnt_jpeg = mbps_cnt_jpeg + 1
                        mbps_cnt_webp = mbps_cnt_webp - 1

                        if mbps_cnt_webp < 0:
                            mbps_cnt_webp = 0
                        
                        #d_vu - note: only switch mode if the mbps higher in multiple time
                        if mbps_cnt_jpeg > mbps_cnt_retrybusylevel_:
                            if self.IM_QUALITY != ToFImageRendering.JPEG: # to reduce the console print (less mess)
                                print("camera.py - [INFO] - switching to JPEG for better streaming fps...")
                                                    
                            self.IM_QUALITY = ToFImageRendering.JPEG
                            mbps_cnt_jpeg = 0
                            mbps_cnt_webp = 0
                    else:
                        mbps_cnt_jpeg = mbps_cnt_jpeg - 1
                        mbps_cnt_webp = mbps_cnt_webp + 1

                        if mbps_cnt_jpeg < 0:
                            mbps_cnt_jpeg = 0
                        
                        #d_vu - note: only switch mode if the mbps higher in multiple time
                        if mbps_cnt_webp > mbps_cnt_retrybusylevel_:
                            predict_mbps_after_switch_to_webp = self.avg_rate_wsbp_per_jpeg  * bw_network_usage
                            predict_mbps_after_switch_to_webp_usage = 100.0 * predict_mbps_after_switch_to_webp / HardwareMonitoring.getInstance().nic_min_mbps
                            
                            # d_vu - add - dont switch back to webp if predicted mbps value higher than expected - 20190918
                            if predict_mbps_after_switch_to_webp_usage >= mbps_busy_threshold_pc:
                                print("app.py - [INFO] kept JPEG (predicted webp mbps=%.2f)"% predict_mbps_after_switch_to_webp_usage)
                            elif self.IM_QUALITY != ToFImageRendering.WEBP:
                                print("camera.py - [INFO] - switching to WEBP for better display..")    
                            
                                self.IM_QUALITY = ToFImageRendering.WEBP
                                mbps_cnt_jpeg = 0
                                mbps_cnt_webp = 0
                prev_data_size_sr = new_value
            time.sleep(self.hwUsage_inteval)
        
        return

    def convert_to_mbit(self, value):
        return value/1024./1024.*8

    def convert_to_kbit(value):
        return value/1024.*8
    
    global codeColorMap_cmd
    codeColorMap_cmd = '1'# jpeg rainbow

    #d_vu - add - 20191015
    def apply_colormap_code(code):
        #print("apply code ")

        global codeColorMap_cmd
        
        if code == 0:
            #print("\tcode 0")

            codeColorMap_cmd = 2 #jpeg AUTUM
        elif code == 11:
            #print("\tcode 11")

            codeColorMap_cmd = 3 #jpeg HOT
        elif code == 7:
            #print("\tcode 7")

            codeColorMap_cmd = 4 #jpeg SPRING
        elif code == 9:
            #print("\tcode 9")
            
            codeColorMap_cmd = 9 #jpeg normal grayscale d_vu - add - 20191015
        else:
            #print("\tcode 1")

            codeColorMap_cmd = 1  #jpeg RAINBOW
    
    def start_record(self, mode, fps_number):
        print('Camera.py::: start_record')
        self.mode = mode       
        self.is_record = True   
        
        self.fps_number = fps_number
        if self.fps_number == "20":
            second = round((1/20), 9)
        else:
            second = round((1/30), 9)
        # print(self.fps_number)
        # print(type(self.fps_number))
        self.recordingThread = RecordingThread("Video Recording Thread", self.buff, second, self.mode, self.fps_number)
        self.recordingThread.start() 
        self.buff_ss = None

        while self.is_record:
            # a1 = time.perf_counter()
            #print(type(self.buffer_jpeg))
            self.recordingThread.lientuc(self.buffer_jpeg, self.vn)
            time.sleep(second)

            # if self.buff is None:
            #     self.recordingThread.lientuc(self.buff_ss, self.vn)
            # else:
            #     self.buff_ss = self.buff
            #     self.recordingThread.lientuc(self.buff, self.vn)
            # self.vn = None
            # a2 = time.perf_counter()
            # a3 = round((a2 - a1), 9)              
            # time.sleep(round((second - a3), 9))
            
      
    def check_ajax(self, vn):
        self.vn = vn

    def stop_record(self):
        try:
            print('Camera.py: stop_record')    
            self.is_record = False

            if self.recordingThread != None:
                self.recordingThread.stop()
        except Exception as et:
            pass

        # while True:
        #     print(type(self.buffer_jpeg))
        #     time.sleep(0.02)
  
class RecordingThread (threading.Thread):
    def __init__(self, name, camera, second, mode, fps_number):
        print('Camera.py::: __init - RecordingThread__')
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True
        self.cap = camera
        self.second = second  
        self.fps_number = fps_number
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.mode = mode
        print('Camera.py :::>>> ')
        print(self.mode)
        if self.mode: #Recorder with mode DEPTHIR
            if self.fps_number == "20":
                self.out = cv2.VideoWriter('video.avi',fourcc, 20, (1280,480))
            else:
                self.out = cv2.VideoWriter('video.avi',fourcc, 30, (1280,480))
        else:         #Recorder with mode DEPTH or IR
            if self.fps_number == "20":
                self.out = cv2.VideoWriter('video.avi',fourcc, 20, (640,480))
            else:
                self.out = cv2.VideoWriter('video.avi',fourcc, 30, (640,480))
        self.vn = None
        self.count = 0
        self.data = None
               
    def run(self):
        self.count = 0       
        image1 = cv2.imread('./static/image.jpg')
        time.sleep(0.5)
        while self.isRunning:
            try:
                start12 = time.perf_counter()
                if self.count >= 150:
                    print('Camera.py::: STOP')
                    self.isRunning = False
                    self.stop()                  
                    break
                
                try:                                                 
                    frame = self.cap  
                    #print(type(frame))         
                    if frame is None:
                        print('Thay the truong hop khong co du lieu NoneType')                       
                        image = np.asarray(bytearray(self.data), dtype="uint8")
                    else:                    
                        self.data = frame
                        image = np.asarray(bytearray(frame), dtype="uint8")                 
                    
                    image = cv2.imdecode(image, cv2.IMREAD_COLOR) # image is numpy.ndarray
                                      
                    # if self.mode: #Recorder with mode DEPTHIR    
                    #     #image1 = cv2.imread('./static/image.jpg')                    
                    #     im_v = cv2.hconcat([image1, image])
                    #     self.out.write(im_v)  
                    # else:         #Recorder with mode DEPTH or IR
                    #     self.out.write(image)     

                    self.out.write(image)     
                                                
                except Exception as et:        
                    print("Camera.py: Err Recorder ::: ====> )", str(et))
                    continue
                
                if self.vn:
                    self.count = 0
                else:
                    self.count = self.count + 1 

                try:
                    end12 = time.perf_counter()
                    time12 = round((end12 - start12), 9)   
                    #print(time12)
                    time123 = round((self.second - time12), 9)  
                    #print(time123)      
                    time.sleep(time123)                       
                    continue 
                except Exception as et2:                 
                    #print("Camera.py ::: ===> )", str(et2))
                    continue       
                      
            except Exception as et:
                self.count = 0
                continue

        self.out.release()

    def stop(self):
        print('Camera.py: Stop running')
        self.isRunning = False

    def lientuc(self, hang, vn):
        self.cap = hang   # kieu du lieu "byte"        
        self.vn = vn
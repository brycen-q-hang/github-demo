import os, sys, string, random
from flask import Flask, redirect, render_template, request, session, abort, Response, url_for, send_file, redirect, url_for, jsonify, json, send_file
import cv2
import numpy as np
import time
from pathlib import Path
from waitress import serve
import socket
from threading import Thread, Lock
import os.path
from os import path
from camera import CameraStream

from ToFMode import ToFMode
from ToFImageRendering import ToFImageRendering

from hwmonitoring import HardwareMonitoring

import threading
from threading import Thread

app = Flask(__name__)

color = ""
K_Mode=''
user_name = None
iStart = True
flgConsolePreparetoRun = False
colorParam = 4  
dictUser = {'User1': '', 'User2': 'pass2', 'User3': 'pass3'}

def WritePid():
    pid = str(os.getpid())
    print(pid)
    pidfile = "/home/root/btof/btof_ss/build/app.pid"
    open(pidfile,'w+').write(pid)

    return 1

#d_vu - disable: temporary disable watchdog
#WritePid()

@app.route('/')
def home():
    if not session.get('logged_in'):
        allow_login = allowNewLogin()
        if allow_login:
            return render_template('login.html')
        else:
            return render_template('busy.html')
    
    #username = request.form['username']
    my_file = Path('param.txt')
    if my_file.is_file():
        try:
            f = open("param.txt", "r+")
            lst_content = f.readlines()
            fileLenght = len(lst_content)        
            f.close()
        except Exception as e:
            print("app.py param.txt exceltion %s", str(e))
        finally:
            try:
                f.close()
            except Exception as e2:
                print("app.py param.txt unable to close param.txt, exception %s", str(e))

        if fileLenght >= 11:
            global K_Mode
            global color            
            K_Mode = lst_content[0]          
            K_Mode = K_Mode.strip() 
            K_LD1 = lst_content[1]
            K_LD1 = K_LD1.strip()
            K_LD2 = lst_content[2]
            K_LD2 = K_LD2.strip()
            K_LD3 = lst_content[3]
            K_LD3 = K_LD3.strip()
            K_LD4 = lst_content[4]
            K_LD4 = K_LD4.strip()
            K_PULSE = lst_content[5]
            K_PULSE = K_PULSE.strip()
            K_NRFI = lst_content[6]
            K_NRFI = K_NRFI.strip()
            K_GAIN = lst_content[7]
            K_GAIN = K_GAIN.strip()
            K_FAR_NEAR = lst_content[8]
            K_FAR_NEAR = K_FAR_NEAR.strip()
            K_Threthold = lst_content[9]
            K_Threthold = K_Threthold.strip()
            color = lst_content[10]
            color = color.strip()            
        else:
            K_Mode, K_LD1, K_LD2, K_LD3, K_LD4, K_PULSE, K_NRFI, K_GAIN, K_FAR_NEAR, K_Threthold, color = "IR", "checked", "checked", "checked", "checked", "2000", "off", "800", "300mm-1000mm", "10", "RAINBOW"       
    else:
        K_Mode, K_LD1, K_LD2, K_LD3, K_LD4, K_PULSE, K_NRFI, K_GAIN, K_FAR_NEAR, K_Threthold, color = "IR", "checked", "checked", "checked", "checked", "2000", "off", "800", "300mm-1000mm", "10", "RAINBOW"

    step = '10'
    print("home")
    fromHome = True
    return param_result(K_PULSE,K_Threthold,K_GAIN,K_NRFI,K_LD1,K_LD2,K_LD3,K_LD4,K_FAR_NEAR,K_Mode,color,step, fromHome)
    # return param_result(K_PULSE,K_Threthold,K_GAIN,K_NRFI,K_LD1,K_LD2,K_LD3,K_LD4,K_FAR_NEAR,K_Mode,username,color,step, fromHome)
   
#Create login page
@app.route('/streaming', methods=['POST'])
def do_admin_login():
    global username
    username = request.form['username']
    userpass = request.form['password']
    global lang
    lang = request.form.get('lang')
    for key in dictUser:       
        if username == key  and  userpass == dictUser[key]:            
            session['logged_in'] = True
            #return render_template('test.html')
            return home()
    message = ' '
    return render_template('login.html', message = message, lang = lang, username = username ) 

@app.route('/streaming')
def login():
    print("login")
    global flg_unity_control
    flg_unity_control = False
    return redirect(url_for('home'))

@app.route('/streaming/')
def login1():
    print("login1")
    return redirect(url_for('home'))

@app.route('/logout', methods=['POST'])
def logout(): 
    print("logout")
    lang = request.form.get('language')    
    session.pop('logged_in', None)    
    #--- Check again ---
    return render_template('login.html', lang = lang)

cap = None
capid = 0 #d_vu - add - 20190906

#d_vu - add - check if 3d mode is supported (3d depth server running or not) - 20190724
def _bvnIs3dModeSupported():
    sCmd = '4' #~52 in ASCII
    flg = _bvnClientForDepthServer(sCmd)

    return flg

global flgStartDownload
flgStartDownload = False

#t_lanh - add - sent depth file to client - 20190723
@app.route('/download')
def download():
    global flgStartDownload
    flgStartDownload = True

    try:
        cap.release()
    except Exception as e4:
        #print("From_app_py_i2 just want to release you CAMERA")
        print("app.py - Unable to release camera (2), exception e = ", str(e4))

    #xóa file cũ
    sPath = "/home/root/btof/btof_ss/build/depth.bin"
    isFileExist = path.exists(sPath)
    if isFileExist:
        os.remove(sPath)

    #time.sleep(1)
    #sinh file mới
    try:
        if K_Mode_B:
            os.system("/home/root/btof/btof_dd/build/btof_depthdump current_depth")#CURRENT = DEPTH
        else:
            os.system("/home/root/btof/btof_dd/build/btof_depthdump current_ir")#CURRENT = IR
    except:
        print("app.py - ERROR when execute DEPTH srv")

    #đổi chế độ
    #global flgStartDownload # d_vu - disable this line: ignore WARNING/Syntax Error - 20190905
    flgStartDownload = False

    #kiểm tra file tồn tại
    isFileExist = path.exists(sPath)
    if not isFileExist:
        return Response('file_not_exist',status=200, mimetype='text/html')
    
    fileSize = os.path.getsize(sPath)
        
    if not fileSize == 614400:# kiểm tra size file depth.bin (2*480*640)
        return Response('file_size_incorrect', status=200, mimetype='text/html')

    return send_file(sPath, as_attachment=True)

#d_vu - add - thiếu
global K_Mode_B
K_Mode_B = False

##########################################################################
global imgdis
imgdis = None

global img3d
img3d = None

global tunningms
tunningms = 0

global flgIsFirst
flgIsFirst = True

global imgpause
imgpause = None

global imgready
imgready = None

global imgloading
imgloading = None

fps = 0

data = None
img_ir_main = None

def gen():
    global tunningms
    tunningms = 0
    
    global flgIsFirst
    flgIsFirst = True
    
    #print("gen")

    time_fps_start = time.perf_counter()
    n_NumberOfFrame = 0
    time_fps_diff = 0
    flg = 0    
    prevfps = 10000000
    
    #20200305 
    # if K_Mode_B:      
    #     CameraStream.apply_colormap_code(colorParam)
    # else:
    #     CameraStream.apply_colormap_code(9)      

    #d_vu - init camera instance - 20190905
    global cap
    cap = CameraStream.getInstance()
    cap.start()
    global fps
    fps = 0
    capid = cap.capid()#d_vu - current video device id - 20190905

    prevReadTime = time.perf_counter()
    flgError = False
    prevError = not flgError
    ifirst = True

    prevErrTime = time.perf_counter()
    flgSentMsg = False    
    cnt = 0
    
    abc = 0
    while True:
        flgReady = cap.isReady()
        cnt = cnt + 1
        
        if flgReady == False:
            global imgready
            if imgready == None:
                imgready = open('static/ready.jpg', 'rb').read()            
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgready + b'\r\n')
            flgSentMsg  = True
        elif flgError == True: #d_vu - flgError == True always cause by image processing error in cap.nextImage() - 20190920            
            #print("error")

            global imgpause
            if imgpause == None:
                imgpause = open('static/pause.jpg', 'rb').read()            
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgpause + b'\r\n')
            flgSentMsg  = True
        
        if flgReady == False or flgError == True:
            if cap != None:
                time_sleep = cap.getMinBetweenRead()
            else:
                time_sleep = 0.2#default value

            #print("time sleep ", time_sleep)
            time.sleep(time_sleep)

            diff = time.perf_counter() - prevErrTime
            if diff > 1:
                if flgReady == False:
                    print("app.py - [MSG] camera not ready")
                
                if flgError == True:
                    print("app.py - [MSG] pause streaming")
                
                prevErrTime = time.perf_counter()
        
        if flgReady == False:#d_vu - wait until camera ready - 20191016 (disable)
            continue
        
        # d_vu - update camera.py mode - 20190906
        if K_Mode_B:
            CameraStream.mode = ToFMode.DEPTH
            # CameraStream.codeColorMap = colorParam
            CameraStream.apply_colormap_code(colorParam)
        else:
            CameraStream.apply_colormap_code(9)
            CameraStream.mode = ToFMode.IR
                
        global data
        data = cap.nextImage() #d_vu - comment: the implementation of nextImage() must be exception-free - 20190920        

        global img_ir_main, bbb        
        if data == None:
            flgError = True                           
            ready = open('static/ready.jpg', 'rb').read()                               
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + ready + b'\r\n')
        elif status_submit == True:
            ready = open('static/ready.jpg', 'rb').read()                               
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + ready + b'\r\n')
            continue 
        else:                                 
            try:    
                image = np.asarray(bytearray(data), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR) 
                bbb = image.shape                
            except Exception as err1:
                #print('app.py :::--> (Get size image bbb)', str(err1))    
                continue
            
            if K_Mode == "DEPTHIR" and bbb[1] == 1280:
                try:                        
                    img_ir = image[0:480, 640:1280]; #[cao, rộng]
                    img_ir_main = cv2.imencode('a.jpg', img_ir)[1].tobytes()
                    
                    img_depth = image[0:480, 0:640]; #[cao, rộng]
                    img_depth_main = cv2.imencode('b.jpg', img_depth)[1].tobytes()
                   
                except Exception as err:                            
                    print('app.py :::--> (cat anh)', str(err))                    
                    continue

                flgError = False
                
                if flg_unity_control == False:                    
                    yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + img_depth_main + b'\r\n')
                else:
                    ready = open('static/ready.jpg', 'rb').read()                               
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + ready + b'\r\n')
                
            else:
                img_ir_main = None
                flgError = False           

                if flg_unity_control == False:                    
                    yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + data + b'\r\n')
                else:                    
                    ready = open('static/ready.jpg', 'rb').read()            
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + ready + b'\r\n')
            
        # d_vu - add - tunning streaming-fps:
        #   => (1) to reduce cpu usage
        #   => (2) to reduce network bandwidth - 20190907
        time_now = time.perf_counter()
        time_diff = time_now - prevReadTime
        min_ms_between_read = cap.getMinBetweenRead()
        if time_diff < min_ms_between_read:
            #print(fps)
            # d_vu - add - tunning sleeping time automatically - 20190917            
            if fps > cap.limitfps:
                tunningms = tunningms + 0.001
            elif fps < cap.limitfps:
                tunningms = tunningms - 0.001
            else:
                tunningms = 0
                        
            time_to_sleep = min_ms_between_read - time_diff
            time_to_sleep = time_to_sleep + tunningms

            if time_to_sleep < 0:
                time_to_sleep = 0
            
            #print("sleep a bit %s", str(time_to_sleep))

            time.sleep(time_to_sleep)                            
        prevReadTime = time_now

        if data != None:#d_vu - add - 20191020
            n_NumberOfFrame = n_NumberOfFrame + 1 # count number of frame, for fps calculation

        time_fps_diff = time.perf_counter() - time_fps_start
        
        fps_check = n_NumberOfFrame / time_fps_diff

        #print('hw!!!!!!!!!!!!!!!!!!!!!!!!!')
        #print fps & other INFO
        if time_fps_diff >= 1:
            fps = fps_check
            prevfps = fps

            cpu_p = HardwareMonitoring.getInstance().cpu_p
            mbps = HardwareMonitoring.getInstance().bw_mbps
            mbps_pc = HardwareMonitoring.getInstance().bw_network_usage
            global mime
            mime = "jpeg"
            if cap.IM_QUALITY == ToFImageRendering.WEBP:
                mime = "webp"
            
            #print('app.py - [INFO] streaming [%s, %.2f fps], cpu: %.2f%%, nic [%.2f Mbps, %.2f%%]'% (mime, fps, cpu_p, mbps, mbps_pc))

            n_NumberOfFrame = 0
            time_fps_start = time.perf_counter()
        #print('hw!!!!!!!!!!!!!!!!!!!!!!!!!DONE')
        #d_vu - disable - break this loop will affect ajax - 20190913
        #if not iStart: 
        #    break


        #print('hw!!!!!!!!!!!!!!!!!!!!!!!!!DONE')
        #d_vu - disable - break this loop will affect ajax - 20190913
        #if not iStart: 
        #    break
    
    '''
    #d_vu - disable - no need to release - 20190907
    #the current cap.release() currently raise some unexpected bug
    try:
        cap.release()
    except Exception as e3:
        print("app.py - Unable to release camera (1), exception e = ", str(e3))    
    '''

#########################################################################
@app.route('/video_feed', methods=['GET'])
def video_feed():
    print("app.py - [MSG] start /video_feed")
    #d_vu - add - 20190905
    try:
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print("app.py video_feed - EXCEPTION ", str(e))
        return None

@app.route('/video_feed_3')
def video_feed_3():
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frame():   
    # print('app.py :::>>> video_feed_3 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')    
    ready = open('static/ready.jpg', 'rb').read()     
    unity = open('static/cam3d.jpg', 'rb').read()                              
    while True:
        try:
            if status_submit == True:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + ready + b'\r\n') 
                time.sleep(1/30)
                continue   
                                   
            if img_ir_main == None:                                                        
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + ready + b'\r\n')             
                time.sleep(1)
                #continue
            else:                                                   
                try:                                                  
                    if flg_unity_control == False:                
                        yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + img_ir_main + b'\r\n')
                    else:                                   
                        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + ready + b'\r\n')
                except Exception as tt:
                    print('app.py :::>>> ', str(tt))
                time.sleep(1/30)      

        except Exception as err:
            print('app.py :::>>> (source err img IR) ', str(err))
            continue

flg_unity_control = False
@app.route('/Unity_control', methods=['GET', 'POST', 'PUT', 'DELETE'])
def Unity_control():    
    print("App.py : Unity_control")   
    global flg_unity_control, status_submit
    try:
        if flg_unity_control == False and status_submit == False: 
            status_submit = True
            flg_unity_control = True

            data = request.get_data()
            data = data.decode('utf-8')     
            print(data) 
            print()     
            data = data.split('xxx')
       
            K_FAR_NEAR = data[0]
            K_LD1 = data[1]
            K_LD2 = data[2]
            K_LD3 = data[3]
            K_LD4 = data[4]
            K_NRFI = data[5]
            K_GAIN = data[6]
            K_PULSE = data[7]
            K_Threthold = data[8]
                
            f = open("param.txt", "r+")
            lines = f.readlines()
            K_Mode,color = lines[0],lines[10]
            K_Mode,color = K_Mode.strip(),color.strip()
            f.close()
        
            step = '15'
            fromHome = False           
            return param_result(K_PULSE,K_Threthold,K_GAIN,K_NRFI,K_LD1,K_LD2,K_LD3,K_LD4,K_FAR_NEAR,K_Mode,color,step, fromHome)
            # return param_result(K_PULSE,K_Threthold,K_GAIN,K_NRFI,K_LD1,K_LD2,K_LD3,K_LD4,K_FAR_NEAR,K_Mode,username,color,step, fromHome)
        else:
            print('App.py :::>>> System busy: Unity could not control param')
            return ('', 204)             

    except Exception as err:
        print('App.py:::>>> (Err) Unity Control', str(err))
        return jsonify(data={})      

@app.route('/send_unity', methods=['GET', 'POST', 'PUT', 'DELETE'])
def send_unity():  
    print("App.py : Response Control")
    try:
        if flg_unity_control == False and status_submit == False:

            f = open("param.txt", "r+")
            lines = f.readlines()
            K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = lines[0],lines[1],lines[2],lines[3],lines[4],lines[5],lines[6],lines[7],lines[8],lines[9],lines[10]
            K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = K_Mode.strip(),K_LD1.strip(),K_LD2.strip(),K_LD3.strip(),K_LD4.strip(),K_PULSE.strip(),K_NRFI.strip(),K_GAIN.strip(),K_FAR_NEAR.strip(),K_Threthold.strip(),color.strip()
            f.close()

            res = K_FAR_NEAR + "xxx" + K_LD1 + "xxx" + K_LD2 + "xxx" + K_LD3 + "xxx" + K_LD4 + "xxx" + K_NRFI + "xxx" + K_GAIN + "xxx" + K_PULSE + "xxx" + K_Threthold
            return res
        else:
            return ('', 204)
    except Exception as err:
        print('App.py:::>>> (Err) Response Control', str(err))
        return jsonify(data={})            

@app.route('/load_color', methods=['POST'])
def load_color():
    print("load_color")
    global flg_params, user_name
    flg_params = True
    color = request.form.get('color')
    user_name = request.form.get('user_name')
    
    global colorParam 
    if color=="AUTUMN":
        colorParam=0
    elif color=="HOT":
        colorParam=11
    elif color=="SPRING":
        colorParam=7
    else:
        colorParam=4    

    f = open("param.txt", "r+")
    lines = f.readlines()
    K_Mode = lines[0]
    K_Mode = K_Mode.strip()
    lines[10] = color + '\n'
    f.close()
    f = open("param.txt", "w+")
    f.writelines(lines)
    f.close()

    try:      
        f = open("param.txt", "r+")
        lines = f.readlines()
        K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = lines[0],lines[1],lines[2],lines[3],lines[4],lines[5],lines[6],lines[7],lines[8],lines[9],lines[10]
        K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = K_Mode.strip(),K_LD1.strip(),K_LD2.strip(),K_LD3.strip(),K_LD4.strip(),K_PULSE.strip(),K_NRFI.strip(),K_GAIN.strip(),K_FAR_NEAR.strip(),K_Threthold.strip(),color.strip()
        f.close()
    except Exception as et:
        print("app.py - /load_parameters() EXCEPTION  ", str(et))       
        pass
    
    load_colors = 'self'
    return jsonify(data={'load_colors':load_colors, 'color':color, 'K_Mode':K_Mode, 'K_LD1':K_LD1, 'K_LD2':K_LD2, 'K_LD3':K_LD3, 'K_LD4':K_LD4, 'K_PULSE':K_PULSE, 'K_NRFI':K_NRFI, 'K_GAIN':K_GAIN, 'K_FAR_NEAR':K_FAR_NEAR, 'K_Threthold':K_Threthold})

@app.route('/convert_mode', methods=['POST'])
def convert_mode():
    convert = request.form.get('convert')
    print(convert)
    if convert == "isdepthir":
        f = open("param.txt", "r+")
        lines = f.readlines()
        lines[0] = "DEPTHIR" + '\n'
        f.close()
    elif convert == "isdepth":
        f = open("param.txt", "r+")
        lines = f.readlines()
        lines[0] = "DEPTH" + '\n'
        f.close()
   
    f = open("param.txt", "w+")
    f.writelines(lines)
    f.close()  
    return jsonify(data={})

@app.route('/load_temp', methods=['POST'])
def load_temp():
    print("load-temp")
    #bcmd='LD_LIBRARY_PATH=/home/root/tedtof_ubuntu/lib /home/root/tedtof_ubuntu/TedTofOpenCV/build/TedTofConsole /dev/video%s' %(capid)
    #os.system(bcmd)
                
    global cap
    global capid    
    if cap is None:
        cap =  CameraStream.getInstance()
        capid = cap.capid()#d_vu - current video device id - 20190905
    
    lines = cap.getTemperature()

    LT='0'
    IM='0'
    temp = "Error querying camera"

    #d_vu - add try/exception - 20190913
    try:
        #parsing, processing...
        temp = lines[0]
        temp = temp.strip()
        temp = temp.replace("*","°")
        temp = temp.replace(" / ", "/") #d_vu - add - 20190913

        LT = lines[1]
        IM = lines[2]
        
        LT = LT.strip()            
        IM = IM.strip()
        pass
    except Exception as et:
        print("app.py - /load_temp() EXCEPTION  ", str(et))        
        pass
    print(temp)
    return jsonify(data={'temp':temp,'LT':LT, 'IM':IM,})
#------Load CPU 

mime = ''
bbb = None
@app.route('/upload_cpu', methods=['POST'])
def upload_cpu(): 
    #print(type(img_ir_main))
    cpu_p = HardwareMonitoring.getInstance().cpu_p
    mbps = HardwareMonitoring.getInstance().bw_mbps
    mbps_pc = HardwareMonitoring.getInstance().bw_network_usage
    
    return jsonify(data={'cpu_p':cpu_p,'fps':fps,'mbps':mbps,'mbps_pc':mbps_pc,'mime':mime, 'flg_params':flg_params, 'flg_record':flg_record, 'user_name':user_name, 'disable_download_app':disable_download_app, 'flg_check_status_reset':flg_check_status_reset, 'user_name_record':user_name_record, 'name_file_rc' : name_file_rc, 'check_user_name_record':check_user_name_record, 'bbb':bbb, 'flg_unity_control':flg_unity_control})

flg_params = False
#----- Load parameters 
@app.route('/flg_params_to_false', methods=['POST'])
def flg_params_to_false():
    global flg_params
    flg_params = False
    return jsonify(data={})

K_Mode = ''
@app.route('/load_params', methods=['POST'])
def load_params():
    update_control_panel = request.form.get('update_control_panel')
    # print('>>>>>>>>>>>>>')
    # print(update_control_panel)
    # print('<<<<<<<<<<<<<')
    try:      
        f = open("param.txt", "r+")
        lines = f.readlines()
        K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = lines[0],lines[1],lines[2],lines[3],lines[4],lines[5],lines[6],lines[7],lines[8],lines[9],lines[10]
        K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = K_Mode.strip(),K_LD1.strip(),K_LD2.strip(),K_LD3.strip(),K_LD4.strip(),K_PULSE.strip(),K_NRFI.strip(),K_GAIN.strip(),K_FAR_NEAR.strip(),K_Threthold.strip(),color.strip()
        f.close()
    except Exception as et:
        print("app.py - /load_parameters() EXCEPTION  ", str(et))       
        pass
    if update_control_panel != 'show_snap_view':
        global flg_params
        flg_params = False
    return jsonify(data={'K_Mode':K_Mode, 'K_LD1':K_LD1, 'K_LD2':K_LD2, 'K_LD3':K_LD3, 'K_LD4':K_LD4, 'K_PULSE':K_PULSE, 'K_NRFI':K_NRFI, 'K_GAIN':K_GAIN, 'K_FAR_NEAR':K_FAR_NEAR, 'K_Threthold':K_Threthold, 'color':color})

status_submit = False
letter = None
check_user_name_record = "DQH"
#----- Setup parameter   
@app.route('/ajax', methods=['POST'])
def setup():
    print("setup (ajax)")

    global K_Mode
    global color 
    global iStart
    iStart = False
    flgConsolePreparetoRun = True
    
    global status_submit
    print(status_submit)
    if status_submit:
        flg_thread_status_submit = 'self'
        return jsonify(data={'flg_thread_status_submit':flg_thread_status_submit,})
    status_submit = True

    #d_vu - considering disable - 20190907
    '''
    try:
        global cap
        cap.release()
    except Exception as e6:
        #print("From_app_py_i2 just want to release you CAMERA>>continue and retry")
        print("app.py - EXCEPTION - Unable to release camera (5) - ", str(e6))
    '''
    global user_name_record, name_file_rc, flg_record, check_user_name_record
    if flg_record:        
        check_user_name_record = user_name_record       
        flg_record = False 
        user_name_record = None
        letter = string.ascii_lowercase
        letter = ''.join(random.choice(letter) for i in range(11))
        name_file_rc ='TOF-' + letter 
       
        try:
            print('Xoa het file avi')
            filelist = [ f for f in os.listdir("./static/") if f.endswith(".avi") ]
            for f in filelist:
                os.remove(os.path.join("./static/", f))
        except Exception as et:
            print('err xoa file avi', str(et))
            pass
    else:
        name_file_rc = None

    K_Mode = request.form.get('K_Mode')
    K_LD1 = request.form.get('K_LD1')
    K_LD2 = request.form.get('K_LD2')
    K_LD3 = request.form.get('K_LD3')
    K_LD4 = request.form.get('K_LD4')
    K_PULSE = request.form.get('K_PULSE')  
    K_GAIN = request.form.get('K_GAIN')
    K_FAR_NEAR = request.form.get('K_FAR_NEAR') 
    K_NRFI = request.form.get('K_NRFI') 
    K_Threthold = request.form.get('K_Threthold')  
    color = request.form.get('color')
   
    global user_name, img_ir_main
    user_name = request.form.get('user_name')
    user_name = user_name.strip()
    if K_Mode != "DEPTHIR":
        img_ir_main = None

    print('-----------------------------------------')
    print(user_name)
    print('-----------------------------------------')
    
    step = '20'
    
    fromHome = False
    return param_result(K_PULSE,K_Threthold,K_GAIN,K_NRFI,K_LD1,K_LD2,K_LD3,K_LD4,K_FAR_NEAR,K_Mode,color,step, fromHome)
    # return param_result(K_PULSE,K_Threthold,K_GAIN,K_NRFI,K_LD1,K_LD2,K_LD3,K_LD4,K_FAR_NEAR,K_Mode,username,color,step, fromHome)

# def param_result(K_PULSE,K_Threthold,K_GAIN,K_NRFI,K_LD1,K_LD2,K_LD3,K_LD4,K_FAR_NEAR,K_Mode,username,color,step,fromhome):
def param_result(K_PULSE,K_Threthold,K_GAIN,K_NRFI,K_LD1,K_LD2,K_LD3,K_LD4,K_FAR_NEAR,K_Mode,color,step,fromhome):
    print("param_result")        
    
    global K_Mode_B
    if K_Mode == "IR":
        K_Mo = 1
        K_Mode_B = False    
    else: 
        K_Mo = 0
        K_Mode_B = True

    if K_LD1 == "checked" or K_LD1 == 'true': 
        K_LD1="checked"  
        K_L_D1 = 1
    else: 
        K_LD1 = "off"
        K_L_D1 = 0

    if K_LD2 == "checked" or K_LD2 == 'true':
        K_LD2="checked"     
        K_L_D2 = 2
    else: 
        K_LD2 = "off"
        K_L_D2 = 0

    if K_LD3 == "checked" or K_LD3 == 'true':
        K_LD3="checked"  
        K_L_D3 = 3 
    else:
        K_LD3 = "off"
        K_L_D3 = 0

    if K_LD4 == "checked" or K_LD4 == 'true':
        K_LD4="checked"
        K_L_D4 = 4
    else:
        K_LD4 = "off"
        K_L_D4 = 0
    
    #d_vu - bug => near = 0, far = 1 - 20191108
    #issue no.11, no.15/1
    #https://cb.brycen.co.jp/cgi-bin/cbag/ag.cgi?page=FileView&ffid=490129
    '''
    if K_FAR_NEAR == "300mm-1000mm":
        K_RANGE = 1           
    else:
        K_RANGE = 0
    '''
    if K_FAR_NEAR == "300mm-1000mm":
        K_RANGE = 0
    else:
        K_RANGE = 1

    if K_NRFI == "checked" or K_NRFI == 'true':
        K_NRFI="checked" 
        K_NR_FI = 1     
    else:
        K_NRFI = "off"
        K_NR_FI = 0

    if K_Mode == "IR":
        color = "RAINBOW"                
    elif color == None:     
        color = "RAINBOW"
        
    try:
        f = open("param.txt", "w")
        f.write(K_Mode)
        f.write('\n')
        f.write(K_LD1)
        f.write('\n')
        f.write(K_LD2)
        f.write('\n')
        f.write(K_LD3)
        f.write('\n')
        f.write(K_LD4)
        f.write('\n')
        f.write(K_PULSE)
        f.write('\n')
        f.write(K_NRFI)
        f.write('\n')
        f.write(K_GAIN)
        f.write('\n')
        f.write(K_FAR_NEAR)
        f.write('\n')
        f.write(K_Threthold)
        f.write('\n')                      
        f.write(color) 
        f.close()
    except Exception as ep:
        print("app.py param.txt exception %s", str(ep))

    global cap
    global capid
    if cap is None:
        #print("re-init cap!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        cap =  CameraStream.getInstance()
        capid = cap.capid()#d_vu - current video device id - 20190905
        #print("re-init cap!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!DONE")    
    #print("cap.applytofparam-before!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    cap.applyToFParam(capid, K_Mo, K_L_D1, K_L_D2, K_L_D3, K_L_D4, K_PULSE, K_GAIN, K_RANGE, K_NR_FI, K_Threthold, color, fromhome)
    #print("cap.applytofparam-after!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!DONE")
   
    LT = 0
    IM = 0
    temp = "operating"
    status = "..."
    resultList = []
    my_result = Path('result.txt')

    #d_vu - need review this codes - 20190913
    try:
        if my_result.is_file():
            fResult= open('result.txt','r')
            for line in fResult:
                resultList.append(line)
            fResult.close()   

            if len(resultList) >=2:
                temp = resultList[0]
                temp = temp.replace("*","°")
                status = resultList[1]
                status = status.strip()
    except Exception as ep0:
        print("app.py - EXCEPTION from READ FILE X ", str(ep0))
        pass

    try:
        os.remove("result.txt")
    except Exception as ep:
        print("app.py - param_result EXCEPTION (khong sao)", str(ep))
        pass

    global colorParam
    if color=="AUTUMN":
        colorParam=0
    elif color=="HOT":
        colorParam=11
    elif color=="SPRING":
        colorParam=7
    else: 
        colorParam=4
    
    global iStart, status_submit, flg_unity_control
    iStart = True 
    flgConsolePreparetoRun = False
    submit = 'self'
    
    if step == '10':
        print('app.py - /ajax finished - return new render setup')
        status_submit = False        
        return render_template('index.html',temp = temp,status = status, K_PULSE = K_PULSE, K_Threthold = K_Threthold, K_GAIN = K_GAIN, K_NRFI=K_NRFI, K_LD1=K_LD1, K_LD2=K_LD2, K_LD3=K_LD3, K_LD4=K_LD4, K_FAR_NEAR=K_FAR_NEAR, K_Mode = K_Mode, username = username, color = color, lang = lang)       
    elif step == '15':
        print('App.py :::>>> Unity_control return')
        flg_unity_control = False
        status_submit = False   
        return ('', 204)          
    else:
        global flg_params
        flg_params = True         
        status_submit = False        
        print('app.py - /ajax finished - return json')
        return jsonify(data={'submit':submit, 'K_Mode' : K_Mode, 'K_LD1' : K_LD1, 'K_LD2' : K_LD2, 'K_LD3' : K_LD3, 'K_LD4' : K_LD4, 'K_PULSE' : K_PULSE, 'K_GAIN' : K_GAIN, 'K_FAR_NEAR' : K_FAR_NEAR, 'K_Threthold' : K_Threthold, 'color' : color, 'temp' : temp, 'status':status, 'LT':LT, 'IM':IM})

'''
    Reject new connection if system out of resource
        => cpu 100%
        => bw 90% + jpeg
            => chỉ check khi login
'''
def allowNewLogin():
    mbps_pc = HardwareMonitoring.getInstance().bw_network_usage

    if mbps_pc > 90:
        if cap != None and cap.IM_QUALITY == ToFImageRendering.JPEG:
            return False
    
    cpu_p = HardwareMonitoring.getInstance().cpu_p
    if cpu_p > 95:
        return False
    
    return True
    
@app.route('/depth_feed', methods=['GET'])
def depth_feed():
    print("app.py - [MSG] start depth_feed")

    return Response(gendepth(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gendepth():
    global cap
    cap = CameraStream.getInstance()
    cap.start()
    
    capid = cap.capid()#d_vu - current video device id - 20190905

    fpslimit = cap.limitfps
    
    # d_vu - update camera.py mode - 20190906
    time_fps_start = -1
    num_of_frame = 0

    mimetype = b'ushort/depth'

    #d_vu - add - custom mime type - 20190926    
    while True:
        if time_fps_start == -1:
            time_fps_start = time.perf_counter()                

        time_read_start = time.perf_counter()
        data = cap.nextDepthFrame()

        print("app.py - next frame...")
        if data is None:
            print ("app.py [WARN] camera frame NONE")
            flgError = True
        else:
            flgError = False
            data2 = cv2.imencode(".jpg", data,[cv2.IMWRITE_JPEG_QUALITY, 60])[1]

            yield (b'--frame\r\n' b'Content-Type: ' + mimetype + b'\r\n\r\n\r\n' + data2.tobytes() + b'\r\n\r\n\r\n')
        
        num_of_frame = num_of_frame + 1

        time_read_end = time.perf_counter()
        time_read_diff = time_read_end - time_read_start

        TIME_T_MIN = cap.getMinBetweenRead()
        if time_read_diff < TIME_T_MIN:
            time_extra = TIME_T_MIN - time_read_diff            
            time.sleep(time_extra)
                        
        time_fps_end = time.perf_counter()
        time_fps_diff = time_fps_end - time_fps_start
        if time_fps_diff >= 1:
            fps = num_of_frame / time_fps_diff
            
            cpu_p = HardwareMonitoring.getInstance().cpu_p
            mbps = HardwareMonitoring.getInstance().bw_mbps
            mbps_pc = HardwareMonitoring.getInstance().bw_network_usage
            
            #print('app.py - [INFO] streaming [%s, %.2f fps], cpu: %.2f%%, nic [%.2f Mbps, %.2f%%]'% (str(mimetype), fps, cpu_p, mbps, mbps_pc))

            #reset
            time_fps_start = -1
            num_of_frame = 0
    
    print('app.py - [INFO] break the loop. I am done serving this thread ', threading.current_thread().ident)

#------ Profile Parameters -----
global flg_reset_option
flg_reset_option = False

@app.route('/default_option', methods=['POST'])
def default_option():
    try:
        print('------------------------------- Default option -----------------------------')
        global user_name
        user_name = request.form.get('user_name')
        user_name = user_name.strip()
        f = open("./option_param/default.txt", "r+")
        lst_content = f.readlines()
        K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = lst_content[0],lst_content[1],lst_content[2],lst_content[3],lst_content[4],lst_content[5],lst_content[6],lst_content[7],lst_content[8],lst_content[9],lst_content[10]
        K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = K_Mode.strip(),K_LD1.strip(),K_LD2.strip(),K_LD3.strip(),K_LD4.strip(),K_PULSE.strip(),K_NRFI.strip(),K_GAIN.strip(),K_FAR_NEAR.strip(),K_Threthold.strip(),color.strip()
        f.close()

    except Exception as et:
        print("app.py - /err_default_option_apply() EXCEPTION  ", str(et))      
        pass
    return jsonify(data={'K_Mode':K_Mode, 'K_LD1':K_LD1, 'K_LD2':K_LD2, 'K_LD3':K_LD3, 'K_LD4':K_LD4, 'K_PULSE':K_PULSE, 'K_NRFI':K_NRFI, 'K_GAIN':K_GAIN, 'K_FAR_NEAR':K_FAR_NEAR, 'K_Threthold':K_Threthold, 'color':color})

@app.route('/insert_option_s', methods=['POST'])
def insert_option_s():
    print('Insert Option SS ---------------------')
    name_insert_option = request.form.get('name_file_s')
    print(name_insert_option)

    number_option = request.form.get('number_option')
    number_option = int(number_option)
    print(number_option)
    try:   
        if number_option < 5 :
            K_Mode = request.form.get('K_Mode')
            K_LD1 = request.form.get('K_LD1')
            K_LD2 = request.form.get('K_LD2')
            K_LD3 = request.form.get('K_LD3')
            K_LD4 = request.form.get('K_LD4')
            K_PULSE = request.form.get('K_PULSE')  
            K_GAIN = request.form.get('K_GAIN')
            K_FAR_NEAR = request.form.get('K_FAR_NEAR') 
            K_NRFI = request.form.get('K_NRFI') 
            K_Threthold = request.form.get('K_Threthold')  
            color = request.form.get('color')  

            if K_LD1 == None:
                K_LD1 = 'off'
            else:
                K_LD1 = 'checked'
            if K_LD2 == None:
                K_LD2 = 'off'
            else:
                K_LD2 = 'checked'
            if K_LD3 == None:
                K_LD3 = 'off'
            else:
                K_LD3 = 'checked'
            if K_LD4 == None:
                K_LD4 = 'off'
            else:
                K_LD4 = 'checked'
            if K_NRFI == None:
                K_NRFI = 'off'
            else:
                K_NRFI = 'checked'
            if color == None:
                color = 'RAINBOW'

            f = open("./option_param/" + name_insert_option + ".txt","w+")
            f.write(K_Mode)
            f.write('\n')
            f.write(K_LD1)
            f.write('\n')
            f.write(K_LD2)
            f.write('\n')
            f.write(K_LD3)
            f.write('\n')
            f.write(K_LD4)
            f.write('\n')
            f.write(K_PULSE)
            f.write('\n')
            f.write(K_NRFI)
            f.write('\n')
            f.write(K_GAIN)
            f.write('\n')
            f.write(K_FAR_NEAR)
            f.write('\n')
            f.write(K_Threthold)
            f.write('\n')                      
            f.write(color) 
            f.close()

            f = open('option_user.txt','a+')
            f.write(name_insert_option)
            f.write('\n')
            f.close()
            #flg_file_name = True
    except Exception as et:
        print("app.py - /insert_option_parameters() EXCEPTION  ", str(et))      
        os.remove("./option_param/" + name_insert_option + ".txt") 
        pass

    global flg_reset_option
    flg_reset_option = True
    
    self_insert = 'self'

    return jsonify(data={'self_insert':self_insert})

@app.route('/insert_option', methods=['POST'])
def insert_option():
    print('Insert Option')
    name_insert_option = request.form.get('name_file')
    setup_name_file = request.form.get('setup_name_file')
    setup_name_file = setup_name_file.strip()
   
    number_option = request.form.get('number_option')
    number_option = int(number_option)
    
    flg_file_name = False
    try:
        if number_option < 5 :
            if setup_name_file == 'load':
                K_Mode = request.form.get('K_Mode')
                K_LD1 = request.form.get('K_LD1')
                K_LD2 = request.form.get('K_LD2')
                K_LD3 = request.form.get('K_LD3')
                K_LD4 = request.form.get('K_LD4')
                K_PULSE = request.form.get('K_PULSE')  
                K_GAIN = request.form.get('K_GAIN')
                K_FAR_NEAR = request.form.get('K_FAR_NEAR') 
                K_NRFI = request.form.get('K_NRFI') 
                K_Threthold = request.form.get('K_Threthold')  
                color = request.form.get('color')  

                if K_LD1 == None:
                    K_LD1 = 'off'
                else:
                    K_LD1 = 'checked'
                if K_LD2 == None:
                    K_LD2 = 'off'
                else:
                    K_LD2 = 'checked'
                if K_LD3 == None:
                    K_LD3 = 'off'
                else:
                    K_LD3 = 'checked'
                if K_LD4 == None:
                    K_LD4 = 'off'
                else:
                    K_LD4 = 'checked'
                if K_NRFI == None:
                    K_NRFI = 'off'
                else:
                    K_NRFI = 'checked'
                if color == None:
                    color = 'RAINBOW'

                f = open("./option_param/" + name_insert_option + ".txt","w+")
                f.write(K_Mode)
                f.write('\n')
                f.write(K_LD1)
                f.write('\n')
                f.write(K_LD2)
                f.write('\n')
                f.write(K_LD3)
                f.write('\n')
                f.write(K_LD4)
                f.write('\n')
                f.write(K_PULSE)
                f.write('\n')
                f.write(K_NRFI)
                f.write('\n')
                f.write(K_GAIN)
                f.write('\n')
                f.write(K_FAR_NEAR)
                f.write('\n')
                f.write(K_Threthold)
                f.write('\n')                      
                f.write(color) 
                f.close()

                f = open('option_user.txt','a+')
                f.write(name_insert_option)
                f.write('\n')
                f.close()
                flg_file_name = True
    except Exception as et:
        print("app.py - /insert_option_parameters() EXCEPTION  ", str(et))      
        os.remove("./option_param/" + name_insert_option + ".txt") 
        pass

    global flg_reset_option
    flg_reset_option = True
    self_insert = 'self'

    return jsonify(data={'self_insert':self_insert,'flg_file_name':flg_file_name})

@app.route('/delete_option', methods=['POST'])
def delete_option():
    print('Delete Option')
    try:
        name_remove = request.form.get('name_remove')  
        os.remove("./option_param/" + name_remove + ".txt")
        f = open('option_user.txt','r+')
        lines = f.readlines()
        fileLenght = len(lines) 
        i = 0
        while(i < fileLenght):
            lines[i] = lines[i].strip()
            if lines[i] == name_remove:
                global index
                index = i
            lines[i] = lines[i] + '\n'         
            i = i + 1      
        f.close()

        f = open('option_user.txt','w+')
        del lines[index]
        f.writelines(lines) 
        f.close()
    except Exception as et:
        print("app.py - /delete_option_parameters() EXCEPTION  ", str(et))       
        pass
    global flg_reset_option
    flg_reset_option = True
    self_delete = 'self'
    return jsonify(data={'self_delete':self_delete})

@app.route('/reset_counter', methods=['POST'])
def reset_counter():
    try:
        f = open('option_user.txt','r+')
        lines = f.readlines()
        f.close()
    except Exception as et:
        print("app.py - /reset_option_parameters() EXCEPTION  ", str(et))       
        pass
    global flg_reset_option
    flg_reset_option = False

    return jsonify(data={'lines':lines})

@app.route('/update', methods=['POST'])
def update():
    return jsonify(data={'flg_reset_option':flg_reset_option})

@app.route('/submit_s', methods=['POST'])
def submit_s():
    try:
        print('-------------------Submit successfully------------------------')
        global user_name
        user_name = request.form.get('user_name')
        user_name = user_name.strip()
        print(user_name)
        print(user_name)
        print(user_name)
        
        option = request.form.get('name')
        option = option.strip()
        print(option)
        f = open("./option_param/" + option +".txt", "r+")
        lst_content = f.readlines()
        K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = lst_content[0],lst_content[1],lst_content[2],lst_content[3],lst_content[4],lst_content[5],lst_content[6],lst_content[7],lst_content[8],lst_content[9],lst_content[10]
        K_Mode,K_LD1,K_LD2,K_LD3,K_LD4,K_PULSE,K_NRFI,K_GAIN,K_FAR_NEAR,K_Threthold,color = K_Mode.strip(),K_LD1.strip(),K_LD2.strip(),K_LD3.strip(),K_LD4.strip(),K_PULSE.strip(),K_NRFI.strip(),K_GAIN.strip(),K_FAR_NEAR.strip(),K_Threthold.strip(),color.strip()
        f.close()

    except Exception as et:
        print("app.py - /err_profile_option_apply() EXCEPTION  ", str(et))      
        pass

    return jsonify(data={'K_Mode':K_Mode, 'K_LD1':K_LD1, 'K_LD2':K_LD2, 'K_LD3':K_LD3, 'K_LD4':K_LD4, 'K_PULSE':K_PULSE, 'K_NRFI':K_NRFI, 'K_GAIN':K_GAIN, 'K_FAR_NEAR':K_FAR_NEAR, 'K_Threthold':K_Threthold, 'color':color})

@app.route('/flg_reset_option_to_false', methods=['POST'])
def flg_reset_option_to_false():
    global flg_reset_option
    flg_reset_option = False
    return jsonify(data={})

#-------- End Profile Parameters --------

#------ Recoding video --------
@app.route('/update_record', methods=['POST'])
def update_record():
    try:
        os.remove('video.avi')
    except Exception as et:
        pass

    try:
        global namefile
        namefile = request.form.get('namefile')
        print('*************************')
        print(namefile)
        print('*************************')
        os.rename('./static/record.avi','./static/' + namefile + '.avi')
    except Exception as et:
        print("app.py - /Err save name file video ()", str(et))
        pass
    return jsonify(data={})

@app.route('/self_record', methods=['POST'])
def self_record():  
    global vn 
    #if flg_record :       
    vn = request.form.get('viet_nam')
    #print('app.py', vn)
    try:
        cameraStream = cap
        cameraStream.check_ajax(vn)
    except Exception as et:
        pass

    try:
        #max_size = False
        size_file = os.path.getsize('video.avi')
        # if size_file >= 52428800:
        #     print('Stop record because max size of file video !!!')
        #     max_size = True
    except Exception as et:
        #max_size = False
        size_file = os.path.getsize('./static/record.avi')
        # if size_file >= 52428800:
        #     print('Stop record because max size of file video (exception) !!!')
        #     max_size = True
        pass

    return jsonify(data={'size_file':size_file})

flg_record = False
user_name_record = None
disable_download_app = False
name_file_rc = None

@app.route('/record_status', methods=['POST'])
def record_status():
    try:        
        global flg_record
        #cameraStream = None
        #if cameraStream == None:
        cameraStream = cap  # cap = CameraStream.getInstance() // cap.start()

        # json = request.get_json()
        # status = json['status']

        status = request.form.get('status')
        mode_present = request.form.get('mode_present')
        fps_number = request.form.get('fps_number')     #string
        # print(fps_number)
        # print(type(fps_number))

        if mode_present == "DEPTHIR":  #when recorder into file .avi with mode DEPTHIR use True
            mode_present = True
        else:
            mode_present = False
        print(status)

        global user_name_record, disable_download_app, name_file_rc
        
        if(status == "true" and flg_record == False):
            print('_________ Recording button __________')
            disable_download_app = False
            #user_name_record = json['user_name_web']
            user_name_record = request.form.get('user_name_web')
            print(user_name_record)
            flg_record = True
            Person().start()
        
            cameraStream.start_record(mode_present, fps_number)

            return jsonify(result="started")
        else:
            print('_________ Stop record button __________')            
            try:
                print('Xoa het file avi')
                filelist = [ f for f in os.listdir("./static/") if f.endswith(".avi") ]
                for f in filelist:
                    os.remove(os.path.join("./static/", f))
            except Exception as et:
                print('err xoa file avi', str(et))
                pass

            user_name_record = None   
            disable_download_app = True
            name_file_rc = request.form.get('name_file_rc')
            print(name_file_rc)

            #return jsonify(result="stopped")
            return jsonify(data={'disable_download_app':disable_download_app})
            
    except Exception as et:
        print("app.py - /Err record video () EXCEPTION  ", str(et))      
        pass

flg_check_status_reset = False
@app.route('/check_status_reset', methods=['POST'])
def check_status_reset():
    global user_name_record, flg_check_status_reset
    flg_check_status_reset = False
    user_web = request.form.get('user_web') 
    if user_web == user_name_record:
        if flg_record:
            flg_check_status_reset = True
            Person().reset_page()
    return jsonify(data={})

@app.route('/check_status_reset_to_false', methods=['POST'])
def check_status_reset_to_false():
    global flg_check_status_reset
    flg_check_status_reset = False
    return jsonify(data={})

vn = None 
count = 0
def yo_yo():
    return vn

def status_user_name():
    global vn 
    vn = None  
    return user_name_record

def re_start_flg_stop_btn():
    print('Button stop record click')
    global flg_record, user_name_record
    flg_record = False
    user_name_record = None
    cameraStream = cap
    cameraStream.stop_record()
    count = 0

    while True:        
        try:
            if count >= 100:
                break
            print(name_file_rc)
            # letters = string.ascii_lowercase
            # letters = ''.join(random.choice(letters) for i in range(10))
            #os.rename('./static/record.avi','./static/' + namefile + '.avi')
            os.rename('video.avi','./static/'+ name_file_rc +'.avi')
            break
        except Exception as et:
            count = count + 1
            time.sleep(0.02)
            continue

def re_start_flg_remove_video():
    print('Reset trang hoac logout')
    global flg_record, user_name_record
    flg_record = False
    user_name_record = None
    cameraStream = cap
    cameraStream.stop_record()
    counts = 0
    while True:
        try:
            if counts >= 100:
                break
            os.remove('video.avi')
            break
        except Exception as et:
            counts = counts + 1
            time.sleep(0.02)
            continue

class Person(threading.Thread):
    def __init__(self):     
        threading.Thread.__init__(self)
        self.buff = None
        self.isRunning = True
        self.count = 0

    def run(self):
        time.sleep(0.5)
        while self.isRunning:       
            #print(user_name_record)
            ha = yo_yo()   
            bb = status_user_name()
            if bb == None:
                print('Delete write video')
                self.count = 0
                self.isRunning = False
                re_start_flg_stop_btn()
                break
            if self.count > 5:
                print('Delete write video')
                self.count = 0
                self.isRunning = False
                re_start_flg_remove_video()
                break
            if ha == None:
                print('app.py', self.count)
                self.count = self.count + 1
            else:
                self.count = 0
                
            time.sleep(1)
     
    def stop(self):
        print('__ Stop __')
        self.isRunning = False
        print(self.isRunning)

    def reset_page(self):
        print('Reset Page')
        re_start_flg_remove_video()
        self.isRunning = False

#---------------------END---------------------------------

if __name__ == "__main__":
    app.debug = False
    app.secret_key = os.urandom(12)

    #app.run(host='10.0.2.15', port=8005, threaded=True)
    #serve(app,host='0.0.0.0',port=8005)
    #https://github.com/Pylons/waitress/issues/176
    serve(app,host='0.0.0.0',port=8005
    ,
        expose_tracebacks=True,
        connection_limit=1000,
        threads=10000,
        channel_timeout=10,
        cleanup_interval=30,
        backlog=2048)

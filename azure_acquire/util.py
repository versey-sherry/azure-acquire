import os
import sys
import time
import cv2
import json
import subprocess

import numpy as np
from datetime import datetime
from multiprocessing import Process, Queue
from pyk4a import *


def display_images(display_queue):
    while True: 
        data = display_queue.get() 
        if len(data)==0: 
            cv2.destroyAllWindows()
            break
        else:
            ir = data[0]
            ir = np.clip(ir+100,160,5500)
            ir = ((np.log(ir)-5)*70).astype(np.uint8)

            cv2.imshow('ir',ir)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 
        # clear queue before next iteration
        while True:
            try: display_queue.get_nowait()
            except: break


def write_frames(filename, frames, threads=6, fps=30, crf=10,
                 pixel_format='gray8', codec='h264', close_pipe=True,
                 pipe=None, slices=24, slicecrc=1, frame_size=None, get_cmd=False):
    """
    Write frames to avi file using the ffv1 lossless encoder
    """

    # we probably want to include a warning about multiples of 32 for videos
    # (then we can use pyav and some speedier tools)

    if not frame_size and type(frames) is np.ndarray:
        frame_size = '{0:d}x{1:d}'.format(frames.shape[2], frames.shape[1])

    command = ['ffmpeg',
               '-y',
               '-loglevel', 'fatal',
               '-framerate', str(fps),
               '-f', 'rawvideo',
               '-s', frame_size,
               '-pix_fmt', pixel_format,
               '-i', '-',
               '-an',
               '-crf',str(crf),
               '-vcodec', codec,
               '-preset', 'ultrafast',
               '-threads', str(threads),
               '-slices', str(slices),
               '-slicecrc', str(slicecrc),
               '-r', str(fps),
               filename]

    if get_cmd:
        return command

    if not pipe:
        pipe = subprocess.Popen(
            command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    for i in range(frames.shape[0]):
        pipe.stdin.write(frames[i,:,:].tobytes())

    if close_pipe:
        pipe.stdin.close()
        return None
    else:
        return pipe


def write_images(image_queue, filename_prefix):
    depth_pipe = None
    ir_pipe = None 
    
    while True: 
        data = image_queue.get() 
        if len(data)==0: 
            depth_pipe.stdin.close()
            ir_pipe.stdin.close()
            break
        else:
            ir,depth = data
            depth_pipe = write_frames(os.path.join(filename_prefix, 'depth.avi'), depth.astype(np.uint16)[None,:,:], codec='ffv1', close_pipe=False, pipe=depth_pipe, pixel_format='gray16')
            ir_pipe = write_frames(os.path.join(filename_prefix, 'ir.avi'), ir.astype(np.uint16)[None,:,:], close_pipe=False, codec='ffv1', pipe=ir_pipe, pixel_format='gray16')

# add camera related stuff here
def write_metadata(filename_prefix, subject_name, session_name, nidaq_channels=0,
                   nidaq_sampling_rate=0.0, depth_resolution=[640, 576], little_endian=True, 
                   depth_data_type="UInt16[]", color_resolution=[640, 576], color_data_type="UInt16[]"):
    
    metadata_dict = {"SubjectName": subject_name, 'SessionName': session_name,
                     "NidaqChannels": nidaq_channels, "NidaqSamplingRate": nidaq_sampling_rate,
                     "DepthResolution": depth_resolution, "IsLittleEndian": little_endian,
                     "DepthDataType": depth_data_type, "ColorResolution": color_resolution,
                     "ColorDataType": color_data_type, "StartTime": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
    
    metadata_name = os.path.join(filename_prefix, 'metadata.json')

    with open(metadata_name, 'w') as output:
        json.dump(metadata_dict, output)
            
            
def capture_from_azure(k4a, filename_prefix, recording_length, 
                       display_frames=False, display_time=False, 
                       realtime_queue=None):
    
    camera_name = filename_prefix.split('.')[-1]
    image_queue = Queue()
    write_process = Process(target=write_images, args=(image_queue, filename_prefix))
    write_process.start()
    
    if display_frames: 
        display_queue = Queue()
        display_process = Process(target=display_images, args=(display_queue,))
        display_process.start()
        
    k4a.start()
    system_timestamps = []
    device_timestamps = []
    start_time = time.time()
    count = 0
    
    try:
        while time.time()-start_time < recording_length:  
            capture = k4a.get_capture()
            if capture.depth is None: 
                print('Dropped frame')
                continue
            
            system_timestamps.append(time.time())
            device_timestamps.append(capture.depth_timestamp_usec)

            depth = capture.depth.astype(np.int16)
            ir = capture.ir.astype(np.uint16)

            image_queue.put((ir,depth))
            if display_frames and count % 2 == 0: 
                display_queue.put((ir[::2,::2],))
                
            if realtime_queue is not None and count%3==0:
                realtime_queue.put((ir,camera_name))

            if display_time and count % 15 == 0: 
                sys.stdout.write('\rRecorded '+repr(int(time.time()-start_time))+' out of '+repr(recording_length)+' seconds')
            count += 1
            
    except OSError:
        print('Recording stopped early')
        
    finally:
        k4a.stop()
        system_timestamps = np.array(system_timestamps)
        
        # np.save(filename_prefix+'.system_timestamps.npy',system_timestamps)
        # np.save(filename_prefix+'.device_timestamps.npy',device_timestamps)
        
        np.savetxt(os.path.join(filename_prefix, 'depth_ts.txt'), system_timestamps, fmt = '%f')
        np.savetxt(os.path.join(filename_prefix, 'device_ts.txt'),device_timestamps, fmt = '%f')
        print(' - Frame rate = ',len(system_timestamps) / (system_timestamps.max()-system_timestamps.min()))

        image_queue.put(tuple())
        write_process.join()

        if display_frames:
            display_queue.put(tuple())
            display_process.join()
            
        if realtime_queue is not None:
            realtime_queue.put(tuple())
            

def start_recording_RT(base_dir, subject_name, session_name, recording_length, 
                       bottom_device_id=0, display='top', teensy_port=None):
    # write recording metadata

    filename_prefix = os.path.join(base_dir,'session_' + datetime.now().strftime("%Y%m%d%H%M%S"))

    os.makedirs(filename_prefix, exist_ok=True)

    write_metadata(filename_prefix, subject_name, session_name)

    k4a_bottom = PyK4A(Config(color_resolution=ColorResolution.RES_720P,
                          depth_mode=DepthMode.NFOV_UNBINNED,
                          synchronized_images_only=False,
                          #wired_sync_mode=WiredSyncMode.MASTER
		), device_id=bottom_device_id)
                     
    p_bottom = Process(target=capture_from_azure, 
                       args=(k4a_bottom, filename_prefix , recording_length),
                       kwargs={'display_frames': True, 'display_time':True})

    p_bottom.start()
    
    
    
def save_camera_params(prefix, bottom_device_id=0, top_device_id=1):
    k4a_bottom = PyK4A(Config(color_resolution=ColorResolution.RES_720P,
                              depth_mode=DepthMode.NFOV_UNBINNED,
                              synchronized_images_only=False,
                              wired_sync_mode=WiredSyncMode.MASTER), device_id=bottom_device_id)

    k4a_top    = PyK4A(Config(color_resolution=ColorResolution.OFF,
                              depth_mode=DepthMode.NFOV_UNBINNED,
                              synchronized_images_only=False,
                              wired_sync_mode=WiredSyncMode.SUBORDINATE,
                              subordinate_delay_off_master_usec=640), device_id=top_device_id)


    k4a_top.start()
    k4a_bottom.start()
    time.sleep(1)
    k4a_bottom.save_calibration_json(prefix+'.bottom.json')
    k4a_top.save_calibration_json(prefix+'.top.json')
    k4a_top.stobp()
    k4a_bottom.stop()

    


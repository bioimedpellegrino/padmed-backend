
from django.conf import settings
from statistics import mean
import cv2
import numpy as np 
import os

def generate_video_measure(file_path, video_id):
    # Read video-blob
    cap = cv2.VideoCapture(os.path.join(settings.MEDIA_ROOT, file_path))
    # Get video resolution
    if settings.ROTATE_90_COUNTERCLOCKWISE:
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
    else:
        frame_width = int(cap.get(4))
        frame_height = int(cap.get(3))        
    # Define video codecs and writer
    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    video_name = 'tmp/' + "{}.avi".format(video_id)
    video_path = os.path.join(settings.MEDIA_ROOT, video_name)
    out = cv2.VideoWriter(video_path,fourcc, 15, (frame_height, frame_width)) 
    video_frames = []
    ret = True
    # Iterate frame by frame and store into a numpy array
    while (ret): 
        ret, frame = cap.read() 
        if ret:
            if settings.ROTATE_90_COUNTERCLOCKWISE:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            video_frames.append(frame)
    video_frames = np.array(video_frames)
    # Save frame array into file
    for frame in video_frames: 
        out.write(frame)
        
    return video_name

def unpack_result_deepaffex(deep_affex_result):
    
    result_unpacked = {}
    result_unpacked["Created"] = deep_affex_result["Created"]
    result_unpacked["Updated"] = deep_affex_result["Updated"]
    result_unpacked["ID"] = deep_affex_result["ID"]
    result_unpacked["StatusID"] = deep_affex_result["StatusID"]
    result_unpacked["StudyID"] = deep_affex_result["StudyID"]
    print("==================================")
    print(deep_affex_result.keys())
    # print("==================================")
    deep_affex_measures = deep_affex_result["Results"]
    # print("==================================")
    print(deep_affex_result["Results"])
    print("==================================")
    
    # Important value HB_BPM, SNR
    hb = deep_affex_measures["HR_BPM"]
    snr = deep_affex_measures["SNR"]
    hb_value = round(mean([mean(hb_data['Data'])/hb_data['Multiplier'] for hb_data in hb]), 2)
    snr_value = round(mean([mean(snr_data['Data'])/snr_data['Multiplier'] for snr_data in snr]), 2)
    result_unpacked["measure"] = {
        "HB_BPM": {
                "value": hb_value,
                "unit": deep_affex_result["SignalUnits"]["HR_BPM"]
                },
        "SNR": {
                "value": snr_value,
                "unit": deep_affex_result["SignalUnits"]["SNR"]
        }
    }
    
    return result_unpacked



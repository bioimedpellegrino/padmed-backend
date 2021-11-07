
from django.conf import settings

import cv2
import numpy as np 
import os

def generate_video_measure(file_path, video_id):
    # Read video-blob
    cap = cv2.VideoCapture(os.path.join(settings.MEDIA_ROOT, file_path))
    # Get video resolution
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    # Define video codecs and writer
    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    video_name = 'tmp/' + "{}.avi".format(video_id)
    video_path = os.path.join(settings.MEDIA_ROOT, video_name)
    out = cv2.VideoWriter(video_path,fourcc, 15, (frame_width,frame_height)) 
    video_frames = []
    ret = True
    # Iterate frame by frame and store into a numpy array
    while (ret): 
        ret, frame = cap.read() 
        if ret: 
            video_frames.append(frame)
    video_frames = np.array(video_frames)
    # Save frame array into file
    for frame in video_frames: 
        out.write(frame)
        
    return video_name
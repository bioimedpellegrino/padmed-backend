
from django.conf import settings
from statistics import mean
import cv2
import numpy as np 
import os
from dfx.models import DeepAffexPoint
from logger.utils import add_log


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
    # print("==================================")
    # print(deep_affex_result.keys())
    # print("==================================")
    deep_affex_measures = deep_affex_result["Results"]
    # print("==================================")
    # print(deep_affex_result["Results"])
    # print("==================================")
    
    # GENERATE MEASURE
    deep_affex_points = DeepAffexPoint.objects.filter(is_measure=True)
    for deep_affex_point in deep_affex_points:
        try:
            raw_data = deep_affex_measures[deep_affex_point.signal_key]
            result_unpacked["measure"][deep_affex_point.signal_key] = deep_affex_point.compute_value(raw_data[0]['Data'])
        except Exception as e:
            add_log(level=5, message=5, custom_message='Error UNPACK MEASURE: %s' % e)
        
    # hb = deep_affex_measures["HR_BPM"]
    # snr = deep_affex_measures["SNR"]
    # hb_value = round(mean([mean(hb_data['Data'])/hb_data['Multiplier'] for hb_data in hb]), 2)
    # snr_value = round(mean([mean(snr_data['Data'])/snr_data['Multiplier'] for snr_data in snr]), 2)
    # result_unpacked["measure"] = {
    #     "HB_BPM": {
    #             "value": hb_value,
    #             "unit": deep_affex_result["SignalUnits"]["HR_BPM"]
    #             },
    #     "SNR": {
    #             "value": snr_value,
    #             "unit": deep_affex_result["SignalUnits"]["SNR"]
    #     }
    # }
    
    return result_unpacked


def measure_json_to_list(measure_json):
    """_summary_
    #TODO DOCS
    Args:
        measure_json (_type_): _description_

    Returns:
        _type_: _description_
    """
    return [{"key": k, "name": v["name"], "value": v["value"], "unit":v["unit"]} for k,v in measure_json.items()]


def print_command_measure(measure, date):
    """_summary_
    #TODO DOCS
    Args:
        measure (_type_): _description_
    """
    signals_list = measure_json_to_list(measure["measure"])
    print_command = "<BIG><BOLD><CENTER> PADMED <BR>\n" + "<CENTER>Esito misurazione<BR>\n" + "<CENTER>Data:" + date +"<BR>\n" + "<BOLD>Misurazione:" +"<BR>\n" + "<BOLD>Misurazione:"+ "<BR>\n";
    for signal_list in signals_list:
        command = "<LEFT><BOLD>" + signal_list.name + ":" + " " + signal_list.value + " " + signal_list.unit + "<BR>\n"
        print_command += command
    print_command += "<CUT>\n"
    
    return print_command
import argparse
import asyncio
import base64
import copy
import glob
import json
import math
import os.path
import random
import string

import aiohttp
import cv2
import dfx_apiv2_client as dfxapi
import libdfx as dfxsdk
import pkg_resources

from django.conf import settings

from dfxutils.app import AppState, MeasurementStep
from dfxutils.dlib_tracker import DlibTracker
from dfxutils.opencvhelpers import CameraReader, VideoReader
from dfxutils.prettyprint import PrettyPrinter as PP
from dfxutils.renderer import NullRenderer, Renderer
from dfxutils.sdkhelpers import DfxSdkHelpers

from .utils import save_config, load_config, generate_reqid, determine_action
from logger.utils import add_log

# Api method for device registration. Be careful with that (must be sure to store the device_token)
async def register(config=None, license_key=None):
    """[summary]

    Args:
        config ([type], optional): [description]. Defaults to None.
        license_key ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    if not license_key:
        license_key = settings.LICENCE_KEY
    
    if dfxapi.Settings.device_token:
        print("Already registered")
        return False

    async with aiohttp.ClientSession() as session:
        status, body = await dfxapi.Organizations.register_license(session, license_key, "LINUX", "DFX Example",
                                                                   "DFXCLIENT", "0.0.1")
        if status < 400:
            config = {}
            config["device_id"] = dfxapi.Settings.device_id
            config["device_token"] = dfxapi.Settings.device_token
            config["role_id"] = dfxapi.Settings.role_id
            config["user_token"] = dfxapi.Settings.user_token
            print(f"Register successful with new device id {config['device_id']}")
            save_config(config)
            return config
        else:
            print(f"Register failed {status}: {body}")
            return {}
# Fast way for register a new device
# TODO  ->Must be tested first!!!
async def register_device():
    config = await register()
    
    if config:
        save_config(config)
# Login to DeepAffex service api. 
async def login(config, email, password):
    """[summary]

    Args:
        config [(dict)]: [Dict previously loaded by the config.json file, which contains user-licence informations]
        email [(str)]: [Email address to DeepAffex dashboard]
        password [(str)]: [Password to DeepAffex dashboard]

    Returns:
        [boolean]: [return True if user_token in the config.json file is populated, False otherwise]
    """
    # if dfxapi.Settings.user_token:
    #     print("Already logged in")
    #     return False

    # if not dfxapi.Settings.device_token:
    #     print("Please register first to obtain a device_token")
    #     return False

    headers = {"Authorization": f"Bearer {dfxapi.Settings.device_token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        status, body = await dfxapi.Users.login(session, email, password)
        if status < 400:
            config["user_token"] = dfxapi.Settings.user_token
            save_config(config)
            print("Login successful")
            return True
        else:
            print(f"Login failed {status}: {body}")
            return False

async def get_studies_by_id(config=None, config_path=None, study_id=None):
    config = load_config(config_path) if not config else config
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        study_id = config["selected_study"] if study_id is None else study_id
        if not study_id or study_id.isspace():
            print("Please select a study or pass a study id")
            return
        _, study = await dfxapi.Studies.retrieve(session, study_id, raise_for_status=False)
        return study

async def get_studies_list(config=None, config_path=None):
    try:
        config = load_config(config_path) if not config else config
    except TypeError:
        raise TypeError("If config argument is not passed, you should pass a valid config.json file path")

    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        _, studies = await dfxapi.Studies.list(session)
        print(json.dumps(studies))
        return studies
    
async def select_study(study_id, config, config_path):
    
    config = load_config(config_path) if (not config or config == "" or config == {}) else config
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        status, response = await dfxapi.Studies.retrieve(session, study_id, raise_for_status=False)
        if status >= 400:
            PP.print_pretty(response)
            return
        config["selected_study"] = study_id
        save_config(config, config_path)
        
async def get_measurements_list(config, status_id_filter=[], limit=10, profile_id="", partner_id=""):
    
    if not config or config == "" or config == {}:
        return "Config dict must be passed!"
    
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        _, measurements = await dfxapi.Measurements.list(session,
                                                            limit=limit,
                                                            user_profile_id=profile_id,
                                                            partner_id=partner_id)
    # Filter sections
    measurements_filtered = list(filter(lambda measurement: measurement['StatusID'] in status_id_filter, measurements)) if status_id_filter else measurements
    return measurements_filtered

async def get_measurement(config, measurement_id=None, pretty_print=False):
    if not config or config == "" or config == {}:
        return "Config dict must be passed!"
    
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        measurement_id = config["last_measurement"] if measurement_id is None else measurement_id
        if not measurement_id or measurement_id.isspace():
            print("Please complete a measurement first or pass a measurement id")
            return
        _, results = await dfxapi.Measurements.retrieve(session, measurement_id)
        if pretty_print:
            PP.print_result(results)
        return results

async def get_study_types(config, status=''):
    if not config or config == "" or config == {}:
        return "Config dict must be passed!"
    
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        _, results = await dfxapi.Studies.types(session, status)
        return results

async def get_list_templates(config, status='ACTIVE', type_=''):
    if not config or config == "" or config == {}:
        return "Config dict must be passed!"
    
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        _, results = await dfxapi.Studies.list_templates(session, status, type_=type_)
        return results

async def retrieve_sdk_config(config, config_file, sdk_id):
    if not config or config == "" or config == {}:
        return "Config dict must be passed!"
    
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        status, response = await dfxapi.Studies.retrieve_sdk_config_data(session, config["selected_study"], sdk_id,
                                                                         config["study_cfg_hash"])
        if status == 304:  # Our hash and data are already correct nothing to do
            pass
        elif status == 200:  # Got a new hash and data
            config["study_cfg_hash"] = response["MD5Hash"]
            config["study_cfg_data"] = response["ConfigFile"]
            print(f"Retrieved new DFX SDK config data with md5: {config['study_cfg_hash']}")
            save_config(config, config_file)
        else:
            raise RuntimeError(f"Could not retrieve DFX SDK config data for Study ID {config['selected_study']}. "
                               "Please contact Nuralogix")

        return base64.standard_b64decode(config["study_cfg_data"])
    
async def make_measure(config, config_path, video_path, demographics=None, start_time=2, end_time=20, rotation=None, fps=None, debug_study_cfg_file=None, profile_id="", partner_id=""):
    
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    # Prepare to make a measurement..
    app = AppState()
    logs = {}
    try:
        # Open the camera or video
        imreader = VideoReader(video_path, start_time, end_time, rotation=rotation, fps=fps)

        # Open the demographics file if provided
        if demographics is not None:
            with open(demographics, "r") as f:
                app.demographics = json.load(f)

        # Create a face tracker
        tracker = DlibTracker()

        # Create DFX SDK factory
        factory = dfxsdk.Factory()
        print("Created DFX Factory:", factory.getVersion())
        logs["1"] = "Created DFX Factory:{}".format(factory.getVersion())
        sdk_id = factory.getSdkId()

        # Get study config data..
        if debug_study_cfg_file is None:
            # ..from API required to initialize DFX SDK collector (or FAIL)
            study_cfg_bytes = await retrieve_sdk_config(config, config_path, sdk_id)
        else:
            # .. or from a file
            with open(debug_study_cfg_file, 'rb') as f:
                study_cfg_bytes = f.read()
    except Exception as ex:
        import traceback
        print(traceback.format_exc())
        logs["exception"] = "{}".format(ex)
        add_log(level=5, message=5, custom_message='Error on STEP 1 make measure: %s' % ex)
        return None, logs
    
    # Create DFX SDK collector (or FAIL)
    if not factory.initializeStudy(study_cfg_bytes):
        print(f"DFX factory creation failed: {factory.getLastErrorMessage()}")
        logs["2"] = f"DFX factory creation failed: {factory.getLastErrorMessage()}"
        return None, logs
    factory.setMode("discrete")
    collector = factory.createCollector()
    if collector.getCollectorState() == dfxsdk.CollectorState.ERROR:
        print(f"DFX collector creation failed: {collector.getLastErrorMessage()}")
        logs["3"] = f"DFX collector creation failed: {collector.getLastErrorMessage()}"
        return None, logs
    
    print("Created DFX Collector:")
    chunk_duration_s = float(settings.CHUNK_DURATION)
    frames_per_chunk = math.ceil(chunk_duration_s * imreader.fps)
    app.number_chunks = math.ceil(imreader.frames_to_process / frames_per_chunk)
    print(imreader.frames_to_process, frames_per_chunk, app.number_chunks)
    app.begin_frame = imreader.start_frame
    app.end_frame = imreader.stop_frame
    logs["4"] = "Created DFX Collector: %s %s %s" %(imreader.frames_to_process, frames_per_chunk, app.number_chunks)
    # Set collector config
    collector.setTargetFPS(imreader.fps)
    collector.setChunkDurationSeconds(chunk_duration_s)
    collector.setNumberChunks(app.number_chunks)
    print(f"    mode: {factory.getMode()}")
    print(f"    number chunks: {collector.getNumberChunks()}")
    print(f"    chunk duration: {collector.getChunkDurationSeconds()}s")
    for constraint in collector.getEnabledConstraints():
        print(f"    enabled constraint: {constraint}")

    # Set the demographics
    if app.demographics is not None:
        print("    Setting user demographics:")
        for k, v in app.demographics.items():
            collector.setProperty(f"{k}:1", str(v))  # The :1 is because we only care about one face in this project
            print(f"       {k}: {v}")
    
    # Make a measurement
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        # Create a measurement on the API and get the measurement ID
        _, response = await dfxapi.Measurements.create(session,
                                                    config["selected_study"],
                                                    user_profile_id=profile_id,
                                                    partner_id=partner_id)
        app.measurement_id = response["ID"]
        print(f"Created measurement {app.measurement_id}")
        logs["5"] = f"Created measurement {app.measurement_id}"
        # Use the session to connect to the WebSocket
        async with session.ws_connect(dfxapi.Settings.ws_url) as ws:
            # Subscribe to results
            results_request_id = generate_reqid()
            await dfxapi.Measurements.ws_subscribe_to_results(ws, generate_reqid(), app.measurement_id,
                                                            results_request_id)

            # Queue to pass chunks between coroutines
            chunk_queue = asyncio.Queue(app.number_chunks)

            # When we receive the last chunk from the SDK, we can check for measurement completion
            app.last_chunk_sent = False
            
            # Null render -> face tracker
            renderer = NullRenderer()
            
            produce_chunks_coro = extract_from_imgs(
                    chunk_queue,  # Chunks will be put into this queue
                    imreader,  # Image reader
                    tracker,  # Face tracker
                    collector,  # DFX SDK collector needed to create chunks
                    renderer,  # Rendering
                    app)  # App

            # Coroutine to get chunks from chunk_queue and send chunk using WebSocket
            async def send_chunks():
                while True:
                    chunk = await chunk_queue.get()
                    if chunk is None:
                        chunk_queue.task_done()
                        break

                    # Determine action and request id
                    action = determine_action(chunk.chunk_number, chunk.number_chunks)

                    # Add data
                    await dfxapi.Measurements.ws_add_data(ws, generate_reqid(), app.measurement_id, chunk.chunk_number,
                                                          action, chunk.start_time_s, chunk.end_time_s,
                                                          chunk.duration_s, chunk.metadata, chunk.payload_data)
                    print(f"Sent chunk {chunk.chunk_number}")
                    renderer.set_sent(chunk.chunk_number)

                    # Update data needed to check for completion
                    app.number_chunks_sent += 1
                    app.last_chunk_sent = action == 'LAST::PROCESS'

                    # Save chunk (for debugging purposes)
                    if settings.DEEPAFFEX_DEBUG:
                        DfxSdkHelpers.save_chunk(copy.copy(chunk), settings.DEEPAFFEX_DEBUG_SAVE_CHUNKS_FOLDER)
                        print(f"Saved chunk {chunk.chunk_number} in '{settings.DEEPAFFEX_DEBUG_SAVE_CHUNKS_FOLDER}'")

                    chunk_queue.task_done()

                app.step = MeasurementStep.WAITING_RESULTS
                print("Extraction complete, waiting for results")
                logs["6"] = "Extraction complete, waiting for results"
            # Coroutine to receive responses using the Websocket
            async def receive_results():
                num_results_received = 0
                async for msg in ws:
                    status, request_id, payload = dfxapi.Measurements.ws_decode(msg)
                    if request_id == results_request_id:
                        sdk_result = collector.decodeMeasurementResult(payload)
                        print("sdk_result", sdk_result)
                        result = DfxSdkHelpers.sdk_result_to_dict(sdk_result)
                        print("result", result)
                        renderer.set_results(result.copy())
                        PP.print_sdk_result(result)
                        num_results_received += 1
                    # We are done if the last chunk is sent and number of results received equals number of chunks sent
                    if app.last_chunk_sent and num_results_received == app.number_chunks_sent:
                        await ws.close()
                        break

                app.step = MeasurementStep.COMPLETED
                print("Measurement complete")
                logs["7"] = "Measurement complete"
            # Coroutine for rendering
            async def render():
                if type(renderer) == NullRenderer:
                    return

            # Wrap the coroutines in tasks, start them and wait till they finish
            tasks = [
                asyncio.create_task(produce_chunks_coro),
                asyncio.create_task(send_chunks()),
                asyncio.create_task(receive_results()),
                asyncio.create_task(render())
            ]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            for p in pending:  # If there were any pending coroutines, cancel them here...
                p.cancel()
            if len(pending) > 0:  # If we had pending coroutines, it means something went wrong in the 'done' ones
                for d in done:
                    e = d.exception()
                    if e is not None and type(e) != asyncio.CancelledError:
                        print(e, "ok")
                print(f"Measurement {app.measurement_id} failed")
                logs["8"] = f"Measurement {app.measurement_id} failed"
            else:
                config["last_measurement"] = app.measurement_id
                save_config(config, config_path)
                print(f"Measurement {app.measurement_id} completed")
                print(f"Use 'python {os.path.basename(__file__)} measure get' to get comprehensive results")
                logs["8"] = f"Measurement {app.measurement_id} completed"
            return app.measurement_id, logs

async def extract_from_imgs(chunk_queue, imreader, tracker, collector, renderer, app):
    # Read frames from the image source, track faces and extract using collector
    while True:
        # Grab a frame
        read, image, frame_number, frame_timestamp_ns = await imreader.read_next_frame()
        if not read or image is None:
            # Video ended, so grab what should be the last, possibly truncated chunk
            collector.forceComplete()
            chunk_data = collector.getChunkData()
            if chunk_data is not None:
                chunk = chunk_data.getChunkPayload()
                await chunk_queue.put(chunk)
                break

        # Start the DFX SDK collection if we received a start command
        if app.step == MeasurementStep.USER_STARTED:
            collector.startCollection()
            app.step = MeasurementStep.MEASURING
            if app.is_camera:
                app.begin_frame = frame_number
                app.end_frame = frame_number + app.end_frame

        # Track faces
        tracked_faces = tracker.trackFaces(image, frame_number, frame_timestamp_ns / 1000000.0)

        # Create a DFX VideoFrame, then a DFX Frame from the DFX VideoFrame and add DFX faces to it
        dfx_video_frame = dfxsdk.VideoFrame(image, frame_number, frame_timestamp_ns,
                                            dfxsdk.ChannelOrder.CHANNEL_ORDER_BGR)
        dfx_frame = collector.createFrame(dfx_video_frame)
        if len(tracked_faces) > 0:
            tracked_face = next(iter(tracked_faces.values()))  # We only care about the first face in this demo
            dfx_face = DfxSdkHelpers.dfx_face_from_json(collector, tracked_face)
            dfx_frame.addFace(dfx_face)

        if app.step == MeasurementStep.NOT_READY and len(tracked_faces) > 0:
            app.step = MeasurementStep.USER_STARTED

        # Extract bloodflow if the measurement has started
        if app.step == MeasurementStep.MEASURING:
            collector.defineRegions(dfx_frame)
            result = collector.extractChannels(dfx_frame)

            # Grab a chunk and check if we are finished
            if result == dfxsdk.CollectorState.CHUNKREADY or result == dfxsdk.CollectorState.COMPLETED:
                chunk_data = collector.getChunkData()
                if chunk_data is not None:
                    chunk = chunk_data.getChunkPayload()
                    await chunk_queue.put(chunk)
                if result == dfxsdk.CollectorState.COMPLETED:
                    break

        await renderer.put_nowait((image, (dfx_frame, frame_number, frame_timestamp_ns)))

    # Stop the tracker
    tracker.stop()

    # Close the camera
    imreader.close()

    # Signal to send_chunks that we are done
    await chunk_queue.put(None)

    # Signal to render_queue that we are done
    renderer.keep_render_last_frame()
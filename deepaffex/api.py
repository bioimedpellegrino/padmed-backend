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
    if dfxapi.Settings.user_token:
        print("Already logged in")
        return False

    if not dfxapi.Settings.device_token:
        print("Please register first to obtain a device_token")
        return False

    headers = {"Authorization": f"Bearer {dfxapi.Settings.device_token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        status, body = await dfxapi.Users.login(session, email, password)
        if status < 400:
            config["user_token"] = dfxapi.Settings.user_token
            print("Login successful")
            return True
        else:
            print(f"Login failed {status}: {body}")
            return False
# Save/Load the config.json file
def save_config(config, config_file_path="./config.json"):
    """[summary]

    Args:
        config [(dict)]: [Actual config dict to store]
        config_file_path [(str), optional]: [description]. Defaults to "./config.json".
    """
    with open(config_file_path, "w") as c:
        c.write(json.dumps(config, indent=4))
        print(f"Config updated in {config_file_path}")
        
def load_config(config_file):
    """[summary]

    Args:
        config_file [(srt)]: [config.json file path]

    Returns:
        (dict): [dict containing config.json]
    """
    config = {
        "device_id": "",
        "device_token": "",
        "role_id": "",
        "user_id": "",
        "user_token": "",
        "selected_study": "",
        "last_measurement": "",
        "study_cfg_hash": "",
        "study_cfg_data": "",
    }
    if os.path.isfile(config_file):
        with open(config_file, "r") as c:
            read_config = json.loads(c.read())
            config = {**config, **read_config}

    dfxapi.Settings.device_id = config["device_id"]
    dfxapi.Settings.device_token = config["device_token"]
    dfxapi.Settings.role_id = config["role_id"]
    dfxapi.Settings.role_id = config["role_id"]
    dfxapi.Settings.user_token = config["user_token"]
    if "rest_url" in config and config["rest_url"]:
        dfxapi.Settings.rest_url = config["rest_url"]
    if "ws_url" in config and config["ws_url"]:
        dfxapi.Settings.ws_url = config["ws_url"]

    return config


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
    
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        status, response = await dfxapi.Studies.retrieve(session, study_id, raise_for_status=False)
        if status >= 400:
            PP.print_pretty(response)
            return
        config["selected_study"] = study_id
        save_config(config, config_path)
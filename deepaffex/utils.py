
import json
import string
import random
import os
import dfx_apiv2_client as dfxapi

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

def generate_reqid():
    return "".join(random.choices(string.ascii_letters, k=10))

def determine_action(chunk_number, number_chunks):
    action = 'CHUNK::PROCESS'
    if chunk_number == 0 and number_chunks > 1:
        action = 'FIRST::PROCESS'
    elif chunk_number == number_chunks - 1:
        action = 'LAST::PROCESS'
    return action


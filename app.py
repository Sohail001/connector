from flask import Flask, jsonify, request
from flask_cors import CORS
from devices import get_device_list
from OEM import LDevAbs, BRDCheckStatus
from helpers import LogController
logController = LogController()
device = LDevAbs()

app = Flask(__name__)
CORS(app)

@app.route("/run_command/", methods=["POST"])
def run_command():
    json_data = request.get_json()
    
    command = json_data['command']

    print("command", json_data)
    
    if command is None:
        return jsonify({
            "output": "No command is passed"
        }), 404
    
    logController.Write(f'Command: {command}')
    """ main method of connector route """
    # command = "CHECK_STATUS"
    result = None
    
    if command == "LIST_DEVICES":
        result = get_device_list()
    elif command == "CHECK_STATUS":
        com_port = "COM4"
        # print("port initialiZe", device.Initialize(com_port))
        logController.Write(f'Initializing {com_port} device')
        if device.Initialize(com_port):
            logController.Write(f'{com_port} initialized successfully!')
            if device.CheckStatus() == BRDCheckStatus.Ready:
                # print("Device is ready!")
                logController.Write(f'{com_port} is ready to use!')
                result = {
                    "status": "SUCCESS",
                    "output": "Device is ready!"
                }
            else:
                result = {
                    "status": "FAILED",
                    "output": "Device is not ready!"
                }
        else:
            message = "Device is in use" if "Access is denied" in device.m_ErrorMessage  else  "Failed to initialize device."
            result = {
                "status": "This is a test from the pc",
                "output": message
            }
            
    print("reslt cloner", result)
    
    return result

if __name__  == "__main__":
    app.run(debug=False, port=2254)
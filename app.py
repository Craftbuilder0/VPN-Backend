from flask import Flask, jsonify, request
from flask_cors import CORS
from auth.firebase_auth import verify_token
from vpn_manager.openvpn import manage_openvpn
from vpn_manager.wireguard import manage_wireguard
import os
import subprocess
from dotenv import load_dotenv
import platform  # <-- Add this import

load_dotenv()

app = Flask(__name__)
CORS(app, origins=os.getenv("ALLOWED_ORIGINS"))
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

# Generic error handler
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "API is running"}), 200

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        token = request.json.get("idToken")
        user = verify_token(token)
        if user:
            return jsonify({"message": "Login successful", "user": user}), 200
        return jsonify({"message": "Invalid token"}), 401
    except Exception as e:
        return handle_exception(e)

# Connect to VPN
@app.route('/vpn/connect', methods=['POST'])
def connect_vpn():
    try:
        data = request.json
        vpn_type = data.get("type")
        config = data.get("config")
        is_windows = platform.system() == "Windows"

        if vpn_type == "openvpn":
            # For OpenVPN, you might not need to change anything if it doesn't use sudo.
            result = manage_openvpn(config, action="connect")
        elif vpn_type == "wireguard":
            # Pass use_sudo flag based on OS
            result = manage_wireguard(config, action="connect", use_sudo=not is_windows)
        else:
            return jsonify({"error": "Invalid VPN type"}), 400

        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "VPN connected successfully", "details": result}), 200
    except Exception as e:
        return handle_exception(e)

# Disconnect VPN
@app.route('/vpn/disconnect', methods=['POST'])
def disconnect_vpn():
    try:
        vpn_type = request.json.get("type")
        is_windows = platform.system() == "Windows"

        if vpn_type == "openvpn":
            result = manage_openvpn(action="disconnect")
        elif vpn_type == "wireguard":
            result = manage_wireguard(action="disconnect", use_sudo=not is_windows)
        else:
            return jsonify({"error": "Invalid VPN type"}), 400

        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "VPN disconnected successfully", "details": result}), 200
    except Exception as e:
        return handle_exception(e)

# VPN status check (detailed for both OpenVPN and WireGuard)
@app.route('/vpn/status', methods=['GET'])
def vpn_status():
    try:
        openvpn_status = None
        wireguard_status = None

        # Check OpenVPN status
        try:
            openvpn_status = subprocess.check_output(["pgrep", "openvpn"]).decode().strip()
        except subprocess.CalledProcessError:
            openvpn_status = None

        # Check WireGuard status
        try:
            wireguard_status = subprocess.check_output(["pgrep", "wireguard"]).decode().strip()
        except subprocess.CalledProcessError:
            wireguard_status = None

        if openvpn_status:
            return jsonify({"status": "connected", "type": "OpenVPN", "pid": openvpn_status}), 200
        elif wireguard_status:
            return jsonify({"status": "connected", "type": "WireGuard", "pid": wireguard_status}), 200
        else:
            return jsonify({"status": "disconnected"}), 200
    except Exception as e:
        return handle_exception(e)

if __name__ == "__main__":
    app.run(debug=True)

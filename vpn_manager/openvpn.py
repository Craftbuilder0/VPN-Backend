import subprocess

def manage_openvpn(config=None, action="connect"):
    try:
        if action == "connect":
            command = ["sudo", "openvpn", "--config", config]
            subprocess.Popen(command)
            return {"status": "connected"}
        elif action == "disconnect":
            subprocess.run(["sudo", "pkill", "openvpn"])
            return {"status": "disconnected"}
        else:
            return {"error": "Invalid action"}
    except subprocess.SubprocessError as e:
        return {"error": f"VPN operation failed: {str(e)}"}

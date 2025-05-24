import subprocess

def manage_wireguard(config=None, action="connect"):
    try:
        if action == "connect":
            command = ["sudo", "wg-quick", "up", config]
            subprocess.Popen(command)
            return {"status": "connected"}
        elif action == "disconnect":
            command = ["sudo", "wg-quick", "down", config]
            subprocess.run(command)
            return {"status": "disconnected"}
    except Exception as e:
        return {"error": str(e)}

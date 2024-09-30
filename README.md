# Wi-Fi Jammer Script

![image](https://github.com/user-attachments/assets/8626b017-2924-4904-a3e8-7c820848a75a)

This script allows you to perform a deauthentication attack on Wi-Fi networks, effectively disconnecting clients from a targeted network.

---

### **Disclaimer**:

This tool is for educational purposes only. Unauthorized use of this script can violate laws and regulations. Always ensure you have permission to test any network before performing any actions.

---

## Requirements

- A Linux system (preferably Kali Linux)
- Python 3.x installed
- `aircrack-ng` tools installed (`airodump-ng`, `aireplay-ng`, `airmon-ng`)
- A Wi-Fi adapter that supports monitor mode

---

### Install necessary tools:

```bash
sudo apt update
sudo apt install aircrack-ng
```

---

## Steps to Use

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/MohitPimoli/Net-Ninja.git
cd wifi-jammer
```

### 2. Run the Script

Before running the script, ensure you have administrative privileges (use sudo):

```bash
sudo python3 wifi_jammer.py
```

### 3. Select the Wi-Fi Interface

The script will list available Wi-Fi interfaces. Select the interface you want to use for the attack by entering the corresponding number.

### Example:

```bash
The following WiFi interfaces are available:
0 - wlan0
1 - wlan1

Please select the interface you want to use for the attack: 0
```

### 4. Monitor Mode

The script will automatically put the selected interface into monitor mode, allowing you to capture Wi-Fi packets and perform attacks.

### 5. Scan for Access Points

The script will start scanning for available access points and display a list of detected networks with details like BSSID, channel, and ESSID.

```bash
Copy code
No |   BSSID               |   Channel |   ESSID
___|_______________________|___________|________________________
0  |   00:14:6C:7E:40:80   |   6       |   MyNetwork
1  |   00:14:6C:7E:40:81   |   11      |   GuestNetwork
```

### 6. Choose a Target

Once the scan is complete, select the network you want to target by entering the corresponding number.

```bash
Please select a choice from above: 0
```

### 7. Deauthentication Attack

The script will now initiate the deauthentication attack on the selected network, sending deauth packets to disconnect clients.

```bash
Deauthenticating clients...
Deauthentication attack in progress. Press Ctrl+C to stop.
```

### 8. Stopping the Attack

To stop the attack, press Ctrl+C. The script will automatically revert the Wi-Fi interface back to managed mode, restoring normal Wi-Fi functionality.

---

## Notes

- Always ensure your Wi-Fi adapter supports monitor mode and packet injection for the script to function correctly.
- You can access any backup .csv files that the script generates in the backup/ folder.

---

## Author

By: Mohit Pimoli
Version: 1.1

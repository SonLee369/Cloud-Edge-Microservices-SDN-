# VMware Networking Troubleshooting Guide

## 🔍 Problem
All VMs (Master, Cloud, Edge) cannot access the internet:
- Cannot download packages with `wget`
- Cannot pull Docker images
- Cannot reach external servers

---

## 📋 Diagnostics

Run this script on **each VM** to diagnose the issue:

```bash
#!/bin/bash
echo "========================================="
echo "Network Diagnostics"
echo "========================================="

echo ""
echo "1. Network Interfaces:"
ip addr show

echo ""
echo "2. Routing Table:"
ip route show

echo ""
echo "3. DNS Configuration:"
cat /etc/resolv.conf

echo ""
echo "4. Test Local Network:"
ping -c 3 192.168.182.1

echo ""
echo "5. Test Internet (IP):"
ping -c 3 8.8.8.8

echo ""
echo "6. Test Internet (DNS):"
ping -c 3 google.com

echo ""
echo "7. Gateway Connectivity:"
ip route | grep default
ping -c 3 $(ip route | grep default | awk '{print $3}')

echo "========================================="
```

Save as `network_diagnostics.sh`, run on each VM.

---

## 🔧 Solution 1: VMware Network Adapter Settings

### Check VMware Settings (Windows Host)

1. **Open VMware Workstation**
2. **Select a VM** → Right-click → **Settings**
3. **Network Adapter** → Check configuration:

**Recommended Settings:**

| Setting | Value |
|---------|-------|
| Network connection | **NAT** (recommended) or **Bridged** |
| Connected | ✅ Checked |
| Connect at power on | ✅ Checked |

**NAT vs Bridged:**
- **NAT**: VMs share host's internet, get 192.168.x.x IPs from VMware
- **Bridged**: VMs get IPs from your router, appear as separate devices

4. **Click OK** → **Restart the VM**

---

## 🔧 Solution 2: Fix VM Network Configuration

### On Each VM:

```bash
# 1. Check network interface name
ip addr show
# Look for: ens33, eth0, or similar

# 2. Restart networking
sudo systemctl restart NetworkManager

# 3. Check if DHCP is working
sudo dhclient -v

# 4. Fix DNS
sudo nano /etc/resolv.conf
# Add these lines:
nameserver 8.8.8.8
nameserver 8.8.4.4

# 5. Make DNS permanent (Ubuntu 22.04)
sudo nano /etc/netplan/00-installer-config.yaml
# Add under 'dhcp4: true':
#   nameservers:
#     addresses: [8.8.8.8, 8.8.4.4]

# 6. Apply netplan
sudo netplan apply

# 7. Test
ping -c 3 google.com
```

---

## 🔧 Solution 3: VMware Virtual Network Editor (Windows)

### Reset VMware NAT Network:

1. **Open VMware Workstation**
2. **Edit** → **Virtual Network Editor**
3. **Click "Change Settings"** (requires admin)
4. **Select VMnet8** (NAT network)
5. **Click "Restore Defaults"**
6. **Click OK**
7. **Restart all VMs**

### Or Manually Configure VMnet8:

1. **Virtual Network Editor** → **VMnet8**
2. **Subnet IP**: `192.168.182.0`
3. **Subnet mask**: `255.255.255.0`
4. **NAT Settings**:
   - Gateway IP: `192.168.182.2`
5. **DHCP Settings**:
   - Start IP: `192.168.182.10`
   - End IP: `192.168.182.100`
6. **Apply** → **Restart VMs**

---

## 🔧 Solution 4: Windows Firewall

Sometimes Windows Firewall blocks VMware NAT:

1. **Windows Security** → **Firewall & network protection**
2. **Advanced settings**
3. **Inbound Rules** → Look for:
   - `VMware NAT Service`
   - Allow all VMware-related rules
4. **Outbound Rules** → Same check

---

## 🔧 Solution 5: VMware Services (Windows)

Restart VMware network services:

```powershell
# Run PowerShell as Administrator
net stop "VMware NAT Service"
net stop "VMware DHCP Service"
net start "VMware DHCP Service"
net start "VMware NAT Service"
```

---

## ✅ Verification Steps

After applying fixes:

```bash
# On each VM:
ping -c 3 8.8.8.8        # Test IP connectivity
ping -c 3 google.com     # Test DNS
wget -O- http://icanhazip.com  # Check public IP

# Test Docker
sudo docker pull hello-world

# Test apt
sudo apt-get update
```

---

## 🎯 Quick Fix Checklist

1. ✅ VMware VM Settings → Network Adapter → **NAT**
2. ✅ Connected + Connect at power on → **Checked**
3. ✅ Restart VM
4. ✅ On VM: `sudo systemctl restart NetworkManager`
5. ✅ Fix DNS: Add `8.8.8.8` to `/etc/resolv.conf`
6. ✅ Test: `ping google.com`

---

## 📞 If Still Not Working

**Check on Windows Host:**

```powershell
# Test if Windows host has internet
ping google.com

# Check VMware NAT device
ipconfig /all
# Look for "VMware Network Adapter VMnet8"
# Should have IP like 192.168.182.1
```

**If VMnet8 missing or disabled:**
- Virtual Network Editor → Restore Defaults
- Or reinstall VMware Workstation

---

## 🔄 Nuclear Option: Complete Reset

If nothing works:

1. **Shutdown all VMs**
2. **Virtual Network Editor** → **Restore Defaults**
3. **Each VM Settings** → Network → **NAT** → **OK**
4. **Start VMs**
5. **On each VM:**
   ```bash
   sudo dhclient -r  # Release IP
   sudo dhclient     # Get new IP
   ping google.com
   ```

---

## Expected Results

**Before Fix:**
```
ping: google.com: Temporary failure in name resolution
```

**After Fix:**
```
PING google.com (142.250.x.x) 56(84) bytes of data.
64 bytes from google.com: icmp_seq=1 ttl=117 time=15.2 ms
```

Then you can proceed with Kafka installation!

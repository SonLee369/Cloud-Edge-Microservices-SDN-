# ONOS Installation Troubleshooting

## Issue Identified
✗ Corrupted ONOS download (ZIP corruption error)

## Root Cause
The `onos-2.7.0.tar.gz` file was incomplete or corrupted during download, causing extraction errors.

## Solution

### Step 1: Clean Up Corrupted Files

On Master VM, run:
```bash
cd ~
rm -rf onos-2.7.0*
```

### Step 2: Use Fixed Installation Script

From WSL, transfer the fixed script:
```bash
scp D:/CloudProject/scripts/install_onos_fixed.sh lehuuson@192.168.182.10:~/
```

On Master VM:
```bash
chmod +x install_onos_fixed.sh
./install_onos_fixed.sh
```

## What the Fixed Script Does

1. **Cleans up** any previous corrupted downloads
2. **Downloads ONOS** with resume capability (`-c` flag)
3. **Verifies file size** before extraction
4. **Tests ONOS** with proper wait loops
5. **Activates required apps** for SDN functionality

## Alternative: Manual Installation

If the script still fails, try manual steps:

```bash
# Remove corrupted files
cd ~
rm -rf onos-2.7.0*

# Download with multiple retries
wget --tries=5 --continue https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.7.0/onos-2.7.0.tar.gz

# Verify file integrity
ls -lh onos-2.7.0.tar.gz
# Should be ~384MB

# If still corrupted, try different mirror
wget https://archive.apache.org/dist/onos/2.7.0/onos-2.7.0.tar.gz

# Extract
tar -xzf onos-2.7.0.tar.gz
cd onos-2.7.0

# Start ONOS
./bin/onos-service start

# Wait 90 seconds
sleep 90

# Test
curl -u onos:rocks http://localhost:8181/onos/v1/applications
```

## Expected Output

After successful installation:
```
✓ ONOS REST API is responding
→ Active ONOS applications:
  "name":"org.onosproject.openflow","state":"ACTIVE"
  "name":"org.onosproject.fwd","state":"ACTIVE"
```

## If Problems Persist

Check ONOS logs:
```bash
tail -100 ~/onos-2.7.0/apache-karaf-*/data/log/karaf.log
```

Check Java heap space:
```bash
free -h
# If < 2GB available, increase VM1 RAM to 5GB
```

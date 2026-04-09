# Installing ONOS via Docker on Master VM

## Why Docker?

Using Docker for ONOS is **much better** because:
- ✅ No corrupted JAR files (pre-built images)
- ✅ Easy to restart/reset
- ✅ Isolated from host system
- ✅ Official ONOS images are tested and stable

---

## Step 1: Install Docker (10 min)

Transfer and run the Docker installation script:

```bash
# From WSL
scp /mnt/d/CloudProject/scripts/install_docker.sh lehuuson@192.168.182.10:~/

# On Master VM
ssh lehuuson@192.168.182.10
chmod +x install_docker.sh
./install_docker.sh
```

**After installation completes:**

```bash
# Log out and log back in for group changes
exit

# SSH back in
ssh lehuuson@192.168.182.10

# Verify Docker works without sudo
docker run hello-world
```

---

## Step 2: Run ONOS in Docker (5 min)

```bash
# From WSL
scp /mnt/d/CloudProject/scripts/run_onos_docker.sh lehuuson@192.168.182.10:~/

# On Master VM
ssh lehuuson@192.168.182.10
chmod +x run_onos_docker.sh
./run_onos_docker.sh
```

**This will:**
1. Clean up old corrupted ONOS installation
2. Pull official ONOS 2.5.1 Docker image
3. Start ONOS container
4. Activate OpenFlow apps
5. Verify ONOS is running

---

## Step 3: Verify ONOS

```bash
# Check ONOS status
curl -u onos:rocks http://localhost:8181/onos/v1/applications

# View logs
docker logs onos

# Enter container
docker exec -it onos bash
```

**Expected output:**
```json
{
  "applications": [
    {
      "name": "org.onosproject.optical-model",
      "state": "ACTIVE",
      ...
    }
  ]
}
```

---

## Managing ONOS Container

```bash
# Stop ONOS
docker stop onos

# Start ONOS
docker start onos

# Restart ONOS
docker restart onos

# View real-time logs
docker logs -f onos

# Remove container (to start fresh)
docker stop onos && docker rm onos
# Then re-run run_onos_docker.sh
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker permission denied | Log out and back in after install |
| Port 8181 already in use | `sudo fuser -k 8181/tcp` |
| Container won't start | Check logs: `docker logs onos` |
| Can't connect to REST API | Wait 2 more minutes for initialization |

---

## Next Steps

✅ After ONOS Docker is running → **Phase 3 & 4**:
1. Complete OVS setup on Edge VM
2. Install Kafka on Cloud VM
3. Deploy AI inference
4. Run verification tests

Total time: ~15 minutes (vs hours of troubleshooting native ONOS!)

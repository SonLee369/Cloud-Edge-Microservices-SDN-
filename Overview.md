# Project Context: SDN-AI Smart Healthcare Research Backtesting

## 1. Research Objective
Backtesting the implementation of the paper: *"A Cloud-Edge Microservices Architecture for Smart Healthcare: SDN-Based Medical Asset Management"*.
**Core Goal:** Integrate SDN (ONOS) and Edge-AI (Autoencoders) to detect medical device anomalies and automate network security enforcement via OpenFlow.

## 2. Environment Constraints (Lê Hữu Sơn's Setup)
* **Host OS:** Windows 10 (16GB RAM) / CPU: i7 6700HQ / GPU: NVIDIA Quadro M1000M.
* **Interface:** WSL2 connecting to 3 Ubuntu VMs via SSH.
* **Resource Management:** Extremely tight RAM. Use lightweight tools (K3s, KRaft) and avoid heavy UI/Desktop environments.

## 3. Network Topology & VM Roles
| VM Node | IP Address | Specs | Primary Software Stack |
| :--- | :--- | :--- | :--- |
| **VM 1 (Master)** | `192.168.182.10` | 4GB / 2 vCPU | ONOS Controller, K3s Control Plane, REST API Server |
| **VM 2 (Cloud)** | `192.168.182.20` | 2GB / 1 vCPU | Kafka (KRaft mode), PostgreSQL, Backend Analytics |
| **VM 3 (Edge)** | `192.168.182.30` | 3GB / 2 vCPU | OVS (Open vSwitch), KubeEdge, AI Inference (Python/PyTorch) |

## 4. Implementation Roadmap for AI Agent
When assisting with code, follow this logic flow derived from the paper:

### Phase A: The SDN & Data Plane (Connectivity)
1.  **OVS Setup:** Configure Open vSwitch on VM 3.
2.  **Controller Handshake:** Connect OVS (VM 3) to the ONOS Controller (VM 1) using OpenFlow 1.3.
3.  **Validation:** Verify that ONOS sees the Edge switch via REST API.

### Phase B: Microservices & Telemetry
1.  **Cluster:** Initialize K3s on VM 1 and join VM 3 using KubeEdge (to handle edge-cloud synchronization).
2.  **Telemetry:** Create a Python-based "Ventilator Simulator" on VM 3 that sends MQTT/JSON data.
3.  **Streaming:** Set up a lightweight Kafka producer on VM 3 to stream data to the Cloud (VM 2).

### Phase C: AI & Security Loop (The "Brain")
1.  **Detection:** Implement a PyTorch Autoencoder on VM 3 to monitor telemetry. 
2.  **Alerting:** If `reconstruction_error > threshold`, trigger a security alert.
3.  **Enforcement:** Use a Python script to call the ONOS REST API (VM 1) to push a "Flow Drop" rule to OVS (VM 3) to isolate the "anomalous" device.

## 5. Performance Benchmarks to Match
Your code suggestions should aim to replicate these paper results:
* **AI Accuracy:** ~94.5% (Anomaly detection).
* **Inference Latency:** Target < 40ms (despite i7 6700HQ hardware).
* **Security Response:** 72% reduction in unauthorized traffic during `hping3` simulation.

## 6. Guidelines for the AI Agent
* **Use SSH:** All commands should be formatted for remote execution (e.g., `ssh lehuuson@192.168.182.x`).
* **Be Minimalist:** Prefer `K3s` over `K8s`, `KRaft` over `Zookeeper`, and `Alpine-based` Docker images to save RAM.
* **Network Paths:** Always use the `.10`, `.20`, and `.30` static IPs for configuration files.
* **No GUI:** Do not suggest tools requiring a GUI; everything must be CLI/API based.


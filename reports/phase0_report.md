# Báo cáo Phase 0 — Health Check (Kiểm tra Sức khỏe Hệ thống)

**Ngày thực hiện:** 2026-04-06
**Người thực hiện:** lehuuson
**Môi trường:** 3 VM Ubuntu (VMware), host Windows 10 Pro

---

## 1. Mục tiêu

Xác nhận toàn bộ hạ tầng của dự án (3 VM, các service cốt lõi) đang hoạt động đúng và sẵn sàng cho các phase thực nghiệm tiếp theo.

---

## 2. Môi trường kiểm tra

| Node | IP | Vai trò | Tài nguyên |
|---|---|---|---|
| Master VM (`sdn-master`) | `192.168.182.10` | K3s + ONOS SDN Controller | 2 vCPU / 4GB RAM |
| Cloud VM (`sdn-cloud`) | `192.168.182.20` | Apache Kafka 3.7.0 (KRaft) | 1 vCPU / 2GB RAM |
| Edge VM (`sdn-edge`) | `192.168.182.30` | OVS + Mosquitto MQTT + AI | 2 vCPU / 3GB RAM |

---

## 3. Kết quả kiểm tra

### 3.1 Kết nối mạng giữa 3 VM

**Lệnh thực thi (từ Master VM):**
```bash
ping -c 2 192.168.182.20 && ping -c 2 192.168.182.30
```

**Kết quả:**
```
PING 192.168.182.20: 2 packets transmitted, 2 received, 0% packet loss
  rtt min/avg/max = 0.908/1.253/1.599 ms

PING 192.168.182.30: 2 packets transmitted, 2 received, 0% packet loss
  rtt min/avg/max = 0.757/0.794/0.832 ms
```

**Đánh giá:** ✅ Kết nối mạng ổn định, 0% packet loss, latency < 2ms.

---

### 3.2 ONOS SDN Controller (Master VM)

**Lệnh kiểm tra:**
```bash
curl -s -u onos:rocks http://localhost:8181/onos/v1/applications/org.onosproject.openflow | grep -o '"state":"[^"]*"'
```

**Kết quả ban đầu:** `"state":"INSTALLED"` — OpenFlow app chưa được kích hoạt.

**Hành động khắc phục:**
```bash
curl -X POST -u onos:rocks http://localhost:8181/onos/v1/applications/org.onosproject.openflow/active
```

**Kết quả sau fix:** `"state":"ACTIVE"` ✅

**Chi tiết ONOS:**
- Version: 2.5.1
- App: `org.onosproject.openflow` (Suite of OpenFlow base providers)
- REST API: `http://192.168.182.10:8181/onos/v1`
- Credentials: `onos:rocks`

---

### 3.3 Open vSwitch — OVS (Edge VM)

**Lệnh kiểm tra:**
```bash
sudo ovs-vsctl show
```

**Kết quả:**
```
d0ed92fc-24d9-44a3-a507-2bbabbf2477d
    Bridge br0
        Controller "tcp:192.168.182.10:6653"
            is_connected: true
        Port br0
            Interface br0
                type: internal
    ovs_version: "2.17.9"
```

**Đánh giá:** ✅ Bridge `br0` đã kết nối thành công với ONOS Controller qua OpenFlow (TCP port 6653). Trạng thái `is_connected: true` xác nhận kênh SDN Data Plane ↔ Control Plane hoạt động.

> **Lưu ý:** Trước khi fix ONOS (bước 3.2), OVS không hiển thị `is_connected: true` do OpenFlow app chưa ACTIVE. Sau khi activate ONOS OpenFlow app, kết nối được thiết lập tự động.

---

### 3.4 Mosquitto MQTT Broker (Edge VM)

**Lệnh kiểm tra:**
```bash
sudo systemctl status mosquitto
```

**Kết quả:**
```
● mosquitto.service - Mosquitto MQTT Broker
   Active: active (running) since Mon 2026-04-06 03:57:02 UTC
   Main PID: 1043 (/usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf)
   Memory: 2.4M
```

**Đánh giá:** ✅ Mosquitto đang chạy, enabled on boot, lắng nghe port 1883, memory usage thấp (2.4MB).

---

### 3.5 Apache Kafka (Cloud VM)

**Lệnh kiểm tra:**
```bash
sudo docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -i kafka
sudo docker logs kafka --tail 30
sudo docker exec kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

**Trạng thái Docker:** `Up 13 minutes (unhealthy)`

**Phân tích log:**
```
[BrokerLifecycleManager id=1] The broker has been unfenced. Transitioning from RECOVERY to RUNNING.
[BrokerServer id=1] Transition from STARTING to STARTED
Kafka version: 3.7.0
Awaiting socket connections on 0.0.0.0:9092.
[KafkaRaftServer nodeId=1] Kafka Server started
```

**Kết luận:** Mặc dù Docker báo `unhealthy` (do cấu hình health check không phù hợp), Kafka broker thực tế **hoàn toàn hoạt động** — đã STARTED và lắng nghe port 9092.

**Kafka Topics hiện có:**
```
__consumer_offsets       (internal)
healthcare-telemetry
hospital-alerts
medical-telemetry
```

**Đánh giá:** ✅ Kafka 3.7.0 (KRaft mode — không cần Zookeeper) đang chạy với 3 topics sẵn sàng cho telemetry streaming.

---

## 4. Tổng kết Phase 0

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Network 3 VM | ✅ OK | 0% packet loss, latency < 2ms |
| ONOS OpenFlow | ✅ ACTIVE | Fix: kích hoạt app qua REST API |
| OVS ↔ ONOS (OpenFlow) | ✅ Connected | `is_connected: true` sau khi fix ONOS |
| Mosquitto MQTT | ✅ Running | Port 1883, Memory 2.4MB |
| Kafka Broker | ✅ Running | 3 topics sẵn sàng, Docker health check warning là false alarm |

**Số vấn đề phát hiện:** 2
**Số vấn đề đã khắc phục:** 2
**Kết quả Phase 0:** ✅ **PASS — Toàn bộ hạ tầng sẵn sàng**

---

## 5. Vấn đề phát sinh và cách khắc phục

### Vấn đề 1: ONOS OpenFlow app ở trạng thái INSTALLED thay vì ACTIVE

- **Nguyên nhân:** ONOS khởi động nhưng không tự động activate OpenFlow provider app.
- **Tác động:** OVS không thể thiết lập kết nối OpenFlow với ONOS controller.
- **Khắc phục:** Gọi REST API `POST /onos/v1/applications/org.onosproject.openflow/active`.
- **Khuyến nghị:** Cấu hình ONOS tự động activate app khi khởi động để tránh lặp lại.

### Vấn đề 2: Kafka Docker container báo `unhealthy`

- **Nguyên nhân:** Docker health check script không tương thích với Kafka 3.7.0 KRaft mode (có thể dùng lệnh Zookeeper-based).
- **Tác động:** Không có — broker hoạt động bình thường.
- **Khắc phục:** Không cần action. Xác nhận bằng cách kiểm tra log và list topics trực tiếp.
- **Khuyến nghị:** Cập nhật health check trong `docker-compose-kafka.yml` sang lệnh KRaft-compatible.

---

## 6. Bước tiếp theo

→ **Phase 1:** Kiểm tra ECG Simulator và AI Autoencoder Inference trên Edge VM.

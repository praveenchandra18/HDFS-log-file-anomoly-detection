# Hadoop Log Anomaly Detection

An end-to-end **Machine Learning system** for detecting failures in **Hadoop logs**, built, containerized, and deployed on **AWS EC2**.

---

## Problem

Hadoop clusters generate large volumes of logs.  
Manually identifying failures such as **machine down**, **network disconnection**, or **disk full** is slow and error-prone.

**Goal:** Automatically classify raw log lines into failure categories.

---

## Data

- Applications: **WordCount**, **PageRank**
- Each application executed multiple times under:
  - Normal
  - Machine Down
  - Network Disconnection
  - Disk Full
- All executions under the same application ID share the same label.

---

## Modeling Approach

### Random Forest (Baseline)
- Manual feature extraction
- Fast and interpretable
- Limited for sequential log patterns

### Neural Network (Final Model)
- Character-level text representation
- Learns directly from raw logs
- Better generalization and accuracy

**Final Choice:** Neural Network  
Reason: Superior performance on unstructured log text.

---

## Inference Pipeline

```
Raw Log → Text Vectorization → Neural Network → Failure Class
```

---

## REST API (Flask)

### Health Check
```
GET /health
```

### Predict
```
POST /predict
```

**Request**
```json
{ "log": "ERROR Disk full on /dev/sda1" }
```

**Response**
```json
{
  "confidence": 0.5891,
  "prediction": "Machine down"
}
```

## Docker
- Inference service packaged as a Docker container
- Model and preprocessing artifacts baked into the image
- Auto-restart enabled for reliability

---

## AWS EC2 Deployment

- Instance: `t2.micro` (Amazon Linux)
- Docker enabled via `systemctl`
- Ports opened: 22 (SSH), 5000 (API)

---

## Key Takeaways

- Compared classical ML vs deep learning
- Neural networks handle unstructured logs better
- Docker ensures reproducibility
- EC2 provides a minimal production setup

---

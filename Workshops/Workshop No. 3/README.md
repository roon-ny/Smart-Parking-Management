
# 🅿️ Smart Campus Parking Management System (SCPMS)
### Workshop No. 3 — Robust System Design & Project Management
**Systems Analysis & Design | Computer Engineering | Universidad Distrital Francisco José de Caldas | Semester 2026-I**

---

## 👥 Team

| Name | Student ID | Role |
|------|-----------|------|
| Kevin Zambrano Matiz | 20251020118 | Technical Coordinator |
| Dilan Santiago Herreño Cifuentes | 20251020117 | Backend Developer 1 |
| Ronaldo Andrés Alvarado Doria | 20251020122 | Backend Developer 2 |
| Esteban Josué Varela Sarmiento | 20251020114 | Server & Testing Lead |

---

## 📋 Overview

SCPMS is a digital reservation platform for Basement 3 motorcycle parking at Universidad Distrital. The system addresses three root causes identified in Workshop 1: **information asymmetry**, **spatial disorder**, and **absence of prioritisation** — without any physical construction in Phases 1–3.

Workshop 3 builds on the W2 architecture by adding:
- Fault-tolerant architecture (circuit-breaker, LWW sync, Redis Sentinel)
- ISO 9001 / ISO 25010 / IEEE 830 quality alignment
- PMBOK 7th + ISO 31000 risk management (RPN-scored register)
- Full project charter, milestone timeline, and resource plan

---

## 🏗️ Architecture

The system is structured in four layers:

```
Presentation Layer   →   Mobile App (Flutter) + Security Dashboard + Map Visualization
Business Logic       →   Parking Control Server + Security Alert Subsystem + Overflow Advisory
Data Layer           →   PostgreSQL + Redis Cache + Audit Module
Integration Layer    →   API Gateway + UD SSO (OAuth 2.0) + IoT Nodes (Phase 4)
```

**Key robustness mechanisms:**
- Circuit-breaker on REST gateway — last valid auth token honoured up to 30 min during SSO outage
- Last-Write-Wins timestamped sync for offline conflict resolution
- Redis Sentinel failover with DB fallback and staleness flag in UI
- Write-once append log for the Security Alert Subsystem (ISO 27001)

---

## ⚠️ Risk Summary (PMBOK / ISO 31000)

RPN = Probability (1–5) × Impact (1–5). Critical ≥ 15.

| Risk | RPN | Category |
|------|-----|----------|
| No accessible API for Academic Schedule DB | **20 ★** | Technical |
| IT department delays server authorization | **15 ★** | Project Mgmt |
| Concurrent reservation race condition | **15 ★** | Technical |
| Low student adoption | **15 ★** | Operational |
| Unauthorized access to reservation data | 10 | Security |

---

## ✅ Quality Gates

| Gate | Transition | Key Criteria |
|------|-----------|-------------|
| Gate 1 | Phase 1 → 2 | Unit tests pass; OAuth with UD SSO succeeds |
| Gate 2 | Phase 2 → 3 | P95 latency < 2 s; UAT ≥ 90% task completion |
| Gate 3 | Phase 3 → 4 | Zero critical OWASP findings; FCM alert < 5 s |
| Gate 4 | Phase 4 → Production | Sensor accuracy ≥ 95%; University Management approval |

---

## 🗓️ Timeline (20 Weeks)

| Phase | Weeks | Milestone |
|-------|-------|-----------|
| 1 — Foundations | 1–4 | Student logs in and sees slot list (UD OAuth + PostgreSQL) |
| 2 — Working App | 5–10 | Full reservation flow live; map update < 3 s; load test passed |
| 3 — Control & Alerts | 11–14 | Violation alert < 5 s; mandatory rollout; OWASP audit |
| 4 — Physical Sensors | 15–20 | ESP32 sensors live; auto-detection ≥ 95% accuracy |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Mobile App | Flutter (Android / iOS) |
| Backend | Node.js + NestJS (microservices) |
| Database | PostgreSQL + Redis |
| Real-time | WebSockets |
| Push Notifications | Firebase Cloud Messaging |
| Authentication | OAuth 2.0 — UD SSO |
| IoT (Phase 4) | ESP32 + ultrasonic sensors via MQTT/TLS |
| CI/CD & Testing | GitHub Actions + Jest + k6 |
---

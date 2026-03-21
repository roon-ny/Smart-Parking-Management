# Smart Campus Parking Management System (SCPMS)
### Systems Analysis & Design — Workshop No. 2 | Universidad Distrital Francisco José de Caldas
### Computer Engineering Program — Semester 2026-I

---

## Authors

| Name | Student ID |
|---|---|
| Kevin Zambrano Matiz | 20251020118 |
| Dilan Santiago Herreño Cifuentes | 20251020117 |
| Ronaldo Andrés Alvarado Doria | 20251020122 |
| Esteban Josué Varela Sarmiento | 20251020114 |

---

## Overview

This repository contains the **System Design Document** for the Smart Campus Parking Management System (SCPMS), a proposed digital solution for the motorcycle parking facility at **Basement 3 of Universidad Distrital Francisco José de Caldas**.

The design addresses three root causes of operational inefficiency identified in Workshop #1:

- **Information asymmetry** — users cannot verify slot availability before arriving.
- **Spatial disorder** — car-painted markings cause a single motorcycle to occupy up to three spaces.
- **Absence of prioritisation** — no mechanism aligns occupancy with academic schedules.

The proposed solution is a **software-first, phased platform** integrated into the university's existing mobile application, with an optional IoT layer introduced in Phase 4.

---

## System Objectives

1. **Operational Optimisation** — Reduce average check-in time to under 3 minutes.
2. **Inventory Efficiency** — Increase effective space utilisation by at least 20% through dynamic slot state management (`FREE / RESERVED / OCCUPIED`).
3. **Regulatory Compliance** — Ensure 100% adherence to Colombian Law 1581 of 2012 (Habeas Data) through anonymisation and automatic purge protocols.
4. **Behavioural Control** — Implement an automatic sanctions mechanism triggered by reservation violations.

---

## Architecture

SCPMS is structured as a modular extension of the university's mobile application. It comprises **five core modules**:

| Module | Responsibility |
|---|---|
| **Reservation & Availability** | Real-time numbered slot map (binary status); slot booking interface |
| **Time-Slot Scheduling Engine** | Academic time-block binding; duplication prevention; automatic priority handoff |
| **User Account Integration** | University credential linkage; plate-to-user attribution; reservation traceability |
| **Security Alert Subsystem** | Violation detection; FCM push notifications to security staff; infraction logging |
| **External Overflow Advisory Module** | Idle reservation detection; overflow guidance for external users |

Three external systems are federated: the **Identity Management System**, the **Academic Schedule Database**, and the **Campus Security Communication Infrastructure**.

All data is stored exclusively on university servers — no external cloud services — in compliance with Law 1581 of 2012.

---

## Technology Stack

| Component | Technology |
|---|---|
| Mobile App | Flutter (Android / iOS) |
| Interactive Slot Map | Dynamic SVG (in-app) |
| Backend / Business Logic | Node.js + NestJS |
| Database | PostgreSQL |
| Live Updates | WebSockets + Redis |
| Push Notifications | Firebase Cloud Messaging (FCM) |
| Physical Sensors (Phase 4) | ESP32 + Ultrasonic Sensor |

---

## Implementation Phases

The system follows a **phased delivery model** where each phase is independently deployable and produces immediate value.

| Phase | Duration | Key Deliverables | Success Criterion |
|---|---|---|---|
| **Phase 1 — Foundations** | Weeks 1–4 | UD SSO integration; PostgreSQL schema; first app screens | Student logs in with UD credentials and sees the slot list |
| **Phase 2 — Working App** | Weeks 5–10 | Live slot map; full reservation flow; TTL auto-release; FCM reminders | Reservation completed in < 3 min; map updates in < 3 s |
| **Phase 3 — Control & Alerts** | Weeks 11–14 | Security staff panel; violation alerts; duplicate prevention; infraction logging | Violation triggers guard alert in < 5 s |
| **Phase 4 — Physical Sensors** | Weeks 15–20 | ESP32 sensors per slot; automated occupancy detection; analytics dashboard | Sensor accuracy ≥ 95%; parking search time reduced ≥ 40% |

---

## Key Performance Indicators

- Slot availability query latency: **< 2 s** (95th percentile)
- Check-in transaction time: **< 3 min** end-to-end
- Slot map update delay: **< 3 s** after status change
- Space utilisation improvement: **≥ 20%** over baseline
- Security alert dispatch time: **< 5 s** after violation trigger
- System availability: **≥ 99%** during operating hours (06:00–22:00)
- Sensor detection accuracy (Phase 4): **≥ 95%**

---

## Engineering Principles

- **Modularity** — Each module has a single, well-defined responsibility; changes to one module do not cascade to others.
- **Scalability** — The PostgreSQL schema and NestJS microservice structure support new parking areas through configuration extension, not core rewrites.
- **Reliability** — Offline contingency mode, transactional locks for concurrent reservations, and Redis-based state caching reduce single points of failure.
- **Compliance-by-design** — Data minimisation, server-side encryption, and automatic purge protocols are architectural decisions built into the system from the outset.

---

## Compliance

All personally identifiable information (vehicle plates, reservation history, campus location data) is processed and stored exclusively on university-owned infrastructure in accordance with **Colombian Law 1581 of 2012 (Habeas Data)**. No data is transmitted to external processors.

---

## Document Structure

```
WORKSHOP2.pdf
├── 1. Analysis Review and Requirements Definition
│   ├── 1.1 Critical Constraints
│   ├── 1.2 Performance Bottlenecks
│   ├── 1.3 Optimisation Opportunities
│   ├── 1.4 Measurable Design Requirements
│   └── 1.5 Stakeholder Needs and System Objectives
├── 2. System Architecture
│   ├── 2.1 High-Level Architecture
│   ├── 2.2 Core Module Responsibilities
│   ├── 2.3 Interface & Integration Diagram
│   ├── 2.4 Process Flow
│   └── 2.5 Systems Engineering Principles Applied
├── 3. Technical Implementation Strategy
│   ├── 3.1 Technology Stack
│   ├── 3.2 Implementation Phases
│   ├── 3.3 University System Integration
│   └── 3.4 Required Team
├── 4. Risk and Complexity Management
│   ├── 4.1 Technical Risks
│   ├── 4.2 Organisational Risks
│   └── 4.3 Complexity Management Strategies
├── 5. Performance and Quality Assurance
│   ├── 5.1 Key Performance Indicators
│   ├── 5.2 Monitoring Strategy
│   ├── 5.3 Validation and Testing Plan
│   └── 5.4 Continuous Improvement
└── 6. Conclusions and Next Steps
    ├── 6.1 Key Design Decisions
    ├── 6.2 Objective Achievement Assessment
    ├── 6.3 Implementation Roadmap
    ├── 6.4 Recommendations for Future Development
    └── 6.5 Final Remarks
```

---

## Immediate Next Steps

The system is ready to proceed to **Phase 1** upon completion of the initial IT department coordination meeting to establish OAuth integration scope and server provisioning agreements.

---

*Bogotá, D.C. — 2026*

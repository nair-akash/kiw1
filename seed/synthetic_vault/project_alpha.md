# Project Alpha — Architecture & Roadmap

## Overview
Project Alpha is a high-reliability distributed telemetry ingestion engine designed for cloud-native workloads.

## Key Decisions
- Boundary Isolation: All external ingestion passes through strict validation proxies.
- Zero-token verification: Data schemas are validated deterministically in Python.
- Storage: Partitioned time-series tables with 30-day retention policies.

## Milestones
- M1: Prototype kernel and core plugin contracts (Completed).
- M2: Telemetry trace collector with per-step latency and cost accounting (In Progress).
- M3: Multi-region rollout with automated failover.

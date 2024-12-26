# High-Performance Rate Limiter (REST, Websocket, Simulated Trades) for Binance and Bybit API
![ezgif-1-069aba7d29](https://github.com/user-attachments/assets/8d8c3a38-745b-4093-a87b-b65a984843bf)

## Overview
This project demonstrates a **high-throughput data collection system** designed for **algorithmic trading** and **high-frequency trading (HFT)** scenarios. It incorporates three distinct mechanisms for gathering market data from Binance and Bybit:

1. **REST API Fetchers**: Implements rate-limited requests for Binance and Bybit to ensure compliance with exchange restrictions while maximizing throughput.
2. **WebSocket Streams**: Leverages real-time data streaming from Binance and Bybit for low-latency market data updates.
3. **Simulated Trades**: Creates an artificial environment to stress-test the system with thousands of trades per second, mimicking HFT conditions.

## Features
### 1. REST API Fetchers
- **Rate Limiting**:
  - Built using an asynchronous rate limiter to enforce exchange-specific constraints.
  - Configured via a `rate_limits.json` file, ensuring up to 1200 requests/second compliance.
- **Batching and Concurrency**:
  - Optimized for high throughput with adjustable batch sizes and concurrency controls.
- **Metrics**:
  - Tracks latency, call metrics, and API response performance.

### 2. WebSocket Streams
- **Real-Time Updates**:
  - Streams live market data from Binance and Bybit using WebSocket connections.
- **Low Latency**:
  - Designed for sub-millisecond data delivery, crucial for HFT applications.
- **Dynamic Dashboard**:
  - Provides a real-time view of market data, call metrics, and system performance.

### 3. Simulated Trades
- **HFT Scalability Testing**:
  - Generates synthetic trade data at thousands of updates per second to simulate extreme trading conditions.
- **Stress Testing**:
  - Evaluates system scalability under high-load scenarios.
- **Integrated Metrics**:
  - Tracks synthetic trade performance alongside real exchange data.

## Use Cases
- **Algorithmic Trading**:
  - Enables the development of trading strategies by efficiently fetching historical and real-time market data.
- **High-Frequency Trading (HFT)**:
  - Tests system readiness for handling massive volumes of trades and updates with low latency.
- **Performance Monitoring**:
  - Visualizes key performance metrics (e.g., latency, throughput) via a dynamic dashboard.

## Architecture
- **Core Components**:
  - **Rate Limiter**: Manages API call frequencies for REST endpoints.
  - **WebSocket Handlers**: Processes real-time updates with asynchronous message handling.
  - **Simulated Environment**: Generates high-frequency synthetic trade data.
- **Dynamic Dashboard**:
  - Displays aggregated metrics, such as:
    - Call throughput (real + simulated).
    - Latency and rate-limit compliance.
    - Real-time price aggregation.

## Exchanges Supported
- **Binance**:
  - REST API: Historical and real-time data.
  - WebSocket: Low-latency streaming of market updates.
- **Bybit**:
  - REST API: Historical and real-time data.
  - WebSocket: Low-latency streaming of market updates.

## Key Metrics Tracked
- **REST API Metrics**:
  - Total calls, allowed calls, throttled calls, and average/max latency.
- **WebSocket Metrics**:
  - Streaming rates, connection health, and data latency.
- **Simulated Trades Metrics**:
  - Throughput, price aggregation, and synthetic latency.

## Conclusion
This project is a comprehensive solution for collecting and analyzing market data from Binance and Bybit. It bridges the gap between REST and WebSocket paradigms while incorporating simulated trades for scalability testing, making it ideal for algorithmic trading and HFT professionals.

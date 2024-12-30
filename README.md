# High-Frequency Trading Simulation and Rate Limiting Dashboard
![ezgif-3-1236e33076](https://github.com/user-attachments/assets/f8ccf4e7-55cf-4891-9db7-adc9c96e1bff)

## Overview  
A platform for **algorithmic trading** and **high-frequency trading (HFT)** simulations, integrating **Binance** and **Bybit APIs** for rate-limiting compliance and synthetic trade generation. It features robust API interaction, stress testing, and real-time performance monitoring through an interactive dashboard.

---

## Features  
- **Simulated Trades**:  
  - Mimics HFT environments by generating thousands of trades per second.  
  - Tracks metrics such as latency, trade volume, and price aggregation.  
  - Stress-tests system scalability under extreme load.  

- **Rate Limiter**:  
  - Enforces Binance and Bybit API constraints using a deque-based mechanism.  
  - Tracks API call rates, latency, and throttled requests.  

- **WebSocket Streams**:  
  - Streams real-time market data from Binance and Bybit.  
  - Monitors connection stability, latency, and streaming rates.  

- **Dynamic Dashboard**:  
  - Visualizes simulated trade metrics, rate limits, and API compliance in real time.  
  - Provides controls to start, reset, and monitor simulations interactively.

---

## Key Metrics  
- **Simulated Trades**: Total trades, latency (average and max), aggregated price data.  
- **Rate Limiting**: API call throughput, throttling, and latency.  
- **WebSocket Streams**: Streaming rates and connection health.  

---

## Supported Exchanges  
- **Binance**: REST API and WebSocket for real-time market data.  
- **Bybit**: REST API and WebSocket for live market updates.

---

## Conclusion  
This platform bridges **HFT simulation** and **rate limiting compliance**, making it an ideal tool for evaluating system performance, testing trading strategies, and ensuring API usage efficiency. Its dynamic dashboard offers real-time insights for stress testing and optimization.

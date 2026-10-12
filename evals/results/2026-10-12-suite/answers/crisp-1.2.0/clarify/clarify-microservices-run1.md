Bottom line: Microservices let teams deploy and scale each service alone, but they add operational complexity, so a team of fewer than ten engineers is often better off starting with a modular monolith.

**Benefits**
- Each service can be deployed, scaled, and updated independently of the others.
- This gives greater scalability and resilience.
- It helps teams that need to ship frequently.

**Costs**
- Microservices can add significant operational complexity.
- You need service discovery.
- You need distributed tracing to debug requests that cross several services.
- You need a strategy for data consistency. Each service typically owns its own database. You can no longer rely on a single ACID transaction across the whole system.
- Network calls between services add latency and new failure modes. Timeouts and retries become essential.

**Recommendation**
- For a team of fewer than ten engineers, a well-structured modular monolith is often the more pragmatic starting point.

Terms:
- Microservices: an architecture where an application is split into small services that run separately.
- Service discovery: a way for services to find each other on the network.
- Distributed tracing: tracking one request as it passes through many services.
- Data consistency: all copies of the data agree with each other.
- ACID transaction: a database operation that fully succeeds or fully fails.
- Modular monolith: one deployable application, split into well-separated internal modules.

Not clear in the original:
- "Significant operational complexity" has no measure.
- "Greater scalability and resilience" has no numbers or comparison.
- "Often the more pragmatic" gives no evidence for how often.
- The threshold of fewer than ten engineers has no stated basis.

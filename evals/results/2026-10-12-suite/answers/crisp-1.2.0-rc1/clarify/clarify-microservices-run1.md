Bottom line: Microservices let teams deploy and scale each service alone, but they add operational work, so a team of fewer than ten engineers will often do better with a modular monolith first.

**Benefits**

Each service can be deployed, scaled, and updated independently of the others. This gives greater scalability and resilience. It helps teams that need to ship frequently.

**Costs**

Microservices can add significant operational complexity. You will need three things:
- Service discovery.
- Distributed tracing, to debug requests that cross several services.
- A strategy for data consistency.

Each service typically owns its own database. You can no longer rely on a single ACID transaction across the whole system.

Network calls between services add latency and new failure modes. Timeouts and retries become essential.

**Recommendation**

A team of fewer than ten engineers will often find a well-structured modular monolith the more pragmatic starting point.

Terms:
- Microservices: an architecture of many small services, each with one job.
- Service discovery: a way for services to find each other's network addresses.
- Distributed tracing: tracking one request as it passes through many services.
- Data consistency: all copies of the data agree with each other.
- ACID transaction: a database operation that fully succeeds or fully fails.
- Modular monolith: one deployable application with clear internal module boundaries.

Not clear in the original:
- "Significant operational complexity" has no measure of how much.
- "Often the more pragmatic" gives no evidence for the under-ten-engineers threshold.
- The original does not say how much scalability or resilience microservices add.

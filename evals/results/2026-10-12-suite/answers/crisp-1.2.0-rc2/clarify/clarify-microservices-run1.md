Bottom line: Microservices let you deploy and scale each service on its own, but they add operational complexity, so a team of fewer than ten engineers will often do better starting with a modular monolith.

Each service can be deployed, scaled, and updated independently of the others. This gives more scalability and resilience. It helps teams that need to ship frequently.

Microservices can also add significant operational complexity. You will need:

- Service discovery, so services can find each other.
- Distributed tracing, to debug requests that cross several services.
- A strategy for data consistency. Each service typically owns its own database. You can no longer rely on a single ACID transaction across the whole system.

Network calls between services add latency and new failure modes. Timeouts and retries become essential.

For a small team of fewer than ten engineers, a well-structured modular monolith is often the more pragmatic starting point.

Terms:
- Microservices: an app built as many small services that run separately.
- Service discovery: a way for services to locate each other on the network.
- Distributed tracing: following one request as it passes through many services.
- ACID transaction: a database update that fully succeeds or fully fails.
- Modular monolith: one deployable app with clear internal module boundaries.

Not clear in the original:
- "Significant" operational complexity has no measure.
- "Often the more pragmatic" has no evidence or criteria. The ten-engineer threshold is not explained.

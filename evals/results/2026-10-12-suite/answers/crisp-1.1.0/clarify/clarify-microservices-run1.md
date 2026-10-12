Bottom line: Microservices let teams deploy and scale each service on its own, but they add operational work, so a team of fewer than ten engineers will often do better with a modular monolith.

Microservices give you scalability and resilience. You can deploy, scale, and update each service independently. This matters most for teams that ship often.

Microservices also add significant operational complexity. You will need:

- Service discovery.
- Distributed tracing, to debug requests that cross several services.
- A strategy for data consistency.

Data consistency needs a strategy because each service usually owns its own database. You can no longer rely on a single ACID transaction across the whole system.

Network calls between services add latency and new failure modes. Because of this, timeouts and retries are essential.

If your team has fewer than ten engineers, start with a well-structured modular monolith. It is often the more practical choice.

Terms:
- Microservices: an architecture where an application is split into small, separate services.
- Service discovery: a way for services to find each other on the network.
- Distributed tracing: tracking one request as it passes through many services.
- ACID transaction: a database operation that fully succeeds or fully fails, as one unit.
- Modular monolith: one deployable application with clear internal modules.

Not clear in the original:
- "Significant operational complexity" has no measure of how much.
- "Often the more pragmatic starting point" has no evidence.
- The "fewer than ten engineers" limit has no stated reason.

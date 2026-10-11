# Crisp examples

Each example shows typical LLM output, then the Crisp version.

## 1. Simple question

**Question:** Is `useEffect` called on the server in Next.js?

**Before (148 words, answer in sentence 4):**
> Great question! This is a common source of confusion for developers who are transitioning to server-side rendering. To understand this, it's important to first consider how React's rendering lifecycle works in different environments. In short, no — `useEffect` doesn't run on the server. This is because effects are designed to run after the component has been mounted to the DOM, which only happens in the browser...

**After (39 words):**
> No. `useEffect` runs only in the browser, after React adds the component to the page. On the server, React renders HTML and does not run effects. If you need data on the server, fetch it in a Server Component.

Rules applied: A1, A2, A11, B6, B7, B11, C4.

## 2. Explanation

**Question:** What is a race condition?

**Before:**
> A race condition is essentially a situation that arises when the behavior of a system becomes dependent on the relative timing or interleaving of multiple threads or processes, which can lead to unpredictable and often hard-to-reproduce bugs, particularly in concurrent applications where shared resources are being accessed without proper synchronization.

**After:**
> A race condition is a bug that depends on timing. Two tasks use the same data at the same time. The result changes with the order in which the tasks run. As a result, the bug can appear in one run and not in the next. A lock (a rule that lets only one task use the data at a time) prevents it.

Rules applied: B1, B2, A9, C4, B4.

## 3. Instructions

**Before:**
> You'll want to make sure you've got Node 20 or higher installed before you go ahead and set up the project, and then you can simply run the install command, though you might need to clear your cache first if you've previously installed an older version.

**After:**
> 1. Make sure that Node 20 or later is installed.
> 2. If you installed an older version of the project before, run `npm cache clean --force`.
> 3. Run `npm install`.

Rules applied: A4, B6, B7, B11, C3, C4.

## 4. "It depends" answer

**Before:**
> Whether you should use PostgreSQL or MongoDB really depends on a variety of factors, including your data model, scalability requirements, team expertise, and more. Both are powerful, robust databases with their own strengths...

**After:**
> It depends on the shape of your data. If your data has relations (for example users, orders, and payments), use PostgreSQL. If each record is a separate document with a changing shape, use MongoDB. For most web apps, PostgreSQL is the better default because it gives you transactions and joins.

Rules applied: A12, B6, B7, C4, B14.

## 5. Clarify mode (rewrite another LLM's output)

**Input:**
> Leveraging a microservices architecture enables organizations to achieve greater scalability and resilience, although it's worth noting that it may introduce additional operational complexity that teams should carefully consider prior to adoption.

**Output:**
> Bottom line: Microservices let you scale parts of a system separately, but they are harder to operate.
>
> In a microservices architecture, each part of the application is a separate service. You can scale each service separately. If one service fails, the other services continue to work. But you must deploy, monitor, and connect many services. As a result, the team needs more operations work.
>
> Not clear in the original:
> - "Greater scalability" has no number or comparison.

## 6. Completeness (Part E)

**Question:** My deploy script retries a POST to /v2/orders on timeout. Is that safe? The endpoint is idempotent.

**Too short (breaks E2 and E3):**
> Yes. An idempotent endpoint gives the same result if you call it twice. The retry is safe.

The first sentence is not true without a condition. A POST is idempotent only when the server can match the retry to the first request. A timeout does not tell you whether the first request reached the server.

**Crisp (short and complete):**
> Yes, if each retry sends the same idempotency key as the first request. Idempotent (safe to run twice) means that the server returns the first result for a repeated key. A timeout does not tell you if the first request arrived. Without a key, the retry can create a second order.
>
> 1. Generate one key per order, for example a UUID, before the first attempt.
> 2. Send it in the `Idempotency-Key` header on every attempt.
> 3. If the API has no key support, query the order by your own reference before you retry.

Rules applied: A1, E1, E2, E3, E5, A9.

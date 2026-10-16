# Unfinished work and next steps

## 1. Real distributed orchestration is not implemented

### What remains unfinished
The repository demonstrates the core pipeline and run-state handling locally, but it does not yet include a full production orchestration layer such as Step Functions, ECS task orchestration, or queue-based fan-out.

### Proposed solution if more time were available
Use EventBridge Scheduler to trigger a worker task, push batches into SQS for downstream processing, and add Step Functions for durable orchestration and retry workflows. This would provide stronger operational recovery and more explicit state transitions for long-running jobs.

### How to validate it
- run the same export and sync flow with a scheduled trigger
- simulate transient failures and verify the orchestration resumes without losing the original export
- confirm the run manifest reaches terminal states and handles retries correctly

### Why it was not completed
This challenge emphasizes prioritization. The highest-risk engineering areas are rate-limit handling, retry policy, partial-failure semantics, and duplicate safety, and those were implemented first.

### Deliberate prioritization or implementation limitation?
Deliberate prioritization.

### Risk created by leaving it unfinished
The local implementation is still a single-process workflow; in production the workflow would need stronger operating boundaries and queueing to cope with larger scale and more complex failure modes.

### Rough priority
High

---

## 2. Full AWS deployment and Terraform validation were not executed

### What remains unfinished
The Terraform is included as infrastructure-as-code representation, but it has not been applied in a real AWS account in this environment.

### Proposed solution if more time were available
Provision the bucket, IAM roles, log group, and ECS or Batch resources in a dedicated dev/test account, then validate the deployment with `terraform plan` and `terraform apply`.

### How to validate it
- run `terraform init`, `terraform validate`, and `terraform plan`
- deploy to a sandbox AWS account
- verify the job writes to the export bucket and logs to CloudWatch

### Why it was not completed
This environment does not include live AWS credentials or a deployed account, so real cloud validation is intentionally out of scope for the local exercise.

### Deliberate prioritization or implementation limitation?
Deliberate prioritization.

### Risk created by leaving it unfinished
The Terraform is structurally representative but not cloud-validated, so there may be account-specific config changes required when moving to a real environment.

### Rough priority
High

---

## 3. Idempotency ledger is local and simple

### What remains unfinished
The dedupe rule is implemented in-process using a stable SKU key and run metadata, but it does not yet include a fully durable cross-run ledger for all historical accepted SKUs at enterprise scale.

### Proposed solution if more time were available
Persist an idempotency ledger to S3 or a database table keyed by SKU and warehouse destination. This would allow the system to detect duplicate sends across restarts or extended outage windows with greater confidence.

### How to validate it
- run the same export twice and confirm no duplicate sends occur
- test a partial failure followed by a retry and verify only unsent records are processed again

### Why it was not completed
The challenge explicitly allows assumptions and scoped implementation. The current ledger is sufficient to demonstrate the required behavior in the repo without designing a full enterprise data store.

### Deliberate prioritization or implementation limitation?
Deliberate prioritization.

### Risk created by leaving it unfinished
At very large scale or across long outage windows, a simple in-memory or local ledger may not be sufficient to guarantee global idempotency.

### Rough priority
Medium-high

---

## 4. No full production observability dashboard was built

### What remains unfinished
There are structured logs and run manifests, but no dashboards, alerts, or metric thresholds were implemented.

### Proposed solution if more time were available
Add CloudWatch dashboards for run duration, WMS rejection rate, API retry rate, and export lag. Add alarms for unusual failure spikes or delayed runs.

### How to validate it
- inspect CloudWatch metrics after a few local runs
- trigger synthetic failures and confirm the alarm logic behaves as expected

### Why it was not completed
The code focuses on correctness and architectural clarity, not a full enterprise monitoring stack.

### Deliberate prioritization or implementation limitation?
Deliberate prioritization.

### Risk created by leaving it unfinished
Operations would have less immediate signal for run performance degradation and rising rejection rates.

### Rough priority
Medium

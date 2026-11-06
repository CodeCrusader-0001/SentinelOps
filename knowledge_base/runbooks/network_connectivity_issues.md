# RUNBOOK: Network Connectivity and Partition Issues

## Identification
- Symptoms: `Connection reset by peer`, `No route to host`, high DNS lookup timeouts, TCP SYN retransmission spikes, inter-service HTTP 504.
- Severity: CRITICAL / HIGH

## Root Causes
1. CoreDNS / kube-dns failure or upstream recursive resolver throttling.
2. Security group / firewall rule modification dropping cross-subnet traffic.
3. Network interface queue exhaustion or dropped packets at virtual switch.
4. Transient cloud provider network partition or routing table misconfiguration.

## Investigation Steps
1. Verify DNS resolution from inside pod (`dig`, `nslookup`).
2. Run network path tracing (`traceroute`, `tcptraceroute`, `mtr`).
3. Check host network socket statistics (`ss -s`, `netstat -s`) for packet drops.
4. Validate VPC route tables, NAT gateway bandwidth, and ACL logs.

## Recommended Remediation Actions
1. Flush local DNS cache and restart local DNS stub resolver.
2. Switch network routing to redundant secondary gateway or alternate AZ.
3. Re-apply validated infrastructure security group rules.
4. Scale up NAT gateway bandwidth or adjust ephemeral port ranges.


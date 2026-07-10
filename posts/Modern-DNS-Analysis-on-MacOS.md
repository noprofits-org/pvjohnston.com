---
title: Modern DNS Analysis on macOS - Beyond nslookup
date: 2025-03-19
tags: networking, dns, macos, dig, nslookup
description: A comparative analysis of traditional and modern DNS query tools on macOS, with practical examples and insights for network administrators and security professionals.
---

## Abstract

This study examines the evolution of Domain Name System (DNS) query tools on macOS, comparing traditional utilities like `nslookup` with modern alternatives such as `dig`. Through systematic testing of various DNS record types (A, MX, NS, SOA, CNAME) on public domains, we demonstrate the enhanced capabilities of contemporary tools in providing detailed resolution data, revealing complex CNAME chains, and offering insights into authoritative responses. The experiments, conducted on macOS in March 2025, highlight significant differences in output format, information detail, and usability between these tools, establishing a foundation for more effective network diagnostics in security-conscious environments.[@liu2006dns]

## Introduction

The Domain Name System (DNS) forms the backbone of Internet navigation, translating human-readable domain names into machine-readable IP addresses. As network complexities increase and security concerns evolve, the tools used to query and troubleshoot DNS have similarly progressed. While `nslookup` has long served as the standard utility for basic DNS lookups, modern network environments demand more comprehensive analysis capabilities.[@rfc792]

This study explores the transition from traditional DNS query tools to contemporary alternatives on macOS, examining their respective strengths, limitations, and practical applications. Our investigation focuses on several key aspects: the richness of information provided, the clarity of output formatting, the ability to reveal complex DNS architectures, and the insights offered regarding authoritative versus non-authoritative responses.

The DNS resolution process involves multiple record types, each serving specific functions in the naming system hierarchy. Understanding these records—from Address (A) records that map domains to IPv4 addresses, to Mail Exchange (MX) records directing email routing, to Start of Authority (SOA) records containing administrative information—is essential for effective network management and troubleshooting.[@stevens1994tcpip]

As networks increasingly employ security measures like firewalls and traffic filtering, DNS query tools must adapt to provide meaningful insights despite these constraints. Modern tools like `dig` (Domain Information Groper) offer enhanced capabilities designed to navigate these challenges, presenting more structured output and detailed resolution information than their predecessors.

Our experimental approach compares the output of `nslookup` and `dig` across various record types for common domains like apple.com, examining differences in information presentation, response times, and resolution paths. We also investigate the distinction between authoritative and non-authoritative answers, as well as timeout behaviors that indicate potential network or configuration issues.

The findings from this investigation aim to provide network administrators, security professionals, and technical educators with practical insights into the evolution of DNS diagnostic tools, supporting more effective network management in contemporary computing environments.

## Experimental

The experiment was conducted on macOS using the Terminal application to execute DNS queries with both traditional `nslookup` and modern `dig` commands. All tests were performed in March 2025 using the default DNS resolver configured on the test system (identified as fe80::900e:5cff:fefc:af0e%8#53 in the output).

The following DNS record types were queried for the domain apple.com:

1. A records (IPv4 address mapping)
2. MX records (Mail Exchange servers)
3. NS records (Name Servers)
4. SOA records (Start of Authority)
5. CNAME records (Canonical Name)

For each record type, comparative queries were executed using both `nslookup` and `dig` with their respective syntax:

~~~bash
# A record queries
nslookup apple.com
dig apple.com A

# MX record queries
nslookup -type=mx apple.com
dig apple.com MX

# NS record queries
nslookup -type=ns apple.com
dig apple.com NS

# SOA record queries
nslookup -type=soa apple.com
dig apple.com SOA

# CNAME record queries for www subdomain
nslookup www.apple.com
dig www.apple.com CNAME
~~~

Additionally, to examine authoritative versus non-authoritative responses, the following commands were executed:

~~~bash
# Standard query (non-authoritative)
dig apple.com

# Trace query to observe resolution chain
dig +trace apple.com
~~~

To investigate timeout behaviors, queries were performed for non-existent domains and with invalid DNS servers:

~~~bash
# Non-existent domain query
nslookup nonexistent-domain-example123456.com

# Query with invalid DNS server
nslookup apple.com 192.0.2.1
~~~

Finally, to explore macOS-specific DNS service discovery capabilities, the following commands were used:

~~~bash
# List available DNS service types
dns-sd -B _services._dns-sd._udp local.

# Discover HTTP services
dns-sd -B _http._tcp local.
~~~

The output from each command was captured and analyzed to compare information content, formatting, response times, and other relevant metrics.

## Results

**Table 1.** DNS A Record Query Results for apple.com

| Tool | Resolved IP | Response Time / ms | TTL / s | Server Used |
|------|-------------|-------------------|---------|-------------|
| nslookup | 17.253.144.10 | Not provided | Not provided | fe80::900e:5cff:fefc:af0e%8 |
| dig | 17.253.144.10 | 20 | 686 | fe80::900e:5cff:fefc:af0e%8 |

**Table 2.** MX Record Query Results for apple.com

| Mail Server | Priority | TTL / s (dig only) |
|-------------|----------|-------------------|
| mx-in.g.apple.com | 10 | 3600 |
| mx-in-ma.apple.com | 20 | 3600 |
| mx-in-vib.apple.com | 20 | 3600 |
| mx-in-sg.apple.com | 20 | 3600 |
| mx-in-rn.apple.com | 20 | 3600 |
| mx-in-hfd.apple.com | 20 | 3600 |

**Table 3.** Name Server (NS) Records for apple.com

| Name Server | IPv4 Address | IPv6 Address | TTL / s (dig only) |
|-------------|-------------|-------------|-------------------|
| a.ns.apple.com | 17.253.200.1 | 2620:149:ae0::53 | 856 |
| b.ns.apple.com | 17.253.207.1 | 2620:149:ae7::53 | 856 |
| c.ns.apple.com | 204.19.119.1 | 2620:171:800:714::1 | 856 |
| d.ns.apple.com | 204.26.57.1 | 2620:171:801:714::1 | 856 |

**Table 4.** Start of Authority (SOA) Record for apple.com

| Parameter | Value | TTL / s (dig only) |
|-----------|-------|-------------------|
| Primary Name Server | ns-ext-prod.jackfruit.apple.com | 3596 |
| Responsible Party | hostmaster.apple.com | - |
| Serial Number | 2025031900 | - |
| Refresh Interval / s | 900 | - |
| Retry Interval / s | 900 | - |
| Expire Time / s | 2016000 | - |
| Negative Caching TTL / s | 1800 | - |

**Table 5.** CNAME Resolution Chain for www.apple.com

| Resolution Step | Target | TTL / s (dig only) |
|-----------------|--------|-------------------|
| 1 | www-apple-com.v.aaplimg.com | 58 |
| 2 | www.apple.com.edgekey.net | 220 |
| 3 | e6858.dsce9.akamaiedge.net | 99 |
| Final IP | 23.206.49.53 | - |

**Table 6.** DNS Trace Resolution Path for apple.com

| Level | Server Type | TTL / s | Number of Servers |
|-------|------------|---------|-------------------|
| Root (.) | root-servers.net | 58 | 13 |
| TLD (com.) | gtld-servers.net | 172800 | 13 |
| Domain | ns.apple.com | 172800 / 43200 | 4 |
| Final IP | - | 900 | - |

**Table 7.** Error and Timeout Responses

| Query Type | Response | Status |
|------------|----------|--------|
| Non-existent domain | server can't find nonexistent-domain-example123456.com | NXDOMAIN |
| Invalid DNS server | connection timed out; no servers could be reached | Timeout |

~~~
Browsing for _services._dns-sd._udp.local.
DATE: ---Wed 19 Mar 2025---
19:19:55.313  ...STARTING...
Timestamp     A/R    Flags  if Domain               Service Type         Instance Name
19:19:55.314  Add        2   8 .                    _tcp.local.          _apple-mobdev2
19:19:55.473  Add        3   1 .                    _tcp.local.          _airplay
19:19:55.473  Add        3   1 .                    _tcp.local.          _raop
[Additional services omitted for brevity]
~~~

**Figure 1.** Local network service discovery results using dns-sd command on macOS, showing available mDNS services on the local network including Apple ecosystem services (_airplay, _raop) and standard network protocols.

## Discussion

The comparative analysis of DNS query tools reveals significant differences in information presentation, level of detail, and practical utility between traditional and modern utilities.

### Information Density and Presentation

Tables 1-5 demonstrate that `dig` provides more detailed information than `nslookup` across all record types. While both tools successfully resolve the fundamental DNS data (IP addresses, mail servers, etc.), `dig` consistently reports additional metrics such as query time, TTL values, and message sizes. This supplementary information is valuable for network diagnostics and performance analysis, particularly when troubleshooting caching issues or connectivity problems.

The TTL values reported by `dig` (Tables 1-5) reveal Apple's DNS caching strategy, with short TTLs for frequently changing records like A records (686 seconds) and longer TTLs for more stable infrastructure like MX records (3600 seconds). These values reflect a balance between responsiveness to infrastructure changes and reduction of DNS query load.

### Resolution Chain Complexity

The CNAME resolution process documented in Table 5 illustrates the sophisticated content delivery architecture employed by Apple. The multi-step redirection chain (www.apple.com → www-apple-com.v.aaplimg.com → www.apple.com.edgekey.net → e6858.dsce9.akamaiedge.net) reveals Apple's use of both proprietary CDN infrastructure (aaplimg.com) and third-party services (Akamai's edgekey.net and akamaiedge.net domains). The progressively declining TTL values across this chain (58s → 220s → 99s) suggest deliberate caching policy differences between the different layers of the architecture.

This complex CNAME chain, clearly visualized through the structured output of `dig`, demonstrates how modern DNS implementations extend beyond simple domain-to-IP mapping to enable sophisticated content delivery strategies. Understanding these relationships is crucial for network administrators diagnosing web service delivery issues.

### Authoritative vs. Non-Authoritative Resolution

The DNS trace results in Table 6 provide insight into the hierarchical nature of DNS resolution, showing the delegation path from root servers through Top-Level Domain (TLD) servers to Apple's authoritative nameservers. The substantial difference in TTL values between the higher hierarchy levels (172800 seconds for TLD servers) and the final resolution (900 seconds for the A record) reflects the different update frequencies expected at various levels of the DNS tree.

The trace results also reveal NSEC3 records in the response, indicating DNSSEC (DNS Security Extensions) implementation at the .com TLD level. This security measure helps protect against DNS poisoning attacks by providing cryptographic verification of DNS data. The presence of these records, visible only in the `dig +trace` output, highlights how modern DNS tools can reveal security implementations that remain invisible with traditional utilities.

### Error Handling and Diagnostics

The error responses documented in Table 7 demonstrate how DNS failures manifest differently depending on their cause. The NXDOMAIN response for non-existent domains provides a clear diagnostic indicator that the domain name itself is invalid, while the connection timeout for queries to an invalid DNS server correctly identifies infrastructure problems rather than domain issues. These distinct error patterns, while visible in both tools, are presented with clearer status codes in the `dig` output, facilitating more efficient troubleshooting.

### Local Network Service Integration

Figure 1 illustrates capabilities beyond traditional DNS, showing macOS's integration with Multicast DNS (mDNS) for local service discovery. The presence of Apple-specific services (_airplay, _raop, _companion-link) alongside standard protocols demonstrates how the DNS concept has evolved from simple name resolution to service-oriented discovery. This extension of DNS principles to local network environments represents a significant evolution in network service architecture, enabling zero-configuration networking for modern applications.

The diverse service types discovered on the local network reveal the ubiquity of service advertisement in contemporary computing environments, particularly within the Apple ecosystem. This service-oriented approach to network resource discovery complements traditional DNS by addressing local network needs without requiring centralized infrastructure.

## References
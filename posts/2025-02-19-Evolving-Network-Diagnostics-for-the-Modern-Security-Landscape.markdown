---
title: Network Path Analysis - Evolving Network Diagnostics for the Modern Security Landscape
date: 2025-02-19
tags: networking, laboratory, ping, traceroute
description: 
---

## Abstract

This study explores the evolution of network diagnostics in security-hardened modern networks, utilizing advanced tools like `kdig`, `nping`, and `tcptraceroute` to overcome limitations of traditional ICMP-based utilities. Conducted on February 24, 2025, using macOS Sequoia 15.3.1, the experiment reveals TCP-based diagnostics’ effectiveness despite widespread UDP and ICMP filtering, offering insights into DNS resolution, connectivity, and path visibility for network professionals navigating contemporary security challenges.[@Hellekson13]

## Introduction

In today’s networks, security isn’t just an added feature; it’s the foundational architecture. Modern networks are increasingly hardened, employing sophisticated firewalls, intrusion detection systems, and traffic filtering policies. While essential for protecting against threats, these security measures significantly impact the effectiveness of traditional network diagnostic tools like `ping`, `traceroute`, and even basic DNS queries using tools like `dig`. These classic utilities, which heavily rely on the Internet Control Message Protocol (ICMP) and simple UDP probes, often find themselves blocked or rate-limited in security-conscious environments, leaving network administrators and security professionals with a diminished ability to diagnose and troubleshoot effectively.[@rfc792]

This blog post modernizes our approach to network diagnostics by introducing a suite of advanced tools designed to navigate the challenges of security-hardened networks. We move beyond the limitations of ICMP-centric utilities and embrace tools that leverage TCP, UDP, and application-layer protocols to gain deeper insights into network behavior. This updated methodology not only ensures continued diagnostic capability but also provides a more accurate representation of network performance as experienced by modern applications and users.

In this experiment, we will explore `kdig` for advanced DNS analysis, `nping` for flexible connectivity and latency testing, `tcptraceroute` for path discovery through firewalls, and `nping` for comprehensive network probing and analysis. These tools represent a significant evolution in network diagnostics, offering robust capabilities for understanding network behavior in the face of modern security implementations; however, their effectiveness depends on navigating complex security policies that obscure traditional diagnostics.[@Hellekson13] By mastering these techniques, network professionals can regain visibility and control, ensuring network reliability and performance even in the most rigorously secured environments.

### Key Concepts and Definitions:

The Internet Control Message Protocol (ICMP) enables network devices to exchange diagnostic information, critical for tools like `ping` and `traceroute` but often filtered in security-hardened networks.[@rfc792] Domain Name System Security Extensions (DNSSEC) ensure DNS query integrity, supported by `kdig` for secure resolution. Time To Live (TTL) limits packet circulation, aiding path analysis, while Maximum Transmission Unit (MTU) defines packet size limits, impacting performance.[@stevens1994tcpip]

### Network Diagnostic Tools

`kdig`, from Knot DNS, offers advanced DNS querying with DNSSEC support, surpassing `dig` in security-focused environments.[@KnotDNS] `nping`, part of Nmap, crafts TCP, UDP, and ICMP packets for flexible testing, bypassing ICMP restrictions.[@NmapNping] `tcptraceroute` uses TCP to trace paths through firewalls, complementing ICMP-based `traceroute`, which relies on ICMP.[@Jac88]

### Notes on Execution
Run each command multiple times (e.g., 3 runs) to account for network variability and collect average results. Record outputs, including errors or timeouts, as they indicate filtering or security policies. For example, packet loss in UDP/ICMP tests suggests potential filtering by firewalls or ISPs. If a target blocks a specific port or protocol, try an alternative (e.g., google.com or cloudflare.com instead of aws.amazon.com).

## Experimental

This experiment uses a 2.6 GHz 6-Core Intel Core i7 MacBook Pro with 16 GB 2667 MHz DDR4 RAM running macOS Sequoia 15.3.1, connected via built-in Wi-Fi. All commands are non-intrusive network diagnostics targeting public services (e.g., `aws.amazon.com`, `level3.net`, `gmail.com`) designed to handle routine testing. Some commands require administrator privileges (`sudo`) due to low-level network access. Rate limiting is inherent in the tools to avoid network flooding, ensuring ethical and safe execution.

Before running the commands, install the required tools using Homebrew (assuming Homebrew is installed):

```zsh
brew install knot        # for `kdig`
brew install tcptraceroute
brew install nmap        # for `nping`
```

1. Advanced DNS Resolution Analysis with kdig:

```zsh
# Basic A record lookup with query timing to benchmark DNS performance
kdig +stats level3.net
```

```zsh
# Trace the full DNS resolution path for a complex CNAME chain (use multiple queries or follow manually)
kdig @8.8.8.8 aws.amazon.com A  # Query with Google’s DNS server for root resolution
kdig @8.8.4.4 aws.amazon.com A  # Query with another server for comparison
# Note: kdig doesn’t have a direct +trace option; use multiple queries or tools like dig for full tracing
```

```zsh
# Validate DNSSEC signatures to assess security implementation
kdig +dnssec aws.amazon.com
```

```zsh
# Query MX records to examine email server resolution
kdig MX gmail.com
```

2. Flexible Connectivity and Latency Testing with nping
```zsh
# TCP SYN ping to port 80 (HTTP) with 5 packets and 100ms delay for basic connectivity
sudo nping --tcp -p 80 --flags SYN --count 5 --delay 100ms aws.amazon.com
```

```zsh
# TCP SYN ping to port 443 (HTTPS) with a 1400-byte packet size to test MTU effects
sudo nping --tcp -p 443 --flags SYN --data-length 1400 --count 5 --delay 100ms aws.amazon.com
```

```zsh
# UDP ping to port 53 (DNS) to compare with TCP, noting potential filtering
sudo nping --udp -p 53 --count 5 --delay 100ms aws.amazon.com
```

```zsh
# ICMP echo probe for baseline comparison with traditional ping
sudo nping --icmp --icmp-type echo-request --count 5 --delay 100ms aws.amazon.com
```

3. Firewall-Penetrating Path Analysis with tcptraceroute:
```zsh
# TCP traceroute to port 80 (HTTP) with numeric output for speed
sudo tcptraceroute -n -p 80 aws.amazon.com
```
```zsh
# TCP traceroute to port 443 (HTTPS) to assess secure connection paths
sudo tcptraceroute -n -p 443 aws.amazon.com
```
```zsh
# Standard ICMP traceroute for comparison, expecting obscurity
traceroute -n -m 15 -w 2 -q 2 aws.amazon.com
```

4. Comprehensive Network Probing with nping

```zsh
# TCP SYN probe to port 80 with 5 packets and 100ms delay
sudo nping --tcp -p 80 --flags SYN --count 5 --delay 100ms aws.amazon.com
```
```zsh
# UDP probe to port 53 (DNS) to test non-TCP behavior
sudo nping --udp -p 53 --count 5 --delay 100ms aws.amazon.com
```
```zsh
# ICMP echo probe for baseline comparison
sudo nping --icmp --icmp-type echo-request --count 5 --delay 100ms aws.amazon.com
```
```zsh
# TCP SYN-based traceroute-like path discovery to port 443
sudo nping --tcp --traceroute -p 443 --flags SYN --count 5 aws.amazon.com
```


## Results

**Table 1.** This table presents the DNS resolution analysis results for various network services, including query times, response sizes, and the DNS servers used, conducted on February 24, 2025, to evaluate performance in security-hardened environments.

<table>
    <thead>
        <tr>
            <th>Target</th>
            <th>Query Type</th>
            <th>Resolution</th>
            <th>Query Time / ms</th>
            <th>Response Size / bytes</th>
            <th>DNS Server</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td data-label="Target">`level3.net`</td>
            <td data-label="Query Type">A</td>
            <td data-label="Resolution">4.68.80.110</td>
            <td data-label="Query Time / ms">53.6</td>
            <td data-label="Response Size / bytes">55</td>
            <td data-label="DNS Server">fe80::dcd1:97ff:fe4c:ca8b%en0</td>
        </tr>
        <tr>
            <td data-label="Target">`aws.amazon.com`</td>
            <td data-label="Query Type">A (via 8.8.8.8)</td>
            <td data-label="Resolution">CNAME chain to 108.138.94.{20,102,17,72}</td>
            <td data-label="Query Time / ms">118.9</td>
            <td data-label="Response Size / bytes">185</td>
            <td data-label="DNS Server">8.8.8.8</td>
        </tr>
        <tr>
            <td data-label="Target">`aws.amazon.com`</td>
            <td data-label="Query Type">A (via 8.8.4.4)</td>
            <td data-label="Resolution">CNAME chain to 108.138.94.{20,17,102,72}</td>
            <td data-label="Query Time / ms">91.8</td>
            <td data-label="Response Size / bytes">185</td>
            <td data-label="DNS Server">8.8.4.4</td>
        </tr>
        <tr>
            <td data-label="Target">`aws.amazon.com`</td>
            <td data-label="Query Type">A (+dnssec)</td>
            <td data-label="Resolution">CNAME chain to 108.138.94.{102,20,17,72}</td>
            <td data-label="Query Time / ms">30.6</td>
            <td data-label="Response Size / bytes">185</td>
            <td data-label="DNS Server">fe80::dcd1:97ff:fe4c:ca8b%en0</td>
        </tr>
        <tr>
            <td data-label="Target">`gmail.com`</td>
            <td data-label="Query Type">MX</td>
            <td data-label="Resolution">Multiple MX records (e.g., `gmail-smtp-in.l.google.com`)</td>
            <td data-label="Query Time / ms">127.1</td>
            <td data-label="Response Size / bytes">161</td>
            <td data-label="DNS Server">fe80::dcd1:97ff:fe4c:ca8b%en0</td>
        </tr>
    </tbody>
</table>

**Table 2.** This table displays the connectivity and latency test results using `nping` across different protocols and ports, including packet sizes, success rates, and round-trip times, performed on February 24, 2025, to assess network behavior in modern, security-hardened networks.

<table>
    <thead>
        <tr>
            <th>Target</th>
            <th>Protocol/Port</th>
            <th>Packet Size / bytes</th>
            <th>Success Rate /%</th>
            <th>Min RTT / ms</th>
            <th>Avg RTT / ms</th>
            <th>Max RTT / ms</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td data-label="Target">`aws.amazon.com`</td>
            <td data-label="Protocol/Port">TCP/80 (SYN)</td>
            <td data-label="Packet Size / bytes">40</td>
            <td data-label="Success Rate /%">100</td>
            <td data-label="Min RTT / ms">24.701</td>
            <td data-label="Avg RTT / ms">33.343</td>
            <td data-label="Max RTT / ms">36.986</td>
        </tr>
        <tr>
            <td data-label="Target">`aws.amazon.com`</td>
            <td data-label="Protocol/Port">TCP/443 (SYN, 1400 bytes)</td>
            <td data-label="Packet Size / bytes">1440</td>
            <td data-label="Success Rate /%">100</td>
            <td data-label="Min RTT / ms">41.325</td>
            <td data-label="Avg RTT / ms">54.492</td>
            <td data-label="Max RTT / ms">61.258</td>
        </tr>
        <tr>
            <td data-label="Target">`aws.amazon.com`</td>
            <td data-label="Protocol/Port">UDP/53</td>
            <td data-label="Packet Size / bytes">28</td>
            <td data-label="Success Rate /%">0</td>
            <td data-label="Min RTT / ms">N/A</td>
            <td data-label="Avg RTT / ms">N/A</td>
            <td data-label="Max RTT / ms">N/A</td>
        </tr>
        <tr>
            <td data-label="Target">`aws.amazon.com`</td>
            <td data-label="Protocol/Port">ICMP (Echo)</td>
            <td data-label="Packet Size / bytes">28</td>
            <td data-label="Success Rate /%">100</td>
            <td data-label="Min RTT / ms">66.956</td>
            <td data-label="Avg RTT / ms">77.384</td>
            <td data-label="Max RTT / ms">93.394</td>
        </tr>
    </tbody>
</table>

**Table 3.** This table outlines the path analysis results using `tcptraceroute` and `traceroute`, detailing visible hops, final hop round-trip times, and path visibility, conducted on February 24, 2025, to investigate network topology visibility in security-hardened environments.

<table>
    <thead>
        <tr>
            <th>Tool</th>
            <th>Target/Port</th>
            <th>Visible Hops</th>
            <th>Final Hop RTT / ms</th>
            <th>Path Visibility</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td data-label="Tool">`tcptraceroute`</td>
            <td data-label="Target/Port">`aws.amazon.com`/80</td>
            <td data-label="Visible Hops">1 (192.168.1.1), 19 (108.138.94.102)</td>
            <td data-label="Final Hop RTT / ms">28.561–36.331</td>
            <td data-label="Path Visibility">Partial (obscured 2–18)</td>
        </tr>
        <tr>
            <td data-label="Tool">`tcptraceroute`</td>
            <td data-label="Target/Port">`aws.amazon.com`/443</td>
            <td data-label="Visible Hops">1 (192.168.1.1), 19 (108.138.94.102)</td>
            <td data-label="Final Hop RTT / ms">31.819–43.631</td>
            <td data-label="Path Visibility">Partial (obscured 2–18)</td>
        </tr>
        <tr>
            <td data-label="Tool">`traceroute`</td>
            <td data-label="Target/Port">`aws.amazon.com` (ICMP)</td>
            <td data-label="Visible Hops">1 (192.168.1.1)</td>
            <td data-label="Final Hop RTT / ms">N/A</td>
            <td data-label="Path Visibility">Obscured (2–15, * * *)</td>
        </tr>
        <tr>
            <td data-label="Tool">`nping` (TCP Traceroute)</td>
            <td data-label="Target/Port">`aws.amazon.com`/443</td>
            <td data-label="Visible Hops">1 (192.168.1.1)</td>
            <td data-label="Final Hop RTT / ms">2.891</td>
            <td data-label="Path Visibility">Obscured (2–5, no response)</td>
        </tr>
    </tbody>
</table>

## Discussion

Our investigation reveals critical insights into the behavior of modern network diagnostics in security-hardened environments, particularly highlighting the challenges and opportunities presented by contemporary security measures.[@Hellekson13] The DNS resolution results (Table 1) demonstrate the complexity of cloud-based service architectures, as seen with `aws.amazon.com`’s multi-layer CNAME chain resolving to CloudFront IPs (108.138.94.{20,102,17,72}). Using Google’s public DNS servers (8.8.8.8 and 8.8.4.4) provided consistent resolution, revealing slight variations in query times (118.9 ms vs. 91.8 ms) and TTL values, suggesting effective load balancing and caching strategies; however, query times were faster via the local resolver (30.6 ms), indicating potential local caching benefits.[@KnotDNS]

Security hardening significantly impacts network visibility, as evidenced by our path analysis (Table 3). Both `tcptraceroute` and `traceroute` results show near-complete path obscurity beyond the first hop (192.168.1.1), with `traceroute` (ICMP-based) failing to reveal any intermediate hops, while `tcptraceroute` (TCP-based) reached the target but obscured hops 2–18. This behavior reflects common security practices like ICMP filtering and firewall rules, designed to reduce network visibility for attackers but challenging for legitimate diagnostics.[@rfc792; @Jac88] The `nping` TCP traceroute similarly showed limited visibility, detecting only the first hop before timing out, underscoring the effectiveness of these security measures.

Connectivity and latency tests (Table 2) highlight protocol-specific behaviors in security-hardened networks. TCP-based probes (ports 80 and 443) achieved 100% success rates with consistent RTTs (33.343 ms and 54.492 ms, respectively), even with a larger 1400-byte packet size, suggesting robust handling of TCP traffic by AWS infrastructure; however, UDP (port 53) and ICMP probes experienced 100% packet loss, indicating stringent filtering of these protocols—likely due to firewall policies or ISP restrictions.[@NmapNping] This contrast underscores the advantage of TCP-based tools like `nping` and `tcptraceroute` in bypassing ICMP limitations, aligning with our objective to evolve diagnostics for modern networks.

The observed differences in protocol behavior raise questions about security policy implementations. The success of TCP probes suggests that AWS and intermediary networks prioritize TCP traffic for web services, possibly to support HTTP/HTTPS applications, while filtering UDP and ICMP to mitigate reconnaissance or denial-of-service attacks; however, the partial visibility in `tcptraceroute` compared to complete obscurity in `traceroute` indicates that TCP-based path analysis can penetrate some security barriers, though not fully, due to dynamic routing or load balancing obscuring intermediate hops.[@stevens1994tcpip]

Several limitations in our methodology should be noted. The single-location testing on macOS limits generalizability across diverse network environments. The fixed packet size (1400 bytes) in TCP tests might miss intermediate MTU thresholds, and our reliance on public targets like AWS may not reflect all security configurations; additionally, `kdig`’s lack of a direct `+trace` option required manual DNS resolution, potentially missing subtle path details.

These findings suggest promising directions for future research. Distributed testing across multiple geographic locations and ISPs could reveal global variations in security policies and MTU behavior. Automated tracing tools or hybrid approaches combining TCP, UDP, and application-layer diagnostics could enhance visibility in security-hardened networks; however, temporal analysis of path stability and protocol performance under varying loads would also deepen our understanding of dynamic routing systems.[@Hellekson13]

## Conclusion

This study demonstrates the evolving challenges and adaptations required for network diagnostics in modern, security-hardened environments. Our key findings reveal the persistence of TCP-based tools like `nping` and `tcptraceroute` in maintaining diagnostic capability, despite widespread ICMP and UDP filtering. DNS resolution patterns highlight the complexity of cloud infrastructures, with `aws.amazon.com`’s CNAME chains and DNSSEC validation showcasing robust security and scalability; however, path obscurity remains a significant barrier, as traditional ICMP-based `traceroute` offers little visibility, while TCP-based alternatives provide partial insights into network topology. [@rfc792; @Jac88]

For network administrators, these results suggest adopting TCP-centric diagnostics alongside modern DNS tools like `kdig` to navigate security restrictions effectively. Leveraging public DNS resolvers (e.g., 8.8.8.8, 8.8.4.4) can provide consistent resolution data, while persistent monitoring with `nping` can uncover latency and connectivity patterns; however, as networks continue to prioritize security through protocol filtering, developing new diagnostic methodologies that balance transparency with protection will be critical. Future research should explore distributed testing, automated path tracing, and protocol-agnostic approaches to enhance network visibility while respecting security constraints.[@Hellekson13]

## Acknowledgements

We gratefully acknowledge the developers of `Knot DNS`, Nmap, and `tcptraceroute` for creating the tools that enabled this research, as well as the open-source community for maintaining these resources. Special thanks to the xAI team for their assistance in refining this analysis. This work was conducted on macOS Sequoia 15.3.1, and we appreciate Apple’s support for network diagnostic capabilities in their operating system.

### References
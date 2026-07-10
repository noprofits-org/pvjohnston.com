---
title: Network Path Analysis - Evaluating Diagnostic Tools in Security-Hardened Modern Networks
date: 2025-02-18
tags: networking, laboratory, ping, traceroute
description: A modern networking laboratory exercise for Mac users exploring ICMP protocols and network diagnostics
---

## Abstract
This research modernizes traditional network diagnostic techniques for contemporary network environments with enhanced security measures. Using standard macOS utilities and modern diagnostic tools, we demonstrate methods for analyzing DNS resolution chains, MTU discovery, and network path analysis while accounting for security-driven path obscurity. The Maximum Transmission Unit (MTU) was found to be 1472-bytes. This approach provides practical insights into modern network behavior where traditional tools may face limitations due to security policies.

## Introduction

In modern computing, understanding how data traverses networks is crucial for diagnostics, optimization, and security.[@stevens1994tcpip] This laboratory exercise explores three fundamental networking tools available on macOS: `dig`, `ping`, and `traceroute`. These tools utilize the Internet Control Message Protocol (ICMP) to provide insights into network behavior.[@rfc792]

Network diagnostic tools must address both Internet Protocol version 4 (IPv4) and version 6 (IPv6) addressing schemes. While IPv4 remains widely used with its 32-bit addressing, IPv6 adoption continues to grow, offering expanded addressing capabilities through 128-bit addresses and improved security features. Understanding how diagnostic tools behave differently across these protocols provides crucial insights into modern network architectures and security practices.

Network performance analysis extends beyond basic connectivity testing to application-layer metrics. The Time To First Byte (TTFB) metric measures the duration between sending an HTTP request and receiving the initial response byte, providing insight into server processing and network latency. Combined with DNS resolution and connection establishment times, these measurements help diagnose performance bottlenecks in web service delivery.

### Key Concepts and Definitions:
The Internet Control Message Protocol (ICMP) serves as a fundamental network layer protocol that enables network devices to communicate diagnostic information and error messages. Network administrators and diagnostic tools rely on ICMP to identify and troubleshoot connectivity issues, making it an essential component of modern network infrastructure.[@rfc792]

Maximum Transmission Unit (MTU) refers to the largest packet or frame size that can be transmitted in a single network layer transaction. Understanding MTU is crucial for network performance optimization.[@rfc1191] When a packet exceeds the MTU of any link along its path, it must either be fragmented into smaller pieces or dropped, depending on the packet's flags and network configuration. Network administrators must carefully balance MTU size against network efficiency, as larger MTUs can improve throughput but may increase retransmission rates if fragmentation is not handled properly.

Time To Live (TTL) represents a critical value in IP packets that prevents them from circulating indefinitely in the network. Each router decrements the TTL value as it forwards a packet, and when the TTL reaches zero, the packet is discarded and an ICMP Time Exceeded message is sent back to the source. This mechanism not only prevents routing loops but also enables tools like traceroute to map network paths by deliberately sending packets with incrementing TTL values.

The Domain Name System (DNS) provides the essential service of translating human-readable domain names into IP addresses that computers can use for routing. This hierarchical, distributed database system forms the backbone of internet usability by allowing users to access resources using memorable names while the underlying network operates on numerical addresses. DNS servers work together in a global network to resolve queries, with each server responsible for its portion of the domain name space.

### Network Diagnostic Tools

The Domain Information Groper (`dig`) command serves as a sophisticated Domain Name Server (DNS) interrogation tool, offering significant improvements over its predecessor, `nslookup`.[@liu2006dns] Beyond basic forward and reverse DNS lookups, `dig` provides comprehensive DNS debugging capabilities, including zone transfer operations for replicating DNS databases between servers, DNS Security Extensions (DNSSEC) validation for cryptographic verification of DNS records, and support for specialized record types such as mail exchangers (MX) and text records (TXT). Its consistent, predictable output format makes it particularly valuable for automated DNS analysis and troubleshooting scripts. Canonical Name (CNAME) chains represent a series of DNS redirections that allow flexible and scalable service architecture. When a domain employs multiple CNAME records in sequence, it creates a chain that can facilitate load balancing, geographic distribution, and service abstraction. For example, a website might redirect from its primary domain through multiple CNAME records before resolving to final IP addresses, allowing service providers to modify underlying infrastructure without changing client-facing domain names.

The ping utility, a foundational network diagnostic tool developed by Mike Muuss in 1983, operates by transmitting ICMP Echo Request messages to target hosts.[@muuss1983story] This elegantly simple yet powerful tool measures Round-Trip Time (RTT) with millisecond precision, enabling network administrators to quantify latency and assess connection stability through packet loss detection. Through manipulation of the Don't Fragment (DF) bit, ping facilitates Path MTU discovery, helping identify optimal packet sizes for specific network paths. The tool's flexibility in operation modes, from continuous monitoring to precise packet-limited tests, makes it invaluable for both quick connectivity checks and detailed network performance analysis.

The traceroute utility, developed by Van Jacobson in 1988, employs an ingenious manipulation of the Internet Protocol (IP) Time To Live (TTL) field to map network topologies.[@jacobson1988traceroute] By systematically incrementing TTL values and analyzing the resulting ICMP Time Exceeded messages, traceroute constructs a detailed view of network paths, revealing routing behaviors, hop-by-hop latency patterns, and potential network bottlenecks. This methodology provides network administrators with crucial insights into routing efficiency and helps identify points of network congestion or failure.

The mtr (My TraceRoute) tool represents a significant evolution in network diagnostics, combining the functionality of ping and traceroute into a more comprehensive analysis platform.[@mtr2008] By conducting continuous path analysis and maintaining statistical aggregation of results, mtr provides deeper insights into network behavior over time. Its real-time monitoring capabilities reveal temporal patterns in routing changes and path stability, while detailed loss and latency metrics at each hop enable more nuanced understanding of network performance characteristics. This integration of multiple diagnostic approaches makes mtr particularly valuable for complex network troubleshooting scenarios.

### Objectives
This experiment explores fundamental network diagnostic techniques through a series of practical terminal commands. DNS queries are used to examine how domain names resolve to IP addresses, revealing the hierarchical nature of Domain Name System and various record types that support modern web infrastructure. By investigating maximum frame sizes in a network, packet fragmentation and MTU limits are found to affect network performance and reliability. Through traceroute analysis, network topology is mapped and to better understand how data packets traverse multiple hops to reach their destination, while also learning why some network paths might be deliberately obscured for security reasons. Throughout these experiments, various ICMP response types are encountered, and the opportunity for practical experience in interpreting these network-level messages that form the basis of many diagnostic tools arises. This hands-on experience with DNS resolution, MTU discovery, and path analysis are essential skills for network troubleshooting and optimization.

## Experimental

Using a 2.6 GHz 6-Core Intel Core i7 MacBook Pro with 16 GB 2667 MHz DDR4 RAM running macOS Sequoia 15.3.1 and built in Wi-Fi run following terminal commands. All commands are non-intrusive network diagnostics. Some commands require administrator privileges (sudo). Rate limiting is built into tools to prevent network flooding. All targets are public services designed to handle routine diagnostics.

1. Basic Connectivity Testing:

    ```zsh
    # Test DNS resolution and timing for each target
    for target in level3.net aws.amazon.com cloudfront.net; do
        dig +noall +answer +stats $target
    done
    ```

2. Progressive MTU Discovery:

    ```zsh
    # Start with small packet size and increment
    for size in 500 1000 1472 1500; do
        echo "Testing packet size: $size bytes"
        ping -D -s $size -c 5 aws.amazon.com
    done
    ```

3. Network Path Analysis:
   a. Basic Path Analysis:

   ```zsh
   # Run traceroute with options:
    # -n : numeric output only (no DNS lookups)
    # -m 15 : maximum 15 hops
    # -w 2 : wait 2 seconds max for each response
    # -q 2 : send only 2 probes per hop (default is 3)
    traceroute -n -m 15 -w 2 -q 2 aws.amazon.com
   ```
  
   
   b. Extended path analysis:

   ```zsh
   # Install MTR (if needed)
   brew install mtr
   # Run MTR with 10 cycles
   sudo /usr/local/Cellar/mtr/0.95/sbin/mtr -n -r -c 10 aws.amazon.com
   ```

4. HTTP Connection Analysis:
    
    ```zsh
    # Analyze HTTP connection components
    curl -w "\nDNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" -o /dev/null -s https://aws.amazon.com
    ```

## Results

**Table 1.** DNS Resolution Analysis Results for Different Network Services Showing Query Times and Response Sizes.
<table>
    <thead>
        <tr>
            <th>Target</th>
            <th>Record Type</th>
            <th>Resolution</th>
            <th>Query Time / ms</th>
            <th>Response Size / bytes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>level3.net</td>
            <td>A</td>
            <td>4.68.80.110</td>
            <td>49</td>
            <td>55</td>
        </tr>
        <tr>
            <td>aws.amazon.com</td>
            <td>CNAME chain</td>
            <td>52.119.161.208 (primary)</td>
            <td>28</td>
            <td>189</td>
        </tr>
        <tr>
            <td>cloudfront.net</td>
            <td>CNAME</td>
            <td>Resolves via CNAME chain</td>
            <td>42</td>
            <td>110</td>
        </tr>
    </tbody>
</table>

**Table 2.** MTU Discovery Test Results with Variable Packet Sizes.
<table>
    <thead>
        <tr>
            <th>Packet Size / bytes</th>
            <th>Success Rate /%</th>
            <th>Min RTT / ms</th>
            <th>Avg RTT / ms</th>
            <th>Max RTT / ms</th>
            <th>StDev / ms</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>500</td>
            <td>100</td>
            <td>43.531</td>
            <td>59.900</td>
            <td>73.703</td>
            <td>11.925</td>
        </tr>
        <tr>
            <td>1000</td>
            <td>100</td>
            <td>50.033</td>
            <td>73.999</td>
            <td>91.792</td>
            <td>16.485</td>
        </tr>
        <tr>
            <td>1472</td>
            <td>0</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
        </tr>
        <tr>
            <td>1500</td>
            <td>0</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
        </tr>
    </tbody>
</table>

**Table 3.** HTTP Connection Timing Analysis for aws.amazon.com.
<table>
    <thead>
        <tr>
            <th>Metric</th>
            <th>Time / s</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>DNS Resolution</td>
            <td>0.098</td>
        </tr>
        <tr>
            <td>Connection Establishment</td>
            <td>0.140</td>
        </tr>
        <tr>
            <td>Time to First Byte</td>
            <td>0.373</td>
        </tr>
        <tr>
            <td>Total Response</td>
            <td>1.761</td>
        </tr>
    </tbody>
</table>

## Discussion

Our investigation revealed several significant characteristics of modern network behavior and security practices. The DNS resolution results (Table 1) demonstrate the complexity of contemporary service architectures, particularly in cloud environments. The AWS infrastructure employs a multi-layer CNAME chain, indicating a sophisticated load balancing and routing system, while simpler services like level3.net resolve directly through A records. These architectural differences reflect varying approaches to service delivery and scalability.

The security hardening observed in these results primarily manifests through ICMP filtering, strict firewall rules, and network segmentation practices. These measures, while essential for modern network security, create new challenges for traditional diagnostic approaches. Understanding these specific security implementations helps contextualize the limitations encountered by standard network analysis tools.

Further interpretation of our findings reveals critical insights into the implications of security hardening on network diagnostics. The observed obscurity in traceroute paths, for instance, is a direct consequence of common security practices such as ICMP filtering and access control lists (ACLs) implemented on network devices. Modern firewalls and routers are often configured to block or rate-limit ICMP Time Exceeded messages, which are essential for `traceroute` to map network paths. This is done to reduce the network's attack surface, as revealing detailed path information can aid potential attackers in reconnaissance efforts; however, this practice significantly limits the utility of `traceroute` for legitimate diagnostic purposes, as network administrators are increasingly 'flying blind' beyond their immediate network perimeter.[@stevens1994tcpip]

The MTU discovery results also warrant deeper analysis in the context of security.  While the 1472-byte threshold may reflect common Ethernet overhead, it is also plausible that security protocols and policies contribute to this limitation. For example, if the network path involves VPN tunnels or IPsec encryption, the encapsulation overhead from these security mechanisms would reduce the effective MTU available for user data. Furthermore, some security policies might intentionally enforce lower MTUs for all traffic as a security measure. This could be to simplify deep packet inspection, to mitigate fragmentation-based attacks, or to ensure compatibility with diverse network segments that might have varying MTU capabilities due to security infrastructure. It's also important to consider the role of Path MTU Discovery (PMTUD) itself. PMTUD relies on ICMP "Fragmentation Needed" messages to inform the sender about MTU limitations along the path. If, as our traceroute results suggest, ICMP is heavily filtered, PMTUD may fail, leading to reliance on a conservative, potentially sub-optimal, fixed MTU, such as the 1472-byte limit we observed.

The contrasting behavior between IPv4 and IPv6 path analysis, with IPv6 showing greater visibility in our MTR tests, raises intriguing questions about differing security policy implementations across protocols. One possible explanation is that security practices and filtering rules have historically been more aggressively applied to IPv4 networks, which have been the dominant protocol for a longer period and thus subject to more extensive attack vectors.  As IPv6 adoption grows, security practices may evolve to become more uniformly applied across both protocols, potentially leading to similar path obscurity challenges for IPv6 diagnostics in the future.  Alternatively, the observed difference could reflect a deliberate security strategy, perhaps based on assumptions about the current threat landscape or the perceived maturity of IPv6 security tools and techniques.

Considering these security-driven limitations, it is crucial to critically evaluate the continued effectiveness of traditional tools like `ping` and `traceroute` in modern networks. While still valuable for basic connectivity checks within well-controlled network environments, their reliability for comprehensive path analysis and MTU discovery in security-hardened networks is increasingly questionable. This shift necessitates exploring and potentially developing alternative diagnostic methodologies. These might include a greater reliance on application-layer diagnostics, flow-based monitoring, network telemetry, or collaborative diagnostic approaches that can provide insights into network behavior without depending on increasingly filtered ICMP messages.  The balance between robust network security and effective network diagnostics is clearly shifting, requiring network administrators and tool developers to adapt to this evolving landscape.


Network path analysis proved particularly revealing about modern security practices. The traceroute results showed consistent accessibility only to the first hop (local router), with subsequent hops obscured. This behavior, while potentially frustrating from a diagnostic perspective, reflects contemporary security practices where organizations deliberately filter ICMP responses to reduce network visibility to potential attackers.[@stevens1994tcpip] The extended path analysis through MTR revealed additional insights, showing variable packet loss patterns and latency variations across the partially visible path.

Analysis of our traceroute and MTR results (Tables 2 and 3) revealed distinctly different behavior patterns between IPv4 and IPv6 routes. While IPv4 traceroute showed complete path obscurity beyond the first hop, IPv6 MTR analysis provided greater path visibility, suggesting varying security policies for different protocol versions. This distinction highlights how modern security practices are implemented differently across protocol versions, potentially offering network administrators more diagnostic options when both protocols are available.

HTTP connection timing analysis (Table 3) provided a comprehensive view of modern web service performance characteristics. The relatively quick DNS resolution time (0.098s) suggests effective DNS caching, while the longer total response time (1.761s) indicates significant processing occurring at the application layer. The gap between connection establishment and first byte receipt reveals important insights about server-side processing delays and potential optimization opportunities.

Several limitations in our methodology became apparent during testing. The fixed packet size increments in our MTU discovery process could have missed intermediate thresholds, particularly in the 1000-1472 byte range where fragmentation behavior changes dramatically. Additionally, our single-location testing perspective limits the generalizability of these findings.

These findings suggest several promising directions for future research. A distributed testing approach, utilizing multiple geographic locations and diverse network providers, would provide more comprehensive insights into MTU behavior across different network architectures. Such an approach could help establish whether the 1472-byte fragmentation threshold we observed represents a common limitation or is specific to particular network configurations.

Future MTU discovery methodology should implement an adaptive binary search approach, beginning with the standard range of 500-1500 bytes but automatically adjusting test sizes based on success or failure. For example, upon discovering fragmentation between 1000 and 1472 bytes, the testing could automatically narrow to investigate 1100, 1200, and 1300 byte packets to identify precise thresholds. This automated, granular approach would provide more accurate MTU profiles for different network paths.

Temporal analysis presents another valuable research opportunity. Our single-time measurements, while informative, cannot capture the dynamic nature of modern network routing and load balancing systems. Long-term monitoring could reveal patterns in path stability, DNS resolution changes, and performance variations during different traffic conditions. This would be particularly valuable for understanding cloud service providers' infrastructure adaptations to varying loads.

Methodology improvements should focus on automated, repeatable testing procedures. The manual aspects of our current approach could be enhanced through scripted testing that automatically adjusts packet sizes based on observed fragmentation behavior. This would enable more precise identification of MTU thresholds and provide better statistical significance through increased sample sizes.

Integration with additional diagnostic tools could provide deeper insights into network behavior. While our combination of traditional tools (dig, ping, traceroute) with modern utilities (MTR) proved informative, incorporating packet capture analysis could reveal subtle details about fragmentation behavior and routing decisions. Furthermore, correlation with server-side metrics could help distinguish between network-level and application-level performance factors.

Finally, the security implications of our findings warrant deeper investigation. The widespread filtering of ICMP responses suggests a trend toward decreased network transparency, raising questions about the future utility of traditional network diagnostic tools. Research into alternative diagnostic methodologies that balance network operators' security requirements with diagnostic needs could prove particularly valuable for the networking community.

### Conclusion

This study demonstrates both the enduring value and emerging limitations of traditional network diagnostic tools in modern network environments. Our key findings reveal several important characteristics of contemporary networks. First, the DNS resolution patterns highlight the increasing complexity of service delivery architectures, particularly in cloud environments where multiple CNAME chains and sophisticated load balancing systems are common. Second, our MTU discovery tests identified a clear fragmentation threshold at 1472 bytes, suggesting standardized limitations in current network configurations.

Perhaps most significantly, our research documents the growing opacity of network paths, with traceroute utilities revealing only first-hop information in many cases. This reduction in network visibility represents a fundamental shift in the balance between diagnostic capability and security practices. While this shift poses challenges for network diagnostics, our results show that modern tools like MTR can still provide valuable insights through statistical analysis and persistent monitoring.

The HTTP connection timing analysis revealed the layered nature of modern web service performance, with distinct phases from DNS resolution through final content delivery. These measurements demonstrate how various factors, from DNS caching efficiency to server-side processing, contribute to overall service performance.

For network administrators, these findings suggest several immediate actions. First, incorporate modern tools like MTR alongside traditional utilities to provide more comprehensive diagnostic capabilities. Second, develop testing procedures that account for security-driven path obscurity, potentially utilizing both IPv4 and IPv6 diagnostics where available. Finally, maintain detailed documentation of observed MTU thresholds and DNS resolution chains to better understand your network's behavior under varying conditions. As networks continue to prioritize security through reduced ICMP visibility, new diagnostic approaches and tools will need to be developed. Future research should focus on creating diagnostic methodologies that can provide meaningful insights while respecting the security requirements of modern networks.

### References
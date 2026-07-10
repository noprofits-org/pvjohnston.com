---
title: Building a Serverless CORS Proxy with Vercel - Simplifying Cross-Origin Requests
date: 2025-05-04
tags: cors proxy, serverless, vercel, javascript, web development
description: A practical exploration of building a serverless CORS proxy using Vercel's serverless functions, offering an elegant solution to the common cross-origin resource sharing challenges faced by frontend developers.
---

## Cross-Origin Headaches and Their Serverless Solution

Cross-origin resource sharing (CORS) remains one of those persistent challenges that frontend developers regularly encounter. A beautiful client-side application might work perfectly in development, but then upon deployment, those dreaded red error messages appear: "Access to fetch at 'https://api.example.com' from origin 'https://app-domain.com' has been blocked by CORS policy." This frustration is especially common when attempting to access third-party APIs that haven't configured CORS to allow requests from the client domain.

After encountering this issue repeatedly in my nonprofit applications, I decided to create a simple yet effective solution: a serverless CORS proxy deployed on Vercel. A proxy server acts as a middleman between client-side code and an API on another server, effectively bypassing CORS restrictions by making server-side requests possible from a browser window that would otherwise be blocked.

## How The CORS Proxy Works

The concept is straightforward: instead of making a direct request from the browser to a target API (which would be blocked by CORS restrictions), requests are sent to the proxy server. The proxy then forwards these requests to the target API, receives the response, and returns it to the application with the appropriate CORS headers that allow the browser to accept the response.

The implementation leverages Vercel's serverless functions, which provide a lightweight and scalable infrastructure without the need to maintain dedicated servers. The core of this solution is a single JavaScript file (proxy.js) that handles incoming requests, forwards them to the specified target URL, and returns the response with properly configured CORS headers.

The most challenging aspect of the implementation was handling different content types correctly. APIs might return JSON data, HTML content, images, or other binary data. The proxy needed to properly identify the content type and pass it through without corruption. Additionally, it needed to ensure compatibility with various HTTP methods (GET, POST, PUT, DELETE, etc.) and correctly forward headers and request bodies.

After several iterations and testing, a solution emerged that handles these requirements elegantly. One key insight was to exclude certain headers that could cause conflicts or security issues (like host, connection, origin, and content-encoding) when forwarding requests.

## Using the CORS Proxy in Projects

Integrating this CORS proxy into projects is remarkably simple. For a basic GET request:

```javascript
const PROXY_URL = 'https://cors-proxy-xi-ten.vercel.app/api/proxy';
const TARGET_API = 'https://api.example.com/data';

fetch(`${PROXY_URL}?url=${encodeURIComponent(TARGET_API)}`)
  .then(response => response.json())
  .then(data => {
    console.log('Data:', data);
  })
  .catch(error => console.error('Error:', error));
```

For POST requests or other methods that require a body and specific headers:

```javascript
const PROXY_URL = 'https://cors-proxy-xi-ten.vercel.app/api/proxy';
const TARGET_API = 'https://api.example.com/data';

fetch(`${PROXY_URL}?url=${encodeURIComponent(TARGET_API)}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ key: 'value' })
})
  .then(response => response.json())
  .then(data => {
    console.log('Data:', data);
  })
  .catch(error => console.error('Error:', error));
```

The proxy seamlessly handles different content types, including JSON, text, and binary data like images, making it versatile for various API integrations.

## Testing the Proxy

To help developers test the proxy with different request configurations, a dedicated testing page is available at [https://noprofits.org/cors-tester/](https://noprofits.org/cors-tester/). This interactive tool allows developers to enter a target URL to access through the proxy, select from various HTTP methods (GET, POST, PUT, etc.), configure request headers and body content, and execute the request to view the response in a user-friendly format.

The tester provides real-time feedback and displays the response data, headers, and any errors that might occur. It's particularly useful for debugging API interactions and understanding how different request configurations affect the results.

## Technical Challenges and Solutions

Building the proxy wasn't without challenges. One particularly troublesome issue was handling content encoding properly. Initial attempts encountered "ERR_CONTENT_DECODING_FAILED" errors when proxying certain responses. After investigation, it became clear that this was happening because the content-encoding header was being forwarded from the target API to the client, but the content had already been decoded by the node-fetch library used in the implementation.

The solution was to explicitly remove the content-encoding header from responses before sending them back to the client:

```javascript
// Explicitly remove content-encoding header to prevent decoding errors
res.removeHeader('content-encoding');
```

Another challenge was handling various content types correctly. For JSON responses, the content needed to be parsed and re-stringified. For binary data like images, the raw buffer had to be forwarded without modification:

```javascript
// Handle different content types appropriately
const contentType = response.headers.get('content-type') || '';

if (contentType.includes('application/json')) {
  const jsonData = await response.json();
  return res.json(jsonData);
} else if (contentType.includes('text/')) {
  const text = await response.text();
  return res.send(text);
} else {
  // Handle binary data (e.g., images)
  const buffer = await response.buffer();
  return res.send(buffer);
}
```

## Open Source and Available for Everyone

This CORS proxy is open source and available on GitHub at [https://github.com/noprofits-org/cors-proxy-server](https://github.com/noprofits-org/cors-proxy-server). Developers can either use the hosted version directly or fork the repository to deploy their own instance on Vercel.

The repository includes comprehensive documentation, example code, and deployment instructions. It's designed to be easy to understand and modify, even for developers who aren't familiar with serverless functions or CORS concepts.

## Beyond Development: Production Considerations

While this CORS proxy is a valuable tool for development and testing, there are important considerations for production use. The proxy is currently open without authentication, making it accessible to anyone. For production applications with significant traffic or sensitive data, deploying a private instance with additional security measures is recommended.

The current implementation relies on Vercel's generous free tier, which includes reasonable limits for most small to medium-sized applications. However, very high-traffic applications might require upgrading to a paid plan or implementing more sophisticated caching and rate-limiting strategies.

## Conclusion

Cross-origin resource sharing doesn't have to be a roadblock in the development process. With this serverless CORS proxy, developers can easily bypass these restrictions and focus on building great applications rather than wrestling with browser security policies.

This tool was originally built to solve challenges when developing applications for nonprofits, and now it's available to the broader development community. Whether for a small personal project or a complex application, this CORS proxy provides a simple, effective solution to a common problem.

Visit [https://noprofits.org/cors-tester/](https://noprofits.org/cors-tester/) to try the proxy, and check out the [GitHub repository](https://github.com/noprofits-org/cors-proxy-server) to learn more about the implementation or deploy a custom instance. Happy coding!
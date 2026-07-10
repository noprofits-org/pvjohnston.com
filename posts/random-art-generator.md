---
title: Building a Random Art Generator with the Met Museum API and a Serverless CORS Proxy
date: 2025-05-06
tags: art, web development, javascript, met museum, cors proxy, serverless
description: Taking a break from science to explore art and technology with a web application that makes the Metropolitan Museum's collection accessible through a custom-built CORS proxy solution.
---

## Bridging Art and Technology

Taking a break from our typically science-focused content, today's post explores a project at the intersection of art and technology. As a graduate of the College of Art and Science, I occasionally find myself drawn back to the arts, especially when technology can make it more accessible and discoverable.

## Bringing Art Discovery to the Web with a Simple Interface

Art appreciation often begins with discovery - stumbling upon a piece that resonates with you unexpectedly. The Metropolitan Museum of Art houses one of the world's most extensive art collections, spanning 5,000 years of human creativity. Their public API offers developers access to this treasure trove, but utilizing it in client-side applications presents a common web development challenge: Cross-Origin Resource Sharing (CORS) restrictions.

After successfully setting up a serverless CORS proxy with Vercel, I wanted to create a practical application to demonstrate its capabilities. This led to the development of the Met Random Art Generator, a simple yet engaging web application that allows users to discover random artworks from the Met's vast collection.

## The Random Art Generator: A CORS Proxy Success Story

The Met Random Art Generator exemplifies how a serverless CORS proxy can enable smooth interaction between client-side applications and third-party APIs. Without the proxy, browser security policies would prevent direct API calls from a web app to the Met's servers. But with our proxy in place, the application seamlessly fetches data and images, creating an intuitive art discovery experience.

The generator allows users to apply filters based on department (from 19 different curatorial departments), date range (spanning the Met's 5,000-year collection), and medium (paintings, sculpture, photographs, and more). With each click of the "Discover Random Artwork" button, users are presented with a new piece from the Met's collection that matches their criteria, complete with its image, title, artist, date, and medium information.

## Technical Implementation and Challenges

Building the Random Art Generator involved several key technical aspects. First was API integration, connecting to multiple Met API endpoints to fetch departments, search for artworks matching specific criteria, and retrieve detailed information about selected pieces. Next came image handling, displaying high-resolution images through the proxy while managing loading states and potential failures. Error handling was crucial for implementing robust fallback options to ensure a smooth user experience even when API requests fail. Finally, responsive design created an interface that works well across different devices and screen sizes.

One particular challenge was handling the large response data from the Met API's search endpoint. Some queries could return thousands of object IDs, potentially overwhelming both the proxy and the client. The solution involved limiting results to manageable sizes and implementing multiple fallback approaches when initial searches failed.

## Why This Matters for Developers

The Random Art Generator demonstrates how a CORS proxy can solve real-world development challenges. By acting as an intermediary between the client and the Met API, the proxy enables functionality that would otherwise be impossible due to browser security restrictions.

This approach can be applied to countless other scenarios where developers need to access third-party APIs from client-side applications. Whether it's weather data, social media feeds, or financial information, a serverless CORS proxy provides a lightweight solution without requiring complex backend infrastructure.

## Beyond Technical Implementation: The Joy of Discovery

While the technical aspects of this project are interesting, the true value lies in the experience it creates for users. The Random Art Generator turns the Met's extensive collection into a digital treasure hunt, where each click might reveal an ancient Egyptian artifact, a Renaissance masterpiece, or a modern photograph.

This combination of technology and art appreciation exemplifies how development tools like our serverless CORS proxy can serve higher purposes - in this case, making art more accessible and discoverable for everyone with an internet connection.

## Try It Yourself

Visit the [Met Random Art Generator](https://noprofits.org/random-art-generator/) to experience the application firsthand. Experiment with different filters to discover artworks that match your interests, or simply click the button repeatedly to take a randomized tour through the Met's collection.

For developers interested in the technical aspects, read about [how the serverless CORS proxy was built](/posts/cors-proxy.html) or explore implementing similar solutions in your own projects.

The combination of a powerful API, a flexible CORS proxy, and thoughtful frontend development creates an experience that's both technically sound and genuinely delightful to use - a small but meaningful contribution to making art more accessible in the digital age.

![Assyrian relief panel showing a winged deity with a bearded face in profile, dating from 883-859 BCE](/images/Reliefpanel.png)

*Gypsum alabaster relief panel from Ancient Near Eastern Art, ca. 883-859 BCE, depicting a winged deity. Image courtesy of The Metropolitan Museum of Art.*
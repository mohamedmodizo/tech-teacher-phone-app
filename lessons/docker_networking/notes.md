# Docker Networking

**Level:** Beginner

## Simple Overview
- Docker includes a networking system for managing communications between containers, your Docker host, and the outside world.
- Docker networking is the system that enables containers to communicate with each other, the host, and external networks.
- Docker networking provides a flexible and powerful way to connect those containers together, with external systems, via whichever network model you choose, regardless of the underlying infrastructure.

## Key Concepts
1. Docker’s built-in networking features are essential for effectively isolating services, securing data flow, and orchestrating scalable microservices architectures.
2. EXPOSE vs Publishing Ports This is one of the most common Docker networking confusions: EXPOSE in a Dockerfile: documents which ports the application uses.
3. This section will provide you with basic knowledge about Docker networking, which is a key component of Docker, and how to evaluate which network configuration will work for your application needs.
4. overlay: This driver is used for multi-host networking and is the preferred choice for Docker Swarm services.

## Real-World Use
- But before getting started, if you’re totally new to Docker, I highly encourage you to check out Introduction to Docker to build a solid foundation before diving deeper into Docker networking.
- Comment Article Tags: Ar
Docker Networking - Basics, Network Types & Examples [Live Webinar] Introducing Spacelift Intelligence.
- Core Networking Concepts To understand how Docker manages this, let's look at a few core Linux networking features that Docker uses: Network Namespaces: This is a Linux kernel feature that provides network isolation.

## What To Practice
- Explain docker networking in your own words.
- Set up a tiny demo project related to docker networking.
- Identify where docker networking fits in a real product.

## Sources
- https://docs.docker.com/engine/network/
- https://tutorials.technology/tutorials/docker-container-networking.html
- https://www.geeksforgeeks.org/devops/basics-of-docker-networking/
- https://spacelift.io/blog/docker-networking
- https://www.datacamp.com/tutorial/docker-networking
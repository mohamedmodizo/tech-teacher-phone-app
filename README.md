
Tech Teacher Phone App

A lightweight local web app that helps users learn technology topics by automatically researching the web and generating structured study materials.

This project is designed to run on a phone-friendly Linux terminal environment and open in a browser on the same device. A user enters a topic such as **Python decorators**, **Docker networking**, or **Linux permissions**, and the app generates:

- lesson notes
- an ASCII learning diagram
- a Mermaid diagram file
- a quiz
- a practice lab
- a saved lesson history


Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Using the App](#using-the-app)
- [Generated Output](#generated-output)
- [API Endpoints](#api-endpoints)
- [Example Topics](#example-topics)
- [GitHub Actions Validation](#github-actions-validation)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)


Project Overview

**Tech Teacher Phone App** is an educational automation tool that turns a simple topic input into a complete mini-lesson.

Instead of manually opening search results, collecting notes, designing questions, and planning a practice task, the application does that flow automatically.

The project is especially useful for:

- self-learning
- quick topic revision
- teaching support
- idea exploration
- creating beginner-friendly learning material on the fly

It is intentionally simple, portable, and lightweight.


Features

1. Topic-based lesson generation
The user enters a tech topic and the app generates a full study package.

2. Local browser interface
The app runs a local HTTP server and opens in the browser at: http://127.0.0.1:8000


Run
python3 app.py

Then open:
http://127.0.0.1:8000

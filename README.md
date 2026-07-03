# IdeasForgeAI

IdeasForgeAI is an AI Product Factory.

It converts a simple idea into a complete product-building pipeline.

Idea to Product Brief to Master UI Image to Pixel-Matched HTML to Responsive Web App to Backend APIs to Database to Authentication to Mobile App Package to Deployment.

## Vision

IdeasForgeAI allows a creator to write a normal idea and generate a usable digital product structure.

It should support:

- SaaS tools
- AI tools
- Admin dashboards
- Landing pages
- Marketplace apps
- Internal business tools
- Mobile app screens
- Full-stack MVPs

## Core Pipeline

1. Idea Intake
2. Product Requirement Understanding
3. Feature Breakdown
4. UI Blueprint
5. Master UI Image Reference
6. Pixel-Matched HTML CSS JS
7. Responsive Web App
8. Backend API Planning
9. Database Schema Planning
10. Authentication Planning
11. Mobile App Packaging
12. Deployment
13. Export Generated App

## Folder Structure

IdeasForgeAI/
- backend/
  - agents/
  - api/
  - core/
- frontend/
  - assets/
  - pages/
- mobile/
- docs/
- prompts/
- exports/
- screenshots/
- generated-apps/

## Agent Architecture

Current starter agents:

- Idea Intake Agent
- UI Blueprint Agent
- HTML Builder Agent
- Backend API Agent
- Mobile Packager Agent
- Orchestrator Agent

## Main Rule

Keep IdeasForgeAI generic.

Do not hardcode any single business, project, or industry inside the core builder system.

Generated app names should only exist inside generated-apps.

## Local Run

cd D:\APPS\IdeasForgeAI
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend\requirements.txt
uvicorn backend.main:app --reload --port 8100

Health check:

http://127.0.0.1:8100/health

## First API

POST /api/generate

This endpoint accepts a product idea and returns a structured builder plan.

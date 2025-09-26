# KredMitra - Agentic Automation Platform (SIH Project)

This repository contains the source code for the KredMitra platform, a plugin-based, agentic automation system designed to deliver fair, transparent, and accessible financial services to India's underserved populations.

## Project Vision

KredMitra uses a sophisticated microservices architecture where specialized AI "agents" work collaboratively to build a multi-dimensional trust profile for users who are often invisible to traditional credit systems. This enables fair credit scoring, fraud detection, and personalized financial coaching.

## High-Level Architecture

The platform is built on four core pillars:

1.  **The Orchestrator (Flask API on Google App Engine):** The central "brain" that receives frontend requests and delegates tasks to the appropriate AI agent.
2.  **The Agentic Core (Docker Containers on Google Cloud Run):** A "plugin" system of independent, containerized AI microservices for specialized tasks (feature extraction, scoring, fraud detection, etc.).
3.  **The Data & Identity Hub (Supabase):** The backend-as-a-service layer providing the PostgreSQL database, user authentication, file storage, and a vector database (`pgvector`) for the RAG agent.
4.  **The Trust Layer (Hyperledger Fabric):** A private blockchain that creates an immutable, tamper-proof audit trail of every critical action, ensuring transparency and trust.

## Directory Structure

```
kredmitra-sih-project/
│
├── frontend/                   # React Single-Page Application
├── backend/                    # All backend microservices
│   ├── orchestrator-api/       # Main Flask API Gateway
│   └── agents/                 # Dockerized AI Agent microservices
├── hyperledger/                # Hyperledger Fabric Network configuration
└── README.md
```

---

## Getting Started & Deployment

### 1. Frontend (React)

The frontend is a standard React application. You will need Node.js and npm installed.

**Local Development:**
```bash
cd frontend
npm install
npm run dev
```

**Deployment:**
The frontend is configured for static hosting and can be deployed to services like Firebase Hosting, Vercel, or Netlify.

### 2. Backend (Python, Flask, Docker)

The backend consists of multiple Flask microservices, each containerized with Docker.

**Prerequisites:**
- Docker installed
- Google Cloud SDK (`gcloud`) configured (for cloud deployment)

**Running a single agent locally (example: feature extractor):**
```bash
cd backend/agents/agent_feature_extractor
docker build -t agent-feature-extractor .
docker run -p 5001:5000 -e API_KEY="YOUR_GEMINI_API_KEY" agent-feature-extractor
```

**Deployment:**
Each service (orchestrator and all agents) is designed to be deployed independently.
- **Orchestrator:** Deploy to Google App Engine using `gcloud app deploy app.yaml`.
- **Agents:** Deploy each agent to Google Cloud Run by building and pushing the Docker image to Google Artifact Registry, then deploying from there.

### 3. Hyperledger Fabric Network

The Hyperledger network provides the audit trail.

**Prerequisites:**
- Docker and Docker Compose
- Go (for chaincode development)
- Hyperledger Fabric binaries

**Starting the network (from `hyperledger/network` directory):**
```bash
./network.sh up
```
This will start the necessary Fabric nodes (peers, orderers) as defined in `docker-compose.yaml`.

**Chaincode:**
The chaincode (smart contract) is located in `hyperledger/chaincode/kredmitra-cc/go` and needs to be installed and instantiated on the network after it's running.

---
This structured setup allows for modular development, independent scaling, and a clear separation of concerns, making it an ideal architecture for the Smart India Hackathon and beyond.

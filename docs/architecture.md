# AegisFlow System Architecture & IBM Integration Guide

## Overview

AegisFlow is an AI-Powered Autonomous Supply Chain Decision Intelligence Platform designed to monitor global supply networks, predict operational disruptions, and recommend optimal recovery strategies using **IBM watsonx.ai** and **IBM Granite**.

---

## IBM AI Architecture Pipeline

```
Data Sources (ERP / News Feeds)
     ↓
IBM Data Prep Kit (Feature Normalization & Cleaning)
     ↓
Prepared Enterprise Data / Documents
     ↓
IBM watsonx.ai RAG (Enterprise Knowledge Retrieval)
     ↓
Specialized AI Agents (News, Supplier Risk, Compliance Agents)
     ↓
IBM Granite LLM (Contextual Reasoning & Synthesis)
     ↓
Decision Agent (Scenario Matrix Evaluation)
     ↓
Risk + Recommendation + Confidence + Explanation
     ↓
Executive Dashboard & Single Page Application
```

---

## Multi-Agent Architecture

1. **News Agent**: Monitors and ingests external environmental, geopolitical, and maritime traffic feeds.
2. **Supplier Risk Agent**: Evaluates supplier reliability indices, lead-times, quality scores, and port-delay vulnerabilities.
3. **Compliance Agent**: Inspects Master Supply Agreements (MSAs), Force Majeure contract clauses, penalty liabilities, and corporate multi-sourcing governance policies.
4. **Decision Agent**: Synthesizes output from all agents, queries IBM watsonx.ai RAG evidence, executes IBM Granite reasoning prompts, and evaluates 5 What-If recovery scenarios.

---

## IBM Cloud / watsonx.ai Configuration

To connect AegisFlow to your live IBM watsonx.ai deployment:

1. Create a `.env` file in the root or `backend/` directory based on `.env.example`:

```env
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_guid_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
MODEL_ID=ibm/granite-13b-instruct-v2
```

2. If environment variables are absent, AegisFlow runs using the IBM Granite analytical baseline engine, allowing zero-friction out-of-the-box demonstration while preserving strict IBM API response schemas.

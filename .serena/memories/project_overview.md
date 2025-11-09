# ConsultantOS Project Overview

## Purpose
ConsultantOS is a multi-agent AI system for generating McKinsey-grade business framework analyses. It orchestrates 5 specialized agents to produce professional PDF reports with visualizations in 30 minutes instead of 32 hours.

## Core Capabilities
- **Multi-Agent Analysis**: 5 specialized agents (Research, Market, Financial, Framework, Synthesis)
- **Business Frameworks**: Porter's 5 Forces, SWOT, PESTEL, Blue Ocean Strategy
- **Professional Reports**: PDF generation with charts and visualizations
- **Web Research**: Real-time data via Tavily API
- **Financial Analysis**: Market data via yfinance, SEC EDGAR
- **Async Processing**: Both sync and async analysis endpoints

## Key Features
- Phased execution model with parallel agent coordination
- Graceful degradation with partial results
- Multi-level caching (disk + semantic)
- Optional Firestore/Cloud Storage integration
- Rate limiting and API key authentication
- Next.js 14 frontend dashboard

## Target Users
Business analysts, consultants, and researchers needing rapid strategic analysis and professional reports.

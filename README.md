<div align="center">

# ✈️ AgentVoli

### Google Flights API for Python · AI Travel Planner Toolkit · MCP Server for Claude

**Real-time flight search in Python, wired into Claude Code via MCP — the starter kit for AI-powered travel planners.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP Ready](https://img.shields.io/badge/Claude%20Code-MCP%20ready-9146FF.svg)](https://modelcontextprotocol.io)
[![Real-time data](https://img.shields.io/badge/data-live%20Google%20Flights-success.svg)](#-features)
[![Made in Italy](https://img.shields.io/badge/made%20in-%F0%9F%87%AE%F0%9F%87%B9-009246.svg)](#-italiano--ricerca-voli-google-in-python)

[Quickstart](#-quickstart) · [Features](#-features) · [Architecture](#-architecture) · [Roadmap](#-roadmap-travel-planner-vision) · [Italiano](#-italiano--ricerca-voli-google-in-python)

</div>

---

## 🚀 What is AgentVoli?

**AgentVoli** is an open-source toolkit that turns the unofficial **Google Flights API** into a working **AI travel planner**, ready to plug into [Claude Code](https://claude.com/claude-code) via the Model Context Protocol (MCP).

Out of the box you get:

- 🔎 **Real-time flight search** powered by Google Flights (round-trip, one-way, multi-city)
- 🤖 **MCP server pre-wired** — Claude calls `search_flights`, `search_dates`, `find_airports` as native tools
- 📅 **Weekend scanner** — finds the cheapest short-haul return from multiple Italian airports
- 🌍 **Route matrix scripts** — built-in examples (e.g. Rome → Malta, Italy → Europe weekend trips)
- 💸 **Free-tier API recipes** — Open-Meteo, Geoapify, Nominatim, Ticketmaster, Groq + a `.env.example` mapping every key needed to grow into a full **AI-powered travel planner**

> Think of it as the "hello world" your Marrakech-on-a-budget agent has been waiting for.

---

## ⚡ Quickstart

### 1. Clone and install

```bash
git clone https://github.com/uppifyagency/AgentVoli.git
cd AgentVoli
uv sync              # installs the flights Python library + the MCP server
```

> No `uv`? Use `pip install -e ".[mcp]"` (or `pipx install flights` for the CLI only).

### 2. Run your first search

```bash
uv run python agentvoli_malta.py
```

Output (live data, prices vary):

```
Scansione 12 combinazioni FCO <-> MLA (andata e ritorno)...

  2026-06-03 -> 2026-06-09: 83 opzioni, min EUR 65
  ...

TOP 12 OFFERTE  ROMA (FCO) <-> MALTA (MLA)
================================================================================
 1. EUR 65
    Andata:  Wed 03-Jun 17:00 -> 18:25  AZ 884  (1h25m, diretto)
    Ritorno: Tue 09-Jun 20:40 -> 22:15  FR 8561  (1h35m, diretto)
```

### 3. Wire the MCP server into Claude Code

Open this project in Claude Code — the bundled [`.mcp.json`](.mcp.json) registers the **flight-search MCP server** automatically. Approve it once and Claude gets first-class flight-search tools (`search_flights`, `search_dates`, `find_airports`).

---

## 🌟 Features

### 🔌 Google Flights API in Python

Direct access to Google Flights data through reverse-engineered endpoints — **no API key, no rate-limited free tier, no paid plan**. Round-trip, one-way, multi-city, premium cabins, alliance filters, per-flight booking deep-links.

### 🧠 MCP-native AI Travel Planner

Drop the bundled MCP server into Claude Code, Claude Desktop, Cursor, or any other STDIO-MCP client. Your AI agent now searches real flights without a single line of glue code.

### 🇮🇹 Real-world Italian routes baked in

Working scripts for the patterns Italian travelers actually search:

| Script | What it does |
|---|---|
| [`agentvoli_malta.py`](agentvoli_malta.py) | Rome (FCO) ⇄ Malta (MLA) round-trip matrix, today/tomorrow + 6 return dates |
| [`agentvoli_weekend_scan.py`](agentvoli_weekend_scan.py) | Saturday → Sunday weekend escape from Pisa/Florence/Bologna to 14 European cities, ≤3h flight |
| [`agentvoli_rerun_missing.py`](agentvoli_rerun_missing.py) | Rate-limit-aware retry of the routes Google throttled in the first pass |

### 🌐 Free-API recipe book

[`.env.example`](.env.example) maps every free-tier key needed to grow into a full travel planner: weather, restaurants, points of interest, events, FX rates, destination imagery, LLM orchestration. **No paid SerpAPI or Amadeus required.**

### ⏱️ Dynamic dates

All scripts compute `date.today()` at runtime — no more hard-coded dates that rot after a week.

---

## 🏗️ Architecture

```
┌────────────────────────┐
│      Claude Code       │
│  (or Claude Desktop /  │
│   Cursor / any MCP)    │
└──────────┬─────────────┘
           │ MCP / stdio
           ▼
┌────────────────────────┐         ┌─────────────────────┐
│  Flight Search MCP     │ ───►    │  Google Flights     │
│      (FastMCP)         │         │  (reverse-engineered│
│                        │ ◄───    │   protobuf API)     │
└──────────┬─────────────┘         └─────────────────────┘
           │
           ▼
┌────────────────────────┐
│  AgentVoli scripts     │
│  - malta.py            │
│  - weekend_scan.py     │
│  - rerun_missing.py    │
└──────────┬─────────────┘
           │
           ▼ (future)
┌────────────────────────────────────────────────────────┐
│  Free-tier travel APIs (see .env.example)              │
│  Open-Meteo · Geoapify · Nominatim · Ticketmaster      │
│  Foursquare · OpenTripMap · Pexels · open.er-api.com   │
└────────────────────────────────────────────────────────┘
```

---

## 🗺️ Roadmap (travel-planner vision)

The end-goal: a prompt like *"Rome → Marrakech, 21–24 May, €300 budget, flights + hotel + experiences"* yields a complete itinerary with **real prices, Google-Places restaurant picks, and a day-by-day plan that fits the budget.**

| Component | Status | Notes |
|---|---|---|
| ✈️ Real-time flight search | ✅ shipped | Google Flights via Python |
| 🤖 Claude Code MCP integration | ✅ shipped | `.mcp.json` |
| 🇮🇹 Italian route examples | ✅ shipped | Malta, weekend short-haul |
| ☀️ Weather (Open-Meteo) | 🟡 next | zero-key, what-to-pack agent |
| 📍 POIs & restaurants (Geoapify) | 🟡 next | free 3k req/day |
| 💱 Multi-currency budget | 🟡 next | open.er-api.com, keyless |
| 🏨 Hotel pricing | 🔴 hard | no real free API — Booking.com affiliate links as fallback |
| 🎟️ Activities & events | 🟡 planned | Ticketmaster + OpenTripMap |
| 🧠 LLM orchestrator | 🟡 planned | Groq / Gemini Free tier for $0 ops |

---

## 🧰 Free APIs reference

A curated set of free-tier APIs perfect for AI travel agents. Full setup in [`.env.example`](.env.example).

| API | Free tier | Card required? | Use case |
|---|---|---|---|
| **Open-Meteo** | unlimited | no | weather forecast |
| **Nominatim** (OSM) | 1 req/sec | no | geocoding |
| **Geoapify Places** | 3,000 req/day | no | POIs, restaurants, isochrones |
| **OpenTripMap** | 5,000 req/day | no | tourist attractions |
| **Foursquare Places** | 950 req/day | no | restaurant data |
| **Ticketmaster Discovery** | 5,000 req/day | no | live events |
| **REST Countries** | unlimited | no | country metadata |
| **open.er-api.com** | unlimited | no | FX rates |
| **Pexels** | unlimited | no | destination images |
| **Google Places (New)** | $200/month credit | **yes** | premium POI data |
| **Groq / Gemini Free** | generous free tier | no | LLM orchestration |

---

## 🐍 Code example: search flights in 12 lines

```python
from datetime import date, timedelta
from fli.models import Airport, FlightSearchFilters, FlightSegment, MaxStops, PassengerInfo, SeatType, SortBy, TripType
from fli.search import SearchFlights

tomorrow = (date.today() + timedelta(days=1)).isoformat()
filters = FlightSearchFilters(
    trip_type=TripType.ONE_WAY,
    passenger_info=PassengerInfo(adults=1),
    seat_type=SeatType.ECONOMY,
    stops=MaxStops.NON_STOP,
    sort_by=SortBy.CHEAPEST,
    flight_segments=[FlightSegment(
        departure_airport=[[Airport.FCO, 0]],
        arrival_airport=[[Airport.MLA, 0]],
        travel_date=tomorrow,
    )],
)
for flight in SearchFlights().search(filters)[:5]:
    print(f"EUR {flight.price:.0f}  {flight.legs[0].airline.name} {flight.legs[0].flight_number}")
```

---

## 🇮🇹 Italiano — Ricerca voli Google in Python

**AgentVoli** è il toolkit open-source per la **ricerca voli in tempo reale** direttamente da Python e da Claude Code via MCP. Sfrutta endpoint Google Flights non ufficiali per ottenere prezzi, orari e disponibilità senza chiavi API a pagamento.

### Cosa puoi fare oggi

- 🔎 **Ricerca voli Google** (FCO, MXP, BGY, CTA, NAP, e tutti gli aeroporti supportati) con prezzi reali e tempi di volo
- 📅 **Scan del weekend** — trova i voli short-haul più economici dall'Italia (Pisa, Firenze, Bologna) verso 14 capitali europee, andata sabato e ritorno domenica sera
- 🤖 **Agente voli per Claude Code** — il server MCP è già configurato in [`.mcp.json`](.mcp.json), basta lanciare Claude e approvare
- 🇲🇹 **Esempio Roma → Malta** completo, con matrice andata/ritorno dinamica

### Come funziona

1. Clona il repo e installa con `uv sync`
2. Lancia `uv run python agentvoli_malta.py` per vedere i voli FCO ⇄ MLA reali di oggi
3. Apri il progetto in Claude Code → l'agente AI ora cerca voli direttamente

### Visione: travel planner AI italiano

L'obiettivo è far diventare AgentVoli un **planner di viaggio AI** in stile *"voglio andare da Roma a Marrakech, 4 giorni, budget 300 €"* — l'agente compone voli + hotel + ristoranti (via Google Places) + esperienze, rispettando il budget. Vedi la [roadmap](#-roadmap-travel-planner-vision) per lo stato dei pezzi mancanti.

---

## 📜 License

[MIT](LICENSE) — do what you want, attribution appreciated.

Third-party dependencies retain their own licenses; respect them when redistributing.

---

<div align="center">

**Built with ✈️ in Italy by [@uppifyagency](https://github.com/uppifyagency)**

If AgentVoli saved you from clicking through Google Flights 47 times, [drop a star](https://github.com/uppifyagency/AgentVoli) ⭐

</div>

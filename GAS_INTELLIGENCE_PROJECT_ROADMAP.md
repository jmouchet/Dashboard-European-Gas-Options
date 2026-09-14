# Gas Intelligence Platform — Project & Learning Roadmap

**Purpose:** Build a personal, long-term European gas and gas-options intelligence platform that simultaneously improves day-to-day market awareness and compounds domain expertise.

**Core stack:** Streamlit + Python + Supabase/PostgreSQL + Plotly + GitHub  
**Initial constraint:** Free/public data only. No private, confidential, or employer-sensitive information should be stored.

---

# 1. North Star

The platform should progressively become a personal operating system for European gas markets.

It should help answer five questions every day:

1. **What changed?**
2. **Why did it change?**
3. **What looks abnormal?**
4. **What could happen next?**
5. **What should I learn from today?**

The application should not become a passive dashboard.

Its purpose is to create a feedback loop:

> Data → Observation → Interpretation → Hypothesis → Market outcome → Post-mortem → Knowledge

Over time, the system should accumulate three forms of capital:

- **Market data**
- **Structured knowledge**
- **Personal judgment**

---

# 2. Design Principles

## 2.1 Start usable, not complete

Every version must already be useful in the morning.

Do not wait until all APIs, analytics, pages, and AI functions are finished.

## 2.2 Everything important should have history

A number without history has limited value.

Whenever possible, store enough historical observations to calculate:

- rolling averages
- percentiles
- z-scores
- seasonality
- deviations
- correlations
- historical analogues

## 2.3 Separate facts, interpretation, and hypotheses

The app should distinguish between:

**Fact**
> Norwegian flows fell 28 mcm/d.

**Interpretation**
> The outage tightens the prompt balance.

**Hypothesis**
> Front-month upside skew may outperform because the market is underpricing outage-extension risk.

This distinction is central to developing judgment.

## 2.4 Learning should be connected to live markets

The knowledge system should not be an independent textbook.

When an LNG outage occurs, the application should surface learning material on:

- LNG supply chains
- liquefaction capacity
- TTF/JKM arbitrage
- shipping economics
- volatility implications

This turns daily markets into a curriculum.

---

# 3. High-Level Application Structure

Recommended Streamlit navigation:

```text
GAS INTELLIGENCE

01  Morning
02  Markets
03  Fundamentals
04  Physical System
05  Options & Volatility
06  Events
07  Companies
08  Intelligence
09  Knowledge Wiki
10  Daily Learning
11  Quiz & Review
12  Journal
13  Data / Admin
```

Each page has a different purpose.

---

# 4. Page 01 — Morning Dashboard

This is the application homepage.

The goal is to understand the market in less than 10 minutes.

## Core blocks

### Market

- TTF prompt
- relevant futures
- main calendar spreads
- daily change
- weekly change
- historical percentile

### Fundamentals

- EU storage
- storage vs 5Y average
- storage vs previous year
- storage daily change
- Norway flows
- LNG send-out
- major pipeline flows
- major outages

### Weather

- European weighted temperature
- HDD
- weather revision
- next 7 days
- next 15 days
- model dispersion when available

### Power

- demand
- wind
- solar
- nuclear availability
- thermal residual demand

### Options

Initially manual if professional implied-volatility data is unavailable.

Track:

- M1 ATM
- M2 ATM
- Q1 ATM
- Winter ATM
- 25D risk reversal
- optionally butterfly
- realized volatility

### Alerts / abnormalities

Examples:

- Norway flows < 5th percentile
- Storage withdrawal > 2 standard deviations
- Weather revision unusually large
- TTF rally inconsistent with fundamentals
- Realized volatility accelerating
- Prompt/calendar spread at extreme percentile

### Today's questions

The system should automatically generate 3–5 questions to investigate.

Example:

> Why did prompt gas rally despite a warmer weather revision?

> Is the increase in front-end volatility consistent with previous Norwegian outages?

> What would make LNG cargoes switch from Europe to Asia at current TTF/JKM spreads?

---

# 5. Page 02 — Markets

A flexible market explorer.

## Instruments

Initially:

- TTF futures
- main TTF calendar spreads
- EUA
- Henry Hub if available
- JKM proxies if available
- power proxies if available

## Functions

For every series:

- date range
- normalized performance
- rolling change
- rolling percentile
- z-score
- rolling volatility
- comparison with another variable
- seasonal comparison

Examples:

> TTF M1 vs storage percentile

> Winter/Summer spread vs storage level

> TTF realized volatility vs Norway flow disruptions

---

# 6. Page 03 — Fundamentals

Central European gas balance page.

Sections:

## Supply

- Norway
- LNG
- North Africa
- Azerbaijan
- domestic production
- remaining Russian flows where relevant

## Demand

Initially estimated through proxies:

- weather-sensitive demand
- industrial demand
- gas-fired power demand
- exports
- storage injection/withdrawal

## Balance

Conceptual equation:

```text
Supply - Demand = storage / balancing residual
```

The long-term goal is to create your own daily balance estimate.

Store both:

- model forecast
- realized observations

This allows model-error analysis later.

---

# 7. Page 04 — Physical System

This is the interactive gas-market encyclopedia.

## Categories

- production fields
- processing plants
- pipelines
- interconnectors
- LNG terminals
- storage facilities
- gas hubs

## Asset profile

Each asset should contain:

```text
asset_id
name
asset_type
country
operator
capacity
connected_market
importance
description
source
latitude
longitude
```

Optional later:

```text
normal_utilization
historical_outages
current_status
connected_assets
```

## Objective

You should eventually recognize important infrastructure immediately.

Examples:

- Troll
- Nyhamna
- Kollsnes
- Langeled
- Zeebrugge
- Gate
- Dunkerque LNG
- Rehden

---

# 8. Page 05 — Options & Volatility

This page should progressively become central.

## Stage 1

Manual collection:

```text
date
underlying
expiry
atm_vol
25d_rr
25d_bf
notes
```

## Stage 2

Add:

- realized volatility
- implied vs realized
- volatility term structure
- skew history
- percentile ranks

## Stage 3

Full surface representation when data becomes available:

```text
date
expiry
strike
delta
call_put
bid_vol
ask_vol
mid_vol
forward
```

## Analytics

- ATM term structure
- skew term structure
- rolling percentile
- vol change
- spot/vol relationship
- skew/spot relationship
- implied/realized spread
- event studies

## Learning objective

Do not just display volatility.

Every move should invite interpretation:

> What uncertainty is the market pricing?

> Which tail is expensive?

> Why is this maturity affected?

> What physical event could justify the change?

---

# 9. Page 06 — Events

Build an event database from the beginning.

Every significant event should have:

```text
event_id
timestamp
category
entity
headline
description
source
expected_duration
estimated_physical_impact
affected_tenors
confidence
market_price_before
market_price_after_1h
market_price_after_1d
vol_before
vol_after
interpretation
lesson
```

Categories:

- Norway outage
- LNG outage
- pipeline disruption
- storage
- weather
- geopolitics
- sanctions
- regulatory
- power
- nuclear
- industrial demand
- shipping
- macro

## Long-term objective

Build historical analogue analysis.

Example:

> Show Norwegian outages between 40 and 80 mcm/d occurring during periods when storage was below the 30th percentile.

Then analyze:

- median prompt return
- median spread move
- realized volatility
- implied-volatility reaction

---

# 10. Page 07 — Companies

Only public information.

The purpose is to understand market participants economically.

## Company profile

```text
company_id
name
country
company_type
business_model
gas_exposure
lng_exposure
power_exposure
storage_exposure
production_exposure
carbon_exposure
public_hedging_policy
annual_report_url
investor_relations_url
notes
```

Possible company types:

- producer
- utility
- LNG portfolio player
- commodity merchant
- industrial
- power generator
- infrastructure operator
- trading house

## Key question

For each company:

> How does this company make and lose money when European gas moves?

Then:

> What risks might it rationally hedge?

No assumption should be presented as private knowledge.

Clearly distinguish:

- public fact
- reasonable inference
- unknown

---

# 11. Page 08 — Intelligence

This page converts raw observations into analysis.

Sections:

## Signals

Quantitative abnormalities:

- z-score
- percentile
- deviation from seasonality
- correlation breakdown

## Cross-market inconsistencies

Examples:

- warmer weather + higher prompt
- higher storage + stronger winter spread
- improving Norwegian supply + rising prompt volatility

These contradictions often generate the best questions.

## Scenarios

Maintain scenario trees.

Example:

```text
Scenario: Cold January + Norwegian outage

Probability:
Physical impact:
TTF impact:
Curve impact:
Vol impact:
Skew impact:
Key confirmation signals:
Invalidation signals:
```

## Historical analogues

Query previous periods with similar states.

---

# 12. Page 09 — Knowledge Wiki

This is the permanent learning encyclopedia.

It should be integrated into the same application.

## Main curriculum tree

### GAS FUNDAMENTALS

1. European gas system
2. Units and conversions
3. Supply
4. Demand
5. Storage
6. LNG
7. Pipelines
8. Hubs
9. Balancing
10. Seasonality
11. Weather
12. Power interaction
13. Carbon interaction
14. Geopolitics

### LNG

1. Liquefaction
2. Shipping
3. Boil-off
4. Regasification
5. Freight
6. Destination flexibility
7. TTF/JKM arbitrage
8. US LNG economics
9. Qatar
10. Portfolio players

### OPTIONS

1. Payoffs
2. Put-call relationships
3. Black-76
4. Delta
5. Gamma
6. Vega
7. Theta
8. Volatility
9. Realized volatility
10. Implied volatility
11. Skew
12. Smile
13. Term structure
14. Risk reversal
15. Butterfly
16. Gamma scalping
17. Vol-of-vol
18. Barrier options
19. Asian options
20. Spread options

### MARKET MECHANICS

1. Futures
2. OTC markets
3. Clearing
4. Margin
5. Bid/ask
6. Liquidity
7. Market makers
8. Brokers
9. Hedgers
10. Speculators
11. Positioning
12. Order flow
13. Price discovery

### QUANTITATIVE TOOLKIT

1. Probability
2. Distributions
3. Expected value
4. Variance
5. Correlation
6. Regression
7. Time series
8. Monte Carlo
9. Percentiles
10. Z-scores
11. Seasonality
12. Event studies

### HISTORICAL EPISODES

Examples:

- 2021 European gas crisis
- Russia/Ukraine escalation
- Nord Stream
- Freeport LNG outage
- major Norwegian outages
- extreme weather episodes
- storage scares

---

# 13. Wiki Article Format

Every article should follow a standardized structure.

Example:

## Title: Winter/Summer Spread

### Definition

Short explanation.

### Why it exists

Economic intuition.

### Physical mechanism

How storage, supply, and demand influence it.

### Trading interpretation

What widening/narrowing may signal.

### Options implication

How it can interact with volatility.

### Worked example

Use numbers.

### Historical example

Real market episode.

### Common mistakes

Misconceptions.

### Related concepts

Internal links.

### Sources

Public references.

### Questions

Questions associated with the article.

### Mastery

```text
Not started
Learning
Familiar
Strong
Mastered
```

---

# 14. Knowledge Database Schema

Suggested table:

## `knowledge_articles`

```text
id
slug
title
category
subcategory
difficulty
summary
content_markdown
importance_score
source_urls
created_at
updated_at
```

## `knowledge_links`

```text
source_article_id
target_article_id
relationship
```

Examples:

```text
TTF → European gas hubs
Storage → Winter/Summer spread
Gamma → Gamma scalping
LNG shipping → TTF/JKM arbitrage
```

This creates a knowledge graph over time.

---

# 15. Page 10 — Daily Learning

This should make learning unavoidable.

Every morning the platform generates a **Daily Learning Pack**.

Target completion time:

**15–25 minutes**

## Structure

### 1. Three facts

Example:

> 1 bcm of natural gas is approximately 10.5–11 TWh depending on gas quality.

> Roughly X% of EU storage capacity is concentrated in countries A/B/C.

> A 25-delta risk reversal compares the implied volatility of an OTM call and put.

Facts should be:

- relevant
- precise
- useful
- connected to curriculum topics

Avoid trivia.

### 2. One concept

Example:

**Why storage creates optionality**

3–5 minute explanation.

### 3. One chart

Example:

Historical EU storage trajectory.

Question:

> What do you notice?

Then reveal interpretation.

### 4. One market mechanism

Example:

> Why can a Norwegian outage affect front-month volatility more than Winter volatility?

### 5. One calculation

Example:

> TTF rises from €32/MWh to €35/MWh. What is the percentage move?

Later:

> Estimate the P&L of a delta position.

### 6. One historical episode

Short description of an important past market event.

### 7. Five-question mini quiz

Generated from previously learned material.

---

# 16. Daily Learning Algorithm

Do not generate random content.

Use a curriculum and spaced repetition.

Each knowledge item gets:

```text
importance
difficulty
last_seen
times_seen
times_correct
times_wrong
mastery_score
```

Suggested priority:

```text
learning_priority =
importance
× weakness
× forgetting_factor
× market_relevance
```

Where:

**importance**

Core concepts receive more weight.

**weakness**

Incorrect questions increase priority.

**forgetting factor**

Older material becomes more likely to return.

**market relevance**

If LNG is driving today's market, LNG concepts get temporarily boosted.

This last factor creates a very powerful learning loop.

---

# 17. Page 11 — Quiz & Review

This is separate from Daily Learning.

The purpose is deliberate recall.

## Quiz modes

### Daily

5–10 questions.

### Weekly

20–30 questions.

### Topic

Example:

> Quiz me only on storage.

### Difficulty

- beginner
- intermediate
- advanced
- broker-level

### Calculation mode

Only numerical questions.

### Market reasoning mode

Questions requiring explanation.

Example:

> European storage is low, weather turns colder, but TTF prompt falls. Give at least four possible explanations.

This is more valuable than memorization.

---

# 18. Question Types

Use multiple formats.

## Recall

> What does LNG stand for?

Useful only for basic facts.

## Explanation

> Why does lower storage increase the convexity of gas prices?

## Calculation

> Convert 50 mcm/d into approximate TWh/day.

## Market reasoning

> Norway loses 60 mcm/d for five days in January. What parts of the curve should be most sensitive and why?

## Options reasoning

> Spot rallies sharply while ATM volatility falls. Give possible explanations.

## Comparison

> Compare an LNG terminal outage with a Norwegian pipeline outage.

## Historical

> Why did Freeport LNG matter for TTF?

## Reverse questions

Instead of:

> What causes contango?

Ask:

> If the curve is in strong contango, what economic incentives does this create?

---

# 19. Quiz Database

## `questions`

```text
id
article_id
question_type
difficulty
question
answer
explanation
importance
created_at
```

## `quiz_attempts`

```text
id
question_id
attempt_date
user_answer
score
confidence
response_time
```

## `learning_progress`

```text
article_id
mastery_score
times_seen
times_correct
times_wrong
last_seen
next_review
```

---

# 20. Confidence Tracking

For every question, record both:

- whether the answer was correct
- how confident you were

Possible confidence:

```text
1 = Guess
2 = Unsure
3 = Reasonably sure
4 = Very sure
```

This identifies dangerous knowledge gaps.

The most important mistake is:

> Wrong + very confident

The learning engine should heavily prioritize these questions.

---

# 21. Page 12 — Journal

This may eventually become the most valuable part of the project.

Do not store confidential employer information.

## Morning thesis

Every morning:

```text
Market regime:
Bull/base/bear scenarios:
Important variables:
Expected volatility:
Expected skew:
Main risk:
Confidence:
```

## Intraday observations

Record significant public-market observations.

## Evening review

Answer:

### What happened?

### What surprised me?

### What did I misunderstand?

### What did I predict correctly?

### What would I watch next time?

### What new concept should be added to the Wiki?

---

# 22. Prediction Tracking

Create a structured prediction table.

## `predictions`

```text
id
date
prediction
category
horizon
confidence
expected_direction
expected_magnitude
reasoning
result
score
post_mortem
```

Examples:

> TTF M1 will outperform M2 over the next 3 sessions.

> Front-month realized volatility will increase.

> Storage will finish the week below consensus trajectory.

The goal is not to prove you are right.

The goal is to **calibrate judgment**.

After one year, analyze:

- accuracy by confidence
- accuracy by topic
- recurring biases
- strongest signals
- weakest signals

---

# 23. Daily Professional Development Routine

The platform should support a repeatable routine.

## Morning — 45 to 60 minutes

### 15 min — Market dashboard

Review:

- TTF
- curve
- storage
- Norway
- LNG
- weather
- power
- events

### 10 min — Explain the market yourself

Before reading external commentary, write:

> What do I think is happening?

This prevents passive dependence on other people's narratives.

### 15–20 min — Daily Learning Pack

- facts
- concept
- calculation
- historical episode
- quiz

### 5 min — Morning hypothesis

Write one falsifiable market hypothesis.

---

# 24. During the Day

Whenever something moves significantly, ask:

1. What moved?
2. What triggered it?
3. Which part of the balance changed?
4. Which tenor reacted?
5. What happened to volatility?
6. Was the reaction logical?
7. Have I seen this before?

Add only meaningful events to the database.

Avoid recording noise.

---

# 25. Evening — 20 to 30 Minutes

## Market replay

Look at the day chronologically.

## Surprise log

Write the biggest surprise.

## Hypothesis review

Was the morning hypothesis:

- correct
- partly correct
- wrong
- impossible to evaluate

## One learning addition

Add or improve one Wiki article.

This creates:

~250 meaningful knowledge improvements per working year.

---

# 26. Weekly Routine

Approximate target:

**4–6 hours outside live-market work**

## 1 physical topic

Examples:

- Norwegian production system
- German storage
- LNG shipping
- French gas network

## 1 options topic

Examples:

- skew
- gamma scalping
- forward volatility
- barrier risk

## 1 historical episode

Examples:

- August 2022 TTF spike
- Freeport outage
- Beast from the East

## 1 company

Understand the business model of one major participant.

## 1 technical improvement

Add one meaningful tool or dataset to the platform.

## Weekly quiz

20–30 questions.

## Weekly market review

Answer:

> What did the market teach me this week?

---

# 27. Monthly Routine

At month-end produce a **Market Learning Review**.

Sections:

### Biggest market events

### Best prediction

### Worst prediction

### Biggest misconception corrected

### New physical-system knowledge

### New options knowledge

### New company knowledge

### Important charts

### Metrics

- questions answered
- quiz accuracy
- Wiki articles added
- concepts mastered
- predictions made
- prediction calibration

---

# 28. Progressive Curriculum — First 6 Months

## Month 1 — Gas System

Learn:

- units
- European hubs
- major pipelines
- Norway
- LNG terminals
- storage
- basic supply/demand

Build:

- Morning page
- storage ingestion
- infrastructure database
- basic Wiki

## Month 2 — Gas Balance

Learn:

- residential demand
- HDD
- industrial demand
- power demand
- injections/withdrawals
- balancing

Build:

- weather ingestion
- fundamental dashboard
- daily balance framework

## Month 3 — Futures & Curve

Learn:

- futures
- settlement
- calendar spreads
- contango
- backwardation
- carry
- storage economics

Build:

- market explorer
- spread analytics
- percentile calculations

## Month 4 — Options Foundations

Learn:

- payoffs
- Black-76 intuition
- delta
- gamma
- vega
- theta
- realized vs implied vol

Build:

- manual options database
- vol dashboard
- realized vol analytics

## Month 5 — Volatility

Learn:

- skew
- smile
- term structure
- risk reversal
- butterfly
- gamma scalping
- vol-of-vol

Build:

- vol-history analytics
- skew tracking
- event/vol relationships

## Month 6 — Integrated Market Reasoning

Learn:

- LNG arbitrage
- gas-power
- carbon
- positioning
- market microstructure
- historical crises

Build:

- event engine
- historical analogues
- client/company public research
- scenario analysis

---

# 29. Free Data Sources — Initial Target List

Data access and terms can change, so each integration should include a source note and date of implementation.

## European gas

### GIE AGSI
Storage.

### GIE ALSI
LNG.

### ENTSOG Transparency Platform
Pipeline and transmission data.

### Gassco
Norwegian infrastructure and maintenance information where publicly available.

## Power

### ENTSO-E Transparency Platform

- load
- generation
- wind
- solar
- nuclear
- cross-border data

## Weather

### Open-Meteo

Use for:

- forecasts
- historical weather
- archived forecasts where available

## Public companies

- annual reports
- investor presentations
- regulatory filings
- company websites

## News

Initially rely on:

- public RSS feeds where legally available
- company announcements
- system operators
- public agencies

Do not create fragile scraping infrastructure before necessary.

---

# 30. Supabase Architecture

Suggested schemas/tables.

## Market

```text
market_prices
market_curves
option_marks
realized_volatility
```

## Fundamentals

```text
storage_daily
lng_daily
gas_flows
weather_daily
weather_forecasts
power_daily
```

## Reference

```text
assets
companies
countries
data_sources
```

## Intelligence

```text
events
signals
scenarios
predictions
```

## Knowledge

```text
knowledge_articles
knowledge_links
questions
quiz_attempts
learning_progress
daily_learning
```

## Personal non-sensitive notes

```text
journal_entries
research_notes
```

---

# 31. Data Engineering Principles

Every observation should ideally contain:

```text
timestamp
value
unit
source
retrieved_at
```

Never overwrite raw observations unnecessarily.

Prefer:

```text
raw → cleaned → derived
```

Keep calculations reproducible.

Example:

```text
raw_storage
    ↓
clean_storage
    ↓
storage_percentiles
    ↓
dashboard
```

---

# 32. Repository Structure

Recommended structure:

```text
gas-intelligence/

│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── pages/
│   ├── 01_Morning.py
│   ├── 02_Markets.py
│   ├── 03_Fundamentals.py
│   ├── 04_Physical_System.py
│   ├── 05_Options.py
│   ├── 06_Events.py
│   ├── 07_Companies.py
│   ├── 08_Intelligence.py
│   ├── 09_Knowledge.py
│   ├── 10_Daily_Learning.py
│   ├── 11_Quiz.py
│   ├── 12_Journal.py
│   └── 13_Admin.py
│
├── components/
│   ├── cards.py
│   ├── charts.py
│   ├── tables.py
│   └── navigation.py
│
├── data/
│   ├── loaders/
│   │   ├── gie.py
│   │   ├── entsog.py
│   │   ├── entsoe.py
│   │   └── weather.py
│   │
│   ├── cleaning/
│   └── reference/
│
├── analytics/
│   ├── storage.py
│   ├── balance.py
│   ├── weather.py
│   ├── curves.py
│   ├── volatility.py
│   ├── anomalies.py
│   ├── event_studies.py
│   └── scenarios.py
│
├── learning/
│   ├── curriculum.py
│   ├── spaced_repetition.py
│   ├── quiz_engine.py
│   └── daily_pack.py
│
├── database/
│   ├── client.py
│   ├── queries.py
│   └── schema.sql
│
├── utils/
│   ├── config.py
│   ├── dates.py
│   ├── units.py
│   └── logging.py
│
└── tests/
```

---

# 33. Development Roadmap

## V0.1 — Skeleton

Deliver:

- Streamlit multipage app
- Supabase connection
- clean navigation
- Morning page
- Knowledge page
- Journal
- manual data input

**Goal:** Start using it immediately.

---

## V0.2 — Storage + LNG

Deliver:

- GIE ingestion
- historical storage charts
- LNG data
- storage seasonality
- percentile calculations

Learning:

- storage Wiki
- first 50 questions

---

## V0.3 — Weather

Deliver:

- forecast ingestion
- weighted European temperature
- HDD
- forecast revisions

Learning:

- weather/gas curriculum

---

## V0.4 — Physical System

Deliver:

- infrastructure database
- asset pages
- European gas system map

Learning:

- asset flashcards
- physical-system quiz

---

## V0.5 — Flows

Deliver:

- ENTSOG integration
- key pipeline monitoring
- Norway dashboard

Learning:

- pipeline system
- Norwegian infrastructure

---

## V0.6 — Market Analytics

Deliver:

- price history
- calendar spreads
- rolling realized volatility
- percentiles
- z-scores

---

## V0.7 — Options

Deliver:

- manual option mark entry
- ATM history
- skew history
- realized/implied comparison

Learning:

- options curriculum
- options quizzes

---

## V0.8 — Events

Deliver:

- event database
- event tagging
- market-response tracking

Learning:

- historical episodes

---

## V0.9 — Intelligence

Deliver:

- anomaly engine
- historical analogue search
- scenarios
- structured predictions

---

## V1.0 — Integrated Learning Engine

Deliver:

- Daily Learning Pack
- dynamic quiz
- mastery scores
- spaced repetition
- market-relevance weighting
- weekly learning report

At this stage the platform becomes both:

**a market terminal**

and

**a personal gas-options university.**

---

# 34. Daily Learning Generation — Practical Implementation

Initially do **not** rely entirely on generative AI.

Use a curated knowledge database.

The system selects:

```text
3 facts
1 concept
1 chart
1 calculation
1 historical event
5 quiz questions
```

based on:

- curriculum progression
- mastery
- time since last review
- recent mistakes
- today's market themes

AI can later help generate:

- alternate explanations
- new question wording
- reasoning questions
- case studies

But the underlying facts should be sourced and stored.

---

# 35. Example Daily Learning Pack

## Daily Pack — Example

### FACT 1

European storage is used not only for seasonal balancing but also to respond to short-term fluctuations in supply and demand.

### FACT 2

The TTF futures curve should not be interpreted simply as the market's expected future spot path.

### FACT 3

Gamma measures the rate at which delta changes as the underlying price changes.

---

### CONCEPT

## Why Winter/Summer spreads matter

If winter gas is expensive relative to summer gas, the market creates an incentive to buy summer gas, store it, and sell winter gas—subject to storage capacity, injection/withdrawal constraints, losses, financing costs, and optionality.

---

### MARKET QUESTION

Norwegian supply falls sharply today.

Which should react more strongly:

A. Cal+3 TTF  
B. Front-month TTF

Why?

---

### CALCULATION

TTF rises from €30/MWh to €33/MWh.

Percentage move:

```text
(33 - 30) / 30 = 10%
```

---

### HISTORICAL EPISODE

Study one major Norwegian outage and record:

- size
- duration
- storage situation
- spot reaction
- curve reaction
- volatility reaction

---

### QUIZ

1. What economic function does storage perform?
2. Why can the prompt market react more than deferred gas to an outage?
3. What is gamma?
4. What does backwardation mean?
5. Why is the forward curve not simply a price forecast?

---

# 36. Long-Term Outcome

After one year of disciplined use:

Approximate accumulated output could be:

- 200+ Wiki articles
- 1,000+ reviewed questions
- 200+ daily hypotheses
- 50+ studied companies/assets
- hundreds of market events
- a proprietary history of personal option observations
- systematic post-mortems
- measurable expertise progression

After several years, the platform should allow you to ask questions such as:

> How does TTF prompt usually behave when Norwegian flows fall >50 mcm/d during low-storage regimes?

> Which historical periods look most similar to today?

> Which concepts do I consistently misunderstand?

> Which types of market prediction am I best at?

> Which parts of the volatility surface tend to react most strongly to specific fundamental shocks?

At that point, the software is no longer merely a dashboard.

It is a structured record of your development as a gas-options market professional.

---

# 37. Immediate First Build

Do not start with APIs.

Start with this minimal production version:

### Page 1 — Morning
Manual market/fundamental snapshot.

### Page 2 — Knowledge
Ten initial Wiki articles.

### Page 3 — Daily Learning
Static selection from those articles.

### Page 4 — Quiz
Twenty initial questions.

### Page 5 — Journal
Morning thesis + evening review.

### Supabase tables

Create:

```text
knowledge_articles
questions
quiz_attempts
learning_progress
journal_entries
predictions
```

Use the system manually for several days.

Then automate the data one source at a time.

This guarantees that technical development remains driven by actual market usefulness rather than by engineering for its own sake.

---

# 38. Guiding Rule

Whenever you consider adding a feature, ask:

> Will this make me understand the gas market, options market, or my own reasoning better?

If the answer is no, it is probably not a priority.

The platform succeeds if, after years of use, it has made you:

- faster at identifying what matters
- better at explaining why markets move
- more technically competent in options
- more knowledgeable about the physical gas system
- better calibrated in your forecasts
- better at connecting events to price and volatility

Everything else is secondary.

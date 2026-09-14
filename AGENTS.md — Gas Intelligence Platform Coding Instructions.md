# Gas Intelligence Platform — Agent Instructions

## 1. Mission

You are developing a long-term personal intelligence platform for European natural gas markets and gas options.

The application has two equally important objectives:

1. Provide a reliable daily market-intelligence platform.
2. Accelerate the user's expertise in gas fundamentals, derivatives, options, volatility, market mechanics, and historical market behavior.

The application must remain:

- reliable
- understandable
- maintainable
- modular
- data-driven
- easy to use
- suitable for desktop and mobile browsers

Do not optimize for engineering sophistication.

Optimize for market usefulness and data integrity.

---

# 2. Fixed Technology Stack

Unless explicitly instructed otherwise, use:

- Python
- Streamlit
- Supabase / PostgreSQL
- pandas
- NumPy
- SciPy where appropriate
- Plotly
- Git / GitHub
- pytest

Do not introduce another major framework, database, cloud provider, orchestration platform, or frontend framework without explicit approval.

Do not replace Streamlit.

Do not replace Supabase.

Avoid unnecessary abstractions and dependencies.

---

# 3. Development Philosophy

Prefer:

**simple + reliable + testable**

over:

**clever + complex**

The platform should evolve incrementally.

Every feature should be independently useful.

Avoid large rewrites.

Do not refactor unrelated parts of the repository unless necessary.

Before making significant architectural changes, explain:

1. why the existing architecture is insufficient;
2. what you propose changing;
3. which files/tables will be affected;
4. the migration risk.

Wait for approval before making major architectural changes.

---

# 4. Critical Data Rule

Never invent data.

Never invent API fields.

Never infer undocumented API behavior.

Never fabricate missing observations.

Never convert missing values into zero unless zero has a real economic meaning.

If a source is unavailable or ambiguous:

- preserve the missing value;
- record the failure;
- show the user that data is unavailable.

Do not silently substitute another source.

---

# 5. Data Lineage

Every externally sourced observation should preserve, where applicable:

```text
source
source_url
source_timestamp
observation_timestamp
retrieved_at
unit
raw_value
clean_value
```

The application must always be able to answer:

> Where did this number come from?

Derived metrics should also be traceable to their underlying inputs and methodology.

---

# 6. Raw / Clean / Derived Separation

Keep data logically separated into three stages:

```text
RAW
↓
CLEAN
↓
DERIVED
```

## RAW

Data as received from the source.

Do not alter historical raw observations except to correct a documented ingestion error.

## CLEAN

Normalized:

- timestamp
- units
- identifiers
- missing values
- naming conventions

## DERIVED

Calculations such as:

- moving averages
- percentiles
- z-scores
- storage deviations
- HDD/CDD
- realized volatility
- spreads
- signals
- event statistics

Never mix raw and derived observations in the same conceptual field.

---

# 7. Units Are Critical

Energy-market unit mistakes are unacceptable.

Always explicitly track units.

Possible examples:

```text
EUR/MWh
TWh
GWh
MWh
bcm
mcm
mcm/d
GW
GWh/d
°C
HDD
%
volatility points
```

Never assume two data sources use equivalent units.

Conversions must live in centralized utility functions and have tests.

Every conversion formula should be documented.

---

# 8. Time Handling

Store timestamps consistently.

Prefer UTC internally where possible.

Preserve the original source timezone if relevant.

The UI can display European market time.

Be especially careful with:

- CET / CEST
- daylight-saving changes
- gas-day definitions
- publication dates
- contract expiry dates
- historical forecast issue times

Never use future information when calculating historical signals.

Avoid look-ahead bias.

---

# 9. Financial Calculations

All financial calculations must have:

- documented methodology
- clear assumptions
- unit tests
- edge-case tests

Particularly sensitive calculations include:

- realized volatility
- annualization
- option Greeks
- Black-76 pricing
- delta conventions
- implied volatility
- risk reversals
- butterflies
- forward volatility
- calendar spreads
- event returns

Do not assume equity-option conventions apply automatically to commodity options.

If contract conventions matter, make them explicit.

---

# 10. Historical Analysis

Never introduce look-ahead bias.

For any historical analysis ask:

> Would this information have been available at that time?

Examples:

Weather analysis should distinguish:

```text
realized weather
historical forecast
current forecast
forecast revision
```

Do not analyze historical prices using weather forecasts that were published later.

Likewise, preserve historical versions when sources revise data where practical.

---

# 11. Data Quality Checks

Every ingestion pipeline should check:

- duplicate observations
- missing dates
- unexpected nulls
- impossible values
- unit changes
- schema changes
- timestamp gaps
- extreme jumps
- API failures

For important series, create sanity ranges.

Example:

```text
EU storage percentage:
0 <= value <= 100
```

A sanity check should not automatically delete suspicious data.

Flag it.

---

# 12. API Connectors

Each data provider must have an isolated connector.

Example:

```text
data/loaders/gie.py
data/loaders/entsog.py
data/loaders/entsoe.py
data/loaders/open_meteo.py
```

The rest of the application should not depend directly on provider-specific JSON structures.

Transform provider responses into standardized internal schemas.

If an external API changes, ideally only its connector should need modification.

---

# 13. Source Priority

Initially prioritize official/public sources.

Examples:

- GIE / AGSI
- GIE / ALSI
- ENTSOG
- ENTSO-E
- Gassco
- system operators
- government/public energy agencies
- company investor-relations documents
- Open-Meteo or other approved weather data

Where multiple sources exist, record which source is considered authoritative.

Do not silently combine inconsistent datasets.

---

# 14. Database Changes

Database migrations must be deliberate.

Before altering the schema:

1. explain why;
2. provide the SQL migration;
3. preserve existing data;
4. document backwards-compatibility implications.

Never delete a table or column containing data without explicit approval.

Prefer additive migrations.

---

# 15. Supabase Security

Never hard-code credentials.

Credentials must use environment variables or Streamlit secrets.

Expected variables may include:

```text
SUPABASE_URL
SUPABASE_ANON_KEY
```

Never commit:

```text
service-role keys
database passwords
API secrets
tokens
```

Never print secrets in logs.

Never expose server-side secrets to the Streamlit UI.

The `.env`, `.streamlit/secrets.toml`, and equivalent secret files must remain ignored by Git.

---

# 16. User Data

The current project is intended to store:

- public market data
- public company information
- personal non-confidential study notes
- personal market hypotheses
- quizzes
- learning progress

Do not design features intended to ingest:

- confidential employer information
- private client data
- internal communications
- proprietary order flow
- non-public transactions

unless explicitly instructed in the future.

---

# 17. Streamlit UX

The application must remain easy to navigate.

Primary navigation:

```text
Morning
Markets
Fundamentals
Physical System
Options & Volatility
Events
Companies
Intelligence
Knowledge Wiki
Daily Learning
Quiz & Review
Journal
Data / Admin
```

Do not overload pages.

Important information should be visible without excessive scrolling.

Prefer:

- clear hierarchy
- compact metric cards
- readable charts
- tooltips
- filters
- expandable advanced sections

The app should remain usable on iPhone/Safari.

Avoid critical interactions requiring mouse hover.

Avoid extremely wide tables where possible.

---

# 18. Morning Dashboard Philosophy

The Morning page should answer:

1. What changed?
2. What matters?
3. What is unusual?
4. What deserves investigation?

Do not turn it into a collection of every available metric.

Prioritize decision relevance.

---

# 19. Knowledge Wiki

The Knowledge Wiki is a core product, not a side feature.

Articles should use a consistent format:

```text
Definition
Why it matters
Physical/economic mechanism
Trading interpretation
Options implication
Worked example
Historical example
Common mistakes
Related concepts
Sources
Associated questions
```

Articles should be factual and sourced.

Do not generate unsourced facts automatically into the permanent knowledge base.

---

# 20. Learning Engine

Daily learning should use:

- curriculum importance
- user's mastery
- time since last review
- historical errors
- current market relevance

Suggested ranking logic:

```text
priority =
importance
× weakness
× forgetting_factor
× market_relevance
```

Do not select purely random topics.

---

# 21. Quiz System

Questions should test more than factual recall.

Supported question styles should include:

- recall
- explanation
- calculation
- comparison
- market reasoning
- options reasoning
- historical analysis

Examples:

> Norway loses 60 mcm/d during a cold January. Which part of the TTF curve should be most sensitive and why?

> Spot rallies while ATM implied volatility falls. Give several possible explanations.

Questions must have:

```text
difficulty
topic
reference article
answer
explanation
importance
```

---

# 22. Confidence Calibration

Where implemented, quizzes should capture:

```text
answer
correctness
confidence
```

Confidence scale:

```text
1 Guess
2 Unsure
3 Reasonably sure
4 Very sure
```

Wrong + highly confident answers should receive high future review priority.

---

# 23. Journal and Predictions

The platform should help build market judgment.

Predictions should ideally be falsifiable.

Store:

```text
prediction
date
horizon
confidence
reasoning
expected outcome
actual outcome
post_mortem
```

Do not rewrite historical predictions after the outcome becomes known.

---

# 24. Event Database

Events should be structured, not merely stored as text headlines.

Suggested fields:

```text
timestamp
category
entity
description
source
estimated physical impact
expected duration
affected tenor
confidence
market reaction
volatility reaction
lesson
```

Examples of categories:

- Norway outage
- LNG
- weather
- storage
- pipeline
- sanctions
- geopolitics
- power
- nuclear
- regulation
- industrial demand

---

# 25. Historical Analogues

When implementing analogue analysis:

Do not claim two periods are "similar" without showing the variables used.

Potential state variables:

- storage percentile
- temperature anomaly
- Norway flows
- LNG sendout
- TTF price
- curve structure
- realized volatility
- season/date

Similarity methodology must be transparent.

---

# 26. Testing Requirements

Every feature should include appropriate tests.

At minimum:

### Unit tests

For transformations/calculations.

### Data validation tests

For ingestion.

### Regression tests

For important calculations.

### Smoke test

Application should start without errors.

Before declaring a ticket complete, run the complete test suite.

Report:

```text
tests run
tests passed
tests failed
known limitations
```

Do not claim success if tests have not been run.

---

# 27. Error Handling

External API failures must not crash the whole application.

The UI should show something like:

> Data unavailable — last successful update: [timestamp]

rather than producing a traceback.

Log enough information to diagnose the problem.

---

# 28. Performance

Use caching appropriately for:

- API data
- database queries
- slow calculations

Do not repeatedly query external APIs on every Streamlit rerun.

Avoid premature optimization.

Correctness comes first.

---

# 29. Logging

Meaningful ingestion and processing operations should be logged.

Useful information:

```text
pipeline
source
start time
end time
records fetched
records inserted
records updated
errors
```

Never log credentials.

---

# 30. Documentation

Every substantial feature should update relevant documentation.

Document:

- purpose
- data source
- data schema
- calculation methodology
- known limitations

Code should explain *why* something is done when the reason is financial/domain-specific.

Do not fill code with comments explaining obvious syntax.

---

# 31. Coding Style

Prefer:

- small functions
- clear names
- type hints where useful
- pure calculation functions
- reusable components
- explicit arguments

Avoid:

- giant files
- global mutable state
- unnecessary class hierarchies
- clever metaprogramming
- duplicated financial formulas

---

# 32. Definition of Done

A feature is not complete because the UI appears.

A ticket is complete only when:

1. the functionality works;
2. data comes from the correct source;
3. units are verified;
4. edge cases are handled;
5. tests pass;
6. documentation is updated;
7. UI is usable;
8. no secrets are exposed;
9. existing functionality is not broken.

---

# 33. Workflow for Every Ticket

Before coding:

### Step 1 — Read

Read:

- `README.md`
- this `AGENTS.md`
- relevant roadmap section
- relevant existing source files

### Step 2 — Inspect

Inspect existing architecture before proposing new code.

Do not duplicate existing functionality.

### Step 3 — Propose

Return a short implementation plan containing:

```text
Files to create
Files to modify
Database changes
External APIs
Financial assumptions
Tests
Potential risks
```

### Step 4 — Implement

Implement only the requested scope.

### Step 5 — Test

Run tests and validate representative data manually where appropriate.

### Step 6 — Review yourself

Specifically look for:

- unit mistakes
- timestamp mistakes
- future-data leakage
- missing-value problems
- API-schema assumptions
- security leaks

### Step 7 — Report

Return:

```text
What changed
Why
Tests run
Results
Known limitations
Next logical task
```

---

# 34. Do Not Do These Without Approval

Do not:

- change framework
- change database
- introduce paid services
- add a major dependency
- redesign the entire UI
- alter core database schemas substantially
- delete historical data
- replace official data sources with scraped substitutes
- automate trades
- connect to brokerage execution
- store private employer/client information
- expose the database publicly

without explicit approval.

---

# 35. Guiding Principle

The purpose of this software is not to demonstrate software engineering.

The purpose is to help the user become exceptionally good at understanding European gas and gas options.

Every proposed feature should therefore answer:

> Does this improve data reliability, market understanding, decision quality, or learning?

If not, it is probably not a priority.
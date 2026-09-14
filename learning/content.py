"""Curated V0.1 curriculum. Illustrative numbers are never market observations.

Sources checked 2026-09-13. Interpretation is explicitly separated from sourced
definitions. Stable UUIDs let bundled questions reference the database seed.
"""
from uuid import NAMESPACE_URL, uuid5


def content_id(slug: str) -> str:
    return str(uuid5(NAMESPACE_URL, "gas-intelligence/v0.1/" + slug))


HISTORY_URL = "https://www.iea.org/reports/gas-market-report-q1-2023"
HISTORY = (
    "In 2022, reduced Russian pipeline deliveries put European gas supply under pressure. "
    "Europe responded with more LNG, storage filling and lower consumption. "
    "This is historical context, not evidence of a specific options-market reaction."
)

# Each entry: slug, title, category, definition, importance, mechanism,
# interpretation, options implication, worked example, common mistake, related, source.
_ARTICLES = [
    (
        "units", "Gas units: energy, volume and flow", "Gas fundamentals",
        "MWh measures energy; MW measures power. m³ measures gas volume; mcm/d measures a daily volume flow.",
        "Comparisons fail when units or measurement bases differ.",
        "Gas volume becomes energy only after applying a calorific value with a stated reference temperature, pressure and HHV/LHV basis.",
        "Check the unit and delivery period before comparing two quoted values.",
        "A premium per MWh needs the contract's delivery energy to become a cash amount.",
        "Illustrative: 2 TWh = 2,000 GWh. At an explicitly assumed 11 kWh/m³, 50 mcm = 550 GWh. This factor is not universal.",
        "Treating MW as MWh, or converting all gas volumes using an undocumented constant.",
        ["ttf", "storage"], "https://www.eia.gov/energyexplained/units-and-calculators/",
    ),
    (
        "storage", "Storage: inventory versus deliverability", "Gas fundamentals",
        "Storage holds gas for later use. Inventory measures the amount held; deliverability measures how quickly gas can be withdrawn.",
        "A large stock does not guarantee a large daily withdrawal capability.",
        "Gas can be injected during lower demand and withdrawn during higher demand, subject to facility constraints.",
        "Reasoning: assess inventory, withdrawal rates and location together when evaluating supply resilience.",
        "Reasoning: limited flexibility can increase exposure to short supply shocks; it does not mechanically determine implied volatility.",
        "Illustrative: 800 TWh of working gas divided by 1,000 TWh of working capacity equals 80% fullness.",
        "Confusing working gas with cushion gas, or assuming national inventories are instantly transferable.",
        ["units", "curve"], "https://www.eia.gov/naturalgas/storage/basics/",
    ),
    (
        "lng", "The LNG supply chain", "Gas fundamentals",
        "LNG is natural gas cooled into liquid form for transport and storage.",
        "It connects gas-producing regions with markets that cannot be reached directly by pipeline.",
        "Liquefaction, shipping, terminal storage, regasification and pipeline send-out are distinct stages.",
        "Reasoning: locate an outage in the chain before estimating its effect on delivered gas.",
        "Reasoning: duration and replacement options influence the uncertainty created by a disruption.",
        "Illustrative: 100 GWh/d of lost send-out for three days equals 300 GWh before replacement supply or demand response.",
        "Treating a cargo arrival as same-day pipeline send-out, or a terminal's capacity as actual flow.",
        ["storage", "units"], "https://www.eia.gov/energyexplained/natural-gas/liquefied-natural-gas.php",
    ),
    (
        "ttf", "TTF and the delivery contract", "Market mechanics",
        "TTF is a virtual gas trading point in the Netherlands. ICE Endex Dutch TTF futures specify delivery at that point.",
        "A price needs an identifiable venue, product and delivery period.",
        "The cited futures contract quotes energy in EUR/MWh and specifies delivery across its delivery period.",
        "Track an exact delivery month. A rolling M1 label changes contract at the roll.",
        "Use the actual underlying futures contract and option exercise convention when analysing options.",
        "Illustrative: 1 MW delivered for an assumed 720 hours equals 720 MWh; at EUR 30/MWh the energy value is EUR 21,600. Actual delivery hours must be checked.",
        "Treating all months as 720 hours or stitching M1 observations without recording the roll.",
        ["units", "curve"], "https://www.ice.com/products/27996665/Dutch-TTF-Natural-Gas-Futures",
    ),
    (
        "curve", "Calendar spreads and curve shape", "Market mechanics",
        "A calendar spread compares two delivery periods. Here M1–M2 means the first month's price minus the second month's price.",
        "The spread measures relative pricing across time.",
        "An upward-sloping section is in contango; a downward-sloping section is in backwardation. Carry costs can influence curve shape.",
        "Reasoning: a curve shape is not a guaranteed forecast of future spot prices or a risk-free storage profit.",
        "Reasoning: a spread option depends on the joint behaviour of both legs, including their correlation.",
        "Illustrative: M1 = EUR 35/MWh and M2 = EUR 32/MWh give M1–M2 = +EUR 3/MWh.",
        "Reversing the spread sign, ignoring costs, or calling an entire seasonal curve upward or downward based on two points.",
        ["ttf", "storage"], "https://www.cmegroup.com/education/courses/introduction-to-ferrous-metals/what-is-contango-and-backwardation",
    ),
    (
        "weather", "Heating degree days", "Gas fundamentals",
        "Heating degree days (HDD) summarize how far daily temperature falls below a stated heating base.",
        "They are a weather-sensitive demand indicator, not a direct gas-consumption measurement.",
        "For a stated daily mean and base, use max(base minus mean, zero). Geography and weighting affect the result.",
        "Compare forecasts for the same valid dates and preserve their issue times to measure a revision.",
        "Reasoning: forecast uncertainty can matter for volatility even when the mean forecast changes little.",
        "Illustrative Celsius convention: base 18°C, mean 10°C gives 8 degree-days. At 20°C it gives zero. This is an assumed base, not a universal standard.",
        "Mixing Celsius and Fahrenheit degree-days or using a later forecast in a historical signal.",
        ["storage", "power"], "https://www.eia.gov/energyexplained/units-and-calculators/degree-days.php",
    ),
    (
        "power", "Gas used for power generation", "Gas fundamentals",
        "Gas-fired plants convert fuel energy into electricity; the two energy quantities are different.",
        "Electricity generation is one channel through which power conditions affect gas demand.",
        "Gas turbines and combined-cycle plants use natural gas. Conversion losses mean fuel input exceeds electric output.",
        "Reasoning: translating electric output into gas demand requires efficiency and a consistent calorific basis.",
        "Reasoning: uncertain power demand or generation availability can add uncertainty to gas demand.",
        "Illustrative: 100 GWh of electric output at an assumed 50% efficiency needs 200 GWh of fuel energy on the same basis.",
        "Equating GWh of electricity with GWh of gas, or treating a renewable-output change as an automatic one-for-one gas change.",
        ["units", "weather"], "https://www.eia.gov/energyexplained/electricity/how-electricity-is-generated.php",
    ),
    (
        "payoff", "Call and put intrinsic value", "Options",
        "A call's intrinsic value is max(F minus K, zero); a put's is max(K minus F, zero), for underlying futures F and strike K.",
        "Intrinsic value is not the same as profit after premium and costs.",
        "Before expiry an option can also have time value. Exercise and settlement rules depend on the contract.",
        "Keep payoff, premium, contract multiplier and total P&L separate.",
        "A position can have positive intrinsic value and still lose money after the initial premium.",
        "Illustrative: F = 40, K = 35 gives call intrinsic value 5 per unit. A premium of 6 gives net expiry result −1 per unit before costs.",
        "Calling payoff profit, or assuming all options exercise or settle in cash in the same way.",
        ["delta", "volatility"], "https://www.cmegroup.com/education/courses/introduction-to-options/calculating-options-moneyness-and-intrinsic-value",
    ),
    (
        "delta", "Delta and changing exposure", "Options",
        "Delta describes local option-price sensitivity to the underlying. Gamma describes how delta changes as the underlying moves.",
        "The exposure of an option is not fixed.",
        "Greeks isolate sensitivities while holding other model inputs constant.",
        "A delta-only P&L estimate is a local approximation, not a full scenario valuation.",
        "State futures versus spot delta and the pricing convention before comparing marks or hedges.",
        "Illustrative: delta 0.40 and a small underlying move of 0.50 imply an approximate price change of 0.20 per unit, holding other inputs fixed.",
        "Using the same delta for a large move, or ignoring changing volatility and time decay.",
        ["payoff", "volatility"], "https://www.cmegroup.com/education/courses/option-greeks",
    ),
    (
        "volatility", "Implied volatility and skew", "Options",
        "Implied volatility is the volatility input consistent with an option price under a specified pricing model. Skew describes differences across strikes or deltas.",
        "Two options on the same underlying can have different implied volatilities.",
        "A volatility quote depends on maturity, strike, forward, option price and model conventions.",
        "Reasoning: an underlying rally alone does not determine the direction of implied volatility.",
        "For this curriculum, 25-delta risk reversal means call implied volatility minus put implied volatility, for matching expiry and conventions.",
        "Illustrative: call volatility 60% and put volatility 55% give a +5 volatility-point risk reversal.",
        "Confusing volatility points with percentage price returns or comparing mismatched expiry/delta conventions.",
        ["delta", "payoff"], "https://www.cmegroup.com/education/articles-and-reports/implied-volatility",
    ),
]


def get_articles() -> list[dict]:
    articles = []
    for order, entry in enumerate(_ARTICLES):
        slug, title, category, definition, why, mechanism, interpretation, options, example, mistakes, related, url = entry
        # History is one shared sourced episode, not ten fabricated case studies.
        sections = {
            "Definition": definition, "Why it matters": why,
            "Physical/economic mechanism": mechanism, "Trading interpretation": interpretation,
            "Options implication": options, "Worked example": example,
            "Historical example": f"Shared case study: Europe's 2022 gas supply shock. See Daily Learning and the [IEA report]({HISTORY_URL}). No historical option marks are supplied.",
            "Common mistakes": mistakes,
            "Related concepts": ", ".join(related),
            "Sources": f"[Primary reference]({url}) · [Historical context]({HISTORY_URL})\n\nChecked 2026-09-13. Interpretations and numerical examples are educational reasoning.",
            "Associated questions": f"Two questions in Quiz & Review, topic: {title}.",
        }
        articles.append({
            "id": content_id(slug), "slug": slug, "title": title, "category": category,
            "difficulty": 1 if order < 7 else 2, "summary": definition,
            "content_markdown": "\n\n".join(f"### {heading}\n\n{body}" for heading, body in sections.items()),
            "source_urls": [url, HISTORY_URL], "importance_score": 10 - order // 3,
            "curriculum_order": order, "sections": sections, "related": related,
        })
    return articles


# slug, type, prompt, answer, explanation; numerical examples are synthetic exercises.
_QUESTIONS = [
    ("units", "calculation", "Convert 2 TWh into GWh.", "2,000 GWh", "1 TWh = 1,000 GWh, so 2 × 1,000 = 2,000."),
    ("units", "explanation", "Why is a calorific value needed to convert mcm to GWh?", "Volume alone does not specify the gas's energy content.", "State composition-related calorific value, reference conditions and HHV/LHV basis."),
    ("storage", "calculation", "Working gas is 800 TWh; working capacity is 1,000 TWh. What is fullness?", "80%", "800 / 1,000 × 100 = 80%. Both quantities must use compatible definitions."),
    ("storage", "market reasoning", "Does high storage fullness guarantee enough gas can be delivered tomorrow?", "No. Withdrawal rates, location and transport constraints also matter.", "Inventory and deliverability measure different things."),
    ("lng", "recall", "List the main LNG stages between production-region gas and import-market pipeline delivery.", "Liquefaction, shipping, storage, regasification and send-out.", "An outage can affect a different stage and need not immediately change all downstream flows."),
    ("lng", "calculation", "Send-out falls by 100 GWh/d for three days. What gross energy is lost?", "300 GWh", "100 × 3 = 300 GWh before replacement supply or demand response."),
    ("ttf", "calculation", "A hypothetical 1 MW delivery runs for 720 hours. How much energy is delivered?", "720 MWh", "Power × time = energy. Do not assume every actual contract has 720 delivery hours."),
    ("ttf", "explanation", "Why can a rolling M1 series change even if an individual delivery contract barely moves?", "The series can roll to a different delivery month.", "Record exact contract identity and apply an explicit roll methodology before return analysis."),
    ("curve", "calculation", "M1 is 35 and M2 is 32 EUR/MWh. Calculate M1–M2.", "+3 EUR/MWh", "35 − 32 = 3. This pair is backwardated under the stated convention."),
    ("curve", "market reasoning", "Does contango guarantee a profitable storage trade?", "No. Costs and physical constraints can exceed the price spread.", "Consider financing, capacity, injection/withdrawal, losses and execution costs."),
    ("weather", "calculation", "With an assumed 18°C base and 10°C daily mean, calculate HDD.", "8 degree-days", "max(18 − 10, 0) = 8, using this stated Celsius convention."),
    ("weather", "historical analysis", "Why must a historical forecast analysis retain forecast issue time?", "To ensure the forecast was available at the decision time.", "Later forecasts would leak future information into the historical analysis."),
    ("power", "calculation", "At an assumed 50% efficiency, what fuel energy produces 100 GWh of electricity?", "200 GWh of fuel", "100 / 0.50 = 200. Keep the same calorific basis throughout."),
    ("power", "comparison", "Are 100 GWh of electricity and 100 GWh of gas interchangeable in a demand balance?", "No; one is output energy and the other is fuel input energy.", "Conversion efficiency is needed to translate between them."),
    ("payoff", "calculation", "A call has strike 35 and expiry underlying 40. Premium was 6. What is net result per unit before costs?", "−1 per unit", "Intrinsic value is max(40 − 35, 0) = 5; subtract premium 6."),
    ("payoff", "comparison", "How do a call's and a put's intrinsic values differ?", "Call: max(F−K, 0). Put: max(K−F, 0).", "These are per-unit intrinsic values, not full position P&L."),
    ("delta", "calculation", "Delta is 0.40; the underlying increases 0.50. Estimate the local option-price change.", "+0.20 per unit", "0.40 × 0.50 = 0.20, holding other inputs fixed and ignoring higher-order effects."),
    ("delta", "options reasoning", "Why can a delta-only estimate fail for a large underlying move?", "Delta can change; volatility and time can also change.", "Gamma captures changing delta. Revaluation needs the relevant pricing inputs and conventions."),
    ("volatility", "calculation", "25D call IV is 60%; 25D put IV is 55%. Under call-minus-put convention, what is the risk reversal?", "+5 volatility points", "60 − 55 = 5, assuming matching expiry and delta conventions."),
    ("volatility", "options reasoning", "Must implied volatility rise whenever the underlying price rises?", "No.", "Price direction alone is insufficient. Consider changing uncertainty, option demand, maturity and skew; these are hypotheses to investigate."),
]


def get_questions() -> list[dict]:
    return [{
        "id": content_id(f"question-{i+1}"), "article_id": content_id(slug),
        "topic": slug, "question_type": kind, "difficulty": 1 if kind in {"recall", "calculation"} else 2,
        "question": prompt, "answer": answer, "explanation": explanation, "importance": 5,
        "curriculum_order": i,
    } for i, (slug, kind, prompt, answer, explanation) in enumerate(_QUESTIONS)]

-- Generated from learning/content.py. Existing IDs are preserved.
begin;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('aac31923-db76-5b60-8baa-89f9f9d1a47b', 'units', 'Gas units: energy, volume and flow', 'Gas fundamentals', 1, 'MWh measures energy; MW measures power. m³ measures gas volume; mcm/d measures a daily volume flow.', '### Definition

MWh measures energy; MW measures power. m³ measures gas volume; mcm/d measures a daily volume flow.

### Why it matters

Comparisons fail when units or measurement bases differ.

### Physical/economic mechanism

Gas volume becomes energy only after applying a calorific value with a stated reference temperature, pressure and HHV/LHV basis.

### Trading interpretation

Check the unit and delivery period before comparing two quoted values.

### Options implication

A premium per MWh needs the contract''s delivery energy to become a cash amount.

### Worked example

Illustrative: 2 TWh = 2,000 GWh. At an explicitly assumed 11 kWh/m³, 50 mcm = 550 GWh. This factor is not universal.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Treating MW as MWh, or converting all gas volumes using an undocumented constant.

### Related concepts

ttf, storage

### Sources

[Primary reference](https://www.eia.gov/energyexplained/units-and-calculators/) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: Gas units: energy, volume and flow.', '["https://www.eia.gov/energyexplained/units-and-calculators/", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 10, 0) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('c4e3cdd1-aee6-57cc-b8cc-cacb21bb5936', 'storage', 'Storage: inventory versus deliverability', 'Gas fundamentals', 1, 'Storage holds gas for later use. Inventory measures the amount held; deliverability measures how quickly gas can be withdrawn.', '### Definition

Storage holds gas for later use. Inventory measures the amount held; deliverability measures how quickly gas can be withdrawn.

### Why it matters

A large stock does not guarantee a large daily withdrawal capability.

### Physical/economic mechanism

Gas can be injected during lower demand and withdrawn during higher demand, subject to facility constraints.

### Trading interpretation

Reasoning: assess inventory, withdrawal rates and location together when evaluating supply resilience.

### Options implication

Reasoning: limited flexibility can increase exposure to short supply shocks; it does not mechanically determine implied volatility.

### Worked example

Illustrative: 800 TWh of working gas divided by 1,000 TWh of working capacity equals 80% fullness.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Confusing working gas with cushion gas, or assuming national inventories are instantly transferable.

### Related concepts

units, curve

### Sources

[Primary reference](https://www.eia.gov/naturalgas/storage/basics/) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: Storage: inventory versus deliverability.', '["https://www.eia.gov/naturalgas/storage/basics/", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 10, 1) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('c02b499f-30d1-51b8-b665-88ccc81c4c98', 'lng', 'The LNG supply chain', 'Gas fundamentals', 1, 'LNG is natural gas cooled into liquid form for transport and storage.', '### Definition

LNG is natural gas cooled into liquid form for transport and storage.

### Why it matters

It connects gas-producing regions with markets that cannot be reached directly by pipeline.

### Physical/economic mechanism

Liquefaction, shipping, terminal storage, regasification and pipeline send-out are distinct stages.

### Trading interpretation

Reasoning: locate an outage in the chain before estimating its effect on delivered gas.

### Options implication

Reasoning: duration and replacement options influence the uncertainty created by a disruption.

### Worked example

Illustrative: 100 GWh/d of lost send-out for three days equals 300 GWh before replacement supply or demand response.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Treating a cargo arrival as same-day pipeline send-out, or a terminal''s capacity as actual flow.

### Related concepts

storage, units

### Sources

[Primary reference](https://www.eia.gov/energyexplained/natural-gas/liquefied-natural-gas.php) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: The LNG supply chain.', '["https://www.eia.gov/energyexplained/natural-gas/liquefied-natural-gas.php", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 10, 2) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('fc11020e-a008-51bd-8934-99486644fbd5', 'ttf', 'TTF and the delivery contract', 'Market mechanics', 1, 'TTF is a virtual gas trading point in the Netherlands. ICE Endex Dutch TTF futures specify delivery at that point.', '### Definition

TTF is a virtual gas trading point in the Netherlands. ICE Endex Dutch TTF futures specify delivery at that point.

### Why it matters

A price needs an identifiable venue, product and delivery period.

### Physical/economic mechanism

The cited futures contract quotes energy in EUR/MWh and specifies delivery across its delivery period.

### Trading interpretation

Track an exact delivery month. A rolling M1 label changes contract at the roll.

### Options implication

Use the actual underlying futures contract and option exercise convention when analysing options.

### Worked example

Illustrative: 1 MW delivered for an assumed 720 hours equals 720 MWh; at EUR 30/MWh the energy value is EUR 21,600. Actual delivery hours must be checked.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Treating all months as 720 hours or stitching M1 observations without recording the roll.

### Related concepts

units, curve

### Sources

[Primary reference](https://www.ice.com/products/27996665/Dutch-TTF-Natural-Gas-Futures) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: TTF and the delivery contract.', '["https://www.ice.com/products/27996665/Dutch-TTF-Natural-Gas-Futures", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 9, 3) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('b17e43eb-30da-5f7f-ba54-fadd639a2ab7', 'curve', 'Calendar spreads and curve shape', 'Market mechanics', 1, 'A calendar spread compares two delivery periods. Here M1–M2 means the first month''s price minus the second month''s price.', '### Definition

A calendar spread compares two delivery periods. Here M1–M2 means the first month''s price minus the second month''s price.

### Why it matters

The spread measures relative pricing across time.

### Physical/economic mechanism

An upward-sloping section is in contango; a downward-sloping section is in backwardation. Carry costs can influence curve shape.

### Trading interpretation

Reasoning: a curve shape is not a guaranteed forecast of future spot prices or a risk-free storage profit.

### Options implication

Reasoning: a spread option depends on the joint behaviour of both legs, including their correlation.

### Worked example

Illustrative: M1 = EUR 35/MWh and M2 = EUR 32/MWh give M1–M2 = +EUR 3/MWh.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Reversing the spread sign, ignoring costs, or calling an entire seasonal curve upward or downward based on two points.

### Related concepts

ttf, storage

### Sources

[Primary reference](https://www.cmegroup.com/education/courses/introduction-to-ferrous-metals/what-is-contango-and-backwardation) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: Calendar spreads and curve shape.', '["https://www.cmegroup.com/education/courses/introduction-to-ferrous-metals/what-is-contango-and-backwardation", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 9, 4) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('8de99cd6-93a0-56c9-b619-a3b97357a450', 'weather', 'Heating degree days', 'Gas fundamentals', 1, 'Heating degree days (HDD) summarize how far daily temperature falls below a stated heating base.', '### Definition

Heating degree days (HDD) summarize how far daily temperature falls below a stated heating base.

### Why it matters

They are a weather-sensitive demand indicator, not a direct gas-consumption measurement.

### Physical/economic mechanism

For a stated daily mean and base, use max(base minus mean, zero). Geography and weighting affect the result.

### Trading interpretation

Compare forecasts for the same valid dates and preserve their issue times to measure a revision.

### Options implication

Reasoning: forecast uncertainty can matter for volatility even when the mean forecast changes little.

### Worked example

Illustrative Celsius convention: base 18°C, mean 10°C gives 8 degree-days. At 20°C it gives zero. This is an assumed base, not a universal standard.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Mixing Celsius and Fahrenheit degree-days or using a later forecast in a historical signal.

### Related concepts

storage, power

### Sources

[Primary reference](https://www.eia.gov/energyexplained/units-and-calculators/degree-days.php) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: Heating degree days.', '["https://www.eia.gov/energyexplained/units-and-calculators/degree-days.php", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 9, 5) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('b7b4f57e-2791-563e-bfee-d04445b21c83', 'power', 'Gas used for power generation', 'Gas fundamentals', 1, 'Gas-fired plants convert fuel energy into electricity; the two energy quantities are different.', '### Definition

Gas-fired plants convert fuel energy into electricity; the two energy quantities are different.

### Why it matters

Electricity generation is one channel through which power conditions affect gas demand.

### Physical/economic mechanism

Gas turbines and combined-cycle plants use natural gas. Conversion losses mean fuel input exceeds electric output.

### Trading interpretation

Reasoning: translating electric output into gas demand requires efficiency and a consistent calorific basis.

### Options implication

Reasoning: uncertain power demand or generation availability can add uncertainty to gas demand.

### Worked example

Illustrative: 100 GWh of electric output at an assumed 50% efficiency needs 200 GWh of fuel energy on the same basis.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Equating GWh of electricity with GWh of gas, or treating a renewable-output change as an automatic one-for-one gas change.

### Related concepts

units, weather

### Sources

[Primary reference](https://www.eia.gov/energyexplained/electricity/how-electricity-is-generated.php) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: Gas used for power generation.', '["https://www.eia.gov/energyexplained/electricity/how-electricity-is-generated.php", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 8, 6) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('e9777be8-13d7-5ec4-9a62-197cd95c5216', 'payoff', 'Call and put intrinsic value', 'Options', 2, 'A call''s intrinsic value is max(F minus K, zero); a put''s is max(K minus F, zero), for underlying futures F and strike K.', '### Definition

A call''s intrinsic value is max(F minus K, zero); a put''s is max(K minus F, zero), for underlying futures F and strike K.

### Why it matters

Intrinsic value is not the same as profit after premium and costs.

### Physical/economic mechanism

Before expiry an option can also have time value. Exercise and settlement rules depend on the contract.

### Trading interpretation

Keep payoff, premium, contract multiplier and total P&L separate.

### Options implication

A position can have positive intrinsic value and still lose money after the initial premium.

### Worked example

Illustrative: F = 40, K = 35 gives call intrinsic value 5 per unit. A premium of 6 gives net expiry result −1 per unit before costs.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Calling payoff profit, or assuming all options exercise or settle in cash in the same way.

### Related concepts

delta, volatility

### Sources

[Primary reference](https://www.cmegroup.com/education/courses/introduction-to-options/calculating-options-moneyness-and-intrinsic-value) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: Call and put intrinsic value.', '["https://www.cmegroup.com/education/courses/introduction-to-options/calculating-options-moneyness-and-intrinsic-value", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 8, 7) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('de95c1ea-9e04-5282-9246-f2008d3fedcc', 'delta', 'Delta and changing exposure', 'Options', 2, 'Delta describes local option-price sensitivity to the underlying. Gamma describes how delta changes as the underlying moves.', '### Definition

Delta describes local option-price sensitivity to the underlying. Gamma describes how delta changes as the underlying moves.

### Why it matters

The exposure of an option is not fixed.

### Physical/economic mechanism

Greeks isolate sensitivities while holding other model inputs constant.

### Trading interpretation

A delta-only P&L estimate is a local approximation, not a full scenario valuation.

### Options implication

State futures versus spot delta and the pricing convention before comparing marks or hedges.

### Worked example

Illustrative: delta 0.40 and a small underlying move of 0.50 imply an approximate price change of 0.20 per unit, holding other inputs fixed.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Using the same delta for a large move, or ignoring changing volatility and time decay.

### Related concepts

payoff, volatility

### Sources

[Primary reference](https://www.cmegroup.com/education/courses/option-greeks) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: Delta and changing exposure.', '["https://www.cmegroup.com/education/courses/option-greeks", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 8, 8) on conflict (id) do nothing;
insert into public.knowledge_articles (id, slug, title, category, difficulty, summary, content_markdown, source_urls, importance_score, curriculum_order) values ('570fc1d1-d178-55d9-9c8f-d471536943b1', 'volatility', 'Implied volatility and skew', 'Options', 2, 'Implied volatility is the volatility input consistent with an option price under a specified pricing model. Skew describes differences across strikes or deltas.', '### Definition

Implied volatility is the volatility input consistent with an option price under a specified pricing model. Skew describes differences across strikes or deltas.

### Why it matters

Two options on the same underlying can have different implied volatilities.

### Physical/economic mechanism

A volatility quote depends on maturity, strike, forward, option price and model conventions.

### Trading interpretation

Reasoning: an underlying rally alone does not determine the direction of implied volatility.

### Options implication

For this curriculum, 25-delta risk reversal means call implied volatility minus put implied volatility, for matching expiry and conventions.

### Worked example

Illustrative: call volatility 60% and put volatility 55% give a +5 volatility-point risk reversal.

### Historical example

Shared case study: Europe''s 2022 gas supply shock. See Daily Learning and the [IEA report](https://www.iea.org/reports/gas-market-report-q1-2023). No historical option marks are supplied.

### Common mistakes

Confusing volatility points with percentage price returns or comparing mismatched expiry/delta conventions.

### Related concepts

delta, payoff

### Sources

[Primary reference](https://www.cmegroup.com/education/articles-and-reports/implied-volatility) · [Historical context](https://www.iea.org/reports/gas-market-report-q1-2023)

Checked 2026-09-13. Interpretations and numerical examples are educational reasoning.

### Associated questions

Two questions in Quiz & Review, topic: Implied volatility and skew.', '["https://www.cmegroup.com/education/articles-and-reports/implied-volatility", "https://www.iea.org/reports/gas-market-report-q1-2023"]'::jsonb, 7, 9) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('0749830f-08e0-5e07-b266-171b9227518f', 'aac31923-db76-5b60-8baa-89f9f9d1a47b', 'units', 'calculation', 1, 'Convert 2 TWh into GWh.', '2,000 GWh', '1 TWh = 1,000 GWh, so 2 × 1,000 = 2,000.', 5, 0) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('47de7b2f-0f59-5adb-8ab7-fabc61e4bf72', 'aac31923-db76-5b60-8baa-89f9f9d1a47b', 'units', 'explanation', 2, 'Why is a calorific value needed to convert mcm to GWh?', 'Volume alone does not specify the gas''s energy content.', 'State composition-related calorific value, reference conditions and HHV/LHV basis.', 5, 1) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('d79cbc1f-097c-5a92-a5f9-664e4d5b0548', 'c4e3cdd1-aee6-57cc-b8cc-cacb21bb5936', 'storage', 'calculation', 1, 'Working gas is 800 TWh; working capacity is 1,000 TWh. What is fullness?', '80%', '800 / 1,000 × 100 = 80%. Both quantities must use compatible definitions.', 5, 2) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('7a001323-d0a2-5e5f-838f-91b247379d82', 'c4e3cdd1-aee6-57cc-b8cc-cacb21bb5936', 'storage', 'market reasoning', 2, 'Does high storage fullness guarantee enough gas can be delivered tomorrow?', 'No. Withdrawal rates, location and transport constraints also matter.', 'Inventory and deliverability measure different things.', 5, 3) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('92b53080-4697-5a9c-8465-661e672aed96', 'c02b499f-30d1-51b8-b665-88ccc81c4c98', 'lng', 'recall', 1, 'List the main LNG stages between production-region gas and import-market pipeline delivery.', 'Liquefaction, shipping, storage, regasification and send-out.', 'An outage can affect a different stage and need not immediately change all downstream flows.', 5, 4) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('ba19ffb8-15ba-573f-b7b4-662664df80ed', 'c02b499f-30d1-51b8-b665-88ccc81c4c98', 'lng', 'calculation', 1, 'Send-out falls by 100 GWh/d for three days. What gross energy is lost?', '300 GWh', '100 × 3 = 300 GWh before replacement supply or demand response.', 5, 5) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('b4357dc2-0426-54ef-ae44-663818e5d16b', 'fc11020e-a008-51bd-8934-99486644fbd5', 'ttf', 'calculation', 1, 'A hypothetical 1 MW delivery runs for 720 hours. How much energy is delivered?', '720 MWh', 'Power × time = energy. Do not assume every actual contract has 720 delivery hours.', 5, 6) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('f0b07188-7e6d-54db-ad39-237b6bf86fc1', 'fc11020e-a008-51bd-8934-99486644fbd5', 'ttf', 'explanation', 2, 'Why can a rolling M1 series change even if an individual delivery contract barely moves?', 'The series can roll to a different delivery month.', 'Record exact contract identity and apply an explicit roll methodology before return analysis.', 5, 7) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('a6913cd6-fb6e-52c1-b0e5-a7c70e5bf66b', 'b17e43eb-30da-5f7f-ba54-fadd639a2ab7', 'curve', 'calculation', 1, 'M1 is 35 and M2 is 32 EUR/MWh. Calculate M1–M2.', '+3 EUR/MWh', '35 − 32 = 3. This pair is backwardated under the stated convention.', 5, 8) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('406d12fa-2234-59b0-9e9c-76283e848330', 'b17e43eb-30da-5f7f-ba54-fadd639a2ab7', 'curve', 'market reasoning', 2, 'Does contango guarantee a profitable storage trade?', 'No. Costs and physical constraints can exceed the price spread.', 'Consider financing, capacity, injection/withdrawal, losses and execution costs.', 5, 9) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('6bf7bc7d-93fa-56bb-a279-71046ec1784b', '8de99cd6-93a0-56c9-b619-a3b97357a450', 'weather', 'calculation', 1, 'With an assumed 18°C base and 10°C daily mean, calculate HDD.', '8 degree-days', 'max(18 − 10, 0) = 8, using this stated Celsius convention.', 5, 10) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('1c18d343-3255-50b7-9975-ac5dcad4e611', '8de99cd6-93a0-56c9-b619-a3b97357a450', 'weather', 'historical analysis', 2, 'Why must a historical forecast analysis retain forecast issue time?', 'To ensure the forecast was available at the decision time.', 'Later forecasts would leak future information into the historical analysis.', 5, 11) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('51a5bdc4-179b-5116-a230-a8dd520be171', 'b7b4f57e-2791-563e-bfee-d04445b21c83', 'power', 'calculation', 1, 'At an assumed 50% efficiency, what fuel energy produces 100 GWh of electricity?', '200 GWh of fuel', '100 / 0.50 = 200. Keep the same calorific basis throughout.', 5, 12) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('d6456015-5b00-5ce3-9a78-5be8255e7ce1', 'b7b4f57e-2791-563e-bfee-d04445b21c83', 'power', 'comparison', 2, 'Are 100 GWh of electricity and 100 GWh of gas interchangeable in a demand balance?', 'No; one is output energy and the other is fuel input energy.', 'Conversion efficiency is needed to translate between them.', 5, 13) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('52f2dd71-7e1c-52e0-a8b1-18a9836f8158', 'e9777be8-13d7-5ec4-9a62-197cd95c5216', 'payoff', 'calculation', 1, 'A call has strike 35 and expiry underlying 40. Premium was 6. What is net result per unit before costs?', '−1 per unit', 'Intrinsic value is max(40 − 35, 0) = 5; subtract premium 6.', 5, 14) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('7da3cdaa-ced7-520b-a528-4a91816996c2', 'e9777be8-13d7-5ec4-9a62-197cd95c5216', 'payoff', 'comparison', 2, 'How do a call''s and a put''s intrinsic values differ?', 'Call: max(F−K, 0). Put: max(K−F, 0).', 'These are per-unit intrinsic values, not full position P&L.', 5, 15) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('4af9fd80-5622-5e4b-aae8-410f0690afd5', 'de95c1ea-9e04-5282-9246-f2008d3fedcc', 'delta', 'calculation', 1, 'Delta is 0.40; the underlying increases 0.50. Estimate the local option-price change.', '+0.20 per unit', '0.40 × 0.50 = 0.20, holding other inputs fixed and ignoring higher-order effects.', 5, 16) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('76514d6d-78e1-51c2-bbd4-5899dac52535', 'de95c1ea-9e04-5282-9246-f2008d3fedcc', 'delta', 'options reasoning', 2, 'Why can a delta-only estimate fail for a large underlying move?', 'Delta can change; volatility and time can also change.', 'Gamma captures changing delta. Revaluation needs the relevant pricing inputs and conventions.', 5, 17) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('82ae9c0d-6642-58d3-99d6-2dc9263782eb', '570fc1d1-d178-55d9-9c8f-d471536943b1', 'volatility', 'calculation', 1, '25D call IV is 60%; 25D put IV is 55%. Under call-minus-put convention, what is the risk reversal?', '+5 volatility points', '60 − 55 = 5, assuming matching expiry and delta conventions.', 5, 18) on conflict (id) do nothing;
insert into public.questions (id, article_id, topic, question_type, difficulty, question, answer, explanation, importance, curriculum_order) values ('047e0458-bae5-5686-a6ac-c68fb067febb', '570fc1d1-d178-55d9-9c8f-d471536943b1', 'volatility', 'options reasoning', 2, 'Must implied volatility rise whenever the underlying price rises?', 'No.', 'Price direction alone is insufficient. Consider changing uncertainty, option demand, maturity and skew; these are hypotheses to investigate.', 5, 19) on conflict (id) do nothing;
commit;

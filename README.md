# Stridewise — Running Shoe Agent

Stridewise is an explainable **Agentic Commerce** MVP that helps recreational runners decide what shoe to buy next. It uses training patterns, current-shoe mileage, preferences, and a curated product catalog to recommend an intentional shoe rotation.

## Business problem

Runners often choose shoes from popularity, isolated reviews, or a single past purchase. That makes it difficult to tell whether an existing pair is nearing retirement, whether a rotation has a coverage gap, and which available model best matches the next training need.

**Target user:** a recreational road or trail runner shopping to replace a pair, build a rotation, or add a workout-specific shoe.

**Useful outcome:** a runner receives:

- Keep / monitor / replace-soon guidance for their current shoes.
- The shoe roles their training requires (daily, recovery, tempo, or trail).
- Ranked, budget-aware options with reasons the product matches.
- Reference product discovery links and simple save/dismiss feedback.

## Architecture

| Layer | MVP implementation | Production evolution |
| --- | --- | --- |
| Runner context | Three-step HTML form | Authenticated runner profile and training integrations |
| Product intelligence | Curated JavaScript catalog in `app.js` | Versioned product database plus retailer/catalog feeds |
| Decision engine | Deterministic client-side filters and weighted scoring | Tested recommendation service/API with versioned rules |
| Feedback state | Browser `localStorage` | Per-user database records and analytics |
| Presentation | Static HTML, CSS, and vanilla JavaScript | Responsive web app with account and retailer integrations |

### Inputs and scoring

The agent collects goal, weekly mileage, surface, workout types, owned shoes and mileage, budget, support preference, cushioning preference, and excluded brands.

It first filters products by shoe role, terrain, price, support, and excluded brands. Eligible products are then scored for cushioning preference, value relative to budget, durability at higher weekly mileage, and stability compatibility. Each recommendation exposes those reasons in the UI; an LLM is deliberately not used to override filters or product facts.

Current-shoe mileage is compared against each known model’s curated expected lifespan:

- **Keep in rotation:** below 65% of the reference lifespan.
- **Monitor:** 65–84% used.
- **Replace soon:** 85% or more used.

These are shopping heuristics, not safety or medical assessments.

## Challenge demo flow

1. Choose **Build a rotation**, 35–50 miles per week, road, with easy, long, and tempo runs.
2. Add `Brooks Ghost 16` with `400` miles.
3. Choose a $200 budget and neutral support, then view results.
4. The agent marks the Ghost pair **replace soon** (400 of 450 reference miles) and recommends daily, tempo, and recovery coverage with transparent product-specific rationale.
5. Demonstrate **Save option**, **Not for me**, and **Find this shoe**. Saved/dismissed product feedback persists in this browser only.

## Run locally

```zsh
cd "/Users/nelsongaitan/Personal Projects/running-gear-scout"
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080).

## Prototype demo flow

1. Select **Find my next shoe** from the landing page.
2. Select **Connect Strava**. This is a deliberately simulated import—no real Strava OAuth connection or user data is involved.
3. Confirm the imported Superblast 2, Adios Pro 4, and Cloudboom Strike rotation.
4. Pick a budget and colors, then open Scout Home.
5. Submit the default long-run prompt to view the visible agent-analysis stage, three ranked matches, and a full shoe-detail / buy-or-save view.

## Scope and responsible-use boundaries

- Catalog details and prices are curated **reference data**, not real-time inventory, retailer pricing, or availability guarantees.
- Product links are discovery searches; this MVP does not process payments.
- Stridewise provides product guidance, not medical advice or injury-prevention guarantees. Runners with pain or recurring injuries should consult a qualified professional.
- The prototype has no user account and intentionally does not collect sensitive health data.

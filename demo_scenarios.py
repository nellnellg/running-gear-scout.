#!/usr/bin/env python3
"""Prototype scenarios for Running Gear Scout.

Runs a set of realistic runner profiles through the recommendation engine and
prints the output for each, so you can see what the product actually produces
for different kinds of runners.

    python3 demo_scenarios.py
"""

from scout import OwnedShoe, Runner, find_shoe, render

SCENARIOS = [
    (
        "1. High-mileage marathoner — worn daily trainer",
        Runner(
            weekly_miles=50,
            run_types=["easy", "long", "tempo", "intervals", "race"],
            foot_type="neutral",
            surface="road",
            budget=200,
            preferred_drop=(4, 10),
            preferred_cushion="balanced",
            rotation=[
                OwnedShoe(find_shoe("Ghost 16"), 470),
                OwnedShoe(find_shoe("Endorphin Speed 4"), 180),
                OwnedShoe(find_shoe("Vaporfly 3"), 60),
            ],
        ),
    ),
    (
        "2. Overpronator rebuilding a base — no stability shoe",
        Runner(
            weekly_miles=25,
            run_types=["easy", "long"],
            foot_type="overpronate",
            surface="road",
            budget=150,
            preferred_drop=(8, 12),
            preferred_cushion="balanced",
            rotation=[],
        ),
    ),
    (
        "3. Trail runner — road shoes only",
        Runner(
            weekly_miles=35,
            run_types=["easy", "long", "trail"],
            foot_type="neutral",
            surface="trail",
            budget=175,
            preferred_drop=(4, 8),
            preferred_cushion="balanced",
            rotation=[
                OwnedShoe(find_shoe("Pegasus 41"), 300),
            ],
        ),
    ),
    (
        "4. Healthy rotation — nothing needed",
        Runner(
            weekly_miles=30,
            run_types=["easy", "tempo"],
            foot_type="neutral",
            surface="road",
            budget=160,
            preferred_drop=(6, 10),
            preferred_cushion="balanced",
            rotation=[
                OwnedShoe(find_shoe("Ride 17"), 120),
                OwnedShoe(find_shoe("Endorphin Speed 4"), 90),
            ],
        ),
    ),
    (
        "5. Tight budget — race shoe wanted, $110 to spend",
        Runner(
            weekly_miles=40,
            run_types=["easy", "long", "tempo", "race"],
            foot_type="neutral",
            surface="road",
            budget=110,
            preferred_drop=(6, 10),
            preferred_cushion=None,
            rotation=[
                OwnedShoe(find_shoe("Novablast 5"), 150),
            ],
        ),
    ),
]


def main() -> None:
    for title, runner in SCENARIOS:
        print("=" * 72)
        print(title)
        print("=" * 72)
        print(render(runner))
        print()


if __name__ == "__main__":
    main()

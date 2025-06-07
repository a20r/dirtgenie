#!/usr/bin/env python3
"""
Demonstrate the improved closed-loop prompt without making API calls.
Shows the exact prompt that will be sent to OpenAI.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def show_improved_prompt():
    """Show the improved closed-loop prompt that addresses the distance issue."""

    # Simulate the parameters you mentioned
    start = "Your house"
    end = "Your house"  # Same location = closed loop
    nights = 5  # 5 nights as you mentioned
    daily_distance = "40-50"  # Your preference

    # Calculate the max radius (this is the key improvement)
    min_daily, max_daily = map(int, daily_distance.split('-'))
    avg_daily = (min_daily + max_daily) / 2  # 45 km
    max_radius_km = int(avg_daily * (nights + 1) * 0.35)  # ≈94 km

    print("🔧 IMPROVED CLOSED-LOOP PROMPT PREVIEW\n")
    print("=" * 80)
    print(f"Trip: {nights + 1} days, {daily_distance} km/day from {start}")
    print(f"OLD PROBLEM: AI could plan 5 days out (225+ km away) then straight back")
    print(f"NEW SOLUTION: Maximum radius constrained to {max_radius_km} km")
    print("=" * 80)

    # Show the key improvements
    print("\n🎯 KEY IMPROVEMENTS:")
    print(f"1. MAXIMUM RADIUS CALCULATION: {max_radius_km} km")
    print("   - Based on: (avg_daily_distance * total_days * 0.35)")
    print("   - Prevents destinations beyond reasonable return distance")

    print(f"\n2. DAILY VALIDATION CHECKLIST:")
    print(f"   - Day 1: Can return in {nights} days at {daily_distance} km/day?")
    print(f"   - Day 2: Can return in {nights-1} days at {daily_distance} km/day?")
    print(f"   - Day 3: Can return in {nights-2} days at {daily_distance} km/day?")
    print(f"   - Day 4: Can return in {nights-3} days at {daily_distance} km/day?")
    print(f"   - Day 5: Can return in {nights-4} days at {daily_distance} km/day?")
    print(f"   - Day 6: MUST be within {daily_distance} km of home")

    print(f"\n3. MATHEMATICAL CONSTRAINT:")
    print("   Every overnight location must satisfy:")
    print("   (distance_from_start_km * 1.4) ≤ (days_remaining * max_daily_distance)")
    print(f"   Example: Day 4 location can be max {max_daily * 2 / 1.4:.0f} km from start")

    print(f"\n4. ROUTE GEOMETRY:")
    print("   - Focus on circular/polygonal patterns around start point")
    print("   - Avoid straight-line out-and-back routes")
    print("   - Think regional loop, not linear progression")

    print("\n" + "=" * 80)
    print("🚫 BEFORE (problematic):")
    print("Day 1: Home → 45km out")
    print("Day 2: 45km → 90km out")
    print("Day 3: 90km → 135km out")
    print("Day 4: 135km → 180km out")
    print("Day 5: 180km → 225km out (Vermont/NH)")
    print("Day 6: 225km → Home (225km = 5x daily limit! ❌)")

    print("\n✅ AFTER (improved):")
    print("Day 1: Home → 45km NE")
    print("Day 2: 45km NE → 45km N (still ~60km from home)")
    print("Day 3: 45km N → 45km NW (still ~70km from home)")
    print("Day 4: 45km NW → 45km W (still ~60km from home)")
    print("Day 5: 45km W → 45km SW (still ~50km from home)")
    print("Day 6: 45km SW → Home (45km ✅)")

    print("\n" + "=" * 80)
    print("🧮 MATH CHECK for your 5-night, 40-50km/day trip:")
    print(f"Maximum safe radius: {max_radius_km} km")
    print("This keeps you in Massachusetts/nearby areas, not Vermont/NH!")
    print("Each day's return distance is validated against remaining days.")

    return max_radius_km


def show_prompt_snippet():
    """Show key parts of the actual improved prompt."""
    print("\n" + "=" * 80)
    print("📝 ACTUAL PROMPT IMPROVEMENTS:")
    print("=" * 80)

    prompt_snippet = """
CRITICAL REQUIREMENTS FOR CLOSED-LOOP TOURS:
1. **Every single day MUST be within 40-50 km** - including the final return day
2. **Plan a true loop, not out-and-back** - avoid going straight out and straight back
3. **Maximum radius calculation** - with 6 days and 40-50 km/day, you can only go about 94km from start as the crow flies
4. **Think circular/polygonal** - plan destinations that form a roughly circular or polygonal pattern around the start point
5. **Balance the loop** - ensure you're never more than 94km from home at any point

VALIDATION CHECKLIST FOR EACH DAY:
- Day 1 destination: Can you get back to home in 5 days at 40-50 km/day?
- Day 2 destination: Can you get back to home in 4 days at 40-50 km/day?
- Day 3 destination: Can you get back to home in 3 days at 40-50 km/day?
- Day 4 destination: Can you get back to home in 2 days at 40-50 km/day?
- Day 5 destination: Can you get back to home in 1 days at 40-50 km/day?
- Final day: MUST be exactly within 40-50 km of home

IMPORTANT: Every overnight location MUST be positioned such that:
(distance_from_start_km * 1.4) <= (days_remaining_to_return * max_daily_distance)
This ensures you can always get back within your daily distance constraints.
"""

    print(prompt_snippet)
    print("=" * 80)


if __name__ == "__main__":
    max_radius = show_improved_prompt()
    show_prompt_snippet()

    print(f"\n🎉 SUMMARY:")
    print(f"The improved prompt now prevents the AI from planning destinations")
    print(f"beyond {max_radius} km from your start point, and validates each day")
    print(f"to ensure you can return within your daily distance constraints.")
    print(f"\nThis should solve the Vermont/New Hampshire problem you experienced!")
    print(f"\nTry running a new tour plan and the AI should keep you within")
    print(f"Massachusetts and nearby areas for a 5-night, 40-50km/day trip.")

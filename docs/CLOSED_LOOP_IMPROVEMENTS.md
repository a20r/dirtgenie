# Closed-Loop Tour Planning Improvements

## Problem Identified
The user reported that when planning a 5-night closed-loop tour (starting and ending at home) with 40-50km daily distance preference, the AI was planning 5 nights progressively further away (potentially reaching Vermont or New Hampshire) and then expecting a massive final day ride back home that would violate the daily distance constraints.

## Root Cause
The original closed-loop prompt didn't adequately consider the "return constraint" - ensuring that every overnight location could be reached from home within the remaining days at the specified daily distance.

## Solution Implemented

### 1. Maximum Radius Calculation
- **Formula**: `max_radius = avg_daily_distance * total_days * 0.35`
- **For 6-day, 40-50km/day trip**: Max radius ≈ 94km from start
- **Purpose**: Prevents AI from planning destinations too far away

### 2. Daily Validation Checklist
Added explicit validation for each day:
- Day 1: Can return home in 5 remaining days?
- Day 2: Can return home in 4 remaining days?
- Day 3: Can return home in 3 remaining days?
- Day 4: Can return home in 2 remaining days?
- Day 5: Can return home in 1 remaining day?
- Day 6: Must be within daily distance of home

### 3. Mathematical Constraint
Every overnight location must satisfy:
```
(distance_from_start_km * 1.4) ≤ (days_remaining * max_daily_distance)
```
The 1.4 factor accounts for the fact that bicycle routes are typically 40% longer than straight-line distance.

### 4. Geometric Planning
- Emphasizes circular/polygonal route patterns
- Discourages linear out-and-back patterns
- Encourages regional loop thinking

### 5. Enhanced JSON Response Format
Added fields to track:
- `distance_from_start_km`: Straight-line distance from home
- `days_remaining_to_return`: Days left to get back
- `validation_note`: Confirms return feasibility

## Example Impact

### Before (Problematic)
```
Day 1: Home → 45km out
Day 2: 45km → 90km out  
Day 3: 90km → 135km out
Day 4: 135km → 180km out
Day 5: 180km → 225km out (Vermont/NH)
Day 6: 225km → Home (225km = 5x daily limit! ❌)
```

### After (Improved)
```
Day 1: Home → 45km NE
Day 2: 45km NE → 45km N (60km from home)
Day 3: 45km N → 45km NW (70km from home)
Day 4: 45km NW → 45km W (60km from home)
Day 5: 45km W → 45km SW (50km from home)
Day 6: 45km SW → Home (45km ✅)
```

## Code Changes
Modified the `plan_tour_itinerary()` function in `src/dirtgenie/planner.py`:

1. **Added radius calculation** for closed-loop tours
2. **Enhanced prompt** with validation requirements
3. **Improved instructions** for geometric planning
4. **Added mathematical constraints** to prevent overextension

## Expected Results
For a 5-night, 40-50km/day trip starting from Massachusetts:
- **Old behavior**: Could plan destinations in Vermont/New Hampshire
- **New behavior**: Should keep destinations within ~94km radius (Massachusetts and nearby areas)
- **Daily distances**: All days should respect 40-50km limit, including final return day

## Testing
The improvements can be tested by running a closed-loop tour plan with the updated prompt. The AI should now:
1. Calculate maximum safe radius
2. Plan destinations in a circular pattern
3. Validate each day's return feasibility
4. Keep final day within daily distance constraints

This solves the specific issue where the AI was violating daily distance constraints on the return journey of closed-loop tours.

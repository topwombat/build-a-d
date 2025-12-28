## Month 1: Detailed Study Plan

**Total hours: 36-40 hours (4 weeks × 9 hrs/week)**

**Materials needed:**
- "Introduction to Flight" 9th Edition by John Anderson
- "Mechanics of Materials" 8th Edition by Beer, Johnston, DeWolf
- Engineering notebook (physical or digital - start your design journal)
- Calculator (or Python/MATLAB for more complex calculations)
- Graph paper or digital sketching tool

**Goal for Month 1:** 
Build foundational understanding of aerodynamics and structural mechanics. Begin conceptual design work. Develop the habit of working problems and documenting decisions.

---

## Week 1: Aerodynamics Foundations (9 hours)

### Day 1 (1.5 hrs)
**Reading:** Anderson Chapter 1 - "The First Aeronautical Engineers"
- Skim for historical context (30 min)
- Focus on fundamental principles and definitions (30 min)

**Reading:** Anderson Chapter 2.1-2.5 - "Aerodynamics: Some Fundamental Principles"
- Continuity equation
- Momentum equation  
- Energy equation (Bernoulli's equation)
- 30 min

**Problems:** (30 min)
- Problem 2.1: Continuity equation application
- Problem 2.3: Bernoulli's equation

**Design Journal:** Write down: "What makes aerobatic aircraft different aerodynamically?" Start a list. (10 min)

### Day 2 (1.5 hrs)
**Reading:** Anderson Chapter 2.6-2.13 (finish Chapter 2)
- Pressure, temperature, density relationships
- Viscosity and Reynolds number
- Speed of sound and Mach number

**Problems:** (45 min)
- Problem 2.8: Standard atmosphere calculations
- Problem 2.12: Reynolds number calculation
- Problem 2.15: Mach number and compressibility

**Design Journal:** Calculate Reynolds number for Super Decathlon wing at cruise. What does this tell you? (15 min)

### Day 3 (1.5 hrs)
**Reading:** Anderson Chapter 3 - "The Standard Atmosphere"
- Skip the historical parts
- Focus on altitude effects, density altitude

**Problems:** (45 min)
- Problem 3.1, 3.3, 3.5: Atmosphere calculations
- Calculate density altitude for your local airport on a hot day

**Practical:** (30 min)
Look up actual Super Decathlon performance data (POH available online). Note how performance degrades with density altitude. This is real engineering - matching theory to data.

### Day 4 (1.5 hrs)
**Reading:** Anderson Chapter 4.1-4.5 - "Basic Aerodynamics" (first half)
- Lift and drag
- Pressure distribution over an airfoil
- Lift coefficient, drag coefficient
- Pitching moment

**Problems:** (30 min)
- Problem 4.1: Lift calculation
- Problem 4.3: Drag calculation

**Design Journal:** (30 min)
Research airfoils used in aerobatic aircraft:
- NACA 0012 (symmetric)
- NACA 23012 (semi-symmetric, used in Super Decathlon)
- NACA 0015
Why would you choose one over another?

### Day 5 (1.5 hrs)
**Reading:** Anderson Chapter 4.6-4.12 (finish Chapter 4)
- Angle of attack effects
- Stall
- Airfoil families (NACA designations)
- High lift devices

**Problems:** (45 min)
- Problem 4.7: Lift coefficient vs angle of attack
- Problem 4.9: Stall angle calculation
- Problem 4.12: NACA airfoil designation

**Critical exercise:** (30 min)
Download XFLR5 (free software). Import NACA 23012 airfoil. Run analysis at Re = 3 million, angle of attack -5° to +15°. Plot Cl vs alpha. Compare to symmetric NACA 0012. Document what you see.

### Day 6 (1.5 hrs)
**Week 1 Integration Day**

**Review:** (30 min)
- Re-work one problem from each chapter that you struggled with
- Review your notes

**Design work:** (45 min)
Create a spreadsheet:
- Input: velocity, altitude, wing area, weight
- Calculate: dynamic pressure, lift coefficient required, Reynolds number
- Test with Super Decathlon data (cruise: 120 kts, 155 sq ft wing, 1800 lbs)
- Does your calculated Cl match typical cruise Cl (~0.3-0.4)?

**Planning:** (15 min)
Review Week 2 plan. Prepare questions you have so far.

---

## Week 2: Finite Wings & Structural Foundations (9 hours)

### Day 7 (1.5 hrs)
**Reading:** Anderson Chapter 5.1-5.6 - "Finite Wings"
- Downwash and induced drag
- Aspect ratio effects
- Lifting line theory basics

**Problems:** (45 min)
- Problem 5.1: Induced drag calculation
- Problem 5.3: Aspect ratio effects
- Problem 5.5: Elliptical lift distribution

**Design Journal:** (15 min)
Super Decathlon has aspect ratio ~6.6 (32 ft span, 155 sq ft area). Why not higher? (Hint: structural weight, roll rate for aerobatics)

### Day 8 (1.5 hrs)
**Reading:** Anderson Chapter 5.7-5.12 (finish Chapter 5)
- Wing planform effects (taper, sweep)
- Tip vortices

**Problems:** (45 min)
- Problem 5.8: Induced drag for different planforms
- Problem 5.11: Effect of aspect ratio on L/D

**Design exercise:** (30 min)
Sketch three wing planforms for your aircraft:
1. Rectangular (simple to build)
2. Tapered (efficiency)
3. Elliptical (optimal, but complex)

Calculate area, aspect ratio, mean chord for each. Which would you choose and why?

### Day 9 (1.5 hrs)
**Reading:** Beer/Johnston Chapter 1 - "Introduction to Mechanics of Materials"
- Concept of stress (normal and shear)
- Concept of strain
- Stress-strain relationships
- Elastic vs plastic behavior

**Problems:** (45 min)
- Problem 1.1: Normal stress calculation
- Problem 1.5: Shear stress
- Problem 1.8: Stress in simple tension

**Connection:** (15 min)
Think about wing spar in 6g pull-up. Sketch the spar. Where is tension? Where is compression?

### Day 10 (1.5 hrs)
**Reading:** Beer/Johnston Chapter 2.1-2.8 - "Stress and Strain - Axial Loading" (first half)
- Normal stress in axial members
- Stress in members of varying cross-section
- Stress concentration

**Problems:** (60 min)
- Problem 2.1, 2.3: Axial stress calculations
- Problem 2.7: Stress concentration
- Problem 2.11: Tapered bar under tension

**Think ahead:** Landing gear leg under landing load is primarily axial compression. Keep this in mind.

### Day 11 (1.5 hrs)
**Reading:** Beer/Johnston Chapter 2.9-2.17 (finish Chapter 2)
- Strain and deformation
- Poisson's ratio
- Generalized Hooke's law
- Saint-Venant's principle

**Problems:** (60 min)
- Problem 2.15: Deformation calculation
- Problem 2.19: Multiple materials
- Problem 2.23: Thermal effects

**Design Journal:** (20 min)
Look up material properties:
- 4130 steel (used in Super Decathlon fuselage): E = 30×10⁶ psi, σ_yield = 75 ksi
- 6061-T6 aluminum: E = 10×10⁶ psi, σ_yield = 40 ksi
- Spruce (wood): E = 1.5×10⁶ psi, σ_allowable = 8 ksi (bending)

Create a material properties table for your design reference.

### Day 12 (1.5 hrs)
**Week 2 Integration Day**

**Review:** (30 min)
Rework difficult problems from Week 2

**Major design exercise:** (60 min)
**Calculate induced drag for your preliminary wing design:**

Given (starting assumptions):
- Wing span: b = 32 ft
- Wing area: S = 155 sq ft  
- Weight: W = 1800 lbs
- Cruise speed: V = 120 kts = 203 ft/s
- Altitude: sea level (ρ = 0.002377 slugs/ft³)

Calculate:
1. Aspect ratio: AR = b²/S
2. Lift coefficient at cruise: CL = W / (0.5 ρ V² S)
3. Induced drag coefficient: CDi = CL² / (π × AR × e) [assume e = 0.8]
4. Induced drag: Di = CDi × 0.5 ρ V² S

Compare to known Super Decathlon data if you can find it.

**Document everything in your design journal.**

---

## Week 3: Airfoil Selection & Beam Bending (9 hours)

### Day 13 (1.5 hrs)
**Reading:** Anderson Chapter 4 - **Re-read with new perspective**
Now that you understand finite wings, re-read the airfoil chapter focusing on:
- Pressure distributions
- Moment coefficient
- Center of pressure vs aerodynamic center

**XFLR5 Work:** (60 min)
Analyze these airfoils in XFLR5:
- NACA 0012 (symmetric)
- NACA 23012 (Super Decathlon airfoil)
- NACA 0015

For each at Re = 3 million:
- Plot Cl vs alpha
- Plot Cd vs alpha  
- Plot Cl/Cd vs alpha
- Note stall angle, max Cl, Cl at zero alpha

**Design decision:** (20 min)
Write one page: "My airfoil choice and justification"

### Day 14 (1.5 hrs)
**Reading:** Anderson Chapter 6.1-6.7 - "Three-Dimensional Incompressible Flow"
- Source and vortex flow
- Lifting line theory (Prandtl's)

This is more theoretical - skim for understanding, focus on concepts over derivations given your math background.

**Problems:** (45 min)
- Problem 6.1: Vortex flow
- Problem 6.3: Circulation and lift

**Design application:** (30 min)
Sketch spanwise lift distribution for your wing. Elliptical? Trapezoidal? What's practical for a strut-braced wing?

### Day 15 (1.5 hrs)
**Reading:** Beer/Johnston Chapter 3 - "Torsion" (critical for aerobatic aircraft!)
- Shear stress in circular shafts
- Angle of twist
- Torsional stress in thin-walled tubes

**Problems:** (60 min)
- Problem 3.1: Torsion in solid shaft
- Problem 3.7: Hollow circular shaft
- Problem 3.11: Angle of twist

**Critical application:** (20 min)
Fuselage tube under torsion during snap roll. Sketch fuselage cross-section. How is it triangulated to resist torsion?

### Day 16 (1.5 hrs)
**Reading:** Beer/Johnston Chapter 4.1-4.6 - "Pure Bending" (first half)
- Symmetric member in pure bending
- Stress and strain distribution
- Bending stress formula: σ = My/I
- Section modulus

**Problems:** (60 min)
- Problem 4.1: Bending stress in beam
- Problem 4.5: Section modulus
- Problem 4.9: Beam of two materials

**Design connection:** (20 min)
Wing spar is a beam in bending. The lift distribution is your loading. The root bending moment is maximum. Keep this in mind.

### Day 17 (1.5 hrs)
**Reading:** Beer/Johnston Chapter 4.7-4.10 (finish Chapter 4)
- Deformations in symmetric beams
- Deflection equations
- Integration methods

**Problems:** (60 min)
- Problem 4.15: Beam deflection
- Problem 4.19: Cantilever beam
- Problem 4.23: Simply supported beam

**Insight:** (20 min)
Wing is like a cantilever beam with distributed load (lift). Root moment is maximum. Tip deflection must be limited (flutter concerns). Write these observations down.

### Day 18 (1.5 hrs)
**Week 3 Integration Day**

**Major structural exercise:** (90 min)

**Design a preliminary wing spar:**

Given:
- Limit load factor: n = +6g
- Gross weight: W = 1800 lbs
- Wing semi-span: b/2 = 16 ft
- Assume elliptical lift distribution

**Calculate:**
1. Total lift at limit load: L = n × W = 10,800 lbs
2. Lift per unit span at root (elliptical): L₀ = 4L/(πb) = 4(10,800)/(π×32) = 429 lb/ft
3. Shear force at root: V = ∫L₀ × [1-(2y/b)²]^0.5 dy from 0 to b/2 = 5,400 lbs
4. Bending moment at root: M = ∫(y × lift distribution) dy ≈ 57,600 ft-lbs = 691,200 in-lbs

5. **Size the spar:**
Assume rectangular spar, 6 inches deep, spruce (σ_allowable = 8,000 psi):

Required section modulus: S = M/σ = 691,200/8,000 = 86.4 in³

For rectangular section: S = bd²/6
If d = 6": 86.4 = b(6²)/6 → b = 14.4 in

That's a 6" × 14.4" spar at the root - massive! 

This is why:
- Strut bracing reduces root bending moment
- I-beam or box spar is more efficient than solid rectangle
- Ultimate load (1.5x limit) drives even larger sizing

**Document this complete calculation. This is real aircraft design.**

---

## Week 4: Drag Analysis & Preliminary Sizing (9 hours)

### Day 19 (1.5 hrs)
**Reading:** Anderson Chapter 5 - **Re-read for drag estimation**
Focus on:
- Total drag breakdown (induced + parasitic)
- Drag polar estimation
- L/D max

**Reading:** Start Anderson Chapter 6.12-6.19 - Drag estimation methods

**Problems:** (45 min)
- Problem 5.15: Drag polar
- Problem 5.17: L/D max calculation

**Design work:** (30 min)
Start building your drag model:
- Induced drag: CDi = CL²/(π × AR × e)
- Parasitic drag: CD₀ = ? (estimate ~0.025 for clean aircraft)
- Total: CD = CD₀ + CDi

Plot drag polar for your design.

### Day 20 (1.5 hrs)
**Reading:** Anderson Chapter 7.1-7.5 - "Compressible Flow"
Skim this - your aircraft is subsonic, but understand:
- Mach number effects
- Critical Mach number
- Compressibility corrections

**Focus on practical:** (60 min)
Calculate for your design:
- Maximum speed estimate: ~180 kts
- Mach number at 180 kts at sea level: M ≈ 0.27
- Conclusion: Compressibility effects negligible

**Start performance analysis:** (30 min)
Power required equation: PR = D × V

Calculate power required vs velocity for your aircraft. Plot it. Where is minimum power? This tells you best endurance speed.

### Day 21 (1.5 hrs)
**Reading:** Anderson Chapter 8.1-8.6 - "Propellers"
- Momentum theory
- Blade element theory  
- Propeller efficiency

**Problems:** (45 min)
- Problem 8.1: Momentum theory
- Problem 8.3: Propeller efficiency

**Design consideration:** (30 min)
Super Decathlon uses constant-speed prop (Hartzell). Why is this essential for aerobatic aircraft? Write your reasoning.

Consider:
- Vertical climb: need fine pitch (high RPM, low airspeed)
- Cruise: need coarse pitch (lower RPM, high airspeed)
- Constant-speed prop adjusts automatically

### Day 22 (1.5 hrs)
**Reading:** Anderson Chapter 11 - "Principles of Stability and Control" (overview)
- Static vs dynamic stability
- Longitudinal stability
- Trim conditions

Skim this for now - you'll come back to it in detail later. Just get the concepts.

**Application:** (60 min)
Draw side view of aircraft. Mark:
- Center of gravity (CG)
- Aerodynamic center of wing (AC) - roughly 25% MAC
- Tail arm (distance from CG to tail AC)

Static margin = (AC - CG) / MAC

For stability, AC must be aft of CG. Typical static margin: 5-15% MAC.

Sketch this and calculate for Super Decathlon geometry.

### Day 23 (1.5 hrs)
**Preliminary sizing day**

**Reading:** Look ahead to Raymer Chapter 3 (if you have the book yet) - "Sizing from a Conceptual Sketch"

Or work from first principles:

**Wing loading selection:** (45 min)

Wing loading W/S affects:
- Stall speed: Vs = √[2W/(ρ S CL_max)]
- Maneuverability: Turn radius
- Structural weight

For aerobatic aircraft, W/S = 11-13 lb/ft² typical

Super Decathlon: 1800 lb / 155 ft² = 11.6 lb/ft²

Choose your wing loading. Calculate wing area needed.

**Power loading selection:** (45 min)

Power loading W/P affects:
- Climb rate
- Acceleration
- Takeoff distance

For aerobatic: W/P = 9-11 lb/hp typical

Super Decathlon: 1800 lb / 180 hp = 10 lb/hp

Choose your power loading. Calculate horsepower needed.

### Day 24 (1.5 hrs)
**Month 1 Review and Documentation**

**Deliverables for Month 1:** (90 min)

Create a document (5-10 pages) with:

**1. Airfoil Selection**
- Chosen airfoil with justification
- XFLR5 analysis plots
- Cl_max, stall angle, L/D characteristics

**2. Preliminary Wing Design**
- Wing area: ___ ft²
- Wing span: ___ ft
- Aspect ratio: ___
- Taper ratio: ___
- Airfoil: ___
- Justification for each choice

**3. Preliminary Spar Sizing**
- Load case: +6g at 1800 lbs
- Root bending moment calculation
- Spar dimensions (rough estimate)
- Material choice

**4. Drag Polar**
- CD vs CL plot
- Estimated L/D_max
- Cruise drag estimate

**5. Performance Estimates (preliminary)**
- Wing loading: ___ lb/ft²
- Power loading: ___ lb/hp
- Estimated cruise speed
- Estimated stall speed

**6. Questions and Uncertainties**
List everything you don't know yet but need to learn

**7. Month 2 Goals**
What will you accomplish next month?

---

## Study Habits for Success

**Problem-solving discipline:**
- Never skip the problems
- Work them on paper first, check with calculator/code
- If you get stuck more than 15 minutes, check the solution, understand it, then re-work it yourself
- Keep a "problem solutions" section in your notebook

**Design journal:**
- Date every entry
- Sketch constantly - visualization matters
- Document assumptions explicitly
- When you make a design choice, write WHY
- Track your evolving understanding

**Software integration:**
- As a software architect, create tools to automate repetitive calculations
- Build up a Python/MATLAB library of aircraft equations
- Version control your design (Git repository for your project)
- But: Work problems by hand first to build intuition

**Connection to flying:**
- After every major concept, think: "How do I experience this as a pilot?"
- When studying stability: Remember how your Decathlon feels in various CG positions
- When studying structures: Think about the g-forces you've felt in aerobatics
- Your intuition is data - use it to validate theory

**Weekly rhythm:**
- Days 1-4: Push forward, new material
- Day 5: Harder problems, integration
- Day 6: Apply to design, document

**Stay focused:**
- It's tempting to go down rabbit holes (composite structures! Turbulence modeling! Computational fluid dynamics!)
- Resist for now - stick to the critical path
- Keep a "Future deep dives" list for interesting tangents
- Your goal is preliminary design in 12-15 months, not a PhD

---

## End of Month 1 Checkpoint

**You should be able to:**
- Calculate lift and drag for a given wing at a given flight condition
- Estimate induced drag for different aspect ratios
- Calculate stress in simple structural members (tension, bending, torsion)
- Justify your preliminary airfoil choice
- Sketch a preliminary wing planform with dimensions
- Estimate a wing spar size for your load case
- Explain why the Super Decathlon is configured the way it is

**You should have:**
- ~40 hours of study logged
- Design journal with 20+ pages of notes, sketches, calculations
- Airfoil analysis in XFLR5
- Preliminary wing design document
- Calculation spreadsheets for drag, performance
- Clear plan for Month 2

**If you're behind:**
Don't panic. Life happens. But diagnose why:
- Not enough time? Adjust schedule
- Skipping problems? Don't - this is where learning happens
- Getting bogged down in details? Focus on critical path

**If you're ahead:**
Excellent. Deep dive into one topic that interests you, but don't skip ahead in the curriculum. Depth beats breadth at this stage.

---

## Looking Ahead to Month 2

**Focus:**
- Finish "Introduction to Flight" (Chapters 9-11: Performance, Stability)
- Continue structures (shear, combined loading, columns)
- Start "Aircraft Design" by Raymer
- Preliminary configuration layout
- Weight estimation
- CG analysis

But that's for next month. For now: **Order your books, start tomorrow, and work that first problem set this weekend.**

You're committed to 1.5 hours/day, 6 days/week. That's enough. The key is consistency and working the problems. Everything else follows.

Ready to start?

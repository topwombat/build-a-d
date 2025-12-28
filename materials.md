Good news: structures is entirely learnable, and for aerobatic aircraft it's arguably THE most critical discipline. Aerodynamics gets you in the air; structures keeps you alive when pulling 6g in a hammerhead turn.

## Structures Learning Path

**Prerequisites - Strength of Materials:**
Before aircraft structures, you need the fundamentals. Start with:

**"Mechanics of Materials" by Beer, Johnston, and DeWolf** - This is THE textbook for basic strength of materials. You need to master:
- Stress and strain (tension, compression, shear)
- Axial loading and deformation
- Torsion (critical for aerobatic aircraft!)
- Bending stress and deflection
- Combined loading
- Column buckling (Euler buckling)

Work through this methodically. Do problems. This is your foundation. **Budget 3-4 months here if you're serious.**

**Aircraft-Specific Structures:**

**"Aircraft Structures for Engineering Students" by T.H.G. Megson** (6th edition) - This is comprehensive but can be dense. The newer editions are more pedagogical. Focus on:
- Part 1: Basic elasticity and structural analysis
- Part 2: Bending, shear, and torsion of open/closed sections
- Part 3: Wing structures, fuselage structures
- Part 4: Loads on aircraft (V-n diagrams, gust loads, landing loads)

Alternative if Megson feels too heavy: **"Analysis and Design of Flight Vehicle Structures" by Bruhn** - This is the industry bible. It's old (1973) but still used by every aircraft structures engineer. More practical, less theoretical than Megson.

## Why Structures is Critical for Your Project

**The Loading Problem:**

A normal general aviation aircraft is certified to +3.8/-1.5g. Your aerobatic aircraft needs +6/-5g minimum. Here's what that means:

At 1800 lbs gross weight:
- Normal aircraft wing: must support 6,840 lbs (3.8g × 1800)
- Your aircraft wing: must support **10,800 lbs** (6g × 1800) limit load
- Ultimate load (1.5x limit): **16,200 lbs** - the wing must hold this without failing

That's nearly **9 times the aircraft's weight** the structure must support without breaking. And it has to do this repeatedly, tens of thousands of times, without fatigue failure.

**The V-n Diagram:**

This is your design bible. It plots load factor (g) vs. airspeed and defines your structural envelope:

```
        +6g _____________ (Vne - never exceed speed)
           /              \
          /                \
    +1g  /                  \
        /____________________\______ speed
       Va                    Vd
    -1g \                    /
         \                  /
      -5g \________________/
```

Every structural member must be designed for the worst-case combination of speed and load factor within this envelope. For aerobatic aircraft:
- **Va (maneuvering speed)**: Speed below which you can apply full control deflection without exceeding limit load. Around 100-120 kts for your aircraft.
- **Vne (never exceed)**: Around 180-200 kts for a Super Decathlon class aircraft.

**Critical Load Cases for Aerobatic Aircraft:**

1. **Positive limit load at Va** (+6g): Bottom of a loop, pull-up from dive
2. **Negative limit load at Va** (-5g): Top of outside loop, push-over
3. **Asymmetric loads**: Snap roll creates massive asymmetric wing loads - one wing stalled, one producing lift
4. **Landing loads**: 3-point landing at gross weight creates huge loads on landing gear and fuselage
5. **Torsional loads**: Snap rolls and autorotation generate enormous torsion in fuselage and wing spars

## Structure-Specific Challenges in Your Design

**Wing Structure:**

The Super Decathlon uses a **Harer wing** - it's a strut-braced design which reduces bending moments in the main spar. This is actually a very smart choice for aerobatic aircraft:

**Bending moment distribution:**
- Cantilever wing: Maximum bending at root, linearly decreasing to tip
- Strut-braced wing: Strut attachment point becomes a support, dramatically reducing root bending moment

You need to calculate:
- **Shear force diagram** along the span
- **Bending moment diagram** along the span  
- **Spar cap stress** (bending stress = My/I where M is moment, y is distance from neutral axis, I is moment of inertia)
- **Web shear stress** in the spar
- **Skin buckling** under compression loads
- **Rib spacing** to prevent skin buckling

The wing spar in a Super Decathlon is a **massive** piece of wood (spruce) or metal. It's oversized because it takes the entire bending load plus landing loads transmitted through the gear.

**Fuselage Structure:**

The Super Decathlon uses **welded 4130 steel tube** construction. This is brilliant for aerobatic aircraft because:

1. **Torsion resistance**: Triangulated tube frame naturally resists torsion. Every bay is triangulated to prevent racking.

2. **Redundancy**: Tubular space frame is highly redundant - load paths are multiple.

3. **Damage tolerance**: Cracks are visible, propagate slowly, and the structure remains intact even with local damage.

4. **Repairability**: Welded steel tube can be repaired in any shop with a TIG welder.

You need to analyze:
- **Torsional rigidity**: J (torsional constant) for the fuselage cross-section
- **Column buckling**: Individual tubes in compression can buckle (Euler buckling or Johnson equation depending on slenderness ratio)
- **Joint strength**: Welded joints must be stronger than tubes
- **Local loads**: Engine mount, landing gear, wing attach, and tail attach fittings

**Critical Concept - Torsion:**

This is where aerobatic aircraft are most different. In a snap roll, you're:
- Stalling one wing (killed lift)
- Full aileron deflection (rolling moment)
- Full rudder (yawing moment)  
- Abrupt pitch input (pitching moment)

The fuselage is subjected to **enormous** torsional loads. For a tube structure:

Torsional stress τ = Tr/J

Where:
- T = applied torque
- r = radius  
- J = polar moment of inertia

For a circular tube: J = π(D⁴ - d⁴)/32

This is why you see such heavy-wall tubing in aerobatic aircraft fuselages. The Super Decathlon uses 4130 steel with 0.058" to 0.095" wall thickness depending on location.

**Wing-Fuselage Attachment:**

This is the highest loaded area of the entire aircraft. The wing attach fittings must transfer:
- Vertical loads (lift)
- Fore-aft loads (drag)
- Spanwise loads (side loads in slips)
- Torsional loads (wing twisting moments)

In the Super Decathlon, these are **massive** steel fittings bolted to the fuselage with AN hex bolts in double shear. You need to calculate:
- **Bearing stress** in bolt holes
- **Shear stress** in bolts  
- **Tensile stress** in fittings
- **Bending stress** in fittings

And ensure the combined loads don't exceed material yield strength with adequate safety factor.

## Practical Learning Exercise

Here's a simplified exercise to build your structures intuition:

**Design a main wing spar for your aircraft:**

Given:
- Wing span: 32 ft
- Wing area: 155 sq ft
- Gross weight: 1800 lbs
- Limit load factor: +6g
- Assume elliptical lift distribution

Calculate:
1. Total lift required at 6g: L = 6 × 1800 = 10,800 lbs
2. Lift per foot of span (at root, elliptical): ~675 lbs/ft
3. Shear force diagram (integrate lift distribution)
4. Bending moment diagram (integrate shear)
5. Maximum bending moment (at root): ~55,000 ft-lbs
6. Required spar cap area (assuming spruce, allowable bending stress ~8000 psi, spar depth 6 inches)

This exercise teaches you the fundamental flow: **Loads → Shear → Moment → Stress → Size structural members**

## Study Strategy

**Month 1-2:** Mechanics of Materials basics
- Do every assigned problem on stress, strain, bending, torsion
- Focus on drawing free body diagrams - this skill is essential

**Month 3-4:** Aircraft loads  
- Learn to construct V-n diagrams
- Calculate limit and ultimate loads
- Study FAR Part 23 requirements for aerobatic category

**Month 5-6:** Wing structures
- Analyze spar bending and shear
- Study rib design and skin buckling
- Strut-braced vs cantilever tradeoffs

**Month 7-8:** Fuselage structures
- Tube structures and torsion
- Landing gear loads
- Tail loads and attachment

**Throughout:** Study actual aircraft
- Get drawings of tube-and-fabric aircraft (Citabria, Decathlon drawings are available)
- Measure tube sizes, wall thickness, triangulation patterns
- Understand WHY each member is sized as it is

## The Bottom Line

Structures is learnable, but it requires discipline. Unlike aerodynamics where you can often develop intuition visually, structures requires:
- Mathematical rigor (no hand-waving)
- Attention to detail (unit errors kill people)
- Conservative design (factors of safety exist for good reason)

But here's the good news: once you understand strength of materials and can draw a proper free body diagram, aircraft structures becomes systematic. It's not creative or artistic - it's methodical analysis. Load path by load path, member by member, joint by joint.

For an aerobatic aircraft, you're designing something that will be deliberately abused. Your structure must be robust, redundant, and damage-tolerant. That's actually easier to design for than an optimized, minimum-weight transport aircraft where every ounce matters.

Want me to work through a specific structures problem as an example? Or discuss material selection (steel tube vs aluminum vs composite)?

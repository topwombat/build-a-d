## Study Plan for Aerobatic Aircraft Design

**Phase 1: Building Intuition (3-4 months)**
- Read "Understanding Flight" cover to cover for conceptual foundation
- Start "Introduction to Flight" chapters 1-6 (aircraft components, atmosphere, basic aerodynamics)
- Simultaneously study/review calculus if rusty - Khan Academy or Paul's Online Math Notes work well
- **Milestone**: Sketch your initial Super Decathlon concept with rough dimensions and explain why each design choice matters

**Phase 2: Core Aerodynamics (4-6 months)**
- Complete "Introduction to Flight" chapters 7-end (performance, stability, control)
- Begin "Fundamentals of Aerodynamics" - focus on chapters 1-6 (incompressible flow, airfoils, finite wings)
- Work through example problems religiously - this is where learning happens
- **Milestone**: Calculate lift/drag polars for candidate airfoils, estimate wing loading and power loading for your design

**Phase 3: Integrated Design (6-8 months)**
- "Aircraft Design: A Conceptual Approach" by Raymer - work through systematically
- Apply each chapter to your Super Decathlon redesign as you go
- Start "Aircraft Structures" - focus on bending, shear, and load analysis chapters
- **Milestone**: Complete preliminary design with weight estimate, performance predictions, and basic structural sizing

**Phase 4: Refinement (ongoing)**
- Deep dive into specific areas: stability derivatives, control surface sizing, flutter analysis
- Study actual certified aircraft data - get your hands on Type Certificates, flight manuals
- Consider CAD work (XFLR5 for aerodynamics is free and excellent for learning)

## What Makes Aerobatic Aircraft Special

**Structural Design - Built for Violence:**

The Super Decathlon is certified for +6/-5g, but you'll design for higher ultimate loads (typically 1.5x limit load = +9/-7.5g). This changes everything:

- **Symmetric airfoils**: Unlike normal aircraft with cambered airfoils optimized for upright flight, aerobatic aircraft use symmetric airfoils (like NACA 0012 or similar). They perform equally well inverted, though you sacrifice some efficiency in cruise. The Super Decathlon actually uses a semi-symmetric airfoil as a compromise.

- **Beef everywhere**: Spars are heavier, skin is thicker, ribs are closer together. Wing attach fittings are massively overbuilt. You're essentially designing a structure that won't fail when loaded to several times the aircraft's weight - repeatedly, for thousands of cycles.

- **Fuselage torsion**: Snap rolls and lomcevaks put huge torsional loads on the fuselage. Tube-and-fabric designs (like the Super D) handle this naturally through triangulation. If you're considering composite construction, torsional stiffness becomes a critical design driver.

**Aerodynamic Characteristics:**

- **High roll rate**: Ailerons must be large and powerful. The Super Decathlon has nearly full-span ailerons. You need enough roll authority to achieve 180+ degrees/second roll rates. This means careful attention to adverse yaw (differential ailerons or coupled rudder).

- **Spin and snap roll recovery**: The tail must be large enough to overpower the wing when stalled and rotating. Vertical tail volume coefficient will be higher than a normal aircraft. You need elevator authority to break the stall in an upright or inverted spin.

- **Knife-edge flight capability**: Large vertical tail area relative to side fuselage area. The rudder must generate enough side force to support the aircraft's weight when flying sideways.

- **Controllable throughout the envelope**: Unlike transport aircraft designed never to stall, your aircraft must remain controllable while fully stalled, spinning, or in other unusual attitudes. Control surfaces stay effective even at high angles of attack.

**Control System Design:**

- **Control forces**: Aerobatic pilots need firm, responsive controls with good feedback. Control stick forces should be high enough to prevent over-control but not so high you can't hold them in a sustained maneuver. Typically 20-40 lbs for full elevator deflection.

- **Push-pull tubes**: Cable systems stretch and add slop. Serious aerobatic aircraft use rigid push-pull tubes for positive control connection. Weight penalty is worth it.

- **No trim tabs in some cases**: Or if used, they're ground-adjustable only. You don't want trim tabs that can accidentally deploy during violent maneuvers.

**Engine and Systems:**

- **Inverted fuel and oil systems**: The engine must run inverted for extended periods. This requires inverted fuel tanks or flop tubes, and an inverted oil system (separate scavenge system or Christen inverted oil system in Lycomings).

- **Constant speed propeller**: Essential for maintaining power in vertical maneuvers and during rapid attitude changes. Fixed-pitch propellers are compromises that work poorly across the aerobatic envelope.

- **Cooling in all attitudes**: Engine cooling must work in knife-edge flight, vertical climbs, and sustained inverted flight where normal cooling assumptions fail.

**Weight and Balance:**

- **Tight CG range**: Aerobatic aircraft have much tighter CG limits than normal aircraft. The Super Decathlon's CG range is only about 4 inches. This is because spin recovery and control harmony require precise weight distribution.

- **Solo aerobatics**: Your aircraft needs to be balanced for solo flight (pilot only) since that's how serious aerobatics are flown. Many designs put the pilot on the CG.

**Performance Targets for a Modern Super Decathlon:**

If you're modernizing the design, consider:
- Current Super D: 180hp, 1800 lbs gross, cruise ~120 kts, climb ~1200 fpm
- Modern improvements: Better engine (maybe 200hp fuel-injected), composite construction saving 100-150 lbs, improved aerodynamics (wheel pants, fairings) gaining 10-15 kts cruise
- But: Keep the benign handling that makes the Super D such a good trainer

**Key Design Decisions You'll Face:**

1. **Tube-and-fabric vs. composite?** Tube-and-fabric is proven, repairable, and handles torsion well. Composites save weight but require careful design for damage tolerance.

2. **Tailwheel vs. tricycle?** Nearly all aerobatic aircraft are taildraggers (better propeller clearance, less weight, cleaner lines), but tricycle gear is easier to land.

3. **Engine choice?** Lycoming IO-360 (180hp) or IO-390 (210hp)? More power is better for vertical performance but adds weight and cost.

4. **Airfoil?** NACA 0012/0015 family for pure symmetry, or something like a NACA 23012 for better cruise efficiency with acceptable inverted performance?

The beauty of using the Super Decathlon as your baseline is that it represents decades of refinement. Champion/Bellanca/American Champion have been building these aircraft since the 1970s, evolving from the original Decathlon. You're standing on the shoulders of giants - your job is to understand WHY each choice was made, then see where modern materials and methods offer improvements.

Does this help frame the challenge? What aspect interests you most - the structures problem, the aerodynamics, or the systems integration?

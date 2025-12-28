Excellent question - this is **flight dynamics and stability & control** territory, which is actually a separate discipline from both aerodynamics and structures. It's the bridge between "how much lift/drag do I generate" and "how does the aircraft actually behave when I move the stick."

## Where This Lives in the Curriculum

**Primary Sources:**

**"Flight Stability and Automatic Control" by Robert Nelson** - This is the standard undergraduate textbook. Chapters 2-4 cover:
- Static longitudinal stability (how CG affects pitch stability)
- Stick-fixed vs stick-free stability  
- Control forces and hinge moments
- Trim conditions

**"Dynamics of Flight: Stability and Control" by Etkin and Reid** - More advanced, graduate level. Chapter 5 specifically addresses spinning, though it's quite mathematical.

**"Airplane Aerodynamics and Performance" by Roskam and Lan** - Part of Roskam's 6-volume series. Volume II focuses on stability and control.

But honestly, for your specific question about the **practical relationship** between CG, spin recovery, and control harmony in aerobatic aircraft, the best source is:

**"Stick and Rudder" by Wolfgang Langewiesche** (for intuition)
**"The Compleat Taildragger Pilot" by Harvey Plourde** (practical aerobatic perspective)
**FAA AC 61-67C "Stall and Spin Awareness Training"** (free, practical)

And most importantly: **NACA/NASA technical reports on spinning** - particularly:
- NACA Report 557 "Spin Tests in the NACA Vertical Wind Tunnel"
- NASA TN D-6575 "Results of Spinning Tests"

## The Interconnected Relationship

Here's why these three things are inseparable in aerobatic design:

**1. CG Position → Static Stability**

The CG position relative to the wing's aerodynamic center (AC) determines your **static margin**:

Static margin = (AC - CG) / MAC × 100%

Where MAC = mean aerodynamic chord

- **Forward CG** (large static margin): Very stable, nose-heavy
  - Requires more elevator to raise nose
  - Harder to stall
  - Exits spins easily (nose wants to drop)
  - Heavy stick forces
  
- **Aft CG** (small static margin): Less stable, tail-heavy  
  - Light elevator forces
  - Easy to stall
  - Spins become flat and unrecoverable
  - Can become neutrally stable or even unstable

For a Super Decathlon, the CG range is roughly **83-87 inches aft of datum** (about 4 inches). That's incredibly tight compared to a Cessna 172 (11-inch range).

**2. CG Position → Spin Characteristics**

This is THE critical safety consideration:

**Forward CG spin:**
- Nose drops steeply (steep spin, 50-70° nose down)
- High rotation rate
- Elevator is powerful enough to break the stall
- Recovery: reduce power, neutralize ailerons, full opposite rudder, forward stick
- Recovers quickly (1-2 turns after inputs)

**Aft CG spin:**
- Nose remains high (flat spin, 20-40° nose down)
- Lower rotation rate but higher sink rate
- Elevator loses effectiveness (short moment arm)
- **MAY NOT RECOVER** - this is how people die
- Flat spin can be unrecoverable in extreme cases

The **aft CG limit** for aerobatic aircraft is typically set by spin recovery testing. They literally flight-test spins with ballast moved progressively aft until recovery becomes marginal, then set the limit forward of that point.

**Why flat spins don't recover:**

In a spin, the inner wing is stalled, outer wing is producing some lift. The aircraft rotates around a nearly vertical axis. Recovery requires:
1. Opposite rudder to stop rotation
2. Forward elevator to unstall the wing (reduce angle of attack)

With aft CG:
- Tail moment arm is reduced (CG moves toward tail)
- Elevator must generate MORE force to pitch nose down
- But wing is stalled, so downwash on tail is disturbed
- Elevator effectiveness is reduced when you need it most

**Flat spin death trap:** Once the spin flattens (nose comes up), centrifugal force pins you in the seat, nose won't drop, and you're corkscrewing straight down. This killed many test pilots in the early days.

**3. CG Position → Control Harmony**

"Control harmony" means the **relative forces and deflections** between elevator, aileron, and rudder feel matched and coordinated to the pilot. Good harmony means:
- Similar stick force per g in pitch and roll
- Rudder pedal force proportional to stick forces
- No surprising force reversals or non-linearities

CG position directly affects this:

**Forward CG:**
- Heavy elevator forces (long moment arm from CG to tail)
- Pitch stick forces become disproportionately heavy vs roll
- Pilot has to "horse" the aircraft around - tiring, imprecise
- Pitch rate is limited by elevator authority

**Aft CG:**
- Light elevator forces (short moment arm)
- Aircraft becomes "twitchy" in pitch
- Too sensitive - hard to hold precise attitudes
- Pitch oversensitivity vs roll leads to PIO (pilot-induced oscillation)

**Optimal CG for aerobatics:**
You want the CG positioned so that:
- Full aft stick at maneuvering speed gives ~6g (limit load)
- Stick force at 4g is moderate (~30-40 lbs)
- Pitch and roll forces are balanced
- Aircraft is stable but responsive

For the Super Decathlon, this sweet spot is around **85 inches** (mid-range of the CG envelope). Solo aerobatic pilots often fly here.

## How These Are Determined in Design

**The Design Process:**

**Step 1: Initial CG estimate**
- Place CG at ~25-30% MAC for initial stability
- This is your starting point

**Step 2: Static stability analysis**
- Calculate stick-fixed neutral point (where AC is)
- Ensure static margin of 5-15% MAC
- Too much = heavy controls, too little = dangerous

**Step 3: Trim analysis**
- At each flight condition (cruise, climb, glide, various speeds)
- Calculate elevator deflection required to trim
- Ensure elevator doesn't run out of authority
- Check stick forces are reasonable (2-4 lbs per g typical)

**Step 4: Spin testing** (in wind tunnel or CFD, then flight test)
- Test spins at forward CG limit - should recover easily
- Move CG aft incrementally
- Find the aft limit where recovery becomes marginal
- Set aft CG limit with safety margin (20-30%) forward of marginal point

**Step 5: Handling qualities assessment**  
- Flight test throughout CG range
- Evaluate control harmony
- Cooper-Harper handling qualities rating
- Adjust if needed (trim tabs, control surface size, etc.)

**Step 6: Iterate**
- If aft CG limit is too restrictive, you might:
  - Increase horizontal tail size (more elevator power)
  - Move horizontal tail aft (longer moment arm)
  - Increase wing sweep (moves AC aft)
  - Add ventral fins or tail strakes (anti-spin)

## Practical Example: Super Decathlon Numbers

Let me give you real numbers to make this concrete:

**CG Range:** 83.0" to 87.0" aft of datum (front face of firewall)
**Mean Aerodynamic Chord (MAC):** ~60 inches
**CG range as % MAC:** Roughly 5-12% MAC (very tight!)

**Why so tight?**

**Forward limit (83"):**
- Set by elevator authority - need to be able to rotate for takeoff
- At forward CG with full aft stick, you can just barely get tail down for 3-point landing
- If more forward, you couldn't flare properly

**Aft limit (87"):**  
- Set by spin recovery - tested in flight
- Beyond 87", recovery from accelerated spins becomes uncertain
- Also approaches neutral stability (pilot workload increases)

**Weight and Balance Example:**

Solo pilot (170 lbs) in front seat:
- Pilot arm: 86" (right in the middle of range)
- With 30 gal fuel: CG at 85.5"  
- Perfect for aerobatics

Add passenger (170 lbs) in back seat:
- Rear seat arm: 118"
- CG shifts to ~87.5" - **OUT OF LIMITS**
- Must add ballast in baggage compartment (arm ~150") to bring CG forward

This is why serious aerobatic flying is done solo. Two-up aerobatics in a Super Decathlon requires careful weight planning.

## Where to Learn This

**Academic progression:**

1. **"Introduction to Flight" (Anderson)** - Chapter 6 covers basic stability concepts. This gives you the vocabulary and basic understanding.

2. **"Flight Stability and Automatic Control" (Nelson)** - Chapters 1-5. Work through the derivations. Pay special attention to:
   - Stick force per g (Chapter 2)
   - Neutral point calculation (Chapter 2)  
   - Longitudinal dynamic modes (Chapter 3) - phugoid and short period

3. **Flight test yourself** - Rent a Super Decathlon or similar. Feel the difference between forward and aft CG. You'll understand immediately why CG position matters.

**Practical sources:**

- **FAA TCDS** (Type Certificate Data Sheet) for the Super Decathlon shows the actual CG limits and moments
- **POH/AFM** (Pilot Operating Handbook) includes weight & balance data
- **FAA AC 23-8C** "Flight Test Guide for Certification of Part 23 Airplanes" - shows how spin testing is actually done

## The Design Challenge for You

When you design your modernized Super Decathlon, you'll face these tradeoffs:

**Option 1: Keep tight CG range (like original)**
- Proven spin recovery
- Good handling  
- But limits payload flexibility

**Option 2: Widen CG range**
- More flexible loading
- But requires larger tail (weight penalty)
- And extensive spin testing to prove it's safe

**Option 3: Design for solo aerobatics primarily**
- Optimize CG for single pilot
- Accept that two-up flight has limitations
- This is what most purpose-built aerobatic aircraft do (Pitts, Extra, etc.)

Most likely: You'll **keep the proven CG range** and optimize everything else (engine, structures, systems). The Super Decathlon's CG range works - don't fix what isn't broken.

Does this clarify where this topic lives and why it matters? Want to dive deeper into the actual calculations for static margin or spin dynamics?

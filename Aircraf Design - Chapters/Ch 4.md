# Chapter 4 — *Thrust-to-Weight Ratio and Wing Loading*

### What this chapter is *really* doing

This chapter is **not** primarily about calculating numbers.

It is about identifying the **two dominant control knobs** of aircraft performance:

* **Thrust-to-weight (T/W)** → *how hard the airplane can fight gravity*
* **Wing loading (W/S)** → *how hard the airplane must fight the air*

Everything else you do in aircraft design is downstream of how you set these two.

If Chapters 2–3 made your airplane *exist*, Chapter 4 determines **how it moves**.

---

## The hidden thesis of the chapter

> **Every major performance requirement can be re-expressed as a constraint in the (T/W, W/S) plane.**

This chapter teaches you how to:

* translate requirements → inequalities
* overlay them
* find a feasible region
* choose a point *inside* it

This is constraint geometry, not algebra.

---

## 5.1 Introduction — why these two ratios matter

**Explicit**

* T/W and W/S dominate:

  * takeoff
  * climb
  * cruise
  * turn
  * landing
* Other parameters influence details, but these set the envelope

**Tacit context**

* These ratios are *dimensionless summaries of intent*
* They compress propulsion, aerodynamics, and mission into two numbers

Good designs cluster in known regions for a reason.

---

## 5.2 Thrust-to-Weight Ratio

### What T/W actually encodes

* Excess power
* Climb capability
* Acceleration
* Go-around margin
* Engine sizing risk

**Tacit context**

* T/W is not “engine size”
* It is **performance margin**

Too low → unsafe or useless
Too high → heavy, expensive, inefficient

---

### Installed vs available thrust

They distinguish:

* static thrust
* installed thrust
* thrust available at altitude/speed

**Tacit context**

* Engines lie on the brochure
* Airplanes fly at altitude, not at sea-level static conditions

The chapter quietly trains you to distrust raw engine numbers.

---

### Thrust lapse with altitude & Mach

Figures show:

* thrust decay with altitude
* afterburning vs non-AB engines
* prop vs jet behavior

**Tacit context**

* Thrust is a *function*, not a constant
* High-altitude performance is purchased dearly

This is why “just add thrust” is rarely free.

---

## Thrust matching (cruise matters more than takeoff)

They introduce:

* thrust matching at cruise
* not oversizing engines unnecessarily

**Tacit context**

* Engines are sized to **sustain**, not just to launch
* Cruise inefficiency compounds over hours

A plane that climbs like a rocket but cruises poorly is a bad airplane.

---

## 5.3 Wing Loading (W/S)

### What wing loading really controls

* Stall speed
* Takeoff & landing distance
* Gust response
* Low-speed handling
* Structural weight

**Tacit context**

* Wing loading is *how much the wing is being asked to suffer*
* Low W/S → gentle, forgiving
* High W/S → compact, fast, demanding

Every aircraft type lives in a narrow W/S band for a reason.

---

### Stall speed constraint

They derive stall speed limits from:

* FAR requirements
* lift coefficient
* wing loading

**Tacit context**

* Stall speed limits are often *regulatory*, not optional
* These constraints carve a hard vertical boundary in W/S

Design freedom ends abruptly here.

---

### Takeoff distance

They relate:

* W/S
* T/W
* runway length
* climb gradient

**Tacit context**

* Takeoff is a coupled problem
* You cannot “fix” takeoff with wing or engine alone

Runway length is a silent stakeholder.

---

### Landing distance

They cover:

* FAR 23 / FAR 25 limits
* approach speed
* braking assumptions

**Tacit context**

* Landing constraints are often stricter than takeoff
* Many designs fail here after looking good everywhere else

This is where aggressive wing loading gets punished.

---

## 5.4 Wing loading for cruise, endurance, maneuver

They derive:

* W/S for maximum range
* W/S for loiter
* W/S for sustained turn

**Tacit context**

* There is no single “best” wing loading
* Mission priority decides which constraint dominates

A fighter, transport, and patrol aircraft *cannot* share the same W/S logic.

---

## Turn performance (quietly important)

They introduce:

* instantaneous vs sustained turn
* load factor limits
* lift coefficient constraints

**Tacit context**

* Turn performance is where aerodynamics, structure, and propulsion collide
* Fighters live here; transports mostly ignore it

This is where design intent becomes unmistakable.

---

## Climb and glide

They relate:

* climb gradient → T/W
* glide → W/S and L/D

**Tacit context**

* Emergency performance shapes certification
* Glide capability is often undervalued until it is desperately needed

---

## The constraint plots (the real payload of the chapter)

Several figures show:

* lines of constant takeoff distance
* stall limits
* climb constraints
* cruise requirements

All plotted in **T/W vs W/S space**.

**Tacit context**

* These plots *are the design*
* Everything else is refinement

Once you see the feasible polygon, design becomes selection, not invention.

---

## 5.4 Selection of T/W and W/S (the actual decision)

**Explicit**

* Choose the lowest T/W and highest W/S that:

  * meet all constraints
  * leave margin

**Tacit context**

* This is an optimization under uncertainty
* Margins are not weakness — they are survival

The “optimal” point on paper often dies in service.

---

## How to read this chapter efficiently

### First pass

* Identify all constraints
* Ignore algebra details
* Focus on *what creates each boundary*

### Second pass

* Deep-read only the constraints that matter to **your mission**
* Skip fighter turns if designing a transport
* Skip catapult launch if not carrier-based

This chapter is modular by design.

---

## The chapter’s hidden invariants

1. **Performance lives in ratios, not absolutes**
2. **Regulations are geometry constraints**
3. **Margins are a design variable**
4. **Feasible regions are usually small**

---

## One-sentence mental compression

> *Chapter 4 teaches you how all performance requirements collapse into a small feasible region defined by thrust-to-weight and wing loading.*

---

If you want to continue the arc, the natural next steps are:

* **Chapter 5/6 (Initial Sizing)** — where these ratios get frozen into hardware
* Or I can extract a **single-page “T/W vs W/S decision checklist”** you can reuse on any concept

Just say where you want to steer next.

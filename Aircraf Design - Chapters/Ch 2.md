# Chapter 2 — *Sizing from a Conceptual Sketch*

### What this chapter is *really* about

This chapter is **not** about getting the “right” weight, thrust, or wing area.

It is about:

> **turning a vague airplane idea into a numerically self-consistent object**
> *as early as possible*.

The chapter teaches you how to:

* go from *sketch → numbers*
* without pretending those numbers are final
* while preserving the ability to iterate quickly

Think of this as **bootstrapping a fixed point**.

---

## High-level outline (explicit structure)

### 3.1 Introduction

**Claim**

* Conceptual design always begins with guesses.
* Analysis exists on a spectrum:

  * historical analogy (fast, crude)
  * detailed simulation (slow, expensive)
* This chapter intentionally sits **near the crude end**.

**Tacit context**

* The authors are explicitly rejecting premature rigor.
* They are optimizing for *iteration speed*, not accuracy.

> If this feels uncomfortable, that’s the point.

---

## 3.2 Takeoff-Weight Buildup (the spine of the chapter)

This is the **central invariant**:

> **Every airplane’s weight can be decomposed into a small number of buckets.**

They define:

* Takeoff gross weight ( W_0 )
* Broken into:

  * crew
  * payload
  * fuel
  * empty weight

**Key move**

* Express everything as *fractions of ( W_0 )*.
* Solve the resulting equation **implicitly**.

**Tacit context**

* This is not a calculation — it’s a *constraint closure*.
* You are finding a self-consistent weight that doesn’t contradict itself.

---

## 3.3 Empty-Weight Estimation

**What’s happening**

* Empty weight is estimated statistically from historical aircraft.
* Different aircraft classes have different coefficients.

**Tacit context**

* This is where design lineage matters.
* Your airplane inherits sins and virtues from its ancestors.

> Choosing a “class” is already a design commitment.

Composite materials, manufacturing philosophy, and mission intent all quietly bias this number.

---

## 3.4 Fuel-Fraction Estimation

This is where missions enter.

**Key idea**

* Fuel is not one number — it’s consumed across **mission segments**.

Segments include:

* warmup & taxi
* takeoff
* climb
* cruise
* loiter
* landing

Each segment has a weight fraction.

**Tacit context**

* Mission definition *is design*.
* Two airplanes with the same geometry but different missions are different aircraft.

The cruise segment dominates fuel sizing, which is why range requirements are so dangerous.

---

## Endurance & range equations (quiet but important)

They introduce:

* Breguet range & endurance equations
* With assumptions baked in:

  * constant ( L/D )
  * constant SFC
  * steady flight

**Tacit context**

* These equations are *fragile but useful*.
* They are good for trends, not promises.

If you forget the assumptions, you will believe lies.

---

## Specific fuel consumption (SFC)

**What’s being done**

* SFC is introduced as a property of engines *and operating regime*.
* Tables give representative values.

**Tacit context**

* Engines don’t have a single SFC — airplanes do.
* Throttle, altitude, Mach, and installation all matter.

This is a reminder that propulsion and aerodynamics are coupled.

---

## L/D estimation (where geometry re-enters)

**Key idea**

* Aerodynamic efficiency is captured in ( L/D ).
* ( L/D ) depends on:

  * aspect ratio
  * wetted area
  * drag breakdown (parasitic vs induced)

**Tacit context**

* This is where sketch quality starts to matter.
* Bad geometry poisons everything downstream.

The chapter quietly teaches you:

> draw well or suffer later.

---

## Wetted area & aspect ratio charts

Several figures show:

* historical trends
* clustering by aircraft type
* envelopes of plausible designs

**Tacit context**

* These plots define the **design feasible region**.
* You are not designing in ℝⁿ — you’re designing in a narrow manifold carved by history.

This is constraint inheritance again.

---

## First-order sizing loop (Fig. 3.7)

This diagram is **the heart of the chapter**.

It shows:

1. Start with a sketch
2. Assume parameters
3. Estimate weights
4. Check mission
5. Iterate

**Tacit context**

* This is a numerical fixed-point iteration.
* Convergence matters more than precision.

If it doesn’t converge, the concept is sick.

---

## Design example: ASW aircraft

They walk through a worked example:

* mission definition
* configuration choices
* tradeoffs

**Tacit context**

* The example exists to show *process*, not to be copied.
* Numbers are illustrative, not authoritative.

---

## Trade studies (range, payload, materials)

This is where design becomes explicit choice.

They vary:

* range
* payload
* materials (composites)

And show:

* how weight and performance respond

**Tacit context**

* These curves are *management weapons*.
* They tell you what costs what.

This is where “can we?” turns into “should we?”

---

## What to keep in your head while reading

### The hidden lessons

1. **Weight is the central coupling variable**

   * everything flows through it

2. **Mission definitions dominate outcomes**

   * vague missions → unstable designs

3. **Early estimates are allowed to be wrong**

   * but not incoherent

4. **Design is iterative constraint satisfaction**

   * not forward calculation

---

## How this chapter prepares you for the rest of the book

After this chapter, you can:

* assign numbers to a sketch
* tell if a concept is *numerically plausible*
* kill bad ideas early

Later chapters will:

* refine the estimates
* tighten assumptions
* add realism

But **none of that matters** if Chapter 2 doesn’t close.

---

## One-sentence mental compression

> *Chapter 2 teaches you how to force an airplane concept to admit whether it can exist.*

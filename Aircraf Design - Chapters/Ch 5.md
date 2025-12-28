# Chapter 5 — *Initial Sizing*

### What this chapter is *really* doing

This chapter is not about discovering new constraints.

It is about **collapsing all prior constraints into a single, self-consistent aircraft** with:

* a takeoff gross weight
* a wing of specific area
* an engine of specific thrust
* a fuselage of specific length
* tails of specific size

After this chapter, the airplane is **no longer hypothetical**.

---

## The hidden thesis

> **Initial sizing is the act of turning ratios and trends into actual mass and length.**

From this point on:

* changes get expensive
* geometry becomes stubborn
* “we’ll adjust later” mostly becomes false

---

## 6.1 Introduction — why sizing is different from estimation

**Explicit**

* Earlier chapters used quick sizing
* This chapter refines that into a method capable of handling most aircraft types

**Tacit context**

* This is the last chapter where *rubber math* is acceptable
* After this, the book expects realism

---

## Fixed engine vs rubber engine (a critical fork)

They define two paths:

### Rubber-engine sizing

* Engine thrust can scale freely
* Used early or when designing a new engine
* Common for fighters, bombers, SST concepts

### Fixed-engine sizing

* Engine size is fixed
* Aircraft must adapt
* Common in GA, transports, cost-sensitive programs

**Tacit context**

* This is a *program-level decision*, not a technical one
* Engine development cost dominates everything

Choosing fixed vs rubber silently commits you to a business model.

---

## 6.2 Rubber-engine sizing (the core loop)

### Review of the loop

The method:

1. Guess takeoff weight ( W_0 )
2. Estimate empty-weight fraction
3. Compute fuel weight by mission segment
4. Sum weights
5. Compare calculated vs guessed ( W_0 )
6. Iterate until convergence

**Tacit context**

* This is a fixed-point iteration in disguise
* Convergence = concept coherence

If it diverges, the design is sick.

---

### Empty-weight fraction (refined)

They introduce improved statistical models:

* dependent on:

  * aspect ratio
  * T/W
  * W/S
  * max speed
* Tables 6.1 & 6.2 encode this

**Tacit context**

* Geometry now *feeds back* into weight
* You can’t choose geometry independently anymore

---

## Fuel weight (mission fidelity increases)

They stop allowing:

* “fuel = fraction of ( W_0 )”

Instead:

* fuel is summed across mission legs:

  * taxi
  * climb
  * cruise
  * loiter
  * combat
  * reserve

**Tacit context**

* Missions are no longer abstract
* Every leg burns real mass

This is where sloppy mission definitions explode.

---

## Segment-by-segment weight accounting

They provide equations for:

* climb & acceleration
* cruise (Breguet)
* loiter
* combat
* descent & landing

**Tacit context**

* The airplane *changes weight continuously*
* Performance must be evaluated at condition-specific W/S

This is why earlier chapters warned you to distinguish takeoff vs cruise wing loading.

---

## Summary of refined sizing method (Fig. 6.1)

This flowchart is the **true payload** of the chapter.

It shows:

* geometry → aerodynamics
* mission → fuel
* weights → convergence
* iteration until closure

**Tacit context**

* This is the design loop you’ll repeat for the rest of your career
* Every later chapter plugs into this box

---

## Alternative sizing approach (reverse thinking)

They mention:

* starting from required empty weight
* then backing out ( W_0 )

**Tacit context**

* This is mathematically equivalent
* Psychologically different
* Useful when packaging dominates (payload-driven aircraft)

---

## 6.3 Fixed-engine sizing

When thrust is fixed:

* mission or performance becomes the fallout variable
* tradeoffs become explicit

**Tacit context**

* Fixed-engine designs are *honesty machines*
* You cannot cheat physics with marketing

This is why many homebuilts end up overweight and underperforming.

---

## 6.4 Geometry sizing (numbers → shape)

Once ( W_0 ) converges:

* fuselage length estimated statistically
* wing area from W/S
* tail size via volume coefficients

**Tacit context**

* This is where numbers become drawing dimensions
* Geometry now inherits all previous compromises

---

### Tail volume coefficients (quietly essential)

They introduce:

* horizontal tail volume coefficient
* vertical tail volume coefficient

**Tacit context**

* Tail sizing is stability insurance
* Under-sized tails are unforgiving and dangerous

Design conservatism here is wisdom, not fear.

---

## 6.5 Control-surface sizing

They provide:

* historical guidelines
* typical span and chord fractions
* flutter considerations

**Tacit context**

* Control surfaces are where aerodynamics meets human strength and structural dynamics
* Flutter is the ghost you must appease early

---

## How to read this chapter efficiently

### First pass

* Follow the **flowchart**
* Ignore constants and coefficients
* Understand what feeds what

### Second pass

* Only deep-read the mission segments you actually need
* Skip combat if you’re designing a transport
* Skip carrier ops if you’re not naval

---

## The chapter’s hidden invariants

1. **Weight convergence is the truth test**
2. **Missions burn mass, not fractions**
3. **Geometry feeds back into weight**
4. **Engine choice dominates feasibility**

---

## One-sentence mental compression

> *Chapter 5 turns ratios into reality by forcing every assumption to agree on a single takeoff weight.*

---

### Where the arc goes next

The book now assumes:

* the airplane exists
* its size is known
* its weight is believable

The next natural steps are:

* **Chapter 6/7: Configuration layout and loft** — turning numbers into drawings
* Or, if you want, I can extract a **one-page “initial sizing checklist”** that collapses Chapters 2–5 into a reusable workflow

# Chapter 3 — *Airfoil and Geometry Selection*

### What this chapter is *really* doing

This chapter is **not** teaching aerodynamics from first principles.

It is teaching you **how geometry locks in performance, stability, and risk before analysis ever starts**.

If Chapter 2 forced your concept to *exist numerically*, Chapter 3 forces it to **exist aerodynamically and geometrically**.

This is the chapter where:

* “we’ll fix it later” stops being true
* shapes begin to **carry consequences**

---

## The hidden agenda of the chapter

Before diving into sections, here’s the tacit thesis:

> **Most aircraft performance is already decided once you choose airfoil family, wing planform, and basic geometry.**

Everything else is trimming.

---

## 4.1 Introduction (why this chapter exists)

**Explicit**

* Geometry selection precedes detailed analysis
* Wing loading, weight, and speed estimates already exist (from Ch. 2)
* This chapter converts those into **actual shapes**

**Tacit context**

* You are no longer allowed to stay abstract
* Geometry is a *commitment*, not a suggestion

This is the point of no return for many concepts.

---

## 4.2 Airfoil Selection (the heart of the chapter)

### What airfoils really control

* Lift capability
* Drag characteristics
* Pitching moment
* Stall behavior
* Sensitivity to contamination, Reynolds number, Mach

**Tacit context**

* Airfoils encode *philosophy*:

  * laminar vs forgiving
  * efficient vs robust
  * aggressive vs docile

Choosing an airfoil is choosing what kind of airplane you are willing to live with.

---

### Airfoil geometry (pages ~34–36)

They walk through:

* camber
* thickness
* leading vs trailing edge
* pressure distributions

**Tacit context**

* These are not academic definitions
* Each geometric feature:

  * moves the center of pressure
  * alters pitching moment
  * changes stall mode

The key realization:

> Lift and moment are born together — you never get one for free.

---

### Lift, drag, and pitching moment

The chapter emphasizes:

* lift coefficient ( C_L )
* drag coefficient ( C_D )
* pitching moment coefficient ( C_m )

**Tacit context**

* Designers obsess over ( C_L ) and forget ( C_m )
* Pitching moment quietly dictates tail size, trim drag, and stability

Bad airfoil → big tail → more drag → worse airplane.

---

### Airfoil families (NACA, modern, supercritical)

They present:

* early NACA series
* laminar-flow airfoils
* modern and supercritical sections

**Tacit context**

* Historical progression = increasing sensitivity
* Modern airfoils demand:

  * manufacturing precision
  * clean surfaces
  * tighter operating envelopes

A forgiving airplane often uses an “inferior” airfoil on paper.

---

## Transonic effects (this matters more than it looks)

They introduce:

* shock formation
* drag rise
* critical Mach number

**Tacit context**

* Transonic drag is a *geometry tax*
* Sweep and thickness ratio exist largely to pay that tax

This is why fast airplanes look the way they do.

---

## Design lift coefficient (a quiet but crucial choice)

They define **design ( C_L )**:

* the lift coefficient the airplane is optimized around

**Tacit context**

* You are choosing where the airplane is happiest
* Cruise-optimized ≠ climb-optimized ≠ loiter-optimized

This one number anchors:

* wing area
* aspect ratio
* stall margin
* cruise efficiency

---

## 4.3 Wing Geometry (where constraints multiply)

This section is deceptively long because geometry is **high-dimensional**.

### Reference wing & mean aerodynamic chord

They introduce:

* reference wing
* MAC
* aerodynamic center

**Tacit context**

* This is bookkeeping for stability
* Geometry must be referenced consistently or nothing balances

---

### Aspect ratio

**Explicit**

* Higher AR → lower induced drag
* Structural penalties increase

**Tacit context**

* Aspect ratio is a structural–aerodynamic trade
* High AR airplanes are *structural arguments* as much as aerodynamic ones

---

### Sweep

**Explicit**

* Used to delay compressibility effects

**Tacit context**

* Sweep:

  * reduces effective lift slope
  * worsens low-speed handling
  * complicates structure
  * affects stall progression

Sweep is paid for everywhere except cruise Mach.

---

### Taper ratio

**Explicit**

* Influences lift distribution
* Affects stall behavior

**Tacit context**

* Taper is a stall management tool
* Designers taper wings to make stall predictable, not just efficient

Elliptical lift is elegant; elliptical stall is terrifying.

---

### Twist

**Explicit**

* Geometric or aerodynamic twist used to control lift distribution

**Tacit context**

* Twist is insurance
* It sacrifices peak performance to guarantee survivable behavior

Most good airplanes are deliberately “imperfect.”

---

### Dihedral

**Explicit**

* Affects roll stability

**Tacit context**

* Dihedral compensates for:

  * wing placement
  * sweep
  * mission stability requirements

Stability is assembled from many weak contributors, not one strong one.

---

## Wing placement (high / mid / low)

They discuss:

* ground clearance
* stability
* payload arrangement
* landing gear integration

**Tacit context**

* Wing placement is a *systems decision*
* It affects:

  * landing gear length
  * fuel storage
  * structural load paths
  * pilot visibility

There is no “best” — only coherent sets.

---

## Wing tips

They cover:

* tip shapes
* vortices
* drag reduction

**Tacit context**

* Tips are second-order in conceptual design
* They refine, not rescue, a bad wing

---

## 4.4 Biplanes (why they’re here at all)

This section exists to show:

* extreme aspect ratio via multiple wings
* induced drag management

**Tacit context**

* Biplanes illustrate trade space limits
* They are mostly a historical boundary case

---

## 4.5 Tail Geometry and Arrangement (stability encoded)

They cover:

* horizontal tail sizing
* vertical tail sizing
* T-tail vs conventional
* canards

**Tacit context**

* Tails exist to correct sins committed earlier
* The better the wing–CG–airfoil integration, the smaller the tail

Canards are not “cool tails”; they are *entirely different stability philosophies*.

---

## Tail arrangement figures (end of chapter)

These figures are showing:

* control effectiveness
* deep-stall risk
* engine-out behavior

**Tacit context**

* Tail choice is often driven by **failure modes**, not nominal flight

Design for the worst day, not the brochure.

---

## How to read this chapter efficiently

### First pass (fast)

* Read headings
* Skim figures
* Identify:

  * what choices exist
  * what each choice trades

### Second pass (selective)

* Only deep-read sections relevant to:

  * your mission
  * your speed regime
  * your configuration

Ignore the rest guilt-free.

---

## The chapter’s hidden invariants

1. **Geometry is destiny**
2. **Efficiency competes with forgiveness**
3. **Stability is distributed, not localized**
4. **Every “optimization” introduces fragility**

---

## One-sentence mental compression

> *Chapter 3 teaches you how shape quietly predetermines performance, stability, and risk long before equations notice.*

---

If you want next:

* Same **map + tacit context** for **Chapter 4 (Fuselage & internal layout)**
* Or I can extract a **“geometry commitment checklist”** you can apply to your own designs before you ever open a CFD tool

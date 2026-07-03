# IdeasForgeAI

## Phase 6D â€” Design Output Templates & Approval Flow

### Version 1.0

## Purpose

This document defines how IdeasForgeAI should present Design System Engine output to the user.

Phase 6 should turn an approved product blueprint into a clear design direction that can be reviewed, revised, approved, and later used by Pixel-Matched Conversion or Frontend Generation.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Phase 6 Output Goal

The Design System Engine should produce a clear design system, not final frontend code.

It should help the user understand:

* What the product should feel like
* What visual style fits the product
* What design rules should guide future screens
* What components are needed
* What should be avoided
* Whether the design is ready for approval

---

# 2. Standard Phase 6 Output Format

Every Phase 6 design response should use this structure:

## Design System Direction

### Design Positioning

One-line design direction.

### Brand Personality

Main visual and emotional traits.

### Visual Style

Light, clean, mobile-first visual rules.

### Typography Rules

Readable type hierarchy.

### Color Rules

Color purpose and usage.

### Spacing & Layout Rules

How the product should breathe and structure content.

### Component Rules

Reusable components and their behavior.

### Interaction Rules

How the user moves through the product.

### Mobile-First Rules

How screens should work on mobile first.

### Accessibility Rules

Readability, contrast, labels, focus, touch targets.

### Screen Design Guidance

Screen-by-screen design direction.

### Do Not Do

Design mistakes to avoid.

### Design Readiness

Ready, partial, or not ready.

### Approval Needed

What the user must approve before moving forward.

### Next Step

Recommended next action.

---

# 3. Design Positioning Template

Use this format:

## Design Positioning

This product should feel like:

`[design personality] + [product type] + [user trust goal]`

Example:

â€œClean founder-friendly AI product studio that feels calm, intelligent, and approval-driven.â€

For IdeasForgeAI:

â€œClean founder-friendly AI product studio.â€

---

# 4. Brand Personality Template

Use:

## Brand Personality

### Should Feel

* Intelligent
* Clean
* Calm
* Founder-friendly
* Premium-light
* Trustworthy
* Creative but controlled

### Should Avoid

* Too flashy
* Too technical
* Too dark
* Too many gradients
* Dashboard clutter
* Form-builder feeling
* Developer-console feeling

---

# 5. Visual Style Template

Use:

## Visual Style

* Light mode by default
* Soft white or light green-white background
* Clean card-based structure
* Deep green or teal primary accent
* Gentle shadows
* Soft borders
* Rounded corners
* Minimal visual noise
* Product preview should feel structured and calm
* AI output should feel like product-team guidance, not raw data

---

# 6. Typography Template

Use:

## Typography Rules

### Page Title

Clear and strong.

### Section Title

Bold and easy to scan.

### Card Title

Compact and structured.

### Field Label

Small, muted, and readable.

### Body Text

Comfortable, simple, and founder-friendly.

### Helper Text

Short and secondary.

### Status Text

Human-readable and calm.

Avoid decorative fonts, tiny labels, and too many font sizes.

---

# 7. Color Template

Use:

## Color Rules

### Background

Soft white or light green-white.

### Surface

White or pale green-white cards.

### Primary

Deep green or teal for important actions and approval.

### Text

Dark green-black or charcoal.

### Border

Soft green-gray.

### Success

Green for ready, saved, approved, running safely.

### Warning

Amber for missing information or approval needed.

### Error

Red only for real blocking issues.

Avoid neon colors, heavy dark mode, and uncontrolled gradients.

---

# 8. Layout Template

Use:

## Layout Rules

* Chat-first layout
* Full-screen Create Mode
* Full-screen Preview Mode
* Cards should group product intelligence clearly
* Mobile screens should stack vertically
* Desktop can use two columns carefully
* Bottom input should remain simple
* Approval should be visible before generation
* Avoid side-heavy admin panels

---

# 9. Component Rules Template

Use:

## Component Rules

### Chat Input

Simple, natural-language entry.

### Question Card

One question at a time.

### Strategy Card

Shows product direction.

### Requirements Card

Shows grouped product needs.

### Blueprint Card

Shows product source of truth.

### Planning Card

Shows next step and approval needs.

### AI Team View Card

Shows compact role-based product guidance.

### Approval Card

Stops premature build and asks for explicit approval.

### Memory Summary Card

Shows simple saved state without raw JSON.

---

# 10. Screen Design Guidance Template

For every screen, use:

## Screen Design Guidance

### Screen Name

Name of the screen.

### Purpose

What this screen helps the user do.

### Main User Action

The primary action.

### Required Components

Components needed.

### Visual Tone

How the screen should feel.

### Mobile Behavior

How the screen works on mobile.

### Empty State

What appears before content exists.

### Approval State

What must be approved before moving forward.

---

# 11. Design Readiness Template

Use:

## Design Readiness

### Ready for Phase 6 Approval

Yes / Partial / No

### Ready for Phase 7 Pixel-Matched Converter

Yes / Partial / No

### Ready for Phase 8 Frontend Generator

Yes / Partial / No

### Missing Before Approval

* Item 1
* Item 2

### Design Risk

* Risk 1
* Risk 2

---

# 12. Approval Flow

Phase 6 must require explicit approval.

Approval message:

â€œApprove Design System v1.0 before moving to Pixel-Matched Conversion or Frontend Generation.â€

Approval options:

* Approve Design System
* Revise Design Direction
* Save Draft
* Ask More Questions
* Freeze Design System

Silence is not approval.

---

# 13. Phase 6 Approval Rules

The system must not move to Phase 7 or Phase 8 unless:

* Product Blueprint v1.0 is approved
* Design System v1.0 is approved
* Screen map is clear
* Component rules are clear
* Mobile-first rules are clear
* Do-not-do rules are clear

---

# 14. Revision Flow

When user asks for changes, IdeasForgeAI should update only the relevant design area.

Examples:

If user says:

â€œMake it more premium.â€

Update:

* Brand personality
* Visual style
* Color rules
* Shadow rules
* Typography tone

If user says:

â€œMake it simpler.â€

Update:

* Layout rules
* Component rules
* Interaction rules
* Do-not-do rules

If user says:

â€œMake it mobile-first.â€

Update:

* Mobile-first rules
* Spacing
* Buttons
* Cards
* Input behavior

Do not restart the entire design system unless needed.

---

# 15. Freeze Flow

When user approves and freezes Phase 6, record:

â€œDesign System v1.0 is frozen. IdeasForgeAI can now move to Phase 7 Pixel-Matched Converter or Phase 8 Frontend Generator after approval.â€

Freeze should lock:

* Design positioning
* Brand personality
* Visual style
* Typography rules
* Color rules
* Component rules
* Layout rules
* Mobile-first rules
* Approval behavior

---

# 16. Do-Not-Do Rules

Phase 6 output must not:

* Generate final frontend code
* Generate backend
* Create database schema
* Add authentication
* Connect Supabase
* Deploy publicly
* Touch IdeasForgeAI production
* Redesign frozen Studio V3
* Add heavy dashboards
* Show raw JSON to the user
* Show raw booleans
* Show technical errors

---

# 17. Example Output for IdeasForgeAI

## Design System Direction

### Design Positioning

Clean founder-friendly AI product studio.

### Brand Personality

Intelligent, calm, premium-light, trustworthy, creative but controlled.

### Visual Style

Light mode, soft cards, deep green/teal accents, rounded corners, structured product preview cards, simple chat-first flow.

### Typography Rules

Use clean sans-serif typography with bold section titles, compact labels, readable body text, and calm status text.

### Color Rules

Use soft white background, pale green-white cards, deep green primary actions, dark readable text, soft borders, and minimal warning/error colors.

### Layout Rules

Create Mode and Product Preview Mode remain full-screen. Cards stack on mobile and can become two-column on desktop.

### Component Rules

Use chat input, question card, strategy card, requirements card, blueprint card, planning card, AI team card, memory summary, and approval card.

### Approval Needed

Approve Design System v1.0 before moving to Pixel-Matched Conversion or Frontend Generation.

---

# 18. Success Criteria

Phase 6D is successful when:

* Design output is structured and reviewable
* User can approve or revise clearly
* Future phases receive clean design instructions
* No code generation starts too early
* Studio V3 remains protected
* Design System v1.0 can be frozen safely
* The product stays aligned with:

**Less UI. More Intelligence.**


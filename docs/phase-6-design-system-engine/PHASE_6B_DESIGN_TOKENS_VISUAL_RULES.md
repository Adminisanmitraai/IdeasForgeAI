# IdeasForgeAI

## Phase 6B â€” Design Tokens & Visual Rules

### Version 1.0

## Purpose

This document defines the design token and visual rule system for IdeasForgeAI Phase 6 â€” Design System Engine.

Design tokens are the reusable visual decisions that keep the product consistent across screens, modes, generated pages, and future frontend output.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Design Token Role

Design tokens define the productâ€™s visual foundation.

They control:

* Color
* Typography
* Spacing
* Radius
* Shadows
* Borders
* Buttons
* Cards
* Inputs
* Status states
* Motion
* Mobile behavior

Design tokens should make IdeasForgeAI feel consistent without adding UI complexity.

---

# 2. Token Philosophy

IdeasForgeAI should feel:

* Clean
* Calm
* Intelligent
* Founder-friendly
* Premium-light
* Trustworthy
* Product-team-like
* Mobile-first

The design should support thinking, previewing, and approving.

It should not feel like:

* A complex dashboard
* A code editor
* A form builder
* A loud AI gimmick
* A heavy admin panel
* A dark developer console

---

# 3. Color Tokens

## Primary Color

Purpose:

Used for main actions, status highlights, selected states, and approval actions.

Recommended direction:

* Deep green
* Teal green
* Calm emerald

Usage:

* Send button
* Continue button
* Approval button
* Active status
* Section accents
* Important labels

Do not overuse primary color.

---

## Background Color

Purpose:

Creates calm working space.

Recommended direction:

* Soft white
* Very light green-white
* Warm off-white

Usage:

* Main app background
* Preview canvas
* Create Mode background

Avoid:

* Pure harsh white everywhere
* Heavy gray backgrounds
* Dark mode as default

---

## Surface Color

Purpose:

Used for cards and panels.

Recommended direction:

* White
* Soft green-white
* Subtle elevated surface

Usage:

* Chat cards
* Product Strategy cards
* Requirements cards
* Blueprint cards
* Planning cards
* Question cards

---

## Text Color

Purpose:

Keeps reading clear.

Recommended hierarchy:

* Primary text: dark green-black / charcoal
* Secondary text: muted gray-green
* Label text: muted bold
* Helper text: softer muted tone

Avoid:

* Low contrast
* Too many text colors
* Decorative text effects

---

## Border Color

Purpose:

Separates sections softly.

Recommended direction:

* Pale green-gray
* Soft neutral border

Usage:

* Cards
* Inputs
* Buttons
* Section groups

Borders should be visible but calm.

---

## Status Colors

Use status colors carefully.

### Success

Use green/teal.

Used for:

* Ready
* Approved
* Saved
* Running safely

### Warning

Use amber.

Used for:

* Needs approval
* Missing information
* Not ready

### Error

Use red only when necessary.

Used for:

* Failed state
* Unsafe state
* Blocking issue

Error states should be rare and human-readable.

---

# 4. Typography Tokens

Typography should make the product easy to read.

## Font Style

Use clean sans-serif fonts.

Preferred qualities:

* Modern
* Friendly
* Readable
* Neutral
* Professional

Avoid:

* Decorative fonts
* Heavy display fonts
* Too many typefaces

---

## Type Hierarchy

Use a simple hierarchy:

### Page Title

Purpose:

Top-level product or mode title.

Style:

* Strong
* Clear
* Not oversized

### Section Title

Purpose:

Groups major cards.

Style:

* Bold
* Short
* Easy to scan

### Card Title

Purpose:

Names each product brain output card.

Style:

* Bold
* Compact

### Field Label

Purpose:

Labels structured values.

Style:

* Small
* Muted
* Bold enough for scanning

### Body Text

Purpose:

Main explanation.

Style:

* Readable
* Comfortable line height
* Not too small

### Helper Text

Purpose:

Secondary explanation.

Style:

* Muted
* Short
* Non-distracting

### Status Text

Purpose:

Shows current state.

Style:

* Compact
* Clear
* Color-supported but not color-only

---

# 5. Spacing Tokens

Spacing should make the interface feel calm.

## Spacing Rules

Use consistent spacing between:

* Cards
* Sections
* Buttons
* Labels and values
* Inputs and actions
* Chat messages
* Preview blocks

Spacing should prevent clutter.

---

## Recommended Scale

Use a simple spacing scale:

* Extra small
* Small
* Medium
* Large
* Extra large

Purpose:

* Extra small: labels and tight field groups
* Small: inside compact controls
* Medium: card padding
* Large: section gaps
* Extra large: major mode separation

---

# 6. Radius Tokens

Rounded corners should make the app feel soft and approachable.

Use:

* Small radius for inputs and chips
* Medium radius for buttons
* Large radius for cards and panels

Avoid:

* Sharp enterprise-style boxes
* Overly round childish cards
* Inconsistent radius

---

# 7. Shadow Tokens

Shadows should be gentle.

Use shadows for:

* Main cards
* Floating input bar
* Preview containers
* Important focus areas

Avoid:

* Heavy shadows
* 3D effects
* Strong drop shadows
* Glow effects

The product should feel premium-light, not flashy.

---

# 8. Border Tokens

Borders should be soft and structural.

Use borders for:

* Input fields
* Product cards
* Question card
* Strategy rows
* Blueprint rows
* Planning rows

Avoid:

* Thick borders
* High-contrast outlines
* Too many nested boxes

---

# 9. Button Tokens

Buttons should be clear and minimal.

## Primary Button

Used for:

* Continue
* Send
* Approve
* Save important action

Style:

* Primary green/teal background
* White text
* Medium radius
* Clear hit area

## Secondary Button

Used for:

* Edit Answer
* Skip
* Save Draft
* Open Tools

Style:

* White or soft surface
* Border
* Dark text
* Calm hover/focus state

## Danger Button

Used only for destructive actions.

Style:

* Red or warning style
* Must require confirmation

Avoid danger buttons in Phase 6 unless needed.

---

# 10. Input Tokens

Inputs should feel simple and human.

Rules:

* Clear placeholder
* Comfortable height
* Rounded corners
* Soft border
* Visible focus state
* Mobile-friendly tap area
* No technical labels unless required

The bottom chat input must stay simple.

---

# 11. Card Tokens

Cards are the main container for intelligence.

Card types:

* AI response card
* User message card
* Question card
* Strategy card
* Requirements card
* Blueprint card
* Planning card
* Approval card
* Memory summary card
* Safe check card

Card rules:

* Clear title
* Concise content
* Soft border
* Light surface
* Consistent spacing
* Avoid overcrowding

Cards should help the user understand the product, not create dashboard clutter.

---

# 12. Chip / Pill Tokens

Chips and pills are useful for compact status or category display.

Use for:

* Intent type
* Status
* Phase
* Feature tags
* Requirement groups
* Readiness states

Rules:

* Short text
* Soft background
* Clear border
* No excessive colors

---

# 13. Status Token Rules

Status should be easy to understand.

Good statuses:

* Ready
* Draft
* Needs Approval
* Approved
* Frozen
* Local Intelligence Mode
* Waiting for Answer
* Ready for Phase 6

Avoid:

* Raw errors
* HTTP codes
* Provider failures
* Technical exception names
* Boolean values like true/false

User-facing statuses must be human-readable.

---

# 14. Motion Tokens

Motion should be minimal.

Use motion for:

* Smooth card appearance
* Gentle focus transitions
* Button hover/focus
* Loading state

Avoid:

* Excessive animation
* Spinning loaders everywhere
* Flashing status
* Distracting motion

Motion should support calm thinking.

---

# 15. Mobile-First Token Rules

Mobile-first means design starts from a narrow screen.

Rules:

* Cards stack vertically
* Buttons remain thumb-friendly
* Inputs remain readable
* Text wraps cleanly
* No tiny controls
* No crowded two-column layout on small screens
* Bottom input remains accessible

Desktop can enhance layout, but mobile is the foundation.

---

# 16. Accessibility Token Rules

Design tokens must support accessibility.

Rules:

* Maintain readable contrast
* Use clear labels
* Avoid color-only meaning
* Use large enough tap targets
* Provide visible focus states
* Keep text readable
* Avoid ultra-light text
* Avoid tiny helper text

Accessibility is part of trust.

---

# 17. IdeasForgeAI Default Token Direction

## Color Direction

* Background: soft white / light green-white
* Surface: white / pale green-white
* Primary: deep green / teal
* Text: dark green-black / charcoal
* Border: soft green-gray
* Success: green
* Warning: amber
* Error: red only when needed

## Typography Direction

* Clean sans-serif
* Bold compact titles
* Readable body text
* Muted labels
* Calm status text

## Shape Direction

* Rounded cards
* Rounded inputs
* Rounded buttons
* Soft structured sections

## Visual Feeling

Clean founder-friendly AI product studio.

---

# 18. Do-Not-Do Rules

Do not:

* Add too many colors
* Add heavy shadows
* Add neon gradients
* Add dark mode as default
* Add complex dashboards
* Add tiny controls
* Add crowded data tables
* Use raw technical statuses
* Use red for normal states
* Make UI feel like a developer console
* Make UI feel like a generic template builder

---

# 19. Design Token Output Format

When the Design System Engine outputs tokens, use:

## Design Tokens

### Colors

* Background:
* Surface:
* Primary:
* Secondary:
* Text:
* Border:
* Success:
* Warning:
* Error:

### Typography

* Font style:
* Page title:
* Section title:
* Card title:
* Body:
* Label:
* Helper:
* Status:

### Spacing

* Extra small:
* Small:
* Medium:
* Large:
* Extra large:

### Radius

* Small:
* Medium:
* Large:

### Shadows

* Card:
* Floating bar:
* Modal/panel:

### Components

* Buttons:
* Inputs:
* Cards:
* Chips:
* Status pills:

### Mobile Rules

* Layout:
* Buttons:
* Inputs:
* Cards:

### Accessibility Rules

* Contrast:
* Focus:
* Labels:
* Touch targets:

---

# 20. Success Criteria

Phase 6B is successful when:

* Visual rules are clear
* Tokens are reusable
* Studio V3 remains protected
* Future generated screens can stay consistent
* Design is clean and mobile-first
* UI does not become heavy
* Statuses are human-readable
* Phase 7 and Phase 8 get a strong design foundation
* The product stays aligned with:

**Less UI. More Intelligence.**


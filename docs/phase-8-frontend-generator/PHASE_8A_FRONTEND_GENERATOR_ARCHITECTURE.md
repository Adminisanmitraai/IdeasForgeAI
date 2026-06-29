# Phase 8A - Frontend Generator Architecture

Status: Completed as architecture only.

Phase 8A defines how the future Frontend Generator should work after approval. It does not generate HTML, CSS, React, app files, routes, deployments, provider calls, database writes, or production output.

## 1. Phase 8 Purpose

Phase 8 will eventually turn approved product intelligence into polished frontend screens. It must use the earlier phases as guardrails instead of acting like a raw prompt-to-code tool.

The Frontend Generator must depend on:

- Product Brain output from Phase 5.
- Design System Engine output from Phase 6.
- Pixel-Matched Converter placeholder/approval outputs from Phase 7.
- Human approval gates.
- Safety locks that prevent premature code generation.

## 2. Future Frontend Generator Responsibility

In later approved Phase 8 steps, the Frontend Generator may create:

- Single-page static previews.
- Multi-page app structures.
- Responsive mobile and desktop screens.
- Design-system-aligned components.
- Safe preview-only frontend artifacts.

It should produce founder-friendly, professional, premium UI output that feels deliberate and product-ready.

## 3. What Phase 8A Does Not Do

Phase 8A does not:

- Generate HTML.
- Generate CSS.
- Generate React.
- Write generated app files.
- Modify `generated-apps/`.
- Add backend generation routes.
- Add frontend generation controls that generate real code.
- Add deployment.
- Add Supabase, authentication, database writes, provider calls, or secrets.
- Unlock production frontend generation.
- Touch KisanMitraAI production.

## 4. Inputs From Product Brain

Future generation requires approved Product Brain output:

- Product name.
- Industry and business type.
- Target users.
- Product Strategy.
- Requirements.
- Product Blueprint.
- Page list and navigation model.
- Roles and permissions.
- Workflows.
- AI Team View.
- Approval checkpoint.

If Product Brain output is missing or unapproved, frontend generation must stay locked.

## 5. Inputs From Design System Engine

Future generation requires approved Phase 6 Design System output:

- Design positioning.
- Brand personality.
- Visual style.
- Typography guidance.
- Color token guidance.
- Component rules.
- Mobile-first rules.
- Accessibility rules.
- Design readiness.
- Explicit Design System approval.

If Design System v1.0 is not approved, generated frontend output must not be produced.

## 6. Inputs From Pixel-Matched Converter Placeholder Track

Future generation may use Phase 7 outputs only after approval:

- Placeholder contract status.
- Local metadata placeholder status.
- Layout detection placeholder.
- Component mapping placeholder.
- Design System alignment placeholder.
- Pixel Match Score preview placeholder.
- Human approval state.

Phase 7 data remains advisory until a future real converter is approved. Phase 8 must not treat placeholder data as real image analysis.

## 7. Screen Generation Pipeline

Future pipeline:

1. Validate Product Brain approval.
2. Validate Design System approval.
3. Validate Phase 7 approval or skip Pixel-Matched input when not needed.
4. Select target output type.
5. Build screen plan.
6. Select components.
7. Apply layout rules.
8. Apply typography and color tokens.
9. Apply responsive behavior.
10. Apply accessibility rules.
11. Create preview artifact in a future approved phase.
12. Require human approval before any handoff.

Phase 8A documents this pipeline only.

## 8. Apple-Like / Premium UI Quality Goals

Future screens should feel:

- Calm.
- Clean.
- Premium.
- Mobile-first.
- Founder-friendly.
- Professional.
- Trustworthy.
- Easy to scan.
- Light mode by default.

Quality rules:

- Avoid clutter.
- Avoid developer jargon in user-facing screens.
- Use strong spacing rhythm.
- Use restrained visual hierarchy.
- Use subtle microinteractions.
- Keep controls obvious and tap-friendly.
- Keep cards purposeful, not decorative.

## 9. Supported Future Output Types

Potential future output types:

- Static HTML/CSS preview.
- Componentized HTML/CSS preview.
- React preview.
- Page bundle.
- Multi-page app shell.
- Mobile-first responsive preview.
- Design System compliance report.

Phase 8A does not create any of these outputs.

## 10. Single-Page Generation Plan

Future single-page generation should:

- Start from one approved page.
- Use the approved screen objective.
- Select a layout pattern.
- Select required components.
- Apply Phase 6 design tokens.
- Generate responsive states.
- Produce a preview artifact only in a later approved phase.
- Require review before any app write.

## 11. Multi-Page App Generation Plan

Future multi-page generation should:

- Use the approved page map from Product Brain.
- Use shared navigation.
- Reuse shared components.
- Apply consistent typography, spacing, and tokens.
- Define safe routing structure.
- Produce preview-only output first.
- Require approval before persistent generated app writes.

## 12. Responsive Mobile/Desktop Strategy

Future output must be mobile-first:

- Mobile layout first.
- Tablet adaptations second.
- Desktop density third.
- Touch targets remain usable.
- Text cannot overflow its containers.
- Navigation adapts by context.
- Bottom navigation is allowed only where the product pattern supports it.

## 13. Component Selection Strategy

Components should be selected from approved needs:

- Header / top navigation.
- Sidebar navigation.
- Hero section.
- Content card / KPI card.
- Button group.
- Form field group.
- Data table.
- Chart placeholder.
- Media block.
- Modal / dialog.
- Chat composer.
- Navigation tabs.
- Bottom navigation.

Future generation must prefer approved Design System components over ad hoc UI.

## 14. Layout Strategy

Future layout should:

- Start with the user workflow.
- Prioritize primary actions.
- Use readable section spacing.
- Keep related content grouped.
- Avoid nested cards.
- Avoid oversized hero patterns inside tools.
- Use stable dimensions for repeated UI.
- Support preview across mobile, tablet, and desktop.

## 15. Typography Strategy

Future typography should:

- Use approved font recommendations.
- Keep headings proportional to context.
- Avoid viewport-based font scaling.
- Avoid negative letter spacing.
- Preserve readability on narrow screens.
- Use strong hierarchy without visual noise.

## 16. Color / Token Strategy

Future color use should:

- Use approved Phase 6 color tokens.
- Avoid one-note palettes.
- Keep contrast readable.
- Use accent color sparingly.
- Reserve status colors for status.
- Keep light mode as default.

## 17. Animation / Microinteraction Strategy

Future microinteractions should:

- Be subtle.
- Support trust and clarity.
- Avoid harsh transitions.
- Avoid decorative motion that distracts from work.
- Respect reduced-motion needs.
- Keep buttons and cards feeling responsive without feeling noisy.

## 18. Accessibility Strategy

Future output must consider:

- Readable contrast.
- Keyboard focus states.
- Tap-friendly target sizes.
- Text wrapping.
- Semantic structure.
- Avoiding hidden content behind fixed bars.
- Responsive accessibility at mobile widths.

## 19. Human Approval Gates

Required approval gates:

- Product Blueprint approval.
- Design System approval.
- Pixel-Matched placeholder approval when used.
- Frontend preview approval.
- Generated app write approval.
- Production/deployment approval.

No future generator may skip approval.

## 20. Safety Locks

Required Phase 8A locks:

```json
{
  "frontend_generation_allowed": false,
  "html_generation_allowed": false,
  "css_generation_allowed": false,
  "react_generation_allowed": false,
  "generated_app_write_allowed": false,
  "phase_8_generation_unlocked": false,
  "approval_required": true
}
```

## 21. Blocked Outputs In Phase 8A

Blocked in Phase 8A:

- HTML output.
- CSS output.
- React output.
- JavaScript app output.
- Generated app files.
- Generated routes.
- Generated assets.
- Generated deployments.
- Provider-generated code.
- Database writes.
- Public publish actions.

## 22. Future Phase 8 Roadmap

- Phase 8A - Frontend Generator Architecture.
- Phase 8B - Safe Frontend Generator Contract.
- Phase 8C - Single Page Static Preview Generator.
- Phase 8D - Multi-page App Structure Generator.
- Phase 8E - Responsive Mobile/Desktop Generator.
- Phase 8F - Design System Enforcement.
- Phase 8G - Studio Preview + Approval Gate.
- Phase 8H - Frontend Generator Freeze Review.

## 23. Validation And Freeze Criteria

Phase 8A is ready to freeze when:

- Architecture document exists.
- No generator implementation exists.
- No backend generation route was added.
- No frontend generation button was added.
- No generated app files were created.
- `generated-apps/` remains untouched.
- Phase 5 remains frozen.
- Phase 6 remains frozen.
- Phase 7 remains fully frozen.
- Frontend generation remains locked.
- Phase 8B is the next approval-gated step.

## Final Phase 8A Statement

Phase 8A is architecture only. It prepares the future Frontend Generator without generating code, writing app files, unlocking Phase 8 generation, or changing production behavior.

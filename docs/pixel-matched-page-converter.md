# Pixel-Matched Page Converter Agent

## Purpose

`PixelMatchedPageConverterAgent` is the Studio V2 agent responsible for turning a screenshot or page image into a responsive frontend page.

The intended output target is:

- `generated-apps/<app>/frontend/converted-page.html`
- `generated-apps/<app>/frontend/converted-page.css`

## Current Placeholder Mode

This phase implements a safe placeholder flow only.

- The Studio V2 UI can upload or paste screenshot metadata.
- The Convert button calls `/api/pixel-convert`.
- The backend returns placeholder layout, component, palette, typography, file path, and responsive notes.
- No external APIs are called.
- No real image analysis is performed yet.
- Existing app generation and IdeasForgeAIProduct live connection remain unchanged.

If no image is provided, the agent returns a placeholder status asking the user to upload or paste a screenshot.

## Future Real Image Analysis Mode

A later phase can add real image processing to:

- Detect page regions, spacing, grid structure, and visual hierarchy.
- Extract color palette and typography hints.
- Identify components such as nav bars, cards, forms, tables, buttons, charts, and hero sections.
- Generate responsive HTML/CSS that matches the screenshot closely.
- Connect generated pages into the app navigation.
- Preview mobile, tablet, and desktop breakpoints.

## Expected Workflow

1. Upload Screenshot.
2. Detect Layout.
3. Extract colors, spacing, and components.
4. Generate HTML/CSS.
5. Connect Navigation.
6. Responsive Preview.

## Safety Rule

Never put secrets in frontend files.

Do not expose OpenAI API keys, Supabase service role keys, private keys, tokens, or credentials in generated HTML, CSS, JavaScript, or app configuration files.


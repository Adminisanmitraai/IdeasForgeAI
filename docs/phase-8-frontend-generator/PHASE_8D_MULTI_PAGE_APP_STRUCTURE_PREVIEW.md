
# Phase 8D - Multi-page App Structure Preview

Status: Completed as Studio-only preview.

## Purpose

Phase 8D adds a safe multi-page app structure preview to Studio V3.

It shows how a future generated app or website may be organized across multiple pages, routes, navigation flows, and user journeys.

## Scope

Phase 8D is preview-only.

It does not generate production HTML, CSS, React, or generated app files.

## Required preview pages

- Home / Landing Page
- About / Product Overview
- Features
- Dashboard
- User Onboarding
- Login / Signup
- Pricing
- Settings
- Support / Contact

## Required preview fields per page

- page_name
- route
- page_type
- purpose
- primary_sections
- connected_navigation
- preview_status
- approval_required

## Safety labels

- Multi-page preview only
- No generated files
- No production code output
- No generated-apps write
- Approval required before generation

## Safety locks

- multi_page_preview_allowed=true
- production_frontend_generation_allowed=false
- html_output_allowed=false
- css_output_allowed=false
- react_output_allowed=false
- generated_app_write_allowed=false
- generated_files_allowed=false
- deployment_allowed=false
- provider_calls_allowed=false
- database_writes_allowed=false
- supabase_allowed=false
- auth_allowed=false
- approval_required=true

## Blocked fields

- html_output
- css_output
- react_output
- generated_files
- generated_app_path
- file_write_request
- deploy_request
- provider_prompt
- secret_value
- database_write
- supabase_config
- auth_config

## Next step

Phase 8E - Responsive Mobile/Desktop Preview, only after Phase 8D freeze review.

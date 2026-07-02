from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


DEFAULT_SECTOR_UI_PROFILE: Dict[str, Any] = {
    "sector_key": "generic_saas",
    "hero_kicker": "Workflow OS",
    "hero_visual_title": "Operations cockpit",
    "visual_mood": "polished modern SaaS workspace",
    "dashboard_card_style": "metric-slab",
    "section_order": ["actions", "records", "guidance", "trust"],
    "premium_sections": {
        "actions_title": "Priority workflows",
        "actions_kicker": "Command center",
        "actions_summary": "High-signal actions for the first usable version.",
        "records_title": "Live workspace examples",
        "records_kicker": "Sample data",
        "records_summary": "Representative rows that make the preview feel populated.",
        "guidance_title": "First-run guidance",
        "guidance_kicker": "Empty state",
        "trust_title": "Operating notes",
        "trust_kicker": "Trust and language",
    },
    "sample_component_labels": ["Workspace", "Tasks", "Reports"],
    "action_component_style": "action-card-solid",
    "record_component_style": "record-card-clean",
    "empty_state_style": "empty-state-panel",
    "trust_note_style": "trust-note-panel",
}


SECTOR_UI_PROFILES: Dict[str, Dict[str, Any]] = {
    "agriculture_farmer": {
        "hero_kicker": "Farm intelligence",
        "hero_visual_title": "Crop-to-market cockpit",
        "visual_mood": "green, earthy, advisory, farmer-first",
        "dashboard_card_style": "metric-leaf",
        "premium_sections": {
            "actions_title": "Farm decisions for today",
            "actions_kicker": "Field actions",
            "actions_summary": "Capture crop, weather, mandi, and buyer workflows without promising yield.",
            "records_title": "Farm and market examples",
            "records_kicker": "Field records",
            "records_summary": "Realistic crop, farm, and buyer records for an agriculture preview.",
            "guidance_title": "Farmer onboarding guidance",
            "guidance_kicker": "Advisory setup",
            "trust_title": "Agriculture advisory notes",
            "trust_kicker": "Safety language",
        },
        "sample_component_labels": ["Crop Health", "Mandi Price", "Farm Tasks"],
        "action_component_style": "action-card-organic",
        "record_component_style": "record-card-harvest",
        "empty_state_style": "empty-state-field",
        "trust_note_style": "trust-note-advisory",
    },
    "insurance_broker": {
        "hero_kicker": "Policy advisory",
        "hero_visual_title": "Claims and renewal desk",
        "visual_mood": "trustworthy finance workspace",
        "dashboard_card_style": "metric-trust",
        "sample_component_labels": ["Policies", "Claims", "Renewals"],
        "action_component_style": "action-card-trust",
        "record_component_style": "record-card-ledger",
        "empty_state_style": "empty-state-compliance",
        "trust_note_style": "trust-note-compliance",
    },
    "mutual_fund_advisor": {
        "hero_kicker": "Wealth advisory",
        "hero_visual_title": "SIP and portfolio console",
        "visual_mood": "calm financial trust with compliance language",
        "dashboard_card_style": "metric-trust",
        "premium_sections": {
            "actions_title": "Investor review workflows",
            "actions_kicker": "Advisor actions",
            "actions_summary": "SIP, portfolio, goal, and risk-profile actions with clear compliance language.",
            "records_title": "Investor examples",
            "records_kicker": "Portfolio records",
            "records_summary": "Sample advisory records that avoid guaranteed-return promises.",
            "guidance_title": "Investor onboarding guidance",
            "guidance_kicker": "Risk setup",
            "trust_title": "Compliance and risk notes",
            "trust_kicker": "Trust language",
        },
        "sample_component_labels": ["AUM", "SIP Book", "Risk Profiles"],
        "action_component_style": "action-card-trust",
        "record_component_style": "record-card-ledger",
        "empty_state_style": "empty-state-compliance",
        "trust_note_style": "trust-note-compliance",
    },
    "school_teacher_parent": {
        "hero_kicker": "Classroom bridge",
        "hero_visual_title": "Teacher-parent dashboard",
        "visual_mood": "soft, clear, student-safe",
        "dashboard_card_style": "metric-soft",
        "sample_component_labels": ["Attendance", "Homework", "Messages"],
        "action_component_style": "action-card-soft",
        "record_component_style": "record-card-clean",
        "empty_state_style": "empty-state-panel",
        "trust_note_style": "trust-note-privacy",
    },
    "clinic_healthcare": {
        "hero_kicker": "Clinic operations",
        "hero_visual_title": "Appointment and patient flow",
        "visual_mood": "calm healthcare, clean scheduling",
        "dashboard_card_style": "metric-calm",
        "premium_sections": {
            "actions_title": "Clinic front-desk actions",
            "actions_kicker": "Care workflow",
            "actions_summary": "Appointment, patient, prescription, and follow-up actions with safe medical language.",
            "records_title": "Clinic examples",
            "records_kicker": "Patient flow",
            "records_summary": "Representative appointment and follow-up records for a healthcare preview.",
            "guidance_title": "Clinic setup guidance",
            "guidance_kicker": "Empty schedule",
            "trust_title": "Healthcare safety notes",
            "trust_kicker": "Care language",
        },
        "sample_component_labels": ["Appointments", "Patients", "Follow-ups"],
        "action_component_style": "action-card-calm",
        "record_component_style": "record-card-clinic",
        "empty_state_style": "empty-state-clinic",
        "trust_note_style": "trust-note-medical",
    },
    "car_detailing": {
        "hero_kicker": "Premium detailing",
        "hero_visual_title": "Studio booking board",
        "visual_mood": "dark automotive premium",
        "dashboard_card_style": "metric-dark",
        "sample_component_labels": ["Bookings", "Services", "Revenue"],
        "action_component_style": "action-card-solid",
        "record_component_style": "record-card-clean",
    },
    "gym_fitness": {
        "hero_kicker": "Fitness studio",
        "hero_visual_title": "Member and class console",
        "visual_mood": "energetic fitness dashboard",
        "dashboard_card_style": "metric-energy",
        "sample_component_labels": ["Members", "Classes", "Payments"],
        "action_component_style": "action-card-solid",
        "record_component_style": "record-card-clean",
    },
    "wedding_event_lawn": {
        "hero_kicker": "Premium venue operations",
        "hero_visual_title": "Wedding lawn booking suite",
        "visual_mood": "elegant, warm, premium event management",
        "dashboard_card_style": "metric-elegant",
        "premium_sections": {
            "actions_title": "Booking and event actions",
            "actions_kicker": "Venue workflows",
            "actions_summary": "Book dates, create events, select packages, assign vendors, and collect advances.",
            "records_title": "Event booking examples",
            "records_kicker": "Sample events",
            "records_summary": "Premium wedding records for engagement, mehendi, and reception workflows.",
            "guidance_title": "Venue onboarding guidance",
            "guidance_kicker": "Event details",
            "trust_title": "Booking and payment notes",
            "trust_kicker": "Venue trust",
        },
        "sample_component_labels": ["Packages", "Decor Themes", "Bookings"],
        "action_component_style": "action-card-elegant",
        "record_component_style": "record-card-event",
        "empty_state_style": "empty-state-event",
        "trust_note_style": "trust-note-event",
    },
    "restaurant_food": {
        "hero_kicker": "Restaurant operations",
        "hero_visual_title": "Orders and table flow",
        "visual_mood": "warm food ordering workspace",
        "dashboard_card_style": "metric-warm",
        "sample_component_labels": ["Orders", "Tables", "Kitchen"],
        "action_component_style": "action-card-warm",
        "record_component_style": "record-card-clean",
    },
    "retail_inventory": {
        "hero_kicker": "Retail inventory",
        "hero_visual_title": "Stock and sales board",
        "visual_mood": "clean inventory grid",
        "dashboard_card_style": "metric-gridline",
        "sample_component_labels": ["Stock", "Sales", "Suppliers"],
        "action_component_style": "action-card-solid",
        "record_component_style": "record-card-clean",
    },
    "government_civic": {
        "hero_kicker": "Civic service desk",
        "hero_visual_title": "Citizen request console",
        "visual_mood": "official, clean, accountable",
        "dashboard_card_style": "metric-civic",
        "sample_component_labels": ["Requests", "Departments", "SLA"],
        "action_component_style": "action-card-civic",
        "record_component_style": "record-card-clean",
        "trust_note_style": "trust-note-civic",
    },
    "real_estate": {
        "hero_kicker": "Property desk",
        "hero_visual_title": "Listings and visit planner",
        "visual_mood": "premium property operations",
        "dashboard_card_style": "metric-slab",
        "sample_component_labels": ["Listings", "Visits", "Deals"],
    },
    "travel_agency": {
        "hero_kicker": "Travel desk",
        "hero_visual_title": "Trips and itinerary planner",
        "visual_mood": "bright travel operations",
        "dashboard_card_style": "metric-slab",
        "sample_component_labels": ["Trips", "Bookings", "Itinerary"],
    },
    "salon_beauty": {
        "hero_kicker": "Beauty studio",
        "hero_visual_title": "Salon appointment suite",
        "visual_mood": "soft beauty booking",
        "dashboard_card_style": "metric-soft",
        "sample_component_labels": ["Services", "Stylists", "Appointments"],
    },
    "accounting_ca": {
        "hero_kicker": "CA workflow",
        "hero_visual_title": "GST and client compliance board",
        "visual_mood": "clean finance compliance",
        "dashboard_card_style": "metric-trust",
        "sample_component_labels": ["GST", "Invoices", "Clients"],
        "trust_note_style": "trust-note-compliance",
    },
    "logistics_delivery": {
        "hero_kicker": "Logistics control",
        "hero_visual_title": "Shipment tracking board",
        "visual_mood": "timeline operations",
        "dashboard_card_style": "metric-slab",
        "sample_component_labels": ["Shipments", "Drivers", "Routes"],
    },
    "construction_project": {
        "hero_kicker": "Site operations",
        "hero_visual_title": "Project progress board",
        "visual_mood": "structured construction dashboard",
        "dashboard_card_style": "metric-gridline",
        "sample_component_labels": ["Progress", "Materials", "Milestones"],
    },
    "hotel_resort": {
        "hero_kicker": "Hospitality desk",
        "hero_visual_title": "Rooms and guest operations",
        "visual_mood": "premium hospitality calm",
        "dashboard_card_style": "metric-slab",
        "sample_component_labels": ["Rooms", "Guests", "Housekeeping"],
    },
    "ngo_social": {
        "hero_kicker": "Impact workspace",
        "hero_visual_title": "Donor and field impact board",
        "visual_mood": "human, clear, impact-focused",
        "dashboard_card_style": "metric-soft",
        "sample_component_labels": ["Donors", "Campaigns", "Impact"],
        "trust_note_style": "trust-note-privacy",
    },
    "generic_saas": DEFAULT_SECTOR_UI_PROFILE,
}


def _merge_profile(sector_key: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(DEFAULT_SECTOR_UI_PROFILE)
    merged.update(profile)
    merged["premium_sections"] = {
        **DEFAULT_SECTOR_UI_PROFILE["premium_sections"],
        **profile.get("premium_sections", {}),
    }
    merged["sector_key"] = sector_key
    return merged


def get_sector_ui_profile(sector_key: str | None) -> Dict[str, Any]:
    normalized = str(sector_key or "generic_saas").strip().lower().replace("-", "_").replace(" ", "_")
    profile = SECTOR_UI_PROFILES.get(normalized, DEFAULT_SECTOR_UI_PROFILE)
    return _merge_profile(normalized if normalized in SECTOR_UI_PROFILES else "generic_saas", profile)


def sector_ui_class_names(profile: Dict[str, Any]) -> str:
    parts = [
        f"sector-ui-{profile.get('sector_key', 'generic_saas')}",
        profile.get("dashboard_card_style", ""),
        profile.get("action_component_style", ""),
        profile.get("record_component_style", ""),
        profile.get("empty_state_style", ""),
        profile.get("trust_note_style", ""),
    ]
    return " ".join(part for part in parts if part)

"""
IdeasForgeAI Phase 33A — Sector Blueprint Pack

Purpose:
- Provide sector-specific generation guidance for supported IdeasForgeAI sectors.
- Keep generated apps industry-specific instead of generic CRM/SaaS.
- Stay backend-only and safe for QA-gated future phases.

This file is intentionally plain Python with no external dependencies.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


SECTOR_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "agriculture_farmer": {
        "sector_key": "agriculture_farmer",
        "app_name_style": "Farmer-first farm intelligence and crop-to-cash assistant",
        "theme_intent": "agriculture-green-dashboard",
        "primary_users": ["Farmer", "FPO operator", "Agri advisor"],
        "must_have_screens": ["dashboard", "farm_profile", "crop_health", "market_prices", "tasks"],
        "suggested_screens": ["weather", "soil_report", "buyer_connect", "expense_tracker"],
        "dashboard_cards": ["Crop health", "Today weather", "Mandi price", "Farm tasks", "Expected income"],
        "primary_actions": ["Add farm", "Check crop", "View market", "Create task", "Contact buyer"],
        "clickable_aliases": ["farm", "crop", "market", "weather", "tasks", "buyer"],
        "domain_terms": ["farm", "crop", "soil", "mandi", "harvest", "buyer", "acre"],
        "forbidden_generic_terms": ["lead pipeline", "generic CRM", "ticket queue"],
        "sample_records": ["Tomato field", "Paddy farm", "FPO buyer request"],
        "empty_state_guidance": "Ask the farmer to add farm location, crop name, and expected harvest date.",
        "trust_and_safety_notes": ["Do not guarantee crop yield.", "Show advisory language for farm decisions."],
        "monetization_suggestions": ["FPO subscription", "Buyer connection fee", "Premium farm intelligence"],
        "compliance_notes": ["Agriculture advice should remain advisory and location-aware."],
    },
    "insurance_broker": {
        "sector_key": "insurance_broker",
        "app_name_style": "Policy advisory and claims support workspace",
        "theme_intent": "finance-trust-blue",
        "primary_users": ["Insurance broker", "Policy advisor", "Claims executive"],
        "must_have_screens": ["dashboard", "clients", "policies", "claims", "renewals"],
        "suggested_screens": ["quotes", "documents", "commission", "followups"],
        "dashboard_cards": ["Active policies", "Renewals due", "Open claims", "Premium collected"],
        "primary_actions": ["Add client", "Create quote", "Track claim", "Upload document", "Set renewal reminder"],
        "clickable_aliases": ["client", "policy", "claim", "renewal", "quote"],
        "domain_terms": ["policy", "premium", "claim", "renewal", "nominee", "coverage"],
        "forbidden_generic_terms": ["student attendance", "table booking", "crop health"],
        "sample_records": ["Health policy renewal", "Motor claim", "Term insurance lead"],
        "empty_state_guidance": "Start by adding a client and attaching policy details.",
        "trust_and_safety_notes": ["Do not promise claim approval.", "Use compliant advisory language."],
        "monetization_suggestions": ["Broker dashboard subscription", "Document automation add-on"],
        "compliance_notes": ["Insurance output must avoid guaranteed returns or guaranteed claim settlement."],
    },
    "mutual_fund_advisor": {
        "sector_key": "mutual_fund_advisor",
        "app_name_style": "Investor portfolio and SIP advisory console",
        "theme_intent": "finance-trust-blue-green",
        "primary_users": ["Mutual fund advisor", "RIA team", "Wealth assistant"],
        "must_have_screens": ["dashboard", "investors", "portfolio", "sip_tracker", "risk_profile"],
        "suggested_screens": ["goals", "fund_watchlist", "compliance_notes", "reports"],
        "dashboard_cards": ["AUM", "SIP book", "Risk profiles", "Goal progress", "Review due"],
        "primary_actions": ["Add investor", "Create SIP review", "Update risk profile", "Generate report"],
        "clickable_aliases": ["investor", "portfolio", "sip", "risk", "goal"],
        "domain_terms": ["SIP", "portfolio", "AUM", "risk profile", "fund", "goal"],
        "forbidden_generic_terms": ["guaranteed return", "claim approval", "patient queue"],
        "sample_records": ["Monthly SIP review", "Retirement goal", "ELSS portfolio"],
        "empty_state_guidance": "Ask for investor goal, horizon, risk profile, and SIP amount.",
        "trust_and_safety_notes": ["Do not guarantee returns.", "Show investment risk disclaimer."],
        "monetization_suggestions": ["Advisor subscription", "Portfolio report credits"],
        "compliance_notes": ["Investment output must be educational/advisory, not guaranteed financial promise."],
    },
    "school_teacher_parent": {
        "sector_key": "school_teacher_parent",
        "app_name_style": "Private tutor class manager and student progress app",
        "theme_intent": "education-soft-blue",
        "primary_users": ["Private tutor", "Teacher", "Parent", "Student"],
        "must_have_screens": ["dashboard", "students", "classes", "attendance", "homework", "fees", "messages"],
        "suggested_screens": ["progress_report", "schedule", "parent_messages", "timetable"],
        "dashboard_cards": ["Attendance", "Homework due", "Parent messages", "Class notices", "Fees pending"],
        "primary_actions": ["Mark attendance", "Assign homework", "Message parent", "Update fees", "Schedule class"],
        "clickable_aliases": ["student", "students", "class", "classes", "attendance", "homework", "fees", "parent", "message", "schedule"],
        "domain_terms": ["tutor", "student", "class", "batch", "attendance", "homework", "fees", "parent", "notice", "schedule"],
        "forbidden_generic_terms": ["policy premium", "mandi", "table booking"],
        "sample_records": ["Batch A attendance", "Math homework", "Parent message", "Fees pending"],
        "empty_state_guidance": "Ask the tutor to add students, class batches, parent contacts, and fee status.",
        "trust_and_safety_notes": ["Protect student data.", "Avoid exposing sensitive child information."],
        "monetization_suggestions": ["Tutor subscription", "Per-student class management plan", "Parent communication module"],
        "compliance_notes": ["Student data must be handled privately and safely."],
    },
    "clinic_healthcare": {
        "sector_key": "clinic_healthcare",
        "app_name_style": "Clinic appointment and patient care management app",
        "theme_intent": "healthcare-calm-teal",
        "primary_users": ["Doctor", "Clinic receptionist", "Patient coordinator"],
        "must_have_screens": ["dashboard", "appointments", "patients", "prescriptions", "billing"],
        "suggested_screens": ["lab_reports", "followups", "queue", "inventory"],
        "dashboard_cards": ["Today appointments", "Waiting patients", "Follow-ups", "Billing"],
        "primary_actions": ["Book appointment", "Add patient", "Create prescription", "Schedule follow-up"],
        "clickable_aliases": ["appointment", "patient", "prescription", "billing", "queue"],
        "domain_terms": ["patient", "appointment", "doctor", "prescription", "clinic", "follow-up"],
        "forbidden_generic_terms": ["guaranteed cure", "investment return", "crop harvest"],
        "sample_records": ["Dental appointment", "General checkup", "Follow-up visit"],
        "empty_state_guidance": "Start by adding doctor schedule and patient appointment slots.",
        "trust_and_safety_notes": ["Do not provide diagnosis guarantees.", "Use medical safety disclaimers."],
        "monetization_suggestions": ["Clinic monthly subscription", "Appointment booking add-on"],
        "compliance_notes": ["Healthcare information must remain private and advisory."],
    },
    "car_detailing": {
        "sector_key": "car_detailing",
        "app_name_style": "Car detailing booking and service workflow app",
        "theme_intent": "premium-automotive-dark",
        "primary_users": ["Detailing studio owner", "Service manager", "Technician"],
        "must_have_screens": ["dashboard", "bookings", "vehicles", "services", "payments"],
        "suggested_screens": ["packages", "before_after_gallery", "staff_tasks", "customer_feedback"],
        "dashboard_cards": ["Today bookings", "Revenue", "Pending services", "Customer ratings"],
        "primary_actions": ["Book service", "Add vehicle", "Assign technician", "Collect payment"],
        "clickable_aliases": ["booking", "vehicle", "service", "package", "payment"],
        "domain_terms": ["vehicle", "detailing", "ceramic coating", "wash", "polish", "booking"],
        "forbidden_generic_terms": ["student attendance", "SIP", "crop soil"],
        "sample_records": ["SUV ceramic coating", "Interior detailing", "Premium wash"],
        "empty_state_guidance": "Add service packages, time slots, and vehicle details.",
        "trust_and_safety_notes": ["Do not promise impossible restoration results."],
        "monetization_suggestions": ["Booking fee", "Premium package upsell", "Membership plans"],
        "compliance_notes": [],
    },
    "gym_fitness": {
        "sector_key": "gym_fitness",
        "app_name_style": "Fitness membership and workout tracking app",
        "theme_intent": "fitness-energy-bold",
        "primary_users": ["Gym owner", "Trainer", "Member"],
        "must_have_screens": ["dashboard", "members", "workouts", "classes", "payments"],
        "suggested_screens": ["trainer_schedule", "diet_plan", "progress", "membership"],
        "dashboard_cards": ["Active members", "Today classes", "Payment due", "Workout progress"],
        "primary_actions": ["Add member", "Assign workout", "Schedule class", "Renew membership"],
        "clickable_aliases": ["member", "workout", "class", "trainer", "payment"],
        "domain_terms": ["member", "workout", "trainer", "membership", "fitness", "class"],
        "forbidden_generic_terms": ["patient prescription", "policy premium", "mandi"],
        "sample_records": ["Monthly membership", "Strength plan", "Yoga class"],
        "empty_state_guidance": "Add member profile, plan duration, and trainer assignment.",
        "trust_and_safety_notes": ["Avoid unsafe health promises.", "Encourage professional fitness guidance."],
        "monetization_suggestions": ["Membership plans", "Trainer packages", "Class bookings"],
        "compliance_notes": ["Fitness guidance should not replace medical advice."],
    },
    "wedding_event_lawn": {
        "sector_key": "wedding_event_lawn",
        "app_name_style": "Wedding lawn booking and event operations app",
        "theme_intent": "wedding-elegant-warm",
        "primary_users": ["Venue owner", "Event manager", "Decorator"],
        "must_have_screens": ["dashboard", "bookings", "events", "packages", "payments"],
        "suggested_screens": ["decor_plan", "guest_capacity", "vendor_tasks", "gallery"],
        "dashboard_cards": ["Upcoming events", "Booked dates", "Payment pending", "Package value"],
        "primary_actions": ["Book date", "Create event", "Select package", "Assign vendor", "Collect advance"],
        "clickable_aliases": ["booking", "event", "package", "decor", "payment", "vendor"],
        "domain_terms": ["wedding", "event", "lawn", "decor", "guest", "package", "venue"],
        "forbidden_generic_terms": ["generic CRM", "patient", "SIP portfolio"],
        "sample_records": ["Engagement booking", "Mehendi setup", "Reception package"],
        "empty_state_guidance": "Ask for event date, guest count, package type, and decor preference.",
        "trust_and_safety_notes": ["Do not hide booking conflicts.", "Show advance/payment status clearly."],
        "monetization_suggestions": ["Booking commission", "Decor package upsell", "Vendor marketplace"],
        "compliance_notes": [],
    },
    "restaurant_food": {
        "sector_key": "restaurant_food",
        "app_name_style": "Restaurant ordering and table operations app",
        "theme_intent": "restaurant-warm-food",
        "primary_users": ["Restaurant owner", "Manager", "Waiter", "Kitchen staff"],
        "must_have_screens": ["dashboard", "menu", "orders", "tables", "payments"],
        "suggested_screens": ["kitchen_display", "inventory", "offers", "delivery"],
        "dashboard_cards": ["Today orders", "Table status", "Kitchen queue", "Revenue"],
        "primary_actions": ["Add menu item", "Create order", "Assign table", "Send to kitchen", "Collect payment"],
        "clickable_aliases": ["menu", "order", "table", "kitchen", "payment"],
        "domain_terms": ["menu", "order", "table", "kitchen", "dish", "bill"],
        "forbidden_generic_terms": ["policy claim", "student homework", "crop mandi"],
        "sample_records": ["Paneer butter masala", "Table 4 order", "Online delivery"],
        "empty_state_guidance": "Add menu categories, table layout, and payment settings.",
        "trust_and_safety_notes": ["Show food allergy notes where needed."],
        "monetization_suggestions": ["Order commission", "Restaurant POS subscription"],
        "compliance_notes": ["Food-related data should include basic allergy/safety awareness."],
    },
    "retail_inventory": {
        "sector_key": "retail_inventory",
        "app_name_style": "Retail stock, billing, and inventory management app",
        "theme_intent": "retail-inventory-grid",
        "primary_users": ["Shop owner", "Cashier", "Inventory manager"],
        "must_have_screens": ["dashboard", "products", "inventory", "sales", "billing"],
        "suggested_screens": ["suppliers", "purchase_orders", "low_stock", "reports"],
        "dashboard_cards": ["Low stock", "Today sales", "Fast moving items", "Gross margin"],
        "primary_actions": ["Add product", "Update stock", "Create bill", "Add supplier"],
        "clickable_aliases": ["product", "stock", "sale", "bill", "supplier"],
        "domain_terms": ["stock", "SKU", "bill", "supplier", "inventory", "sale"],
        "forbidden_generic_terms": ["patient queue", "class attendance", "crop soil"],
        "sample_records": ["Low stock alert", "Supplier invoice", "Counter sale"],
        "empty_state_guidance": "Start by adding products, opening stock, and supplier details.",
        "trust_and_safety_notes": ["Do not show fake tax compliance guarantees."],
        "monetization_suggestions": ["Retail POS subscription", "Inventory analytics add-on"],
        "compliance_notes": ["Tax/GST fields should be configurable by country."],
    },
    "government_civic": {
        "sector_key": "government_civic",
        "app_name_style": "Citizen grievance and civic service tracking app",
        "theme_intent": "government-civic-clean",
        "primary_users": ["Citizen", "Civic officer", "Department admin"],
        "must_have_screens": ["dashboard", "grievances", "departments", "status_tracker", "reports"],
        "suggested_screens": ["public_services", "documents", "field_updates", "feedback"],
        "dashboard_cards": ["Open grievances", "Resolved cases", "Department load", "SLA status"],
        "primary_actions": ["File grievance", "Assign department", "Update status", "Upload proof"],
        "clickable_aliases": ["grievance", "department", "status", "report", "service"],
        "domain_terms": ["grievance", "citizen", "department", "service", "status", "SLA"],
        "forbidden_generic_terms": ["sales lead", "restaurant table", "gym workout"],
        "sample_records": ["Road repair complaint", "Water supply issue", "Streetlight request"],
        "empty_state_guidance": "Ask for location, issue category, photo proof, and contact details.",
        "trust_and_safety_notes": ["Avoid political persuasion.", "Do not expose private citizen data."],
        "monetization_suggestions": [],
        "compliance_notes": ["Civic systems must protect personal identity and public records carefully."],
    },
    "real_estate": {
        "sector_key": "real_estate",
        "app_name_style": "Property listing, lead, and site visit management app",
        "theme_intent": "generic-modern-saas",
        "primary_users": ["Broker", "Builder", "Property manager"],
        "must_have_screens": ["dashboard", "properties", "leads", "site_visits", "deals"],
        "suggested_screens": ["documents", "pricing", "availability", "brokerage"],
        "dashboard_cards": ["Active listings", "New leads", "Site visits", "Deal value"],
        "primary_actions": ["Add property", "Add lead", "Schedule visit", "Update deal"],
        "clickable_aliases": ["property", "lead", "visit", "deal", "document"],
        "domain_terms": ["property", "listing", "site visit", "brokerage", "buyer", "rent"],
        "forbidden_generic_terms": ["patient prescription", "student homework", "crop mandi"],
        "sample_records": ["2BHK apartment", "Commercial shop", "Site visit scheduled"],
        "empty_state_guidance": "Add property location, price, availability, and lead source.",
        "trust_and_safety_notes": ["Do not show fake legal ownership guarantees."],
        "monetization_suggestions": ["Broker CRM subscription", "Listing promotion credits"],
        "compliance_notes": ["Property documents and ownership claims need verification."],
    },
    "travel_agency": {
        "sector_key": "travel_agency",
        "app_name_style": "Travel package, itinerary, and booking management app",
        "theme_intent": "generic-modern-saas",
        "primary_users": ["Travel agent", "Tour operator", "Booking manager"],
        "must_have_screens": ["dashboard", "packages", "bookings", "customers", "payments"],
        "suggested_screens": ["itinerary", "vendors", "documents", "support"],
        "dashboard_cards": ["Upcoming trips", "Booking value", "Payment due", "Customer requests"],
        "primary_actions": ["Create package", "Add booking", "Build itinerary", "Collect payment"],
        "clickable_aliases": ["package", "booking", "itinerary", "customer", "payment"],
        "domain_terms": ["trip", "itinerary", "package", "booking", "traveller", "hotel"],
        "forbidden_generic_terms": ["patient queue", "policy claim", "crop soil"],
        "sample_records": ["Goa package", "Family tour", "Hotel voucher"],
        "empty_state_guidance": "Add destination, travel dates, number of travellers, and package price.",
        "trust_and_safety_notes": ["Do not guarantee visa approval or travel availability."],
        "monetization_suggestions": ["Package margin", "Booking commission", "Vendor marketplace"],
        "compliance_notes": ["Travel documents and visa information must be verified by official sources."],
    },
    "salon_beauty": {
        "sector_key": "salon_beauty",
        "app_name_style": "Salon appointment, service, and staff management app",
        "theme_intent": "generic-modern-saas",
        "primary_users": ["Salon owner", "Stylist", "Receptionist"],
        "must_have_screens": ["dashboard", "appointments", "clients", "services", "payments"],
        "suggested_screens": ["staff_schedule", "packages", "before_after_gallery", "inventory"],
        "dashboard_cards": ["Today appointments", "Staff availability", "Service revenue", "Repeat clients"],
        "primary_actions": ["Book appointment", "Add client", "Assign stylist", "Collect payment"],
        "clickable_aliases": ["appointment", "client", "service", "staff", "payment"],
        "domain_terms": ["salon", "service", "stylist", "appointment", "client", "package"],
        "forbidden_generic_terms": ["SIP portfolio", "crop mandi", "government grievance"],
        "sample_records": ["Hair spa booking", "Bridal makeup", "Stylist schedule"],
        "empty_state_guidance": "Add services, staff timings, and appointment slots.",
        "trust_and_safety_notes": ["Avoid unrealistic beauty result promises."],
        "monetization_suggestions": ["Salon subscription", "Package upsell", "Membership plans"],
        "compliance_notes": [],
    },
    "accounting_ca": {
        "sector_key": "accounting_ca",
        "app_name_style": "CA office client, GST, invoice, and compliance workflow app",
        "theme_intent": "finance-trust-blue",
        "primary_users": ["Chartered accountant", "Tax assistant", "Client manager"],
        "must_have_screens": ["dashboard", "clients", "invoices", "gst_returns", "tasks"],
        "suggested_screens": ["documents", "payments", "compliance_calendar", "reports"],
        "dashboard_cards": ["GST due", "Invoices pending", "Client tasks", "Payments received"],
        "primary_actions": ["Add client", "Create invoice", "Upload document", "Track GST return"],
        "clickable_aliases": ["client", "invoice", "gst", "task", "document"],
        "domain_terms": ["GST", "invoice", "client", "return", "tax", "ledger"],
        "forbidden_generic_terms": ["patient appointment", "restaurant table", "crop harvest"],
        "sample_records": ["GST filing", "Invoice pending", "Client document request"],
        "empty_state_guidance": "Add client GSTIN, billing details, filing frequency, and document checklist.",
        "trust_and_safety_notes": ["Do not guarantee tax outcomes.", "Show compliance reminder language."],
        "monetization_suggestions": ["CA office subscription", "Client portal add-on"],
        "compliance_notes": ["Tax/GST data must be accurate and verified by professional review."],
    },
    "logistics_delivery": {
        "sector_key": "logistics_delivery",
        "app_name_style": "Delivery fleet, shipment, and route tracking app",
        "theme_intent": "generic-modern-saas",
        "primary_users": ["Logistics manager", "Dispatcher", "Delivery partner"],
        "must_have_screens": ["dashboard", "shipments", "drivers", "routes", "delivery_status"],
        "suggested_screens": ["vehicles", "proof_of_delivery", "customer_updates", "billing"],
        "dashboard_cards": ["Active shipments", "Delayed deliveries", "Driver status", "Route efficiency"],
        "primary_actions": ["Create shipment", "Assign driver", "Update status", "Upload proof"],
        "clickable_aliases": ["shipment", "driver", "route", "delivery", "vehicle"],
        "domain_terms": ["shipment", "driver", "route", "delivery", "vehicle", "POD"],
        "forbidden_generic_terms": ["student homework", "SIP", "salon service"],
        "sample_records": ["Express parcel", "Driver assigned", "Proof of delivery"],
        "empty_state_guidance": "Add shipment ID, pickup, drop location, driver, and delivery SLA.",
        "trust_and_safety_notes": ["Do not expose live personal location unnecessarily."],
        "monetization_suggestions": ["Fleet subscription", "Route analytics add-on"],
        "compliance_notes": ["Location and delivery proof must be handled securely."],
    },
    "construction_project": {
        "sector_key": "construction_project",
        "app_name_style": "Construction project, site task, and material tracking app",
        "theme_intent": "generic-modern-saas",
        "primary_users": ["Builder", "Project manager", "Site supervisor"],
        "must_have_screens": ["dashboard", "projects", "site_tasks", "materials", "progress"],
        "suggested_screens": ["workers", "vendors", "documents", "expenses"],
        "dashboard_cards": ["Project progress", "Material stock", "Pending tasks", "Site expenses"],
        "primary_actions": ["Create project", "Assign site task", "Update material", "Log expense"],
        "clickable_aliases": ["project", "site", "task", "material", "expense"],
        "domain_terms": ["project", "site", "material", "contractor", "progress", "vendor"],
        "forbidden_generic_terms": ["patient", "restaurant order", "SIP portfolio"],
        "sample_records": ["Foundation work", "Cement stock", "Vendor bill"],
        "empty_state_guidance": "Add project site, timeline, material list, and supervisor.",
        "trust_and_safety_notes": ["Do not ignore safety requirements for construction work."],
        "monetization_suggestions": ["Project management subscription", "Vendor tracking add-on"],
        "compliance_notes": ["Construction safety and legal approvals must be verified separately."],
    },
    "hotel_resort": {
        "sector_key": "hotel_resort",
        "app_name_style": "Hotel room, guest, and booking operations app",
        "theme_intent": "generic-modern-saas",
        "primary_users": ["Hotel owner", "Front desk", "Housekeeping manager"],
        "must_have_screens": ["dashboard", "rooms", "bookings", "guests", "payments"],
        "suggested_screens": ["housekeeping", "restaurant", "reviews", "offers"],
        "dashboard_cards": ["Occupancy", "Check-ins today", "Room status", "Revenue"],
        "primary_actions": ["Add booking", "Check in guest", "Assign room", "Collect payment"],
        "clickable_aliases": ["room", "booking", "guest", "checkin", "payment"],
        "domain_terms": ["room", "guest", "booking", "check-in", "occupancy", "housekeeping"],
        "forbidden_generic_terms": ["crop mandi", "student attendance", "policy claim"],
        "sample_records": ["Deluxe room booking", "Guest check-in", "Housekeeping pending"],
        "empty_state_guidance": "Add room inventory, rates, booking calendar, and guest details.",
        "trust_and_safety_notes": ["Protect guest identity and booking details."],
        "monetization_suggestions": ["Hotel PMS subscription", "Booking engine add-on"],
        "compliance_notes": ["Guest records may require local compliance and privacy handling."],
    },
    "ngo_social": {
        "sector_key": "ngo_social",
        "app_name_style": "NGO donor, campaign, and beneficiary impact app",
        "theme_intent": "generic-modern-saas",
        "primary_users": ["NGO admin", "Volunteer", "Donor manager"],
        "must_have_screens": ["dashboard", "donors", "campaigns", "beneficiaries", "reports"],
        "suggested_screens": ["volunteers", "donations", "field_updates", "impact_stories"],
        "dashboard_cards": ["Donations", "Active campaigns", "Beneficiaries reached", "Volunteer tasks"],
        "primary_actions": ["Add donor", "Create campaign", "Log donation", "Update impact"],
        "clickable_aliases": ["donor", "campaign", "beneficiary", "donation", "volunteer"],
        "domain_terms": ["donor", "campaign", "beneficiary", "donation", "impact", "volunteer"],
        "forbidden_generic_terms": ["sales CRM", "patient prescription", "restaurant order"],
        "sample_records": ["Education campaign", "Monthly donor", "Field impact update"],
        "empty_state_guidance": "Add campaign goal, donor list, beneficiary category, and impact metric.",
        "trust_and_safety_notes": ["Do not expose vulnerable beneficiary identity.", "Avoid fake impact claims."],
        "monetization_suggestions": ["Donor management subscription", "Impact report generator"],
        "compliance_notes": ["Donation and beneficiary data must be transparent and privacy-safe."],
    },
    "generic_saas": {
        "sector_key": "generic_saas",
        "app_name_style": "Modern SaaS dashboard and workflow app",
        "theme_intent": "generic-modern-saas",
        "primary_users": ["Admin", "Team member", "Customer"],
        "must_have_screens": ["dashboard", "records", "tasks", "analytics", "settings"],
        "suggested_screens": ["users", "billing", "activity", "reports"],
        "dashboard_cards": ["Active records", "Tasks due", "Usage", "Revenue"],
        "primary_actions": ["Create record", "Assign task", "View report", "Invite user"],
        "clickable_aliases": ["dashboard", "record", "task", "analytics", "settings"],
        "domain_terms": ["dashboard", "workflow", "record", "task", "team", "analytics"],
        "forbidden_generic_terms": [],
        "sample_records": ["Customer workspace", "Task board", "Analytics report"],
        "empty_state_guidance": "Ask the user what workflow, records, roles, and actions the SaaS app needs.",
        "trust_and_safety_notes": ["Avoid pretending generic output is a regulated expert system."],
        "monetization_suggestions": ["Subscription tiers", "Usage-based credits"],
        "compliance_notes": [],
    },
}


REQUIRED_BLUEPRINT_FIELDS: List[str] = [
    "sector_key",
    "app_name_style",
    "theme_intent",
    "primary_users",
    "must_have_screens",
    "dashboard_cards",
    "primary_actions",
    "clickable_aliases",
    "domain_terms",
    "forbidden_generic_terms",
    "empty_state_guidance",
    "trust_and_safety_notes",
]


def list_sector_keys() -> List[str]:
    """Return all supported sector keys."""
    return sorted(SECTOR_BLUEPRINTS.keys())


def get_sector_blueprint(sector_key: str | None, fallback: str = "generic_saas") -> Dict[str, Any]:
    """Return a deep copy of a sector blueprint with safe fallback."""
    key = (sector_key or "").strip()
    if key in SECTOR_BLUEPRINTS:
        return deepcopy(SECTOR_BLUEPRINTS[key])
    return deepcopy(SECTOR_BLUEPRINTS[fallback])


def build_generation_hints(sector_key: str | None) -> Dict[str, Any]:
    """Build compact hints that can be injected into future app generation flows."""
    blueprint = get_sector_blueprint(sector_key)
    return {
        "sector_key": blueprint["sector_key"],
        "app_name_style": blueprint["app_name_style"],
        "theme_intent": blueprint["theme_intent"],
        "primary_users": blueprint["primary_users"],
        "must_have_screens": blueprint["must_have_screens"],
        "suggested_screens": blueprint.get("suggested_screens", []),
        "dashboard_cards": blueprint["dashboard_cards"],
        "primary_actions": blueprint["primary_actions"],
        "clickable_aliases": blueprint["clickable_aliases"],
        "domain_terms": blueprint["domain_terms"],
        "empty_state_guidance": blueprint["empty_state_guidance"],
        "trust_and_safety_notes": blueprint["trust_and_safety_notes"],
        "compliance_notes": blueprint.get("compliance_notes", []),
    }


def apply_sector_blueprint(app_payload: Dict[str, Any], sector_key: str | None) -> Dict[str, Any]:
    """
    Defensive helper for future integration.

    It does not change existing app payload shape aggressively.
    It adds a non-user-facing generation_hints block and fills missing
    screens/aliases only when safe.
    """
    payload = deepcopy(app_payload) if isinstance(app_payload, dict) else {}
    blueprint = get_sector_blueprint(sector_key)

    payload.setdefault("sector_key", blueprint["sector_key"])
    payload.setdefault("theme_family", blueprint["theme_intent"])
    payload.setdefault("generation_hints", build_generation_hints(blueprint["sector_key"]))

    if isinstance(payload.get("screens"), list):
        existing = {str(screen).strip().lower() for screen in payload["screens"]}
        for screen in blueprint["must_have_screens"]:
            if screen.lower() not in existing:
                payload["screens"].append(screen)

    if isinstance(payload.get("clickable_aliases"), list):
        existing_aliases = {str(alias).strip().lower() for alias in payload["clickable_aliases"]}
        for alias in blueprint["clickable_aliases"]:
            if alias.lower() not in existing_aliases:
                payload["clickable_aliases"].append(alias)

    return payload


def validate_blueprint_coverage() -> Dict[str, Any]:
    """Validate all blueprint records for required fields and basic structure."""
    errors: List[str] = []
    warnings: List[str] = []

    for sector_key, blueprint in sorted(SECTOR_BLUEPRINTS.items()):
        for field in REQUIRED_BLUEPRINT_FIELDS:
            if field not in blueprint:
                errors.append(f"{sector_key}: missing required field '{field}'")

        if blueprint.get("sector_key") != sector_key:
            errors.append(f"{sector_key}: sector_key mismatch")

        for list_field in [
            "primary_users",
            "must_have_screens",
            "dashboard_cards",
            "primary_actions",
            "clickable_aliases",
            "domain_terms",
        ]:
            value = blueprint.get(list_field)
            if not isinstance(value, list) or not value:
                errors.append(f"{sector_key}: '{list_field}' must be a non-empty list")

        if sector_key != "generic_saas" and "generic_saas" in blueprint.get("sector_key", ""):
            warnings.append(f"{sector_key}: suspicious generic sector naming")

    return {
        "passed": not errors,
        "total_sectors": len(SECTOR_BLUEPRINTS),
        "errors": errors,
        "warnings": warnings,
        "sectors": list_sector_keys(),
    }


def main() -> int:
    result = validate_blueprint_coverage()
    print("IdeasForgeAI Phase 33A Sector Blueprint Coverage")
    print(f"Total sectors: {result['total_sectors']}")
    print(f"Passed: {result['passed']}")

    for sector in result["sectors"]:
        blueprint = SECTOR_BLUEPRINTS[sector]
        print(f"- {sector}: {len(blueprint['must_have_screens'])} screens, {len(blueprint['clickable_aliases'])} aliases")

    if result["warnings"]:
        print("\nWarnings:")
        for warning in result["warnings"]:
            print(f"- {warning}")

    if result["errors"]:
        print("\nErrors:")
        for error in result["errors"]:
            print(f"- {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

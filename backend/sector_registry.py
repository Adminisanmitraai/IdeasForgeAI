from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


SectorEntry = Dict[str, Any]

GLOBAL_SAFETY_RULES = [
    "Do not create fake certificates, fake approvals, fake policies, or fake government documents.",
    "Do not support fraud workflows, impersonation, illegal advice, or harmful/illegal app outputs.",
    "Keep regulated financial, medical, legal, and government decisions advisory or workflow-only.",
]

GLOBAL_FORBIDDEN_OUTPUTS = [
    "fake certificates",
    "fake government documents",
    "fake insurance policies",
    "guaranteed investment returns",
    "illegal financial advice",
    "fraud workflows",
    "frontend secrets or raw API keys",
]


def _sector(
    sector_id: str,
    display_name: str,
    strong_keywords: List[str],
    weak_keywords: List[str],
    negative_keywords: List[str],
    priority: int,
    theme_family: str,
    layout_family: str,
    app_name_options: List[str],
    app_type: str,
    target_users: List[str],
    core_features: List[str],
    screens: List[str],
    clickable_aliases: Dict[str, str],
    sample_metrics: List[List[str]],
    sample_cards: List[List[str]],
    currency_default: str,
    admin_dashboard_fields: List[str],
    legacy_domain: str | None = None,
    safety_rules: List[str] | None = None,
    forbidden_outputs: List[str] | None = None,
) -> SectorEntry:
    return {
        "sector_id": sector_id,
        "display_name": display_name,
        "strong_keywords": strong_keywords,
        "weak_keywords": weak_keywords,
        "negative_keywords": negative_keywords,
        "priority": priority,
        "theme_family": theme_family,
        "layout_family": layout_family,
        "app_name_options": app_name_options,
        "app_type": app_type,
        "target_users": target_users,
        "core_features": core_features,
        "screens": screens,
        "clickable_aliases": clickable_aliases,
        "sample_metrics": sample_metrics,
        "sample_cards": sample_cards,
        "currency_default": currency_default,
        "safety_rules": [*GLOBAL_SAFETY_RULES, *(safety_rules or [])],
        "forbidden_outputs": [*GLOBAL_FORBIDDEN_OUTPUTS, *(forbidden_outputs or [])],
        "admin_dashboard_fields": admin_dashboard_fields,
        "legacy_domain": legacy_domain or sector_id,
    }


SECTOR_REGISTRY: Dict[str, SectorEntry] = {
    "agriculture_farmer": _sector(
        "agriculture_farmer",
        "Agriculture / Farmer",
        ["farmer", "farm", "farming", "agriculture", "crop", "crop health", "mandi", "soil", "weather", "satellite", "ndvi", "farm records", "farmer profile", "agri", "kisan", "fpo", "harvest", "irrigation"],
        ["acreage", "buyer matching", "seed", "fertilizer", "field", "advisory"],
        ["clinic", "doctor", "patient", "hospital", "dental", "prescription", "opd"],
        100,
        "agriculture-green-dashboard",
        "hero-stat-stack",
        ["Farmer Dashboard", "Kisan Farm Hub", "Agri Intelligence Desk"],
        "agriculture farm intelligence and farmer dashboard app",
        ["farmers", "FPO teams", "agri advisors", "farm admins"],
        ["crop health cards", "weather cards", "mandi price cards", "satellite intelligence", "farmer profile", "farm records", "AI chat button", "soil and crop advisory", "alerts and recommendations"],
        ["Home Dashboard", "Crop Health", "Weather", "Mandi Prices", "Satellite Intelligence", "Farmer Profile", "Farm Records", "AI Chat", "Admin Dashboard"],
        {"dashboard": "dashboard", "crop_health": "crop", "crop": "crop", "weather": "weather", "mandi": "mandi", "mandi_prices": "mandi", "satellite": "satellite", "satellite_intelligence": "satellite", "farmer_profile": "profile", "farm_records": "records", "ai_chat": "chat", "admin": "admin"},
        [["Crop Health", "86% stable"], ["Mandi Rate", "INR 4,200/q"], ["Weather Risk", "Low"]],
        [["North Field", "Wheat healthy"], ["Soil Moisture", "Good"], ["Scout Priority", "Medium"]],
        "INR",
        ["farmer_count", "crop_alerts", "advisory_status", "mandi_followups"],
        legacy_domain="agriculture",
    ),
    "insurance_broker": _sector(
        "insurance_broker",
        "Insurance Broker",
        ["insurance", "policy", "claim", "premium", "renewal", "coverage", "insurer", "policy holder"],
        ["quote", "nominee", "advisor", "settlement", "underwriting"],
        ["mutual fund", "sip", "systematic investment plan", "portfolio", "nav", "amc"],
        80,
        "finance-trust-blue",
        "timeline-tracker",
        ["Insurance Trust Desk", "Policy Broker Hub", "Claims and Renewal Desk"],
        "insurance policy, quote, and claim tracker app",
        ["insurance advisors", "policy holders", "finance admins", "claim support teams"],
        ["policy cards", "quote builder", "claim tracker timeline", "advisor contact cards", "renewal reminders", "customer enquiry form", "finance dashboard"],
        ["Home", "Policy Cards", "Quote Builder", "Claim Tracker", "Advisor Contacts", "Renewals", "Admin Dashboard"],
        {"dashboard": "dashboard", "policy_cards": "policy_cards", "quote_builder": "quote_builder", "view_quote": "quote_builder", "claim_tracker": "claim_tracker", "advisor_contacts": "advisor_contacts", "renewals": "renewals", "admin": "admin_dashboard"},
        [["Active Policies", "248"], ["Claims Open", "12"], ["Renewals", "44"]],
        [["Health Protect", "Renewal due"], ["Vehicle Shield", "Quote pending"], ["Term Secure", "Nominee verified"]],
        "USD",
        ["active_policies", "claim_status", "renewal_due", "advisor_owner"],
        legacy_domain="finance_insurance",
        safety_rules=["Do not create fake insurance policies, fake claim approvals, or misleading coverage documents."],
        forbidden_outputs=["fake insurance policy", "fake claim approval"],
    ),
    "mutual_fund_advisor": _sector(
        "mutual_fund_advisor",
        "Mutual Fund Advisor",
        ["mutual fund", "sip", "systematic investment plan", "investment advisor", "wealth advisor", "portfolio tracker", "kyc", "risk profile", "fund comparison", "amc", "nav", "portfolio"],
        ["investor", "monthly investment", "fund category", "advisor booking", "asset management"],
        ["insurance", "policy", "claim", "premium", "coverage"],
        95,
        "finance-trust-blue-green",
        "card-first-dashboard",
        ["Mutual Fund Advisor", "SIP Investment Hub", "Wealth Advisor App", "Fund Portfolio Desk"],
        "mutual fund broker and investment advisor customer service app",
        ["investors", "SIP customers", "mutual fund advisors", "broker admins"],
        ["mutual fund categories", "compare funds", "SIP calculator", "portfolio tracker", "KYC document upload", "risk profile form", "advisor call booking", "SIP reminders", "customer enquiry form", "admin dashboard"],
        ["Home Dashboard", "Mutual Fund Categories", "Compare Funds", "SIP Calculator", "Portfolio Tracker", "KYC Upload", "Risk Profile", "Advisor Booking", "SIP Reminders", "Admin Dashboard"],
        {"dashboard": "dashboard", "funds": "funds", "mutual_fund_categories": "funds", "compare_funds": "compare", "compare": "compare", "sip": "sip", "sip_calculator": "sip", "portfolio": "portfolio", "portfolio_tracker": "portfolio", "kyc": "kyc", "kyc_upload": "kyc", "risk": "risk", "risk_profile": "risk", "advisor": "advisor", "advisor_booking": "advisor", "reminders": "reminders", "sip_reminders": "reminders", "enquiry": "enquiry", "admin": "admin"},
        [["SIP Amount", "INR 5,000/mo"], ["Portfolio Value", "INR 4.6L"], ["Advisory Leads", "28"]],
        [["Equity Funds", "Estimated growth view"], ["Hybrid Funds", "Balanced risk profile"], ["Debt Funds", "Lower volatility"]],
        "INR",
        ["advisory_leads", "kyc_pending", "sip_reminders", "portfolio_reviews"],
        safety_rules=["Show estimated growth only, never guaranteed returns.", "Do not create fake investment documents or fake KYC approvals.", "Do not provide illegal financial advice, promise profit, or mislead users."],
        forbidden_outputs=["guaranteed returns", "promised profit", "fake KYC approval", "fake investment document"],
    ),
    "school_teacher_parent": _sector(
        "school_teacher_parent",
        "School / Teacher / Parent / Tutor",
        ["school", "teacher", "student", "homework", "attendance", "exam marks", "parent messages", "timetable", "notices", "tutor", "tutors", "private tutor", "private tutors", "tuition", "tuition teacher", "coaching class", "private class"],
        ["fees", "class", "classes", "parent", "education", "marks", "report card", "batch", "student batch", "schedule"],
        ["clinic", "insurance", "mutual fund"],
        70,
        "education-soft-blue",
        "card-first-dashboard",
        ["Tutor Class Manager", "Private Tutor App", "School Parent Connect", "Teacher Parent Portal"],
        "tutor, class, parent communication, and attendance app",
        ["private tutors", "teachers", "parents", "students"],
        ["student records", "class and batch schedule", "attendance tracking", "homework updates", "fee status", "parent messages", "class dashboard"],
        ["Home", "Students", "Classes", "Attendance", "Homework", "Fees", "Parent Notices", "Parent Messages", "Exam Results", "Schedule", "Admin Dashboard"],
        {"dashboard": "dashboard", "students": "students", "classes": "classes", "attendance": "attendance", "homework": "homework", "fees": "fees", "notices": "parent_notices", "parent_notices": "parent_notices", "parent_messages": "parent_messages", "schedule": "schedule", "exam_results": "exam_results", "teacher_contact": "teacher_contact", "admin": "admin_dashboard"},
        [["Attendance", "12"], ["Homework Due", "8"], ["Parent Messages", "249"]],
        [["Batch A", "Math homework due"], ["Riya Sharma", "Fees pending"], ["Class 8", "Attendance marked"]],
        "USD",
        ["attendance_status", "homework_due", "fee_status", "notice_count"],
        legacy_domain="school",
        safety_rules=["Protect student data and parent contact information."],
    ),
    "clinic_healthcare": _sector(
        "clinic_healthcare",
        "Clinic / Healthcare",
        ["clinic", "doctor", "patient", "appointment", "hospital", "dental", "treatment", "prescription", "opd", "queue"],
        ["consultation", "follow-up", "health package", "reception"],
        ["crop health", "farm health", "soil health", "farmer", "mandi", "kisan"],
        72,
        "healthcare-calm-teal",
        "timeline-tracker",
        ["Clinic Appointment Hub", "Healthcare Queue Desk", "Doctor Booking App"],
        "clinic appointment app",
        ["doctors", "clinic staff", "patients"],
        ["appointment booking", "doctor schedule", "patient records", "queue status", "follow-up reminders", "payment status", "admin dashboard"],
        ["Home", "Appointments", "Doctor Schedule", "Patients", "Queue Status", "Follow-ups", "Admin Dashboard"],
        {"dashboard": "dashboard", "appointments": "appointments", "book_appointment": "appointments", "doctor_schedule": "doctor_schedule", "patients": "patients", "queue_status": "queue_status", "follow_ups": "follow_ups", "admin": "admin_dashboard"},
        [["Appointments", "42 today"], ["Queue", "8 waiting"], ["Open Slots", "11"]],
        [["Dr. Kapoor", "3 open slots"], ["Dental Wing", "2 slots"], ["Follow-up", "Tomorrow"]],
        "USD",
        ["appointments_today", "queue_count", "open_slots", "followups_due"],
        legacy_domain="clinic",
        safety_rules=["Do not present medical decisions as final diagnosis or treatment decisions."],
    ),
    "car_detailing": _sector(
        "car_detailing", "Car Detailing", ["car detailing", "car wash", "detailing", "vehicle", "washing", "doorstep", "ceramic"], ["auto", "bike", "polish", "interior clean"], [], 60, "premium-automotive-dark", "gallery-first-showcase", ["Premium Car Detailing", "Auto Detail Booking"], "car detailing and washing service booking app", ["car owners", "service admins", "doorstep service customers"], ["service packages", "doorstep booking", "before-after gallery", "booking calendar", "payment status", "admin dashboard"], ["Home", "Service Packages", "Doorstep Booking", "Before-After Gallery", "Booking Calendar", "Payment Status", "Admin Dashboard"], {"dashboard": "dashboard", "service_packages": "service_packages", "doorstep_booking": "doorstep_booking", "gallery": "before_after_gallery", "admin": "admin_dashboard"}, [["Daily Bookings", "18"], ["Revenue", "4.6k"], ["Leads", "7"]], [["Express Wash", "Quick exterior care"], ["Interior Deep Clean", "Cabin reset"], ["Ceramic Detail", "Premium finish"]], "USD", ["bookings", "revenue", "lead_status"], legacy_domain="car_detailing"
    ),
    "gym_fitness": _sector(
        "gym_fitness", "Gym / Fitness", ["gym", "fitness", "trainer", "workout", "membership"], ["class booking", "diet", "attendance", "member"], [], 58, "fitness-energy-bold", "hero-feature-grid", ["Fitness Studio", "Gym Member Hub"], "fitness studio membership and class booking app", ["gym owners", "members", "trainers"], ["membership plans", "trainer profiles", "class booking", "attendance tracking", "diet consultation", "payment dashboard"], ["Home", "Membership Plans", "Trainer Profiles", "Class Booking", "Attendance Tracking", "Diet Consultation", "Payment Dashboard"], {"dashboard": "dashboard", "membership_plans": "membership_plans", "trainers": "trainer_profiles", "class_booking": "class_booking", "attendance": "attendance_tracking", "payments": "payment_dashboard"}, [["Members", "286"], ["Class Bookings", "34"], ["Attendance", "91%"]], [["Starter Plan", "Gym access"], ["Transformation", "Trainer match"], ["Elite Coaching", "Premium sessions"]], "USD", ["members", "attendance", "class_bookings"], legacy_domain="gym"
    ),
    "wedding_event_lawn": _sector(
        "wedding_event_lawn", "Wedding / Event Lawn", ["wedding", "event lawn", "lawn", "venue", "haldi", "mehendi", "banquet", "marriage"], ["booking lead", "package", "gallery", "site visit"], [], 58, "wedding-elegant-warm", "gallery-first-showcase", ["Wedding Venue Booking", "Event Lawn Desk"], "wedding venue booking app", ["couples", "families", "event planners", "venue managers"], ["wedding packages", "Haldi theme", "Mehendi theme", "gallery", "booking calendar", "enquiry form", "admin lead dashboard"], ["Home", "Wedding Packages", "Haldi Theme", "Mehendi Theme", "Gallery", "Booking Calendar", "Enquiry Form", "Admin Lead Dashboard"], {"dashboard": "dashboard", "wedding_packages": "wedding_packages", "haldi_theme": "haldi_theme", "mehendi_theme": "mehendi_theme", "gallery": "gallery", "enquiry": "enquiry_form", "admin": "admin_lead_dashboard"}, [["Booking Leads", "24"], ["Date Holds", "8"], ["Pipeline", "INR 38L"]], [["Haldi Theme", "Outdoor decor"], ["Mehendi Theme", "Family lounge"], ["Royal Wedding", "Full venue"]], "INR", ["booking_leads", "date_holds", "package_interest"], legacy_domain="wedding_venue"
    ),
    "restaurant_food": _sector(
        "restaurant_food", "Restaurant / Food", ["restaurant", "food", "menu", "order", "table booking", "cafe", "tiffin"], ["kitchen", "dish", "reservation", "takeaway"], [], 55, "restaurant-warm-food", "split-action-dashboard", ["Restaurant Order Hub", "Food Ordering Desk"], "restaurant ordering app", ["restaurant owners", "kitchen staff", "customers"], ["menu catalog", "food ordering", "table booking", "kitchen queue", "payment status", "admin dashboard"], ["Home", "Menu", "Food Ordering", "Table Booking", "Kitchen Queue", "Payment Dashboard", "Admin Dashboard"], {"dashboard": "dashboard", "menu": "menu", "order_food": "food_ordering", "book_table": "table_booking", "kitchen_queue": "kitchen_queue", "payments": "payment_dashboard"}, [["Orders", "86"], ["Reservations", "18"], ["Revenue", "6.8k"]], [["Chef Thali", "Lunch combo"], ["Paneer Bowl", "Bestseller"], ["Dinner Pack", "Family bundle"]], "USD", ["orders", "reservations", "payment_status"], legacy_domain="restaurant"
    ),
    "retail_inventory": _sector(
        "retail_inventory", "Retail Inventory", ["retail", "inventory", "stock", "shop", "store", "catalog"], ["sku", "supplier", "sales", "low stock"], [], 52, "retail-inventory-grid", "admin-metrics-grid", ["Retail Inventory Hub", "Store Stock Desk"], "retail inventory app", ["store owners", "sales staff", "inventory managers"], ["product catalog", "inventory tracking", "low-stock alerts", "sales dashboard", "purchase orders", "payment status"], ["Home", "Product Catalog", "Inventory", "Low Stock", "Sales Records", "Revenue Dashboard", "Admin Dashboard"], {"dashboard": "dashboard", "product_catalog": "product_catalog", "inventory": "inventory", "low_stock": "low_stock", "sales_dashboard": "revenue_dashboard", "admin": "admin_dashboard"}, [["Products", "312 SKUs"], ["Low Stock", "14"], ["Revenue", "8.2k"]], [["Wireless Earbuds", "48 in stock"], ["Backpack", "12 left"], ["Smart Watch", "PO pending"]], "USD", ["products", "low_stock", "sales_records"], legacy_domain="retail"
    ),
    "government_civic": _sector(
        "government_civic",
        "Government / Civic",
        ["government", "citizen service", "officer dashboard", "scheme", "grievance", "public service", "department", "municipality", "district", "panchayat", "audit"],
        ["certificate", "application", "ward", "sla", "civic", "municipal"],
        ["fake document", "fake certificate", "impersonate"],
        85,
        "government-civic-clean",
        "timeline-tracker",
        ["Civic Service Desk", "Citizen Grievance Portal", "Officer Review Dashboard"],
        "government citizen service and officer dashboard app",
        ["citizens", "field officers", "department admins", "audit teams"],
        ["role-based cards", "citizen services", "officer dashboard", "audit/status cards", "application tracker", "service request form", "department metrics"],
        ["Home", "Citizen Services", "Officer Dashboard", "Application Tracker", "Audit Status", "Service Request", "Department Metrics"],
        {"dashboard": "dashboard", "citizen_services": "citizen_services", "officer_dashboard": "officer_dashboard", "track_status": "application_tracker", "audit_status": "audit_status", "submit_request": "service_request", "department_metrics": "department_metrics"},
        [["Citizen Services", "74 active"], ["Officer Reviews", "18 pending"], ["Audit Status", "96% verified"]],
        [["Certificate", "Officer review"], ["Water Request", "In progress"], ["Scheme Form", "Verified"]],
        "INR",
        ["service_requests", "officer_reviews", "audit_status", "sla_risk"],
        legacy_domain="government",
        safety_rules=["No fake documents, fraud, impersonation, or unauthorized public-service claims."],
        forbidden_outputs=["fake government document", "fake certificate", "impersonation workflow"],
    ),
    "real_estate": _sector("real_estate", "Real Estate", ["real estate", "property", "broker", "listing", "flat", "apartment", "plot"], ["site visit", "rent", "buyer", "seller"], [], 42, "generic-modern-saas", "card-first-dashboard", ["Property Broker Hub"], "real estate listing and lead management app", ["brokers", "buyers", "property admins"], ["property listings", "site visit booking", "lead tracker", "document checklist", "admin dashboard"], ["Home", "Listings", "Site Visits", "Lead Tracker", "Document Checklist", "Admin Dashboard"], {"dashboard": "dashboard", "listings": "dashboard", "site_visits": "dashboard", "admin": "dashboard"}, [["Listings", "42"], ["Site Visits", "9"], ["Leads", "18"]], [["2BHK Apartment", "Site visit"], ["Commercial Plot", "Interested"], ["Villa", "Document check"]], "USD", ["listings", "leads", "site_visits"]),
    "travel_agency": _sector("travel_agency", "Travel Agency", ["travel", "tour", "trip", "itinerary", "visa", "hotel booking", "flight"], ["package", "destination", "booking"], [], 42, "generic-modern-saas", "card-first-dashboard", ["Travel Agency Desk"], "travel package and booking management app", ["travel agents", "customers", "operations teams"], ["trip packages", "itinerary builder", "booking tracker", "visa checklist", "admin dashboard"], ["Home", "Packages", "Itinerary", "Bookings", "Visa Checklist", "Admin Dashboard"], {"dashboard": "dashboard", "packages": "dashboard", "bookings": "dashboard", "admin": "dashboard"}, [["Bookings", "32"], ["Trips", "12"], ["Visa Pending", "7"]], [["Dubai Package", "Quote sent"], ["Japan Trip", "Itinerary ready"], ["Europe Tour", "Visa pending"]], "USD", ["bookings", "itineraries", "visa_status"]),
    "salon_beauty": _sector("salon_beauty", "Salon / Beauty", ["salon", "beauty", "spa", "haircut", "makeup", "bridal makeup"], ["stylist", "appointment", "package"], [], 42, "generic-modern-saas", "gallery-first-showcase", ["Salon Booking Studio"], "salon appointment and package booking app", ["salon owners", "stylists", "customers"], ["service menu", "appointment booking", "stylist calendar", "package gallery", "payments"], ["Home", "Services", "Appointments", "Stylists", "Gallery", "Payments", "Admin Dashboard"], {"dashboard": "dashboard", "services": "dashboard", "appointments": "dashboard", "admin": "dashboard"}, [["Bookings", "26"], ["Stylists", "8"], ["Revenue", "5.4k"]], [["Hair Spa", "Booked"], ["Bridal Makeup", "Quote sent"], ["Skin Care", "Follow-up"]], "USD", ["appointments", "stylists", "payments"]),
    "accounting_ca": _sector("accounting_ca", "Accounting / CA", ["accounting", "chartered accountant", "ca firm", "gst", "tax filing", "invoice", "ledger", "reconciliation"], ["audit", "client books", "return filing"], [], 48, "finance-trust-blue", "admin-metrics-grid", ["CA Client Desk", "Accounting Workflow Hub"], "accounting and tax workflow app", ["CAs", "accountants", "business clients"], ["client dashboard", "GST tracker", "tax filing checklist", "invoice records", "reconciliation queue"], ["Home", "Clients", "GST Tracker", "Tax Filing", "Invoices", "Reconciliation", "Admin Dashboard"], {"dashboard": "dashboard", "clients": "dashboard", "gst_tracker": "dashboard", "admin": "dashboard"}, [["Clients", "64"], ["GST Due", "11"], ["Reconciliations", "28"]], [["ABC Traders", "GST due"], ["Invoice #204", "Matched"], ["FY Return", "Checklist ready"]], "INR", ["clients", "gst_due", "filing_status"]),
    "logistics_delivery": _sector("logistics_delivery", "Logistics / Delivery", ["logistics", "delivery", "courier", "shipment", "fleet", "driver", "route"], ["tracking", "pod", "dispatch"], [], 42, "generic-modern-saas", "timeline-tracker", ["Delivery Operations Hub"], "logistics delivery tracking app", ["dispatch teams", "drivers", "customers"], ["shipment tracker", "driver assignment", "route board", "proof of delivery", "admin dashboard"], ["Home", "Shipments", "Drivers", "Routes", "Delivery Proof", "Admin Dashboard"], {"dashboard": "dashboard", "shipments": "dashboard", "drivers": "dashboard", "admin": "dashboard"}, [["Shipments", "128"], ["Drivers", "22"], ["Delayed", "6"]], [["Order #891", "Out for delivery"], ["Route 4", "Assigned"], ["POD", "Pending"]], "USD", ["shipments", "drivers", "route_status"]),
    "construction_project": _sector("construction_project", "Construction Project", ["construction", "contractor", "site project", "civil work", "material", "site progress"], ["labour", "boq", "milestone"], [], 42, "generic-modern-saas", "admin-metrics-grid", ["Construction Site Desk"], "construction project management app", ["contractors", "site managers", "clients"], ["site progress", "material tracker", "labour attendance", "milestone billing", "admin dashboard"], ["Home", "Site Progress", "Materials", "Labour", "Milestones", "Admin Dashboard"], {"dashboard": "dashboard", "site_progress": "dashboard", "materials": "dashboard", "admin": "dashboard"}, [["Progress", "64%"], ["Materials", "12 pending"], ["Labour", "48 today"]], [["Foundation", "Complete"], ["Cement", "Low stock"], ["Milestone 2", "Billing ready"]], "USD", ["progress", "materials", "labour"]),
    "hotel_resort": _sector("hotel_resort", "Hotel / Resort", ["hotel", "resort", "room booking", "guest", "reservation", "front desk"], ["check-in", "housekeeping", "occupancy"], [], 42, "generic-modern-saas", "card-first-dashboard", ["Hotel Guest Desk"], "hotel reservation and operations app", ["hotel managers", "front desk staff", "guests"], ["room booking", "guest check-in", "housekeeping board", "payment status", "admin dashboard"], ["Home", "Rooms", "Reservations", "Guests", "Housekeeping", "Payments", "Admin Dashboard"], {"dashboard": "dashboard", "rooms": "dashboard", "reservations": "dashboard", "admin": "dashboard"}, [["Occupancy", "82%"], ["Check-ins", "18"], ["Housekeeping", "7 rooms"]], [["Room 204", "Ready"], ["Family Suite", "Booked"], ["Payment", "Pending"]], "USD", ["occupancy", "reservations", "housekeeping"]),
    "ngo_social": _sector("ngo_social", "NGO / Social", ["ngo", "nonprofit", "donation", "volunteer", "social work", "beneficiary"], ["campaign", "impact", "field worker"], [], 42, "generic-modern-saas", "card-first-dashboard", ["NGO Impact Desk"], "NGO donor and beneficiary management app", ["NGO admins", "field workers", "donors"], ["donor tracker", "campaign dashboard", "beneficiary records", "volunteer scheduling", "impact reports"], ["Home", "Campaigns", "Donors", "Beneficiaries", "Volunteers", "Impact Reports"], {"dashboard": "dashboard", "campaigns": "dashboard", "donors": "dashboard", "admin": "dashboard"}, [["Donors", "248"], ["Volunteers", "39"], ["Beneficiaries", "820"]], [["Food Drive", "Active"], ["School Kit", "Funded"], ["Field Visit", "Scheduled"]], "USD", ["donors", "campaigns", "impact"]),
    "generic_saas": _sector("generic_saas", "Generic SaaS", [], ["dashboard", "crm", "workflow", "customer", "task", "team", "analytics"], [], 1, "generic-modern-saas", "card-first-dashboard", ["IdeasForgeAI Work Assistant", "Workflow Dashboard"], "mobile-first SaaS workflow app", ["business owners", "operators", "team members"], ["guided onboarding", "role-aware dashboard", "task cards", "approval flow", "reports and insights"], ["Home Dashboard", "Intake and Setup", "Workflow Board", "Reports and Insights"], {"dashboard": "dashboard", "workflow": "dashboard", "reports": "dashboard"}, [["Active Items", "24"], ["Tasks", "8"], ["Team", "5"]], [["Lead Follow-up", "Today"], ["Report", "Ready"], ["Approval", "Pending"]], "USD", ["active_items", "tasks", "team"])
}

LEGACY_DOMAIN_TO_SECTOR_ID = {
    entry["legacy_domain"]: sector_id for sector_id, entry in SECTOR_REGISTRY.items()
}
SECTOR_ID_TO_LEGACY_DOMAIN = {
    sector_id: entry["legacy_domain"] for sector_id, entry in SECTOR_REGISTRY.items()
}


def get_sector_entry(sector_id: str) -> SectorEntry:
    if sector_id in SECTOR_REGISTRY:
        return deepcopy(SECTOR_REGISTRY[sector_id])
    if sector_id in LEGACY_DOMAIN_TO_SECTOR_ID:
        return deepcopy(SECTOR_REGISTRY[LEGACY_DOMAIN_TO_SECTOR_ID[sector_id]])
    return deepcopy(SECTOR_REGISTRY["generic_saas"])


def list_sector_ids() -> List[str]:
    return list(SECTOR_REGISTRY.keys())


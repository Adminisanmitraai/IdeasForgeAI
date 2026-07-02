import html
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from backend.core.project_paths import PROJECT_ROOT
from backend.generated_app_quality_agent import quality_notes_for_generated_app
from backend.image_first_mockup_engine import build_image_first_mockup
from backend.premium_ui_image_concept import build_premium_ui_image_concept
from backend.sector_registry import LEGACY_DOMAIN_TO_SECTOR_ID, SECTOR_ID_TO_LEGACY_DOMAIN, get_sector_entry
from backend.sector_router import route_sector
from backend.sector_templates import product_plan_from_sector
from backend.sector_ui_rendering import get_sector_ui_profile, sector_ui_class_names


BACKEND_GENERATED_APPS_DIR = PROJECT_ROOT / "backend" / "generated_apps"
MAX_REFERENCE_IMAGE_TEXT_LENGTH = 1200
REFERENCE_IMAGE_KEYS = {"referenceImage", "reference_image", "imageReference", "image_metadata"}

AGRICULTURE_KEYWORDS = [
    "farmer",
    "farm",
    "farming",
    "agriculture",
    "crop",
    "crop health",
    "mandi",
    "soil",
    "weather",
    "satellite",
    "ndvi",
    "farm records",
    "farmer profile",
    "agri",
    "kisan",
    "fpo",
    "buyer matching",
    "harvest",
    "irrigation",
]

CURRENCY_PROFILES: Dict[str, Dict[str, str]] = {
    "INR": {"currency_code": "INR", "currency_symbol": "₹", "currency_locale": "en-IN", "country_hint": "India"},
    "USD": {"currency_code": "USD", "currency_symbol": "$", "currency_locale": "en-US", "country_hint": "United States"},
    "GBP": {"currency_code": "GBP", "currency_symbol": "£", "currency_locale": "en-GB", "country_hint": "United Kingdom"},
    "EUR": {"currency_code": "EUR", "currency_symbol": "€", "currency_locale": "de-DE", "country_hint": "Europe"},
    "AED": {"currency_code": "AED", "currency_symbol": "AED", "currency_locale": "en-AE", "country_hint": "United Arab Emirates"},
    "SAR": {"currency_code": "SAR", "currency_symbol": "SAR", "currency_locale": "ar-SA", "country_hint": "Saudi Arabia"},
    "BDT": {"currency_code": "BDT", "currency_symbol": "৳", "currency_locale": "bn-BD", "country_hint": "Bangladesh"},
    "JPY": {"currency_code": "JPY", "currency_symbol": "¥", "currency_locale": "ja-JP", "country_hint": "Japan"},
}

LOCATION_CURRENCY_RULES = [
    ("INR", ["india", "delhi", "punjab", "kolkata", "mumbai", "assam", "bihar", "west bengal", "kisan", "mandi", "farmer"]),
    ("USD", ["usa", "u.s.", "united states", "new york", "california"]),
    ("GBP", ["uk", "u.k.", "united kingdom", "london"]),
    ("EUR", ["europe", "germany", "france", "italy", "spain"]),
    ("AED", ["uae", "dubai", "abu dhabi", "united arab emirates"]),
    ("SAR", ["saudi", "riyadh", "saudi arabia"]),
    ("BDT", ["bangladesh", "dhaka"]),
    ("JPY", ["japan", "tokyo"]),
]

LOCALE_CURRENCY_RULES = [
    ("INR", ["en-in", "hi-in", "asia/kolkata", "asia/calcutta"]),
    ("USD", ["en-us", "america/new_york", "america/los_angeles", "america/chicago"]),
    ("GBP", ["en-gb", "europe/london"]),
    ("EUR", ["de-de", "fr-fr", "it-it", "es-es", "europe/berlin", "europe/paris", "europe/rome", "europe/madrid"]),
    ("AED", ["en-ae", "ar-ae", "asia/dubai"]),
    ("SAR", ["ar-sa", "en-sa", "asia/riyadh"]),
    ("BDT", ["bn-bd", "en-bd", "asia/dhaka"]),
    ("JPY", ["ja-jp", "en-jp", "asia/tokyo"]),
]
CLINIC_KEYWORDS = [
    "clinic",
    "doctor",
    "patient",
    "appointment",
    "hospital",
    "dental",
    "treatment",
    "prescription",
    "queue",
    "opd",
]

TUTOR_KEYWORDS = [
    "private tutor",
    "private tutors",
    "tutor",
    "tutors",
    "tuition",
    "tuition teacher",
    "coaching class",
    "private class",
    "student batch",
    "tutor student",
]

MUTUAL_FUND_KEYWORDS = [
    "mutual fund",
    "sip",
    "systematic investment plan",
    "investment advisor",
    "wealth advisor",
    "portfolio tracker",
    "kyc",
    "risk profile",
    "fund comparison",
    "asset management",
    "amc",
    "portfolio",
    "nav",
    "investment guidance",
]

INSURANCE_KEYWORDS = [
    "insurance",
    "policy",
    "claim",
    "premium",
    "renewal",
    "coverage",
    "insurer",
    "policy holder",
]

LAYOUT_VARIANTS = [
    "hero-stat-stack",
    "hero-feature-grid",
    "split-action-dashboard",
    "card-first-dashboard",
    "gallery-first-showcase",
    "timeline-tracker",
    "admin-metrics-grid",
]

THEME_FAMILIES: Dict[str, Dict[str, Any]] = {
    "finance-trust-blue": {
        "domains": ["finance_insurance", "mutual_fund_advisor"],
        "keywords": ["insurance", "finance", "policy", "claim", "quote", "loan", "bank", "mutual fund", "sip", "investment advisor", "portfolio", "nav"],
        "style": "blue and white finance trust interface with policy, investment, portfolio, advisor, and clean dashboard panels",
    },
    "finance-trust-blue-green": {
        "domains": ["mutual_fund_advisor"],
        "keywords": ["mutual fund", "sip", "investment advisor", "portfolio", "kyc", "risk profile", "nav"],
        "style": "blue and green finance trust interface with SIP, fund comparison, portfolio, KYC, risk profile, and advisor guidance panels",
    },
    "premium-automotive-dark": {
        "domains": ["car_detailing"],
        "keywords": ["car", "detailing", "vehicle", "ceramic", "auto"],
        "style": "premium dark automotive interface with metallic accent, service packages, before-after proof, booking, and payment cards",
    },
    "fitness-energy-bold": {
        "domains": ["gym"],
        "keywords": ["gym", "fitness", "trainer", "workout", "membership"],
        "style": "bold energetic fitness interface with strong CTAs, membership cards, trainer cards, progress, and attendance sections",
    },
    "wedding-elegant-warm": {
        "domains": ["wedding_venue"],
        "keywords": ["wedding", "venue", "haldi", "mehendi", "banquet", "lawn"],
        "style": "elegant warm event interface with Haldi and Mehendi accents, gallery mosaic, packages, enquiry, and lead dashboard",
    },
    "education-soft-blue": {
        "domains": ["school"],
        "keywords": ["school", "student", "teacher", "parent", "homework", "attendance"],
        "style": "soft blue education interface with student cards, homework cards, attendance, notices, and parent communication",
    },
    "healthcare-calm-teal": {
        "domains": ["clinic"],
        "keywords": CLINIC_KEYWORDS,
        "style": "calm teal healthcare interface with doctor cards, appointments, patient enquiries, and treatment packages",
    },
    "restaurant-warm-food": {
        "domains": ["restaurant"],
        "keywords": ["restaurant", "menu", "food", "table", "order", "cafe"],
        "style": "warm food interface with menu cards, table booking, order summary, and popular dishes",
    },
    "retail-inventory-grid": {
        "domains": ["retail"],
        "keywords": ["retail", "shop", "inventory", "stock", "store", "catalog"],
        "style": "inventory grid interface with product cards, stock alert chips, and revenue dashboard",
    },
    "agriculture-green-dashboard": {
        "domains": ["agriculture"],
        "keywords": AGRICULTURE_KEYWORDS,
        "style": "green, earthy, farm-friendly mobile dashboard with crop health cards, weather cards, mandi price cards, satellite intelligence, farmer profile, farm records, and AI chat CTA",
    },
    "government-civic-clean": {
        "domains": ["government"],
        "keywords": ["government", "civic", "citizen", "officer", "audit", "municipal", "scheme"],
        "style": "clean official civic interface with role cards, citizen services, officer dashboard, and audit status cards",
    },
    "generic-modern-saas": {
        "domains": ["generic"],
        "keywords": [],
        "style": "modern SaaS interface with balanced cards, workflow metrics, and clear action states",
    },
}


def _clean_text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str):
        cleaned = " ".join(value.split())
        return cleaned or fallback
    return fallback


def _clean_list(value: Any, fallback: Iterable[str]) -> List[str]:
    if isinstance(value, list):
        items = [_clean_text(item) for item in value]
        items = [item for item in items if item]
        if items:
            return items
    if isinstance(value, str) and value.strip():
        return [_clean_text(value)]
    return list(fallback)


def normalize_reference_image_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw = None
    for key in REFERENCE_IMAGE_KEYS:
        if key in payload:
            raw = payload.get(key)
            break

    if not isinstance(raw, dict):
        return {}

    allowed = {
        "name",
        "fileName",
        "type",
        "mimeType",
        "size",
        "sourcePath",
        "path",
        "width",
        "height",
        "layoutHint",
        "visualNotes",
        "source",
    }
    normalized: Dict[str, Any] = {}
    for key in allowed:
        value = raw.get(key)
        if isinstance(value, str):
            value = value.strip()[:MAX_REFERENCE_IMAGE_TEXT_LENGTH]
            if value:
                normalized[key] = value
        elif isinstance(value, (int, float)) and value >= 0:
            normalized[key] = value

    if not normalized:
        return {}

    normalized["inputMode"] = "image-guided-metadata-only"
    normalized["binaryUploadReceived"] = False
    normalized["ocrOrVisionPerformed"] = False
    return normalized


def _apply_image_guidance(plan: Dict[str, Any], reference_image: Dict[str, Any]) -> Dict[str, Any]:
    if not reference_image:
        return plan

    source_label = (
        reference_image.get("name")
        or reference_image.get("fileName")
        or reference_image.get("sourcePath")
        or reference_image.get("path")
        or "reference image metadata"
    )
    guided = dict(plan)
    guided["input_mode"] = "image-guided"
    guided["image_guided"] = True
    guided["reference_image"] = reference_image
    guided["visual_reference_summary"] = (
        f"Using {source_label} metadata as a visual guide for mobile layout, hierarchy, spacing, "
        "and interface rhythm. No image bytes, OCR, or pixel analysis are processed in this phase."
    )
    guided["design_inspiration_note"] = (
        "Use safe reference metadata only to guide visual rhythm, hierarchy, spacing, and mobile screen feel."
    )
    guided["interface_design_priorities"] = [
        "Reference-inspired mobile first screen",
        "App-like header/navigation hierarchy",
        "Compact card/list sections instead of generic landing content",
        "Sticky primary actions and clean iPhone-sized rendering",
    ]
    guided["screens"] = [
        "Image-guided Home",
        "Reference Layout Dashboard",
        "Primary Action Flow",
        "Details and Form",
        "Review and Approval",
    ]
    base_features = _clean_list(guided.get("core_features"), [])
    guided["core_features"] = [
        "Reference-inspired mobile interface structure",
        "Visual hierarchy and spacing scaffold",
        "Mobile dashboard and action flow",
        *base_features[:4],
    ]
    return guided


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:42] or "ideasforge-app"


def _title_from_idea(idea: str) -> str:
    stop_words = {
        "build", "make", "create", "need", "want", "with", "that", "this",
        "from", "into", "using", "for", "app", "tool", "website",
    }
    words = [
        word.strip(".,!?;:()[]{}").capitalize()
        for word in idea.split()
        if len(word.strip(".,!?;:()[]{}")) > 2
        and word.strip(".,!?;:()[]{}").lower() not in stop_words
    ]
    if not words:
        return "IdeasForge App"
    return " ".join(words[:3])


def _matches_keywords(lower_text: str, tokens: set[str], keywords: Iterable[str]) -> bool:
    for keyword in keywords:
        normalized_keyword = keyword.lower()
        if " " in normalized_keyword:
            if normalized_keyword in lower_text:
                return True
        elif normalized_keyword in tokens:
            return True
    return False


def _text_has_location(lower_text: str, keyword: str) -> bool:
    normalized = keyword.lower()
    if "." in normalized:
        return normalized in lower_text
    if " " in normalized:
        return normalized in lower_text
    return re.search(rf"\b{re.escape(normalized)}\b", lower_text) is not None


def _extract_client_currency_context(payload: Dict[str, Any] | None) -> Dict[str, str]:
    if not isinstance(payload, dict):
        return {}
    context = payload.get("client_context") or payload.get("clientContext") or payload.get("client_metadata") or payload.get("clientMetadata")
    if not isinstance(context, dict):
        context = payload
    return {
        "client_locale": _clean_text(
            context.get("client_locale")
            or context.get("clientLocale")
            or context.get("browser_locale")
            or context.get("browserLocale")
            or context.get("locale")
            or context.get("language")
        ),
        "client_timezone": _clean_text(
            context.get("client_timezone")
            or context.get("clientTimezone")
            or context.get("browser_timezone")
            or context.get("browserTimezone")
            or context.get("timeZone")
            or context.get("timezone")
        ),
        "currency_hint": _clean_text(context.get("currency_hint") or context.get("currencyHint")),
    }


def resolve_currency_profile(
    source_text: str,
    client_metadata: Dict[str, Any] | None = None,
    detected_domain: str = "generic",
) -> Dict[str, str]:
    lower_text = _clean_text(source_text).lower()
    client_context = _extract_client_currency_context(client_metadata)
    hint = client_context.get("currency_hint", "").upper()
    if hint in CURRENCY_PROFILES:
        return dict(CURRENCY_PROFILES[hint])

    for code, keywords in LOCATION_CURRENCY_RULES:
        if any(_text_has_location(lower_text, keyword) for keyword in keywords):
            return dict(CURRENCY_PROFILES[code])

    locale_text = f"{client_context.get('client_locale', '')} {client_context.get('client_timezone', '')}".lower()
    for code, keywords in LOCALE_CURRENCY_RULES:
        if any(keyword in locale_text for keyword in keywords):
            return dict(CURRENCY_PROFILES[code])

    if detected_domain in {"agriculture", "mutual_fund_advisor"} or any(
        _text_has_location(lower_text, keyword)
        for keyword in [
            "farmer",
            "farm",
            "agriculture",
            "crop",
            "mandi",
            "kisan",
            "fpo",
            "mutual fund",
            "sip",
            "systematic investment plan",
        ]
    ):
        return dict(CURRENCY_PROFILES["INR"])

    return dict(CURRENCY_PROFILES["USD"])


def _apply_currency_profile(
    plan: Dict[str, Any],
    source_text: str,
    client_metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    enriched = dict(plan)
    domain = _domain_from_plan(enriched)
    profile = resolve_currency_profile(source_text, client_metadata, detected_domain=domain)
    enriched.update(profile)
    enriched["currency_resolution"] = {
        "source_priority": "prompt-location, browser-locale-timezone, industry-fallback",
        "client_locale": _extract_client_currency_context(client_metadata).get("client_locale", ""),
        "client_timezone": _extract_client_currency_context(client_metadata).get("client_timezone", ""),
        "live_exchange_conversion": False,
    }
    return enriched


def _attach_premium_ui_image_concept(plan: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(plan)
    mockup = build_image_first_mockup(enriched)
    if mockup.get("ok"):
        enriched["image_first_mockup"] = mockup
    concept = build_premium_ui_image_concept(enriched)
    if concept.get("ok"):
        enriched["premium_ui_image_concept"] = concept
    return enriched


DOMAIN_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "mutual_fund_advisor": {
        "keywords": MUTUAL_FUND_KEYWORDS,
        "app_name": "Mutual Fund Advisor",
        "app_name_options": ["Mutual Fund Advisor", "SIP Investment Hub", "Wealth Advisor App", "Fund Portfolio Desk"],
        "app_type": "mutual fund broker and investment advisor customer service app",
        "target_users": ["investors", "SIP customers", "mutual fund advisors", "broker admins"],
        "core_features": [
            "mutual fund categories",
            "compare funds",
            "SIP calculator",
            "portfolio tracker",
            "KYC document upload",
            "risk profile form",
            "advisor call booking",
            "SIP reminders",
            "customer enquiry form",
            "admin dashboard",
        ],
        "screens": [
            "Home Dashboard",
            "Mutual Fund Categories",
            "Compare Funds",
            "SIP Calculator",
            "Portfolio Tracker",
            "KYC Upload",
            "Risk Profile",
            "Advisor Booking",
            "SIP Reminders",
            "Admin Dashboard",
        ],
        "data_needs": [
            "investor name",
            "mobile number",
            "monthly SIP amount",
            "risk profile",
            "portfolio value",
            "KYC status",
            "fund category",
            "advisor booking date",
            "enquiry note",
        ],
        "api_needs": [
            "customer enquiry via backend proxy",
            "advisor booking via backend proxy",
            "portfolio summary via backend proxy",
            "SIP reminder notification via backend proxy",
        ],
        "monetization": ["advisor subscription", "broker admin seat", "investment enquiry lead credits"],
        "preview_summary": "Help investors review mutual fund categories, compare funds, estimate SIP growth, track portfolio summaries, upload KYC documents, complete risk profiles, book advisor calls, and manage SIP reminders without promising returns.",
        "safety_rules": [
            "Show estimated growth only, never guaranteed returns.",
            "Do not create fake investment documents or fake KYC approvals.",
            "Do not provide illegal financial advice, promise profit, or mislead users.",
            "Use advisor guidance, risk profile, portfolio summary, and SIP reminder wording.",
        ],
    },
    "finance_insurance": {
        "keywords": INSURANCE_KEYWORDS,
        "app_name": "Insurance Trust Desk",
        "app_type": "insurance policy, quote, and claim tracker app",
        "target_users": ["insurance advisors", "policy holders", "finance admins", "claim support teams"],
        "core_features": [
            "policy cards",
            "quote cards",
            "claim tracker timeline",
            "advisor contact cards",
            "renewal reminders",
            "customer enquiry form",
            "finance dashboard",
        ],
        "screens": ["Home", "Policy Cards", "Quote Builder", "Claim Tracker", "Advisor Contacts", "Renewals", "Admin Dashboard"],
        "data_needs": ["customer name", "policy type", "premium amount", "claim status", "renewal date", "advisor", "contact number"],
        "api_needs": ["quote submission via backend proxy", "claim status via backend proxy", "advisor notification via backend proxy"],
        "monetization": ["monthly advisor subscription", "policy lead credits", "premium support desk add-on"],
        "preview_summary": "Manage policy cards, quote requests, claim tracker timelines, renewals, advisor contact, and finance admin follow-up in one trust-focused app.",
    },
    "car_detailing": {
        "keywords": ["car", "detailing", "washing", "vehicle", "doorstep", "car wash", "auto detailing"],
        "app_name": "Premium Car Detailing",
        "app_type": "car detailing and washing service booking app",
        "target_users": ["car owners", "premium vehicle owners", "doorstep service customers", "service admins"],
        "core_features": [
            "service packages",
            "doorstep booking",
            "before-after gallery",
            "customer enquiry form",
            "booking calendar",
            "payment status",
            "admin dashboard",
            "daily bookings and revenue",
        ],
        "screens": [
            "Home",
            "Service Packages",
            "Doorstep Booking",
            "Before-After Gallery",
            "Enquiry",
            "Booking Calendar",
            "Payment Status",
            "Admin Dashboard",
        ],
        "data_needs": [
            "customer name",
            "mobile number",
            "vehicle type",
            "service package",
            "booking date",
            "address",
            "payment status",
            "service status",
        ],
        "api_needs": [
            "booking submission via backend proxy",
            "payment status via backend proxy",
            "optional WhatsApp/SMS notification via backend proxy",
        ],
        "monetization": [
            "monthly service business subscription",
            "booking credits",
            "premium service package upsell",
        ],
        "preview_summary": "Book premium car detailing packages, doorstep washing, enquiries, payments, and admin revenue from one mobile-first app.",
    },
    "gym": {
        "keywords": ["gym", "fitness", "trainer", "membership", "workout", "class booking"],
        "app_name": "Fitness Studio",
        "app_type": "fitness studio membership and class booking app",
        "target_users": ["gym owners", "members", "trainers", "front desk admins"],
        "core_features": [
            "membership plans",
            "trainer profiles",
            "class booking",
            "attendance tracking",
            "diet consultation",
            "payment dashboard",
            "member records",
        ],
        "screens": [
            "Home",
            "Membership Plans",
            "Trainer Profiles",
            "Class Booking",
            "Attendance Tracking",
            "Diet Consultation",
            "Payment Dashboard",
            "Member Records",
        ],
        "data_needs": ["member name", "mobile number", "membership plan", "trainer", "class time", "attendance status", "diet consultation notes", "payment status"],
        "api_needs": ["membership signup via backend proxy", "class booking via backend proxy", "payment status via backend proxy", "optional SMS reminders via backend proxy"],
        "monetization": ["monthly gym subscription", "trainer session fees", "diet consultation add-on", "premium membership upsell"],
        "preview_summary": "Run memberships, trainer slots, class bookings, attendance, diet consultations, member records, and payments in one polished fitness studio app.",
    },
    "wedding_venue": {
        "keywords": ["wedding", "venue", "lawn", "event", "haldi", "mehendi", "banquet", "marriage"],
        "app_name": "Wedding Venue Booking",
        "app_type": "wedding venue booking app",
        "target_users": ["couples", "families", "wedding planners", "venue managers"],
        "core_features": [
            "wedding packages",
            "Haldi theme",
            "Mehendi theme",
            "gallery",
            "enquiry form",
            "booking calendar",
            "booking lead capture",
            "package comparison",
            "admin lead dashboard",
            "enquiry management",
            "event date tracking",
        ],
        "screens": ["Home", "Wedding Packages", "Haldi Theme", "Mehendi Theme", "Gallery", "Booking Calendar", "Enquiry Form", "Admin Lead Dashboard", "Package Comparison"],
        "data_needs": [
            "package name",
            "package price",
            "guest capacity",
            "event date",
            "customer name",
            "customer mobile",
            "enquiry message",
            "lead status",
        ],
        "api_needs": [
            "enquiry submission via backend proxy",
            "optional WhatsApp/SMS notification via backend proxy",
            "optional payment gateway via backend proxy",
        ],
        "monetization": [
            "monthly venue subscription",
            "lead credits",
            "premium listing",
            "commission per booking",
        ],
        "preview_summary": "Show wedding packages, Haldi and Mehendi themes, gallery, booking calendar, enquiry form, lead dashboard, and package comparison from one mobile-first venue app.",
    },
    "restaurant": {
        "keywords": ["restaurant", "menu", "table", "order", "food", "tiffin", "cafe"],
        "app_name": "Restaurant Order Hub",
        "app_type": "restaurant ordering app",
        "target_users": ["restaurant owners", "kitchen staff", "customers"],
        "core_features": ["menu catalog", "food ordering", "table booking", "daily specials", "kitchen order queue", "payment status", "customer reorder list"],
        "screens": ["Home", "Menu", "Food Ordering", "Table Booking", "Kitchen Queue", "Payment Dashboard", "Admin Dashboard"],
        "data_needs": ["dish name", "price", "category", "order status", "customer mobile", "table size", "payment status"],
        "api_needs": ["order submission via backend proxy", "table booking via backend proxy", "payment gateway via backend proxy", "optional WhatsApp notification via backend proxy"],
        "monetization": ["monthly restaurant subscription", "online order fees", "featured daily specials", "loyalty add-on"],
        "preview_summary": "Take menu orders, table bookings, kitchen queue updates, payments, and repeat customer requests from one restaurant app.",
    },
    "school": {
        "keywords": ["school", "parents", "homework", "fees", "attendance", "education", "student", "teacher", *TUTOR_KEYWORDS],
        "app_name": "School Parent Connect",
        "app_type": "school, tutor, parent communication, and attendance app",
        "target_users": ["private tutors", "teachers", "parents", "students"],
        "core_features": ["student records", "class and batch schedule", "attendance tracking", "homework updates", "fee status", "parent messages", "class dashboard"],
        "screens": ["Home", "Students", "Classes", "Attendance", "Homework", "Fees", "Parent Messages", "Schedule", "Admin Dashboard"],
        "data_needs": ["student name", "class or batch", "attendance status", "homework", "fee status", "parent mobile", "teacher remarks", "class schedule"],
        "api_needs": ["parent notification via backend proxy", "fee status via backend proxy", "attendance sync via backend proxy", "class schedule sync via backend proxy"],
        "monetization": ["monthly tutor subscription", "per-student communication plan", "premium analytics for educators"],
        "preview_summary": "Give tutors and parents a clear portal for students, classes, attendance, homework, fees, parent messages, schedule, and student records.",
    },
    "retail": {
        "keywords": ["shop", "inventory", "retail", "stock", "store", "catalog", "ecommerce"],
        "app_name": "Retail Inventory Hub",
        "app_type": "retail inventory app",
        "target_users": ["store owners", "sales staff", "inventory managers"],
        "core_features": ["product catalog", "inventory tracking", "low-stock alerts", "sales dashboard", "purchase orders", "customer enquiries", "payment status"],
        "screens": ["Home", "Product Catalog", "Inventory", "Low Stock", "Orders", "Purchase Orders", "Admin Dashboard"],
        "data_needs": ["product name", "SKU", "price", "stock", "supplier", "customer mobile", "payment status"],
        "api_needs": ["inventory sync via backend proxy", "payment gateway via backend proxy", "supplier notification via backend proxy"],
        "monetization": ["monthly store subscription", "premium catalog listing", "multi-branch inventory add-on"],
        "preview_summary": "Track products, low stock, orders, supplier purchases, payments, and customer enquiries from one retail inventory app.",
    },
    "clinic": {
        "keywords": CLINIC_KEYWORDS,
        "app_name": "Clinic Appointment Hub",
        "app_type": "clinic appointment app",
        "target_users": ["doctors", "clinic staff", "patients"],
        "core_features": ["appointment booking", "doctor schedule", "patient records", "queue status", "follow-up reminders", "payment status", "admin dashboard"],
        "screens": ["Home", "Appointments", "Doctor Schedule", "Patients", "Queue Status", "Follow-ups", "Admin Dashboard"],
        "data_needs": ["patient name", "mobile", "appointment date", "doctor", "visit reason", "queue status", "payment status"],
        "api_needs": ["appointment submission via backend proxy", "notification service via backend proxy", "payment status via backend proxy"],
        "monetization": ["monthly clinic subscription", "appointment credits", "follow-up reminder add-on"],
        "preview_summary": "Manage appointment booking, doctor schedules, patient records, queue status, follow-ups, and payments in one clinic app.",
    },
    "agriculture": {
        "keywords": AGRICULTURE_KEYWORDS,
        "app_name": "Farmer Dashboard",
        "app_type": "agriculture farm intelligence and farmer dashboard app",
        "target_users": ["farmers", "FPO teams", "agri advisors", "farm admins"],
        "core_features": [
            "crop health cards",
            "weather cards",
            "mandi price cards",
            "satellite intelligence",
            "farmer profile",
            "farm records",
            "AI chat button",
            "soil and crop advisory",
            "alerts and recommendations",
        ],
        "screens": [
            "Home Dashboard",
            "Crop Health",
            "Weather",
            "Mandi Prices",
            "Satellite Intelligence",
            "Farmer Profile",
            "Farm Records",
            "AI Chat",
            "Admin Dashboard",
        ],
        "data_needs": ["farmer name", "crop", "acreage", "soil health", "weather risk", "mandi price", "farm records", "advisory status"],
        "api_needs": ["weather feed via backend proxy", "mandi price feed via backend proxy", "farm advisory via backend proxy"],
        "monetization": ["monthly farm advisory subscription", "FPO dashboard license", "premium crop intelligence add-on"],
        "preview_summary": "Show a green Farmer Dashboard with crop health, weather, mandi prices, satellite intelligence, farmer profile, farm records, AI chat, and admin recommendations.",
    },
    "government": {
        "keywords": ["government", "civic", "citizen", "officer", "audit", "municipal", "scheme", "department"],
        "app_name": "Civic Service Desk",
        "app_type": "government citizen service and officer dashboard app",
        "target_users": ["citizens", "field officers", "department admins", "audit teams"],
        "core_features": ["role-based cards", "citizen services", "officer dashboard", "audit/status cards", "application tracker", "service request form", "department metrics"],
        "screens": ["Home", "Citizen Services", "Officer Dashboard", "Application Tracker", "Audit Status", "Service Request", "Department Metrics"],
        "data_needs": ["citizen name", "service type", "application ID", "officer", "status", "submission date", "audit note"],
        "api_needs": ["service request via backend proxy", "status sync via backend proxy", "department notification via backend proxy"],
        "monetization": ["department SaaS license", "service desk support plan", "workflow analytics add-on"],
        "preview_summary": "Offer a clean official portal for citizen services, officer review, status tracking, audit cards, and department metrics.",
    },
}


def _detect_domain(text: str) -> str:
    sector_result = route_sector(text)
    sector_id = sector_result["sector_id"]
    return SECTOR_ID_TO_LEGACY_DOMAIN.get(sector_id, "generic")


def _is_tutor_idea(lower_idea: str) -> bool:
    return any(keyword in lower_idea for keyword in TUTOR_KEYWORDS)


def _tutor_product_title_for_idea(lower_idea: str) -> str:
    if "coaching" in lower_idea:
        return "Coaching Class App"
    if "tuition" in lower_idea:
        return "Tuition Teacher App"
    return "Private Tutor App"


def _apply_tutor_plan_language(plan: Dict[str, Any]) -> Dict[str, Any]:
    lower_idea = _clean_text(plan.get("idea")).lower()
    tutor_title = _tutor_product_title_for_idea(lower_idea)
    plan["app_name"] = tutor_title
    plan["product_name"] = tutor_title
    plan["app_type"] = "private tutor, tuition, and coaching class management app"
    plan["target_users"] = ["private tutors", "tuition teachers", "coaching class owners", "students", "parents"]
    plan["core_features"] = [
        "student records",
        "student batches",
        "class schedule",
        "attendance tracking",
        "homework and assignments",
        "fees pending tracker",
        "parent messages",
        "student progress",
        "test results",
        "payment reminders",
        "tutor dashboard",
    ]
    plan["screens"] = [
        "Tutor Dashboard",
        "Students",
        "Student Batches",
        "Class Schedule",
        "Attendance",
        "Homework",
        "Fees Pending",
        "Parent Messages",
        "Student Progress",
        "Test Results",
        "Notes & Assignments",
        "Payment Reminders",
    ]
    plan["data_needs"] = [
        "student name",
        "batch or class",
        "attendance status",
        "homework and notes",
        "fee status",
        "parent mobile",
        "class schedule",
        "test result summary",
    ]
    plan["api_needs"] = [
        "parent notification via backend proxy",
        "fee reminder via backend proxy",
        "attendance sync via backend proxy",
        "class schedule sync via backend proxy",
    ]
    plan["monetization"] = ["monthly tutor subscription", "per-student class management plan", "parent communication add-on"]
    plan["tutor_mode"] = True
    plan["tutor_subdomain"] = "private_tutor"
    plan["preview_summary"] = (
        f"{tutor_title} helps tutors run student batches, class schedules, attendance, homework, fees pending, "
        "parent messages, student progress, test results, notes, and payment reminders from one tutor dashboard."
    )
    return plan


def _domain_from_plan(plan: Dict[str, Any]) -> str:
    explicit_sector = _clean_text(plan.get("sector_id") or plan.get("detected_sector") or plan.get("detectedSector"))
    if explicit_sector:
        return SECTOR_ID_TO_LEGACY_DOMAIN.get(explicit_sector, explicit_sector if explicit_sector in DOMAIN_BLUEPRINTS else "generic")

    explicit_domain = _clean_text(plan.get("detected_domain") or plan.get("detectedIndustry") or plan.get("industry"))
    normalized_explicit = explicit_domain.lower().replace("-", "_").replace(" ", "_")
    if normalized_explicit in DOMAIN_BLUEPRINTS or normalized_explicit == "generic":
        return normalized_explicit
    if normalized_explicit in LEGACY_DOMAIN_TO_SECTOR_ID:
        sector_id = LEGACY_DOMAIN_TO_SECTOR_ID[normalized_explicit]
        return SECTOR_ID_TO_LEGACY_DOMAIN.get(sector_id, normalized_explicit)

    values = []
    for value in plan.values():
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return _detect_domain(" ".join(values))


def create_product_plan(
    idea: str,
    reference_image: Dict[str, Any] | None = None,
    client_metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    clean_idea = _clean_text(idea, "A useful mobile-first product")
    lower_idea = clean_idea.lower()
    reference_image = reference_image or {}
    sector_result = route_sector(clean_idea, reference_image=reference_image, locale_currency_metadata=client_metadata)
    domain = SECTOR_ID_TO_LEGACY_DOMAIN.get(sector_result["sector_id"], "generic")

    if domain in DOMAIN_BLUEPRINTS:
        blueprint = DOMAIN_BLUEPRINTS[domain]
        plan = {
            "idea": clean_idea,
            "detected_domain": domain,
            "sector_id": sector_result["sector_id"],
            "sector_confidence": sector_result["confidence"],
            "sector_reasons": sector_result["reasons"],
            "sector_top_candidates": sector_result["top_candidates"],
            "clarification_needed": sector_result["clarification_needed"],
            "clarification_prompt": sector_result["clarification_prompt"],
            "theme_family": sector_result["theme_family"],
            "layout_family": sector_result["layout_family"],
            "visualThemeFamily": sector_result["theme_family"],
            "layoutVariant": sector_result["layout_family"],
            "app_name": blueprint["app_name"],
            "app_type": blueprint["app_type"],
            "target_users": list(blueprint["target_users"]),
            "core_features": list(blueprint["core_features"]),
            "screens": list(blueprint["screens"]),
            "data_needs": list(blueprint["data_needs"]),
            "api_needs": list(blueprint["api_needs"]),
            "monetization": list(blueprint["monetization"]),
            "preview_summary": blueprint["preview_summary"],
            "clickable_aliases": get_sector_entry(sector_result["sector_id"]).get("clickable_aliases", {}),
            "admin_dashboard_fields": get_sector_entry(sector_result["sector_id"]).get("admin_dashboard_fields", []),
            "safety_rules": get_sector_entry(sector_result["sector_id"]).get("safety_rules", []),
            "forbidden_outputs": get_sector_entry(sector_result["sector_id"]).get("forbidden_outputs", []),
            "next_action": "approve_generate",
        }
        if domain == "school" and _is_tutor_idea(lower_idea):
            plan = _apply_tutor_plan_language(plan)
        plan = _apply_currency_profile(plan, clean_idea, client_metadata)
        plan = _attach_premium_ui_image_concept(plan)
        return _apply_image_guidance(plan, reference_image)

    if sector_result["sector_id"] != "generic_saas":
        template_plan = product_plan_from_sector(sector_result, clean_idea, reference_image)
        template_plan = _apply_currency_profile(template_plan, clean_idea, client_metadata)
        template_plan = _attach_premium_ui_image_concept(template_plan)
        return _apply_image_guidance(template_plan, reference_image)

    app_type = "mobile-first web app"
    target_users = ["busy operators", "team members", "decision makers"]
    data_needs = ["user profiles", "activity records", "dashboard metrics"]
    api_needs = []
    monetization = "subscription-ready with free trial and paid workspace tiers"

    if any(word in lower_idea for word in ["shop", "store", "commerce", "catalog", "retail"]):
        app_type = "commerce operations app"
        target_users = ["store owners", "sales staff", "customers"]
        data_needs = ["products", "orders", "customers", "inventory"]
        api_needs = ["payments", "inventory sync", "order notifications"]
    elif any(word in lower_idea for word in ["crm", "lead", "sales", "customer"]):
        app_type = "CRM dashboard app"
        target_users = ["sales teams", "founders", "account managers"]
        data_needs = ["leads", "pipeline stages", "follow-ups", "customer notes"]
        api_needs = ["email provider", "calendar provider", "CRM import"]
    elif any(word in lower_idea for word in ["farm", "farmer", "crop", "mandi", "agri"]):
        app_type = "agriculture workflow app"
        target_users = ["farmers", "FPO teams", "agri buyers"]
        data_needs = ["farms", "crops", "market prices", "tasks"]
        api_needs = ["weather", "market price feed", "advisory alerts"]
    elif any(word in lower_idea for word in ["food", "restaurant", "tiffin", "menu"]):
        app_type = "food business operations app"
        target_users = ["home chefs", "restaurant teams", "repeat customers"]
        data_needs = ["menus", "orders", "delivery slots", "customer feedback"]
        api_needs = ["WhatsApp notifications", "payment gateway", "delivery status"]
    elif any(word in lower_idea for word in ["student", "school", "course", "learn", "teacher", *TUTOR_KEYWORDS]):
        app_type = "education workflow app"
        target_users = ["students", "teachers", "parents", "private tutors"]
        data_needs = ["students", "classes", "attendance", "homework", "fees", "parent messages"]
        api_needs = ["parent notifications", "calendar reminders", "fee status sync"]
        monetization = "per-classroom or per-student subscription"

    app_name = _title_from_idea(clean_idea)
    core_features = [
        "Guided onboarding for the main workflow",
        "Role-aware dashboard with key metrics",
        "Task cards for daily actions",
        "Review and approval flow before important changes",
    ]
    screens = [
        "Home dashboard",
        "Intake and setup",
        "Workflow board",
        "Reports and insights",
    ]

    plan = {
        "idea": clean_idea,
        "detected_domain": domain,
        "sector_id": sector_result["sector_id"],
        "sector_confidence": sector_result["confidence"],
        "sector_reasons": sector_result["reasons"],
        "sector_top_candidates": sector_result["top_candidates"],
        "clarification_needed": sector_result["clarification_needed"],
        "clarification_prompt": sector_result["clarification_prompt"],
        "theme_family": sector_result["theme_family"],
        "layout_family": sector_result["layout_family"],
        "visualThemeFamily": sector_result["theme_family"],
        "layoutVariant": sector_result["layout_family"],
        "app_name": app_name,
        "app_type": app_type,
        "target_users": target_users,
        "core_features": core_features,
        "screens": screens,
        "data_needs": data_needs,
        "api_needs": api_needs,
        "monetization": monetization,
        "preview_summary": (
            f"{app_name} is a {app_type} for {', '.join(target_users[:2])}. "
            "The first prototype includes a mobile dashboard, feature cards, "
            "screen sections, mock actions, and placeholder data."
        ),
        "clickable_aliases": get_sector_entry(sector_result["sector_id"]).get("clickable_aliases", {}),
        "admin_dashboard_fields": get_sector_entry(sector_result["sector_id"]).get("admin_dashboard_fields", []),
        "safety_rules": get_sector_entry(sector_result["sector_id"]).get("safety_rules", []),
        "forbidden_outputs": get_sector_entry(sector_result["sector_id"]).get("forbidden_outputs", []),
        "next_action": "approve_generate",
    }
    plan = _apply_currency_profile(plan, clean_idea, client_metadata)
    plan = _attach_premium_ui_image_concept(plan)
    return _apply_image_guidance(plan, reference_image)


def normalize_product_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    idea = _clean_text(plan.get("idea") or plan.get("source_idea") or plan.get("preview_summary") or plan.get("product_name"))
    domain_text = " ".join(
        str(item)
        for value in plan.values()
        for item in (value if isinstance(value, list) else [value])
    )
    idea_domain = _detect_domain(idea) if idea else "generic"
    plan_domain = _domain_from_plan(plan)
    reference_image = normalize_reference_image_metadata(plan)
    if not reference_image and isinstance(plan.get("reference_image"), dict):
        reference_image = normalize_reference_image_metadata({"referenceImage": plan.get("reference_image")})
    normalized = create_product_plan(
        idea if idea_domain != "generic" else domain_text or idea or "Generated app prototype",
        reference_image=reference_image,
        client_metadata=plan,
    )
    can_preserve_plan_fields = idea_domain == "generic" or idea_domain == plan_domain

    if can_preserve_plan_fields:
        normalized["app_name"] = _clean_text(plan.get("app_name") or plan.get("product_name"), normalized["app_name"])
        normalized["app_type"] = _clean_text(plan.get("app_type") or plan.get("category"), normalized["app_type"])
        normalized["target_users"] = _clean_list(plan.get("target_users"), normalized["target_users"])
        normalized["core_features"] = _clean_list(plan.get("core_features"), normalized["core_features"])
        normalized["screens"] = _clean_list(plan.get("screens"), normalized["screens"])
        normalized["data_needs"] = _clean_list(plan.get("data_needs"), normalized["data_needs"])
        normalized["api_needs"] = _clean_list(plan.get("api_needs"), normalized["api_needs"])
        normalized["monetization"] = _clean_list(plan.get("monetization"), normalized["monetization"] if isinstance(normalized["monetization"], list) else [normalized["monetization"]])
        normalized["preview_summary"] = _clean_text(plan.get("preview_summary"), normalized["preview_summary"])

    normalized["next_action"] = "approve_generate"
    if plan.get("tutor_mode"):
        normalized["tutor_mode"] = True
    if _clean_text(plan.get("tutor_subdomain")):
        normalized["tutor_subdomain"] = _clean_text(plan.get("tutor_subdomain"))
    normalized = _apply_currency_profile(normalized, f"{idea} {domain_text}", plan)
    normalized = _attach_premium_ui_image_concept(normalized)
    if reference_image:
        normalized = _apply_image_guidance(normalized, reference_image)
    return normalized


def _render_list(items: List[str]) -> str:
    return "\n".join(f"<li>{html.escape(item)}</li>" for item in items)


def _render_feature_cards(features: List[str]) -> str:
    cards = []
    for index, feature in enumerate(features, start=1):
        cards.append(
            f"""
          <article class="feature-card">
            <span>0{index}</span>
            <h3>{html.escape(feature)}</h3>
            <p>Mock workflow ready for prototype review and future backend wiring.</p>
          </article>"""
        )
    return "\n".join(cards)


def _render_screen_sections(screens: List[str]) -> str:
    sections = []
    for screen in screens:
        safe_screen = html.escape(screen)
        sections.append(
            f"""
          <section class="screen-section">
            <div>
              <span class="screen-kicker">Screen</span>
              <h2>{safe_screen}</h2>
              <p>Static prototype section with representative controls and placeholder content.</p>
            </div>
            <button type="button">Open {safe_screen}</button>
          </section>"""
        )
    return "\n".join(sections)


def _render_image_guided_reference(plan: Dict[str, Any]) -> str:
    if not plan.get("image_guided"):
        return ""

    reference = plan.get("reference_image") if isinstance(plan.get("reference_image"), dict) else {}
    source_label = html.escape(
        _clean_text(
            reference.get("name")
            or reference.get("fileName")
            or reference.get("sourcePath")
            or reference.get("path"),
            "Reference image metadata",
        )
    )
    visual_summary = html.escape(
        _clean_text(
            plan.get("visual_reference_summary"),
            "This preview uses reference metadata as safe layout guidance. No image bytes, OCR, or pixel analysis are processed.",
        )
    )
    priorities = _clean_list(
        plan.get("interface_design_priorities"),
        [
            "Reference-inspired mobile first screen",
            "App-like hierarchy and spacing",
            "Compact cards and clear bottom actions",
        ],
    )

    return f"""
    <section class="content-block image-guided-panel">
      <div class="section-heading">
        <span class="eyebrow">Image-guided preview</span>
        <h2>Reference-inspired mobile interface</h2>
      </div>
      <div class="image-guided-grid">
        <article>
          <span>Reference</span>
          <strong>{source_label}</strong>
          <p>{visual_summary}</p>
        </article>
        <article>
          <span>Design scaffold</span>
          <ul>{_render_list(priorities)}</ul>
        </article>
      </div>
    </section>"""


def _render_metric_cards(domain: str, plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    blueprint_cards = _blueprint_list(plan, "dashboard_cards")
    if blueprint_cards:
        sector_values = {
            "school": {
                "attendance": "12",
                "homework due": "8",
                "homework": "8",
                "parent messages": "249",
                "messages": "249",
                "class notices": "38",
                "notices": "38",
                "fees pending": f"{money['feesPending']} fees",
                "fees": f"{money['feesPending']} fees",
            },
            "agriculture": {
                "crop health": "86%",
                "today weather": "31C",
                "weather": "31C",
                "mandi price": money["mandiRate"],
                "mandi rate": money["mandiRate"],
                "farm tasks": "8",
                "expected income": money["profitEstimate"],
            },
        }.get(domain, {})
        generic_values = ["12", "8", "96%", "38", "24"]
        metrics = []
        for index, label in enumerate(blueprint_cards):
            normalized_label = str(label).strip().lower()
            value = sector_values.get(normalized_label, generic_values[index % len(generic_values)])
            metrics.append((label, value))
    else:
        metrics = {
            "car_detailing": [
                ("Daily Bookings", "18"),
                ("Revenue", money["revenueShort"]),
                ("Payment Status", "7 pending"),
                ("Customer Leads", "31"),
            ],
            "gym": [("Member Records", "286"), ("Class Bookings", "34"), ("Attendance", "91%"), ("Payment Dashboard", money["monthlyRevenue"])],
            "wedding_venue": [
                ("Total Enquiries", "128"),
                ("Booking Leads", "24"),
                ("Lawn Bookings", "17"),
                ("Package Revenue", money["weddingPipeline"]),
            ],
            "restaurant": [("Today Orders", "86"), ("Kitchen Queue", "12"), ("Table Bookings", "18"), ("Revenue", money["dailyRevenue"])],
            "school": [("Attendance", "12"), ("Homework Due", "8"), ("Parent Messages", "249"), ("Class Notices", "38")],
            "retail": [("Total Products", "312"), ("Low Stock", "14"), ("Today Orders", "57"), ("Revenue", money["retailRevenue"])],
            "clinic": [("Appointments", "42"), ("Queue Status", "8 waiting"), ("Follow-ups", "16"), ("Open Slots", "11")],
            "mutual_fund_advisor": [("SIP Amount", f"{money['sipAmount']}/mo"), ("Portfolio Value", money["portfolioValue"]), ("Advisory Leads", "28"), ("KYC Pending", "12")],
            "finance_insurance": [("Active Policies", "248"), ("Quote Requests", "31"), ("Claims Open", "12"), ("Renewals", "44")],
            "agriculture": [("Crop Health", "86%"), ("Today Weather", "31C"), ("Mandi Price", money["mandiRate"]), ("Farm Tasks", "8")],
            "government": [("Citizen Services", "74"), ("Officer Reviews", "18"), ("Audit Status", "96%"), ("Pending Cases", "11")],
        }.get(domain, [("Workflow Items", "1,248"), ("Approvals Due", "36"), ("New Requests", "18"), ("Completion", "82%")])

    return "\n".join(
        f'<article data-screen="{html.escape(_screen_slug(label))}"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></article>'
        for label, value in metrics
    )


def _render_package_cards(items: List[tuple[str, str, str]], button_label: str) -> str:
    return "\n".join(
        f"""
        <article class="package-card">
          <span>{html.escape(price)}</span>
          <h3>{html.escape(name)}</h3>
          <p>{html.escape(detail)}</p>
          <button type="button">{html.escape(button_label)}</button>
        </article>"""
        for name, price, detail in items
    )


def _render_gallery_tiles(items: List[str]) -> str:
    return "\n".join(f"<span>{html.escape(item)}</span>" for item in items)


def _render_status_rows(rows: List[tuple[str, str, str]]) -> str:
    return "\n".join(
        f"<li><strong>{html.escape(name)}</strong><span>{html.escape(detail)}</span><em>{html.escape(status)}</em></li>"
        for name, detail, status in rows
    )


def _screen_slug(label: str) -> str:
    return _slugify(label).replace("-", "_")


def _display_label(value: Any, fallback: str = "") -> str:
    text = _clean_text(value, fallback).replace("_", " ").replace("-", " ")
    if not text:
        return fallback
    preserved = {"ai", "api", "aum", "gst", "id", "kyc", "pod", "sip", "sla", "sku"}
    words = []
    for word in text.split():
        stripped = word.strip()
        if stripped.lower() in preserved:
            words.append(stripped.upper())
        elif stripped.isupper() and len(stripped) > 1:
            words.append(stripped)
        else:
            words.append(stripped[:1].upper() + stripped[1:])
    return " ".join(words)


def _blueprint_ui(plan: Dict[str, Any]) -> Dict[str, Any]:
    value = plan.get("blueprint_ui")
    return value if isinstance(value, dict) else {}


def _blueprint_list(plan: Dict[str, Any], key: str, fallback: Iterable[str] = ()) -> List[str]:
    blueprint = _blueprint_ui(plan)
    return [_display_label(item) for item in _clean_list(blueprint.get(key), fallback)]


def _blueprint_text(plan: Dict[str, Any], key: str, fallback: str = "") -> str:
    blueprint = _blueprint_ui(plan)
    return _clean_text(blueprint.get(key), fallback)


def _sector_key_from_plan(plan: Dict[str, Any]) -> str:
    blueprint = _blueprint_ui(plan)
    sector_key = _clean_text(
        blueprint.get("sector_key")
        or plan.get("sector_id")
        or plan.get("detected_sector")
        or plan.get("detected_domain")
        or plan.get("theme_family"),
        "generic_saas",
    )
    if sector_key in LEGACY_DOMAIN_TO_SECTOR_ID:
        return LEGACY_DOMAIN_TO_SECTOR_ID[sector_key]
    return sector_key


def _sector_ui_profile(plan: Dict[str, Any]) -> Dict[str, Any]:
    return get_sector_ui_profile(_sector_key_from_plan(plan))


def _premium_section(profile: Dict[str, Any], key: str, fallback: str) -> str:
    sections = profile.get("premium_sections") if isinstance(profile.get("premium_sections"), dict) else {}
    return _clean_text(sections.get(key), fallback)


def _action_description(profile: Dict[str, Any], action: str) -> str:
    descriptions = profile.get("action_descriptions") if isinstance(profile.get("action_descriptions"), dict) else {}
    exact = _clean_text(descriptions.get(action))
    if exact:
        return exact
    normalized = action.strip().lower()
    for label, description in descriptions.items():
        if str(label).strip().lower() == normalized:
            return _clean_text(description)
    return f"Open the {action.lower()} workflow with sector-ready fields and next steps."


def _render_blueprint_sections(plan: Dict[str, Any]) -> str:
    if not _blueprint_ui(plan):
        return ""

    profile = _sector_ui_profile(plan)
    actions = _blueprint_list(plan, "primary_actions")
    sample_records = _blueprint_list(plan, "sample_records")
    guidance = _blueprint_text(plan, "empty_state_guidance")
    trust_notes = _blueprint_list(plan, "trust_and_safety_notes")
    domain_terms = _blueprint_list(plan, "domain_terms")

    action_cards = "\n".join(
        f"""
        <article class="feature-card premium-action-card" data-screen="{html.escape(_screen_slug(action))}">
          <span>{html.escape(_display_label(profile.get("action_badge"), "Workflow"))}</span>
          <h3>{html.escape(action)}</h3>
          <p>{html.escape(_action_description(profile, action))}</p>
        </article>"""
        for action in actions
    )
    record_cards = "\n".join(
        f"""
        <article class="package-card premium-record-card" data-screen="{html.escape(_screen_slug(record))}">
          <span>{html.escape(_premium_section(profile, "records_kicker", "Sample record"))}</span>
          <h3>{html.escape(record)}</h3>
          <p>{html.escape(_premium_section(profile, "records_summary", "Representative data row from the selected sector blueprint."))}</p>
          <button type="button" data-screen="{html.escape(_screen_slug(record))}">Open {html.escape(record)}</button>
        </article>"""
        for record in sample_records
    )

    guidance_items = []
    if guidance:
        guidance_items.append(f"<li><strong>Empty state</strong><span>{html.escape(guidance)}</span></li>")
    guidance_items.extend(
        f"<li><strong>Safety note</strong><span>{html.escape(note)}</span></li>"
        for note in trust_notes
    )
    if domain_terms:
        guidance_items.append(
            f"<li><strong>Domain terms</strong><span>{html.escape(', '.join(domain_terms))}</span></li>"
        )

    sections = []
    if action_cards:
        sections.append(
            f"""
    <section class="content-block blueprint-panel">
      <div class="section-heading">
        <span class="eyebrow">{html.escape(_premium_section(profile, "actions_kicker", "Blueprint actions"))}</span>
        <h2>{html.escape(_premium_section(profile, "actions_title", "Primary workflows from the sector blueprint"))}</h2>
      </div>
      <div class="feature-grid">{action_cards}</div>
    </section>"""
        )
    if record_cards:
        sections.append(
            f"""
    <section class="content-block blueprint-panel">
      <div class="section-heading">
        <span class="eyebrow">{html.escape(_premium_section(profile, "records_kicker", "Sample records"))}</span>
        <h2>{html.escape(_premium_section(profile, "records_title", "Realistic seed examples for this preview"))}</h2>
      </div>
      <div class="package-grid">{record_cards}</div>
    </section>"""
        )
    if guidance_items:
        sections.append(
            f"""
    <section class="content-block blueprint-panel">
      <div class="section-heading">
        <span class="eyebrow">{html.escape(_premium_section(profile, "guidance_kicker", "Blueprint guidance"))}</span>
        <h2>{html.escape(_premium_section(profile, "guidance_title", "Empty state, trust, and domain language"))}</h2>
      </div>
      <ul class="status-list">{''.join(guidance_items)}</ul>
    </section>"""
        )

    return "\n".join(sections)


def _domain_screen_labels(domain: str, plan: Dict[str, Any]) -> List[str]:
    blueprint_screens = _blueprint_list(plan, "must_have_screens")
    if blueprint_screens:
        return blueprint_screens

    labels = {
        "car_detailing": [
            "Dashboard",
            "Service Packages",
            "Doorstep Booking",
            "Before-After Gallery",
            "Booking Calendar",
            "Payment Status",
            "Admin Dashboard",
        ],
        "gym": [
            "Dashboard",
            "Membership Plans",
            "Trainer Profiles",
            "Class Booking",
            "Attendance Tracking",
            "Diet Consultation",
            "Payment Dashboard",
        ],
        "wedding_venue": [
            "Dashboard",
            "Wedding Packages",
            "Haldi Theme",
            "Mehendi Theme",
            "Gallery",
            "Booking Calendar",
            "Enquiry Form",
            "Admin Lead Dashboard",
        ],
        "restaurant": [
            "Dashboard",
            "Menu",
            "Food Ordering",
            "Table Booking",
            "Kitchen Queue",
            "Payment Dashboard",
            "Admin Dashboard",
        ],
        "clinic": [
            "Dashboard",
            "Appointments",
            "Doctor Schedule",
            "Patients",
            "Queue Status",
            "Follow-ups",
            "Admin Dashboard",
        ],
        "school": [
            "Dashboard",
            "Parent Portal",
            "Attendance",
            "Homework",
            "Fees",
            "Parent Notices",
            "Exam Results",
            "Teacher Contact",
        ],
        "retail": [
            "Dashboard",
            "Product Catalog",
            "Inventory",
            "Low Stock",
            "Sales Records",
            "Revenue Dashboard",
            "Admin Dashboard",
        ],
        "finance_insurance": [
            "Dashboard",
            "Policy Cards",
            "Quote Builder",
            "Claim Tracker",
            "Advisor Contacts",
            "Renewals",
            "Admin Dashboard",
        ],
        "mutual_fund_advisor": [
            "Dashboard",
            "Mutual Fund Categories",
            "Compare Funds",
            "SIP Calculator",
            "Portfolio Tracker",
            "KYC Upload",
            "Risk Profile",
            "Advisor Booking",
            "SIP Reminders",
            "Admin Dashboard",
        ],
        "agriculture": [
            "Dashboard",
            "Crop Health",
            "Weather",
            "Mandi Prices",
            "Satellite Intelligence",
            "Farmer Profile",
            "Farm Records",
            "AI Chat",
            "Admin Dashboard",
        ],
        "government": [
            "Dashboard",
            "Citizen Services",
            "Officer Dashboard",
            "Application Tracker",
            "Audit Status",
            "Service Request",
            "Department Metrics",
        ],
    }
    if domain in labels:
        return labels[domain]
    screens = [screen for screen in plan["screens"] if screen.lower() != "home"]
    return ["Dashboard", *screens[:7]]


def _render_screen_nav(labels: List[str]) -> str:
    return "\n".join(
        f'<button type="button" data-screen="{html.escape(_screen_slug(label))}">{html.escape(label)}</button>'
        for label in labels
    )


def _strip_universal_screen_config(script: str) -> str:
    start_marker = "const SCREEN_CONFIG = {\n"
    end_marker = "SCREEN_CONFIG.generic = {"
    start = script.find(start_marker)
    end = script.find(end_marker)
    if start == -1 or end == -1 or end <= start:
        return script
    return f"{script[:start]}const SCREEN_CONFIG = {{}};\n\n{script[end:]}"


def _strip_inactive_domain_aliases(script: str, domain: str) -> str:
    if domain == "agriculture":
        return script
    agriculture_alias_terms = (
        "crop",
        "mandi",
        "satellite",
        "farmer",
        "farm_records",
        "view_field",
        "save_update",
    )
    kept_lines = []
    for line in script.splitlines():
        normalized = line.strip().lower()
        if any(term in normalized for term in agriculture_alias_terms):
            continue
        kept_lines.append(line)
    return "\n".join(kept_lines) + ("\n" if script.endswith("\n") else "")


def _theme_hash_key(plan: Dict[str, Any], app_id: str, domain: str) -> str:
    reference = plan.get("reference_image") if isinstance(plan.get("reference_image"), dict) else {}
    reference_bits = " ".join(
        _clean_text(reference.get(key))
        for key in ("name", "fileName", "layoutHint", "visualNotes", "source")
        if reference.get(key)
    )
    return "|".join(
        [
            app_id,
            domain,
            _clean_text(plan.get("app_name")),
            _clean_text(plan.get("app_type")),
            _clean_text(plan.get("preview_summary")),
            reference_bits,
        ]
    )


def _stable_index(seed: str, count: int) -> int:
    if count <= 0:
        return 0
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % count


def _currency_sample_values(plan: Dict[str, Any]) -> Dict[str, str]:
    code = _clean_text(plan.get("currency_code"), "USD").upper()
    symbol = _clean_text(plan.get("currency_symbol"), "$")
    if code == "INR":
        return {
            "basic": f"{symbol}499",
            "premium": f"{symbol}2,499",
            "serviceSmall": f"{symbol}29",
            "serviceMedium": f"{symbol}79",
            "serviceLarge": f"{symbol}249",
            "revenueShort": f"{symbol}4.6L",
            "revenueWeekly": f"{symbol}4.6L this week",
            "monthlyRevenue": f"{symbol}12.4L",
            "dailyRevenue": f"{symbol}6.8L",
            "settled": f"{symbol}5.9L",
            "collections": f"{symbol}2.8L",
            "retailRevenue": f"{symbol}8.2L",
            "weddingPipeline": f"{symbol}38L pipeline",
            "weddingPackage": f"{symbol}2.49L",
            "weddingPremium": f"{symbol}4.99L",
            "weddingRoyal": f"{symbol}8.99L",
            "mandiRate": f"{symbol}4,200/q",
            "mandiSoybean": f"{symbol}5,100/q",
            "inputCost": f"{symbol}1,250",
            "dieselCost": f"{symbol}3,800",
            "profitEstimate": f"{symbol}82,000",
            "sipAmount": f"{symbol}5,000",
            "monthlyInvestment": f"{symbol}10,000",
            "portfolioValue": f"{symbol}4.6L",
            "feesPending": f"{symbol}38k",
        }
    if code == "AED":
        prefix = "AED "
    elif code == "SAR":
        prefix = "SAR "
    else:
        prefix = symbol
    return {
        "basic": f"{prefix}29",
        "premium": f"{prefix}249",
        "serviceSmall": f"{prefix}29",
        "serviceMedium": f"{prefix}79",
        "serviceLarge": f"{prefix}249",
        "revenueShort": f"{prefix}4.6k",
        "revenueWeekly": f"{prefix}4.6k this week",
        "monthlyRevenue": f"{prefix}12.4k",
        "dailyRevenue": f"{prefix}6.8k",
        "settled": f"{prefix}5.9k",
        "collections": f"{prefix}2.8k",
        "retailRevenue": f"{prefix}8.2k",
        "weddingPipeline": f"{prefix}38k pipeline",
        "weddingPackage": f"{prefix}2.49k",
        "weddingPremium": f"{prefix}4.99k",
        "weddingRoyal": f"{prefix}8.99k",
        "mandiRate": f"{prefix}42/q",
        "mandiSoybean": f"{prefix}51/q",
        "inputCost": f"{prefix}125",
        "dieselCost": f"{prefix}380",
        "profitEstimate": f"{prefix}820",
        "sipAmount": f"{prefix}100",
        "monthlyInvestment": f"{prefix}250",
        "portfolioValue": f"{prefix}4.6k",
        "feesPending": f"{prefix}38k",
    }


def select_visual_theme(plan: Dict[str, Any], app_id: str) -> Dict[str, Any]:
    domain = _domain_from_plan(plan)
    source_text = " ".join(
        [
            domain,
            _clean_text(plan.get("app_name")),
            _clean_text(plan.get("app_type")),
            _clean_text(plan.get("preview_summary")),
            " ".join(_clean_list(plan.get("core_features"), [])),
        ]
    ).lower()
    reference = plan.get("reference_image") if isinstance(plan.get("reference_image"), dict) else {}
    image_metadata_text = " ".join(
        _clean_text(reference.get(key))
        for key in ("name", "fileName", "layoutHint", "visualNotes", "source")
        if reference.get(key)
    ).lower()
    combined_text = f"{source_text} {image_metadata_text}"

    requested_family = _clean_text(plan.get("theme_family") or plan.get("visualThemeFamily"))
    family = requested_family if requested_family in THEME_FAMILIES else "generic-modern-saas"
    if not requested_family:
        for candidate, config in THEME_FAMILIES.items():
            if domain in config["domains"]:
                family = candidate
                break
        else:
            for candidate, config in THEME_FAMILIES.items():
                if any(re.search(rf"\b{re.escape(keyword)}\b", combined_text) for keyword in config["keywords"]):
                    family = candidate
                    break

    layout_pool = {
        "finance_insurance": ["timeline-tracker", "hero-stat-stack", "card-first-dashboard"],
        "mutual_fund_advisor": ["hero-stat-stack", "card-first-dashboard", "admin-metrics-grid"],
        "car_detailing": ["gallery-first-showcase", "split-action-dashboard", "hero-feature-grid"],
        "gym": ["hero-feature-grid", "card-first-dashboard", "admin-metrics-grid"],
        "wedding_venue": ["gallery-first-showcase", "hero-feature-grid", "split-action-dashboard"],
        "school": ["card-first-dashboard", "hero-stat-stack", "admin-metrics-grid"],
        "clinic": ["timeline-tracker", "card-first-dashboard", "hero-stat-stack"],
        "restaurant": ["gallery-first-showcase", "split-action-dashboard", "card-first-dashboard"],
        "retail": ["admin-metrics-grid", "card-first-dashboard", "hero-stat-stack"],
        "agriculture": ["hero-stat-stack", "admin-metrics-grid", "card-first-dashboard"],
        "government": ["timeline-tracker", "admin-metrics-grid", "card-first-dashboard"],
        "generic": LAYOUT_VARIANTS,
    }.get(domain, LAYOUT_VARIANTS)
    requested_layout = _clean_text(plan.get("layout_family") or plan.get("layoutVariant"))
    seed = _theme_hash_key(plan, app_id, domain)
    layout_variant = requested_layout if requested_layout in LAYOUT_VARIANTS else layout_pool[_stable_index(seed, len(layout_pool))]
    density = ["compact", "balanced", "spacious"][_stable_index(f"{seed}|density", 3)]
    radius = ["sharp", "soft", "rounded"][_stable_index(f"{seed}|cards", 3)]

    return {
        "family": family,
        "class_name": f"theme-family-{family}",
        "layout_variant": layout_variant,
        "layout_class": f"layout-{layout_variant}",
        "card_style": radius,
        "density": density,
        "detected_industry": domain,
        "style_notes": THEME_FAMILIES[family]["style"],
        "image_guided_design_note": (
            "Reference metadata influenced visual rhythm, hierarchy, and spacing; no image bytes, OCR, or pixel analysis were used."
            if plan.get("image_guided")
            else ""
        ),
    }


def _domain_theme_class(domain: str, theme: Dict[str, Any] | None = None) -> str:
    if theme:
        return " ".join(
            [
                html.escape(theme["class_name"]),
                html.escape(theme["layout_class"]),
                f"card-style-{html.escape(theme['card_style'])}",
                f"density-{html.escape(theme['density'])}",
            ]
        )
    return f"theme-{domain.replace('_', '-')}" if domain != "generic" else "theme-generic"


def _render_app_visual(domain: str, profile: Dict[str, Any] | None = None) -> str:
    visual = {
        "car_detailing": ("Detail route", "Ceramic SUV", "Paid", ["Foam wash", "Interior reset", "Coating prep"]),
        "gym": ("Tonight", "HIIT 7 PM", "34 booked", ["Strength", "Yoga", "Diet consult"]),
        "wedding_venue": ("Date hold", "Royal Lawn", "Visit booked", ["Haldi", "Mehendi", "Reception"]),
        "restaurant": ("Kitchen", "Order #2184", "8 min", ["Thali", "Table 6", "Paid"]),
        "clinic": ("Queue", "Dr. Kapoor", "3 slots", ["Checked in", "Follow-up", "Invoice"]),
        "school": ("Parent view", "Class 5A", "92%", ["Homework", "Fees", "Notice"]),
        "retail": ("Stock desk", "Backpack", "12 left", ["Low stock", "Sales", "PO sent"]),
        "finance_insurance": ("Policy desk", "Claim timeline", "12 open", ["Quote", "Renewal", "Advisor"]),
        "mutual_fund_advisor": ("SIP desk", "Portfolio summary", "₹4.6L", ["Compare", "Risk", "KYC"]),
        "agriculture": ("Farm view", "Crop health", "86%", ["Weather", "Mandi", "Advisory"]),
        "government": ("Civic desk", "Service status", "96%", ["Citizen", "Officer", "Audit"]),
    }.get(domain, ("Workspace", "Live preview", "82%", ["Intake", "Review", "Dashboard"]))
    title, focus, status, chips = visual
    if profile:
        title = _clean_text(profile.get("hero_kicker"), title)
        focus = _clean_text(profile.get("hero_visual_title"), focus)
        chips = _clean_list(profile.get("sample_component_labels"), chips)
    chip_markup = "".join(f"<span>{html.escape(chip)}</span>" for chip in chips)
    return f"""
        <aside class="hero-visual" aria-label="Generated app visual preview">
          <div class="phone-mock">
            <div class="phone-top"><span>{html.escape(title)}</span><strong>{html.escape(status)}</strong></div>
            <div class="phone-focus">
              <small>Featured screen</small>
              <strong>{html.escape(focus)}</strong>
            </div>
            <div class="phone-chip-grid">{chip_markup}</div>
            <div class="phone-bar"><span></span><span></span><span></span></div>
          </div>
        </aside>"""


def _render_form_fields(fields: List[tuple[str, str]]) -> str:
    return "\n".join(
        f"<label>{html.escape(label)}<input value=\"{html.escape(value)}\" readonly></label>"
        for label, value in fields
    )


def _render_operations_section(
    eyebrow: str,
    title: str,
    form_title: str,
    form_fields: List[tuple[str, str]],
    button_label: str,
    admin_eyebrow: str,
    admin_title: str,
    rows: List[tuple[str, str, str]],
) -> str:
    return f"""
    <section class="content-block enquiry-admin-grid" aria-label="{html.escape(title)}">
      <div class="workflow-label">{html.escape(title)}</div>
      <article class="enquiry-card">
        <span class="eyebrow">{html.escape(eyebrow)}</span>
        <h2>{html.escape(form_title)}</h2>
        {_render_form_fields(form_fields)}
        <button type="button">{html.escape(button_label)}</button>
      </article>
      <article class="admin-card">
        <span class="eyebrow">{html.escape(admin_eyebrow)}</span>
        <h2>{html.escape(admin_title)}</h2>
        <ul>{_render_status_rows(rows)}</ul>
      </article>
    </section>"""


def _render_wedding_venue_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    packages = [
        ("Haldi Theme", money["weddingPackage"], "Outdoor lawn booking, marigold decor, turmeric color palette, and welcome drinks"),
        ("Mehendi Theme", money["weddingPremium"], "Stage seating, artist corner, photo wall, and family lounge setup"),
        ("Royal Wedding", money["weddingRoyal"], "Full venue, banquet package, premium decor, catering coordination, and VIP support desk"),
    ]
    package_cards = _render_package_cards(packages, "Compare Package")
    leads = [
        ("Aarav & Meera", "Royal Wedding", "Booking Lead"),
        ("Kapoor Family", "Banquet Package", "Date hold pending"),
        ("Nisha Events", "Haldi Theme", "Quotation sent"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Wedding Packages</span>
        <h2>Package Comparison for lawn and banquet events</h2>
      </div>
      <div class="package-grid">{package_cards}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Gallery</span>
        <h2>Haldi, Mehendi, and wedding lawn showcase</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Haldi Theme", "Mehendi Theme", "Lawn Booking", "Banquet Package"])}
      </div>
    </section>

    {_render_operations_section(
        "Enquiry Form",
        "Booking Calendar",
        "Capture event enquiries",
        [("Customer name", "Priya Sharma"), ("Event date", "24 Feb 2027"), ("Guest capacity", "300 guests")],
        "Send Enquiry",
        "Admin Lead Dashboard",
        "Booking calendar and lead status",
        leads,
    )}"""


def _render_car_detailing_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    packages = [
        ("Express Wash", money["serviceSmall"], "Exterior foam wash, tyre shine, and quick interior vacuum"),
        ("Interior Deep Clean", money["serviceMedium"], "Seats, mats, dashboard, odor treatment, and stain care"),
        ("Premium Ceramic Detail", money["serviceLarge"], "Paint polish, ceramic coating prep, and premium finish protection"),
    ]
    package_cards = _render_package_cards(packages, "Book Package")
    bookings = [
        ("Doorstep Booking", "SUV ceramic detail", "Today 4:30 PM"),
        ("Booking Calendar", "Interior deep clean", "Tomorrow 10:00 AM"),
        ("Payment Status", "Express wash", "Paid"),
        ("Admin Dashboard", "Daily Bookings", f"Revenue {money['revenueShort']}"),
        ("Customer Leads", "Ceramic detail enquiry", "Call back"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Service Packages</span>
        <h2>Premium car detailing packages</h2>
      </div>
      <div class="package-grid">{package_cards}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Before-After Gallery</span>
        <h2>Show visible detailing results</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Exterior Shine", "Interior Reset", "Wheel Detail", "Ceramic Finish"])}
      </div>
    </section>

    {_render_operations_section(
        "Doorstep Booking",
        "Booking Calendar",
        "Customer enquiry form",
        [("Customer name", "Rohan Mehta"), ("Vehicle type", "Premium SUV"), ("Booking date", "Today, 4:30 PM")],
        "Submit Booking",
        "Admin Dashboard",
        "Daily bookings, revenue, and leads",
        bookings,
    )}"""


def _render_gym_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    plans = [
        ("Starter Plan", f"{money['basic']}/mo", "Gym floor access, progress check-in, and monthly attendance summary"),
        ("Transformation Plan", f"{money['serviceMedium']}/mo", "Personal trainer profile match, class booking, and diet consultation"),
        ("Elite Coaching", f"{money['serviceLarge']}/mo", "Premium trainer sessions, weekly diet review, and payment dashboard access"),
    ]
    rows = [
        ("Ananya Rao", "Transformation Plan", "Paid"),
        ("Karan Singh", "HIIT class booking", "Today 7 PM"),
        ("Neha Patel", "Diet consultation", "Follow-up due"),
        ("Front Desk", "Attendance Tracking", "91% this week"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Membership Plans</span>
        <h2>Fitness studio plans and trainer-led upsells</h2>
      </div>
      <div class="package-grid">{_render_package_cards(plans, "Choose Plan")}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Trainer Profiles</span>
        <h2>Class booking and coaching preview</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Strength Coach", "Yoga Trainer", "HIIT Classes", "Diet Consultation"])}
      </div>
    </section>

    {_render_operations_section(
        "Class Booking",
        "Member Records",
        "Book a fitness session",
        [("Member name", "Ananya Rao"), ("Trainer", "Riya Kapoor"), ("Class time", "Today, 7:00 PM")],
        "Book Class",
        "Payment Dashboard",
        "Attendance, payments, and member records",
        rows,
    )}"""


def _render_restaurant_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    menu_items = [
        ("Chef Thali", money["serviceSmall"], "Best-selling lunch combo with dal, curry, rice, roti, and dessert"),
        ("Paneer Tikka Bowl", money["basic"], "Fast ordering item with add-on beverage and spice preference"),
        ("Family Dinner Pack", money["serviceMedium"], "Four-person bundle with payment status and kitchen queue tracking"),
    ]
    rows = [
        ("Order #2184", "Family Dinner Pack", "Preparing"),
        ("Table Booking", "6 guests at 8:30 PM", "Confirmed"),
        ("Payment Status", "Chef Thali x 4", "Paid"),
        ("Kitchen Queue", "Paneer Tikka Bowl", "8 min"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Menu Catalog</span>
        <h2>Food ordering with realistic menu cards</h2>
      </div>
      <div class="package-grid">{_render_package_cards(menu_items, "Add to Order")}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Daily Specials</span>
        <h2>Customer-facing food sections</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Lunch Combos", "Dinner Packs", "Cafe Snacks", "Chef Specials"])}
      </div>
    </section>

    {_render_operations_section(
        "Food Ordering",
        "Kitchen Queue",
        "Place a customer order",
        [("Customer name", "Isha Menon"), ("Order type", "Dine-in table 6"), ("Pickup time", "Today, 8:30 PM")],
        "Send Order",
        "Restaurant Dashboard",
        "Orders, tables, and payment status",
        rows,
    )}"""


def _render_clinic_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    services = [
        ("General Consultation", money["serviceSmall"], "Appointment booking with visit reason and queue status"),
        ("Dental Checkup", money["serviceMedium"], "Doctor schedule slot with follow-up reminder"),
        ("Health Package", money["serviceLarge"], "Patient records, payment status, and admin dashboard review"),
    ]
    rows = [
        ("Meera Shah", "General Consultation", "Checked in"),
        ("Ravi Jain", "Dental Checkup", "Waiting"),
        ("Dr. Kapoor", "Doctor schedule", "3 open slots"),
        ("Follow-up Reminder", "Health package", "Tomorrow"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Appointment Booking</span>
        <h2>Clinic services with schedule-aware booking</h2>
      </div>
      <div class="package-grid">{_render_package_cards(services, "Book Visit")}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Doctor Schedule</span>
        <h2>Patient flow and care sections</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Doctor Schedule", "Patient Records", "Queue Status", "Follow-ups"])}
      </div>
    </section>

    {_render_operations_section(
        "Patient Intake",
        "Admin Dashboard",
        "Book an appointment",
        [("Patient name", "Meera Shah"), ("Doctor", "Dr. Kapoor"), ("Visit time", "Today, 5:15 PM")],
        "Confirm Appointment",
        "Clinic Dashboard",
        "Queue, payments, and follow-ups",
        rows,
    )}"""


def _render_school_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    modules = [
        ("Parent Portal", f"{money['basic']}/student", "Attendance, notices, homework, and teacher remarks in one parent view"),
        ("Class Dashboard", f"{money['serviceMedium']}/mo", "Teacher workload, class attendance, and assignment status"),
        ("Fee Desk", f"{money['serviceLarge']}/mo", "Fee status, reminders, receipts, and school admin overview"),
    ]
    rows = [
        ("Aarohi Class 5A", "Attendance tracking", "Present"),
        ("Homework", "Math worksheet", "Due tomorrow"),
        ("Fee Status", "Term 2", "Pending"),
        ("Parent Notice", "Sports day", "Sent"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Parent Portal</span>
        <h2>School communication modules</h2>
      </div>
      <div class="package-grid">{_render_package_cards(modules, "View Module")}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Student Records</span>
        <h2>Daily parent-facing updates</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Attendance", "Homework", "Fees", "Parent Notices"])}
      </div>
    </section>

    {_render_operations_section(
        "Teacher Update",
        "Class Dashboard",
        "Send parent update",
        [("Student name", "Aarohi Sharma"), ("Class", "5A"), ("Update", "Homework assigned")],
        "Send Notice",
        "Admin Dashboard",
        "Attendance, fees, and notices",
        rows,
    )}"""


def _render_retail_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    items = [
        ("Wireless Earbuds", money["serviceMedium"], "SKU EB-204, 48 in stock, high reorder velocity"),
        ("Travel Backpack", money["serviceSmall"], "SKU BG-118, 12 in stock, low-stock alert active"),
        ("Smart Watch", money["serviceLarge"], "SKU SW-331, supplier purchase order pending"),
    ]
    rows = [
        ("Low Stock", "Travel Backpack", "12 left"),
        ("Purchase Order", "Smart Watch", "Supplier sent"),
        ("Customer Enquiry", "Wireless Earbuds", "Callback"),
        ("Payment Status", "Order #8841", "Paid"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Product Catalog</span>
        <h2>Inventory shop cards with stock context</h2>
      </div>
      <div class="package-grid">{_render_package_cards(items, "Update Stock")}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Inventory Tracking</span>
        <h2>Shop operations at a glance</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Low Stock", "Purchase Orders", "Sales Dashboard", "Customer Enquiries"])}
      </div>
    </section>

    {_render_operations_section(
        "Inventory Update",
        "Admin Dashboard",
        "Record a stock movement",
        [("Product", "Travel Backpack"), ("SKU", "BG-118"), ("New stock", "12 units")],
        "Save Stock",
        "Retail Dashboard",
        "Stock, orders, and payments",
        rows,
    )}"""


def _render_finance_insurance_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    policies = [
        ("Family Health Protect", f"{money['serviceMedium']}/mo", "Policy card with coverage summary, renewal date, and advisor contact"),
        ("Vehicle Shield Plus", f"{money['serviceSmall']}/mo", "Quote card for premium comparison, document checklist, and payment state"),
        ("Term Life Secure", f"{money['basic']}/mo", "Claim-ready record with nominee details and review status"),
    ]
    rows = [
        ("Claim Tracker", "Health Protect", "Documents received"),
        ("Quote Request", "Vehicle Shield", "Advisor review"),
        ("Renewal", "Term Life Secure", "Due in 14 days"),
        ("Advisor Contact", "Meera Kapoor", "Call scheduled"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Policy Cards</span>
        <h2>Trust-first insurance workspace</h2>
      </div>
      <div class="package-grid">{_render_package_cards(policies, "View Quote")}</div>
    </section>

    <section class="content-block gallery-panel timeline-panel">
      <div class="section-heading">
        <span class="eyebrow">Claim Tracker</span>
        <h2>Policy status timeline and advisor follow-up</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Quote Cards", "Policy Review", "Claim Timeline", "Advisor Contact"])}
      </div>
    </section>

    {_render_operations_section(
        "Quote Builder",
        "Advisor Dashboard",
        "Capture a policy enquiry",
        [("Customer name", "Asha Mehta"), ("Policy type", "Family Health"), ("Renewal date", "14 Aug 2026")],
        "Send Enquiry",
        "Finance Desk",
        "Claims, quotes, renewals, and advisors",
        rows,
    )}"""


def _render_mutual_fund_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    funds = [
        ("Equity Funds", "Estimated growth", "Compare category, risk profile, NAV trend, and advisor guidance"),
        ("Hybrid Funds", "Balanced risk", "Review portfolio fit, SIP reminders, and customer enquiry readiness"),
        ("Debt Funds", "Lower volatility", "Summarize category notes, risk profile, and advisor follow-up"),
    ]
    rows = [
        ("SIP Calculator", "Monthly Investment", money["monthlyInvestment"]),
        ("Portfolio Tracker", "Portfolio Value", money["portfolioValue"]),
        ("KYC Upload", "Pending documents", "12"),
        ("Risk Profile", "Moderate investors", "18"),
        ("Advisor Booking", "Calls scheduled", "9"),
        ("SIP Reminders", "Due this week", "24"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Mutual Fund Categories</span>
        <h2>Finance-oriented fund discovery and comparison</h2>
      </div>
      <div class="package-grid">{_render_package_cards(funds, "Compare Funds")}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">SIP Investment Hub</span>
        <h2>SIP, portfolio, KYC, and risk profile workflow</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["SIP Calculator", "Portfolio Tracker", "KYC Upload", "Risk Profile", "Advisor Booking", "SIP Reminders"])}
      </div>
    </section>

    {_render_operations_section(
        "Customer Enquiry",
        "Advisor Dashboard",
        "Capture investor enquiry",
        [("Investor name", "Priya Sharma"), ("SIP Amount", f"{money['sipAmount']}/mo"), ("Risk profile", "Moderate")],
        "Book Advisor",
        "Admin Dashboard",
        "Advisor guidance, reminders, and portfolio summary",
        rows,
    )}"""


def _render_agriculture_sections(plan: Dict[str, Any]) -> str:
    money = _currency_sample_values(plan)
    cards = [
        ("Wheat Crop Health", money["mandiRate"], "Crop health card with field status, mandi price, and weather risk"),
        ("Input Cost", money["inputCost"], "Seed, fertilizer, and input cost tracking for the current crop cycle"),
        ("Profit Estimate", money["profitEstimate"], "Estimated profit after input and diesel cost review"),
        ("Weather Advisory", "Low risk", "Rain window, temperature signal, and irrigation reminder"),
        ("Satellite Intelligence", "86%", "Satellite intelligence card with scouting priority and NDVI-style status"),
    ]
    rows = [
        ("Crop Health", "North field wheat", "86% stable"),
        ("Weather Card", "Rain chance", "Low risk"),
        ("Mandi Rate", "Wheat", money["mandiRate"]),
        ("Input Cost", "Current crop", money["inputCost"]),
        ("Diesel Cost", "This week", money["dieselCost"]),
        ("Farmer Profile", "Ramesh Patel", "Advisory sent"),
        ("Farm Records", "8 acres", "Updated today"),
        ("AI Chat", "Ask advisory", "Ready"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Farmer Dashboard</span>
        <h2>Crop health, weather, mandi, and satellite intelligence</h2>
      </div>
      <div class="package-grid">{_render_package_cards(cards, "View Field")}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Agriculture Intelligence Hub</span>
        <h2>Green agri cards for daily decisions</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Crop Health", "Weather", "Mandi Prices", "Satellite Intelligence", "Farmer Profile", "Farm Records", "AI Chat"])}
      </div>
    </section>

    {_render_operations_section(
        "AI Chat",
        "Farmer Profile",
        "Record a farm update",
        [("Farmer name", "Ramesh Patel"), ("Crop", "Wheat"), ("Field status", "Healthy")],
        "Save Update",
        "Admin Dashboard",
        "Weather, prices, and field status",
        rows,
    )}"""


def _render_government_sections() -> str:
    services = [
        ("Citizen Certificate", "4 days", "Citizen service card with application status and officer routing"),
        ("Municipal Request", "Open", "Service request with department assignment and SLA status"),
        ("Scheme Application", "Review", "Role-based card for officer review and audit trail"),
    ]
    rows = [
        ("Application Tracker", "CERT-4821", "Officer review"),
        ("Citizen Service", "Water request", "In progress"),
        ("Audit Status", "Scheme application", "Verified"),
        ("Officer Dashboard", "Ward 12", "11 pending"),
    ]
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Citizen Services</span>
        <h2>Clean official service and officer workspace</h2>
      </div>
      <div class="package-grid">{_render_package_cards(services, "Track Status")}</div>
    </section>

    <section class="content-block gallery-panel timeline-panel">
      <div class="section-heading">
        <span class="eyebrow">Audit Status</span>
        <h2>Role-based cards for service accountability</h2>
      </div>
      <div class="gallery-grid">
        {_render_gallery_tiles(["Citizen Services", "Officer Dashboard", "Application Tracker", "Audit Cards"])}
      </div>
    </section>

    {_render_operations_section(
        "Service Request",
        "Department Metrics",
        "Capture a citizen request",
        [("Citizen name", "Nitin Rao"), ("Service type", "Certificate"), ("Application ID", "CERT-4821")],
        "Submit Request",
        "Officer Dashboard",
        "Services, officers, and audit status",
        rows,
    )}"""


def _render_domain_sections(domain: str, plan: Dict[str, Any]) -> str:
    blueprint_sections = _render_blueprint_sections(plan)

    if domain == "finance_insurance":
        return blueprint_sections + _render_finance_insurance_sections(plan)

    if domain == "mutual_fund_advisor":
        return blueprint_sections + _render_mutual_fund_sections(plan)

    if domain == "car_detailing":
        return blueprint_sections + _render_car_detailing_sections(plan)

    if domain == "wedding_venue":
        return blueprint_sections + _render_wedding_venue_sections(plan)

    if domain == "gym":
        return blueprint_sections + _render_gym_sections(plan)

    if domain == "restaurant":
        return blueprint_sections + _render_restaurant_sections(plan)

    if domain == "clinic":
        return blueprint_sections + _render_clinic_sections(plan)

    if domain == "school":
        return blueprint_sections + _render_school_sections(plan)

    if domain == "retail":
        return blueprint_sections + _render_retail_sections(plan)

    if domain == "agriculture":
        return blueprint_sections + _render_agriculture_sections(plan)

    if domain == "government":
        return blueprint_sections + _render_government_sections()

    return blueprint_sections + f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Core features</span>
        <h2>Built from your approved plan</h2>
      </div>
      <div class="feature-grid">
        {_render_feature_cards(plan["core_features"])}
      </div>
    </section>

    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Screens</span>
        <h2>Prototype navigation</h2>
      </div>
      <div class="screen-list">
        {_render_screen_sections(plan["screens"])}
      </div>
    </section>"""


def _build_html(plan: Dict[str, Any], app_id: str) -> str:
    app_name = html.escape(plan["app_name"])
    app_type = html.escape(plan["app_type"])
    summary = html.escape(plan["preview_summary"])
    domain = _domain_from_plan(plan)
    theme = plan.get("visual_theme") if isinstance(plan.get("visual_theme"), dict) else select_visual_theme(plan, app_id)
    sector_profile = _sector_ui_profile(plan)
    sector_classes = html.escape(sector_ui_class_names(sector_profile))
    hero_kicker = html.escape(_clean_text(sector_profile.get("hero_kicker"), plan["app_type"]))
    screen_labels = _domain_screen_labels(domain, plan)
    blueprint_actions = _blueprint_list(plan, "primary_actions")
    actions = {
        "finance_insurance": ("Quote Builder", "Claim Tracker"),
        "mutual_fund_advisor": ("Compare Funds", "SIP Calculator"),
        "car_detailing": ("Service Packages", "Doorstep Booking"),
        "gym": ("Membership Plans", "Class Booking"),
        "wedding_venue": ("Wedding Packages", "Send Enquiry"),
        "restaurant": ("Order Food", "Book Table"),
        "clinic": ("Book Appointment", "Doctor Schedule"),
        "school": ("Parent Portal", "Attendance"),
        "retail": ("Update Stock", "Sales Dashboard"),
        "agriculture": ("Crop Health", "Mandi Prices"),
        "government": ("Citizen Services", "Officer Dashboard"),
    }
    default_primary, default_secondary = actions.get(domain, ("Open Workflow", "View Dashboard"))
    primary_action = blueprint_actions[0] if blueprint_actions else default_primary
    secondary_action = blueprint_actions[1] if len(blueprint_actions) > 1 else default_secondary
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{app_name}</title>
  <link rel="manifest" href="./manifest.json">
  <link rel="stylesheet" href="./style.css">
</head>
<body class="{_domain_theme_class(domain, theme)} {sector_classes}{' is-image-guided' if plan.get('image_guided') else ''}">
  <main class="app-shell">
    <header class="hero">
      <nav class="top-nav" aria-label="Prototype navigation">
        <strong>{app_name}</strong>
        <button type="button" data-screen="dashboard">Preview</button>
      </nav>
      <section class="hero-content">
        <div class="hero-copy">
          <span class="eyebrow">{hero_kicker}</span>
          <h1>{app_name}</h1>
          <p>{summary}</p>
          <div class="hero-actions">
            <button type="button" data-screen="{html.escape(_screen_slug(primary_action))}">{html.escape(primary_action)}</button>
            <button type="button" class="ghost-button" data-screen="{html.escape(_screen_slug(secondary_action))}">{html.escape(secondary_action)}</button>
          </div>
        </div>
        {_render_app_visual(domain, sector_profile)}
      </section>
    </header>

    <section class="app-screen-nav" aria-label="Generated app screens">
      {_render_screen_nav(screen_labels)}
    </section>

    <section class="metric-grid" aria-label="Dashboard metrics">
      {_render_metric_cards(domain, plan)}
    </section>

    <section class="interactive-screen-panel" aria-live="polite">
      <div class="section-heading">
        <span class="eyebrow">Active screen</span>
        <h2>Dashboard</h2>
      </div>
      <p>Select a generated app screen to preview the real in-app flow.</p>
    </section>

    {_render_image_guided_reference(plan)}

    {_render_domain_sections(domain, plan)}
  </main>
  <script src="./app.js"></script>
</body>
</html>
"""


def _build_css() -> str:
    return """:root {
  color-scheme: light;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f4f6fb;
  color: #151821;
  --bg: #f4f6fb;
  --surface: rgba(255,255,255,.94);
  --surface-strong: #fff;
  --text: #151821;
  --muted: #697184;
  --line: #e5e9f2;
  --accent: #3657ff;
  --accent-2: #16a085;
  --accent-soft: #eef2ff;
  --hero-a: #10131d;
  --hero-b: #28364d;
  --hero-c: #4a5f7c;
  --shadow: 0 18px 45px rgba(27, 35, 58, .12);
}

* { box-sizing: border-box; }
html { min-width: 0; overflow-x: hidden; background: var(--bg); }
body { margin: 0; overflow-x: hidden; background: radial-gradient(circle at top left, rgba(54,87,255,.08), transparent 28rem), var(--bg); color: var(--text); }
button { border: 0; font: inherit; cursor: pointer; -webkit-tap-highlight-color: transparent; }
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible { outline: 3px solid color-mix(in srgb, var(--accent) 35%, transparent); outline-offset: 2px; }
.theme-car-detailing { --bg: #090b10; --surface: rgba(20,23,31,.94); --surface-strong: #151923; --text: #f6f7fb; --muted: #a8b0c2; --line: #2a3140; --accent: #f8c15c; --accent-2: #7fd7ff; --accent-soft: #241d12; --hero-a: #06070a; --hero-b: #141923; --hero-c: #b8863b; }
.theme-gym { --bg: #101215; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #151821; --muted: #616b7d; --line: #e6eaf1; --accent: #ff4d2e; --accent-2: #00c782; --accent-soft: #fff0ec; --hero-a: #111318; --hero-b: #28312d; --hero-c: #ff5b34; }
.theme-wedding-venue { --bg: #fbf7fb; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #2b1f2c; --muted: #7d6b7f; --line: #eee3ee; --accent: #b84f7a; --accent-2: #c7974b; --accent-soft: #fff0f6; --hero-a: #3a2334; --hero-b: #8e456b; --hero-c: #d6a85b; }
.theme-restaurant { --bg: #fff8f0; --accent: #d94f21; --accent-2: #16825d; --accent-soft: #fff1e8; --hero-a: #2c1510; --hero-b: #88402a; --hero-c: #e3a045; }
.theme-clinic { --bg: #f2fbfb; --accent: #0f8f94; --accent-2: #4a73d9; --accent-soft: #e8f8f8; --hero-a: #12333a; --hero-b: #176b72; --hero-c: #8ad7d6; }
.theme-school { --bg: #f7f9ff; --accent: #4a67d6; --accent-2: #f0a322; --accent-soft: #edf1ff; --hero-a: #1e2a4f; --hero-b: #4a67d6; --hero-c: #f2c55c; }
.theme-retail { --bg: #f6f9f5; --accent: #27825f; --accent-2: #3357c9; --accent-soft: #eaf6ef; --hero-a: #13251f; --hero-b: #27624b; --hero-c: #83b366; }
.theme-family-finance-trust-blue { --bg: #f4f8ff; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #14213d; --muted: #61708c; --line: #dbe6f7; --accent: #1d5fd1; --accent-2: #27a7d8; --accent-soft: #eaf2ff; --hero-a: #10284f; --hero-b: #174b90; --hero-c: #dcecff; }
.theme-family-finance-trust-blue-green { --bg: #f3faf8; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #10243d; --muted: #607384; --line: #d8e9e5; --accent: #1d65d1; --accent-2: #18a078; --accent-soft: #e8f7f2; --hero-a: #10284f; --hero-b: #126b70; --hero-c: #dff5ee; }
.theme-family-premium-automotive-dark { --bg: #090b10; --surface: rgba(20,23,31,.94); --surface-strong: #151923; --text: #f6f7fb; --muted: #a8b0c2; --line: #2a3140; --accent: #f8c15c; --accent-2: #7fd7ff; --accent-soft: #241d12; --hero-a: #06070a; --hero-b: #141923; --hero-c: #b8863b; }
.theme-family-fitness-energy-bold { --bg: #101215; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #151821; --muted: #616b7d; --line: #e6eaf1; --accent: #ff4d2e; --accent-2: #00c782; --accent-soft: #fff0ec; --hero-a: #111318; --hero-b: #28312d; --hero-c: #ff5b34; }
.theme-family-wedding-elegant-warm { --bg: #fff8f4; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #2b1f2c; --muted: #7d6b7f; --line: #f0dfd8; --accent: #b84f7a; --accent-2: #c7974b; --accent-soft: #fff0e6; --hero-a: #3a2334; --hero-b: #8e456b; --hero-c: #d6a85b; }
.theme-family-education-soft-blue { --bg: #f7f9ff; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #172244; --muted: #64708a; --line: #dfe7fb; --accent: #4a67d6; --accent-2: #f0a322; --accent-soft: #edf1ff; --hero-a: #1e2a4f; --hero-b: #4a67d6; --hero-c: #f2c55c; }
.theme-family-healthcare-calm-teal { --bg: #f2fbfb; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #11313a; --muted: #5d7378; --line: #d8eeee; --accent: #0f8f94; --accent-2: #4a73d9; --accent-soft: #e8f8f8; --hero-a: #12333a; --hero-b: #176b72; --hero-c: #8ad7d6; }
.theme-family-restaurant-warm-food { --bg: #fff8f0; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #2c1510; --muted: #7d6659; --line: #f0ded1; --accent: #d94f21; --accent-2: #16825d; --accent-soft: #fff1e8; --hero-a: #2c1510; --hero-b: #88402a; --hero-c: #e3a045; }
.theme-family-retail-inventory-grid { --bg: #f6f9f5; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #14251f; --muted: #64736c; --line: #dfe9df; --accent: #27825f; --accent-2: #3357c9; --accent-soft: #eaf6ef; --hero-a: #13251f; --hero-b: #27624b; --hero-c: #83b366; }
.theme-family-agriculture-green-dashboard { --bg: #f3fbef; --surface: rgba(255,255,255,.96); --surface-strong: #fff; --text: #18331e; --muted: #61755e; --line: #dcebd5; --accent: #2f8f46; --accent-2: #b28b22; --accent-soft: #eaf7df; --hero-a: #17351f; --hero-b: #2f7640; --hero-c: #b9d981; }
.theme-family-government-civic-clean { --bg: #f7f8fa; --surface: rgba(255,255,255,.97); --surface-strong: #fff; --text: #172033; --muted: #687082; --line: #dfe3ea; --accent: #2457a6; --accent-2: #64748b; --accent-soft: #edf3fb; --hero-a: #182235; --hero-b: #315f9f; --hero-c: #e7edf5; }
.theme-family-generic-modern-saas { --bg: #f4f6fb; --surface: rgba(255,255,255,.94); --surface-strong: #fff; --text: #151821; --muted: #697184; --line: #e5e9f2; --accent: #3657ff; --accent-2: #16a085; --accent-soft: #eef2ff; --hero-a: #10131d; --hero-b: #28364d; --hero-c: #4a5f7c; }
.app-shell { min-height: 100svh; width: min(100%, 1180px); margin: 0 auto; padding: 14px 14px max(92px, calc(env(safe-area-inset-bottom) + 76px)); }
.hero { overflow: hidden; border-radius: 26px; background: linear-gradient(135deg, var(--hero-a) 0%, var(--hero-b) 56%, var(--hero-c) 100%); color: #fff; box-shadow: 0 24px 70px rgba(12,16,26,.24); }
.top-nav { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 16px; }
.top-nav strong { min-width: 0; overflow-wrap: anywhere; font-size: 15px; letter-spacing: 0; }
.top-nav button, .hero-actions button, .screen-section button { min-height: 42px; border-radius: 999px; padding: 0 16px; background: #fff; color: #151821; font-weight: 850; box-shadow: 0 10px 24px rgba(0,0,0,.12); }
.hero-content { display: grid; gap: 22px; padding: 34px 18px 24px; }
.hero-copy { display: grid; gap: 16px; align-content: center; min-width: 0; }
.eyebrow, .screen-kicker { color: var(--accent); font-size: 11px; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }
.hero .eyebrow { color: rgba(255,255,255,.76); }
h1, h2, h3, p { margin: 0; }
h1 { max-width: 720px; font-size: clamp(34px, 8vw, 66px); line-height: .98; letter-spacing: 0; overflow-wrap: anywhere; }
.hero p { max-width: 620px; color: rgba(255,255,255,.78); font-size: 16px; line-height: 1.55; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.hero-actions .ghost-button { background: rgba(255,255,255,.12); color: #fff; outline: 1px solid rgba(255,255,255,.25); }
.hero-visual { min-width: 0; }
.phone-mock { display: grid; gap: 14px; max-width: 360px; margin: 0 auto; padding: 16px; border: 1px solid rgba(255,255,255,.2); border-radius: 28px; background: rgba(255,255,255,.14); box-shadow: inset 0 1px 0 rgba(255,255,255,.2); backdrop-filter: blur(12px); }
.phone-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; color: rgba(255,255,255,.82); font-size: 12px; font-weight: 800; }
.phone-focus { display: grid; gap: 5px; min-height: 118px; align-content: end; padding: 16px; border-radius: 22px; background: rgba(255,255,255,.9); color: #151821; }
.phone-focus small { color: #697184; font-weight: 850; text-transform: uppercase; letter-spacing: .08em; }
.phone-focus strong { font-size: 26px; line-height: 1; }
.phone-chip-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
.phone-chip-grid span { min-height: 56px; padding: 10px; border-radius: 16px; background: rgba(255,255,255,.16); color: #fff; font-size: 12px; font-weight: 850; overflow-wrap: anywhere; }
.phone-bar { display: grid; gap: 7px; }
.phone-bar span { height: 8px; border-radius: 999px; background: rgba(255,255,255,.24); }
.phone-bar span:nth-child(2) { width: 72%; }
.phone-bar span:nth-child(3) { width: 48%; }
.app-screen-nav { position: sticky; top: 0; z-index: 2; display: flex; gap: 8px; margin-top: 14px; overflow-x: auto; padding: 8px 0 10px; scrollbar-width: thin; background: linear-gradient(to bottom, var(--bg), color-mix(in srgb, var(--bg) 82%, transparent)); }
.app-screen-nav button { flex: 0 0 auto; min-height: 38px; border: 1px solid var(--line); border-radius: 999px; padding: 0 14px; background: var(--surface-strong); color: var(--text); font-size: 13px; font-weight: 850; box-shadow: 0 8px 20px rgba(20,28,45,.06); }
.app-screen-nav button.is-active { border-color: var(--accent); background: var(--accent); color: #fff; }
.metric-grid, .feature-grid, .package-grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); margin-top: 14px; }
.metric-grid article, .feature-card, .screen-section, .data-panel, .package-card, .enquiry-card, .admin-card, .gallery-panel, .interactive-screen-panel, .screen-card { border: 1px solid var(--line); border-radius: 20px; background: var(--surface); box-shadow: var(--shadow); color: var(--text); }
.metric-grid article, .feature-card, .screen-section, .package-card, .gallery-grid span, .screen-card { cursor: pointer; transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease; }
.metric-grid article:hover, .feature-card:hover, .screen-section:hover, .package-card:hover, .gallery-grid span:hover, .screen-card:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--accent) 42%, var(--line)); }
.metric-grid article { position: relative; display: grid; gap: 7px; overflow: hidden; padding: 17px; }
.metric-grid article::after { content: ""; position: absolute; inset: auto 14px 14px auto; width: 34px; height: 34px; border-radius: 12px; background: color-mix(in srgb, var(--accent) 16%, transparent); }
.metric-grid span { color: var(--muted); font-size: 12px; font-weight: 750; }
.metric-grid strong { font-size: 28px; line-height: 1; overflow-wrap: anywhere; }
.metric-elegant .metric-grid article { background: linear-gradient(160deg, #fff, color-mix(in srgb, var(--accent-soft) 78%, #fff)); border-color: color-mix(in srgb, var(--accent) 22%, var(--line)); }
.metric-trust .metric-grid article { background: linear-gradient(160deg, #fff, color-mix(in srgb, var(--accent-soft) 84%, #fff)); }
.metric-leaf .metric-grid article { background: linear-gradient(160deg, #fff, #f1fae9); }
.metric-calm .metric-grid article { background: linear-gradient(160deg, #fff, #edfafa); }
.metric-dark .metric-grid article { background: linear-gradient(160deg, color-mix(in srgb, var(--surface) 92%, #000), color-mix(in srgb, var(--accent-soft) 35%, var(--surface))); }
.metric-energy .metric-grid article { background: linear-gradient(160deg, #fff, #fff3ef); }
.metric-warm .metric-grid article { background: linear-gradient(160deg, #fff, #fff3e8); }
.metric-gridline .metric-grid article { background-image: linear-gradient(160deg, var(--surface-strong), color-mix(in srgb, var(--accent-soft) 62%, var(--surface-strong))), linear-gradient(90deg, color-mix(in srgb, var(--line) 55%, transparent) 1px, transparent 1px); background-size: auto, 18px 18px; }
.metric-civic .metric-grid article { background: linear-gradient(160deg, #fff, #f2f6fb); border-style: solid; }
.content-block { display: grid; gap: 14px; margin-top: 26px; }
.interactive-screen-panel { display: grid; gap: 14px; margin-top: 14px; padding: 18px; background: linear-gradient(180deg, var(--surface-strong), color-mix(in srgb, var(--accent-soft) 46%, var(--surface-strong))); }
.interactive-screen-panel p { color: var(--muted); font-size: 14px; line-height: 1.5; }
.section-heading-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.screen-panel-close { display: inline-flex; align-items: center; justify-content: center; min-width: 38px; min-height: 38px; padding: 0 12px; border: 1px solid var(--line); border-radius: 999px; background: color-mix(in srgb, var(--surface-strong) 84%, var(--accent-soft)); color: var(--text); font-size: 12px; font-weight: 850; box-shadow: none; }
.screen-panel-close[hidden] { display: none; }
.screen-card-grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
.screen-card { display: grid; gap: 8px; min-height: 130px; padding: 16px; box-shadow: none; background: var(--surface-strong); }
.screen-card strong { font-size: 17px; }
.screen-card span { color: var(--muted); font-size: 13px; line-height: 1.45; }
.screen-form { display: grid; gap: 10px; }
.screen-form label { display: grid; gap: 6px; color: var(--muted); font-size: 13px; font-weight: 750; }
.screen-form input, .screen-form select, .screen-form textarea { width: 100%; min-height: 42px; border: 1px solid var(--line); border-radius: 12px; padding: 0 12px; color: var(--text); font: inherit; background: var(--surface-strong); }
.screen-form textarea { min-height: 78px; padding-top: 10px; resize: vertical; }
.screen-form button { min-height: 42px; border-radius: 999px; background: var(--accent); color: #fff; font-weight: 850; }
.form-success { min-height: 20px; color: #16825d; font-size: 13px; font-weight: 850; }
.section-heading { display: grid; gap: 6px; }
.section-heading h2, .data-panel h2 { font-size: 24px; line-height: 1.1; }
.feature-card { display: grid; gap: 12px; min-height: 168px; padding: 18px; }
.feature-card span { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 14px; background: var(--accent-soft); color: var(--accent); font-weight: 900; }
.feature-card h3 { font-size: 18px; line-height: 1.2; }
.feature-card p, .screen-section p { color: var(--muted); font-size: 14px; line-height: 1.5; }
.blueprint-panel { position: relative; }
.blueprint-panel::before { content: ""; width: 48px; height: 4px; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }
.premium-action-card, .premium-record-card { border-color: color-mix(in srgb, var(--accent) 24%, var(--line)); }
.premium-action-card { align-content: start; min-height: 154px; gap: 10px; background: linear-gradient(180deg, var(--surface-strong), color-mix(in srgb, var(--accent-soft) 58%, var(--surface-strong))); }
.premium-action-card span { display: inline-flex; width: fit-content; height: auto; min-height: 26px; padding: 0 10px; place-items: initial; align-items: center; border-radius: 999px; font-size: 10px; line-height: 1; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; }
.premium-action-card h3 { font-size: 19px; line-height: 1.15; }
.premium-action-card p { max-width: 30rem; }
.premium-record-card { box-shadow: 0 18px 38px rgba(20,28,45,.1); }
.action-card-elegant .premium-action-card { background: linear-gradient(160deg, #fff, #fff2f6); }
.action-card-organic .premium-action-card { background: linear-gradient(160deg, #fff, #eef9e8); }
.action-card-trust .premium-action-card { background: linear-gradient(160deg, #fff, #edf4ff); }
.action-card-calm .premium-action-card { background: linear-gradient(160deg, #fff, #eafafa); }
.action-card-warm .premium-action-card { background: linear-gradient(160deg, #fff, #fff1e8); }
.action-card-civic .premium-action-card { background: linear-gradient(160deg, #fff, #f1f5fa); }
.record-card-event .premium-record-card { background: linear-gradient(180deg, #fff, #fff7ed); }
.record-card-harvest .premium-record-card { background: linear-gradient(180deg, #fff, #f4fae9); }
.record-card-ledger .premium-record-card { background: linear-gradient(180deg, #fff, #f4f8ff); }
.record-card-clinic .premium-record-card { background: linear-gradient(180deg, #fff, #eefafa); }
.screen-list { display: grid; gap: 12px; }
.screen-section { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px; }
.screen-section button { flex: 0 0 auto; background: var(--accent); color: #fff; }
.data-panel { display: grid; gap: 18px; padding: 18px; }
.data-panel ul { display: grid; gap: 8px; margin: 10px 0 0; padding-left: 18px; color: var(--text); }
.package-card { position: relative; display: grid; gap: 12px; align-content: start; min-height: 190px; overflow: hidden; padding: 18px; }
.package-card::before { content: ""; position: absolute; inset: 0 0 auto; height: 5px; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }
.package-card span { color: var(--accent); font-size: 22px; font-weight: 900; }
.package-card p { color: var(--muted); line-height: 1.45; }
.package-card button, .enquiry-card button { min-height: 42px; border-radius: 999px; background: var(--text); color: #fff; font-weight: 850; }
.gallery-panel { padding: 18px; }
.gallery-grid { display: grid; gap: 10px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 12px; }
.gallery-grid span { display: grid; min-height: 112px; place-items: end start; padding: 14px; border-radius: 16px; background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 16%, #fff), color-mix(in srgb, var(--accent-2) 18%, #fff)); color: var(--text); font-weight: 850; box-shadow: inset 0 0 0 1px rgba(255,255,255,.4); }
.enquiry-admin-grid { display: grid; gap: 14px; }
.workflow-label { color: var(--muted); font-size: 12px; font-weight: 850; text-transform: uppercase; letter-spacing: .08em; }
.enquiry-card, .admin-card { display: grid; gap: 12px; padding: 18px; }
.enquiry-card label { display: grid; gap: 6px; color: var(--muted); font-size: 13px; font-weight: 750; }
.enquiry-card input { width: 100%; min-height: 42px; border: 1px solid var(--line); border-radius: 12px; padding: 0 12px; color: var(--text); font: inherit; background: var(--surface-strong); }
.admin-card ul { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
.admin-card li { display: grid; gap: 3px; padding: 12px; border-radius: 14px; background: color-mix(in srgb, var(--accent-soft) 62%, var(--surface-strong)); }
.admin-card li span { color: var(--muted); font-size: 13px; }
.admin-card li em { color: var(--accent); font-size: 12px; font-style: normal; font-weight: 850; }
.status-list { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
.status-list li { display: grid; gap: 5px; padding: 14px; border: 1px solid var(--line); border-radius: 16px; background: var(--surface); }
.status-list strong { color: var(--text); }
.status-list span { color: var(--muted); line-height: 1.45; }
.empty-state-event .status-list li:first-child, .trust-note-event .status-list li { background: linear-gradient(160deg, #fff, #fff4e8); }
.empty-state-field .status-list li:first-child, .trust-note-advisory .status-list li { background: linear-gradient(160deg, #fff, #eff9e8); }
.empty-state-clinic .status-list li:first-child, .trust-note-medical .status-list li { background: linear-gradient(160deg, #fff, #eafafa); }
.empty-state-compliance .status-list li:first-child, .trust-note-compliance .status-list li { background: linear-gradient(160deg, #fff, #eef4ff); }
.trust-note-privacy .status-list li { background: linear-gradient(160deg, #fff, #f6f7ff); }
.trust-note-civic .status-list li { background: linear-gradient(160deg, #fff, #f2f6fb); }
.card-style-sharp .metric-grid article, .card-style-sharp .feature-card, .card-style-sharp .screen-section, .card-style-sharp .package-card, .card-style-sharp .enquiry-card, .card-style-sharp .admin-card, .card-style-sharp .gallery-panel, .card-style-sharp .interactive-screen-panel, .card-style-sharp .screen-card { border-radius: 10px; }
.card-style-soft .metric-grid article, .card-style-soft .feature-card, .card-style-soft .screen-section, .card-style-soft .package-card, .card-style-soft .enquiry-card, .card-style-soft .admin-card, .card-style-soft .gallery-panel, .card-style-soft .interactive-screen-panel, .card-style-soft .screen-card { border-radius: 18px; }
.card-style-rounded .metric-grid article, .card-style-rounded .feature-card, .card-style-rounded .screen-section, .card-style-rounded .package-card, .card-style-rounded .enquiry-card, .card-style-rounded .admin-card, .card-style-rounded .gallery-panel, .card-style-rounded .interactive-screen-panel, .card-style-rounded .screen-card { border-radius: 24px; }
.density-compact .content-block { margin-top: 18px; gap: 10px; }
.density-compact .metric-grid, .density-compact .feature-grid, .density-compact .package-grid { gap: 9px; }
.density-spacious .content-block { margin-top: 34px; gap: 18px; }
.density-spacious .metric-grid, .density-spacious .feature-grid, .density-spacious .package-grid { gap: 16px; }
.layout-card-first-dashboard .metric-grid { order: -1; }
.layout-card-first-dashboard .interactive-screen-panel { background: var(--surface-strong); }
.layout-gallery-first-showcase .gallery-panel { background: linear-gradient(135deg, var(--surface-strong), color-mix(in srgb, var(--accent-soft) 74%, var(--surface-strong))); }
.layout-gallery-first-showcase .gallery-grid span { min-height: 148px; }
.layout-timeline-tracker .timeline-panel, .layout-timeline-tracker .admin-card { border-left: 5px solid var(--accent); }
.layout-admin-metrics-grid .metric-grid { grid-template-columns: repeat(auto-fit, minmax(132px, 1fr)); }
.layout-admin-metrics-grid .metric-grid article { min-height: 118px; }
.layout-hero-stat-stack .phone-chip-grid { grid-template-columns: 1fr; }
.layout-hero-stat-stack .phone-chip-grid span { min-height: 42px; }
.layout-hero-feature-grid .phone-focus { min-height: 150px; }
.layout-split-action-dashboard .interactive-screen-panel { border-color: color-mix(in srgb, var(--accent) 35%, var(--line)); }
.is-image-guided .hero { border-radius: 30px; background: linear-gradient(160deg, #171b24 0%, var(--hero-b) 54%, var(--accent) 100%); }
.is-image-guided .hero-content { align-items: stretch; }
.is-image-guided .phone-mock { border-radius: 34px; background: rgba(255,255,255,.18); }
.is-image-guided .phone-focus { min-height: 150px; border-radius: 26px; background: linear-gradient(180deg, #ffffff, color-mix(in srgb, var(--accent-soft) 58%, #ffffff)); }
.is-image-guided .phone-chip-grid { grid-template-columns: 1fr 1fr; }
.is-image-guided .phone-chip-grid span:first-child { grid-column: 1 / -1; min-height: 72px; }
.image-guided-panel { padding: 18px; border: 1px solid var(--line); border-radius: 24px; background: linear-gradient(180deg, var(--surface-strong), color-mix(in srgb, var(--accent-soft) 55%, var(--surface-strong))); box-shadow: var(--shadow); }
.image-guided-grid { display: grid; gap: 12px; }
.image-guided-grid article { display: grid; gap: 10px; min-width: 0; padding: 16px; border: 1px solid var(--line); border-radius: 18px; background: var(--surface-strong); }
.image-guided-grid span { color: var(--accent); font-size: 11px; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }
.image-guided-grid strong { overflow-wrap: anywhere; font-size: 19px; }
.image-guided-grid p { color: var(--muted); font-size: 14px; line-height: 1.5; }
.image-guided-grid ul { display: grid; gap: 8px; margin: 0; padding-left: 18px; color: var(--text); }
@media (max-width: 640px) {
  .app-shell { padding: 18px 10px max(108px, calc(env(safe-area-inset-bottom) + 88px)); }
  .hero { border-radius: 22px; }
  .hero-content { padding: 32px 16px 20px; }
  .phone-mock { max-width: none; }
  .is-image-guided .phone-mock { min-height: 360px; }
  .phone-chip-grid span { min-height: 52px; }
  .metric-grid, .package-grid, .feature-grid { grid-template-columns: 1fr; }
  .gallery-grid { grid-template-columns: 1fr 1fr; }
  .screen-section { align-items: flex-start; flex-direction: column; }
  .screen-section button { width: 100%; }
}
@media (max-width: 720px) {
  html, body { width: 100%; max-width: 100%; overflow-x: hidden; }
  body { background: var(--bg); }
  .app-shell { width: 100%; max-width: 100%; padding: max(12px, calc(env(safe-area-inset-top) + 8px)) 10px max(112px, calc(env(safe-area-inset-bottom) + 96px)); }
  .hero { border-radius: 18px; box-shadow: 0 14px 34px rgba(12,16,26,.18); }
  .top-nav { min-height: 40px; padding: 8px 12px 0; }
  .top-nav strong { font-size: 13px; }
  .top-nav button { min-height: 30px; padding: 0 10px; font-size: 12px; box-shadow: none; }
  .hero-content { display: block; padding: 12px 12px 14px; }
  .hero-copy { gap: 8px; }
  .hero .eyebrow { font-size: 10px; letter-spacing: .07em; }
  h1 { font-size: clamp(24px, 8.2vw, 34px); line-height: 1.02; }
  .hero p { max-width: none; font-size: 12.5px; line-height: 1.38; }
  .hero-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .hero-actions button { min-height: 34px; padding: 0 10px; font-size: 11.5px; box-shadow: 0 8px 18px rgba(0,0,0,.12); }
  .hero-visual { display: none; }
  .app-screen-nav { margin-top: 8px; gap: 6px; padding: 7px 2px 9px; scroll-snap-type: x proximity; -webkit-overflow-scrolling: touch; overscroll-behavior-x: contain; }
  .app-screen-nav button { flex-shrink: 0; min-height: 34px; padding: 0 12px; font-size: 12px; scroll-snap-align: start; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 8px; }
  .metric-grid article { min-height: 86px; padding: 12px; border-radius: 16px; }
  .metric-grid article::after { width: 24px; height: 24px; border-radius: 9px; right: 10px; bottom: 10px; }
  .metric-grid span { font-size: 10px; line-height: 1.2; }
  .metric-grid strong { font-size: 20px; }
  .interactive-screen-panel { margin-top: 10px; padding: 12px; border-radius: 16px; }
  .screen-panel-close { min-width: 32px; min-height: 32px; padding: 0 10px; font-size: 11px; }
  .section-heading-row { align-items: center; }
  .content-block { margin-top: 18px; }
  .feature-grid, .package-grid { grid-template-columns: 1fr; gap: 10px; }
  .feature-card, .package-card { min-height: auto; padding: 14px; border-radius: 18px; }
  .premium-action-card { min-height: 128px; }
}
@media (min-width: 860px) {
  .app-shell { max-width: 1160px; margin: 0 auto; padding: 20px 20px 104px; }
  .hero-content { grid-template-columns: minmax(0, 1.25fr) minmax(280px, .75fr); align-items: center; padding: 64px 42px 44px; }
  .data-panel { grid-template-columns: 1fr 1fr; }
  .image-guided-grid { grid-template-columns: 1fr 1fr; }
  .enquiry-admin-grid { grid-template-columns: 1fr 1fr; }
  .workflow-label { grid-column: 1 / -1; }
}
"""


def _build_js(app_id: str, plan: Dict[str, Any]) -> str:
    api_services = [_slugify(service) for service in plan["api_needs"]] or ["future-service"]
    domain = _domain_from_plan(plan)
    sector_profile = _sector_ui_profile(plan)
    blueprint_actions = _blueprint_list(plan, "primary_actions")
    blueprint_records = _blueprint_list(plan, "sample_records")
    blueprint_guidance = _blueprint_text(plan, "empty_state_guidance", "Blueprint-backed preview screen.")
    screen_summary = _premium_section(sector_profile, "actions_summary", blueprint_guidance)
    record_summary = _premium_section(sector_profile, "records_summary", "Sample blueprint record for this generated app.")
    blueprint_screen_config = {
        _screen_slug(label): {
            "title": label,
            "summary": screen_summary,
            "cards": [[action, "Primary action"] for action in blueprint_actions[:3]]
            or [[record, "Sample record"] for record in blueprint_records[:3]]
            or [[label, "Blueprint screen"]],
        }
        for label in _domain_screen_labels(domain, plan)
    }
    for action in blueprint_actions:
        blueprint_screen_config.setdefault(
            _screen_slug(action),
            {
                "title": action,
                "summary": screen_summary,
                "cards": [[record, "Sample record"] for record in blueprint_records[:3]]
                or [[action, "Action preview"]],
            },
        )
    for record in blueprint_records:
        blueprint_screen_config.setdefault(
            _screen_slug(record),
            {
                "title": record,
                "summary": record_summary,
                "cards": [[action, "Related action"] for action in blueprint_actions[:3]]
                or [[record, "Sample record"]],
            },
        )
    currency_metadata = {
        "code": _clean_text(plan.get("currency_code"), "USD"),
        "symbol": _clean_text(plan.get("currency_symbol"), "$"),
        "locale": _clean_text(plan.get("currency_locale"), "en-US"),
        "country": _clean_text(plan.get("country_hint"), "United States"),
        "samples": _currency_sample_values(plan),
    }
    if domain == "school":
        currency_metadata["samples"] = {
            "feesPending": currency_metadata["samples"]["feesPending"],
        }
    elif domain != "agriculture":
        currency_metadata["samples"] = {
            key: value
            for key, value in currency_metadata["samples"].items()
            if "mandi" not in key.lower()
            and key not in {"inputCost", "dieselCost", "profitEstimate", "weddingPipeline"}
        }
    script = f"""const APP_ID = {json.dumps(app_id)};
// Internal runtime proxy placeholders only: {json.dumps([f"/api/runtime/{app_id}/{service}" for service in api_services])}
const API_PROXY_PLACEHOLDERS = [];
const APP_DOMAIN = {json.dumps(domain)};
const IS_TUTOR_MODE = {json.dumps(bool(plan.get("tutor_mode")))};
const CURRENCY = {json.dumps(currency_metadata, ensure_ascii=False)};
const MONEY = CURRENCY.samples;
const REGISTRY_SCREEN_ALIASES = {json.dumps(plan.get("clickable_aliases") if isinstance(plan.get("clickable_aliases"), dict) else {}, ensure_ascii=False)};
const BLUEPRINT_SCREEN_CONFIG = {json.dumps(blueprint_screen_config, ensure_ascii=False)};

const SCREEN_CONFIG = {{
  finance_insurance: {{
    dashboard: {{
      title: "Finance Dashboard",
      summary: "Policies, quote requests, claim timelines, advisor follow-up, and renewal reminders.",
      cards: [["Active Policies", "248 covered customers"], ["Quote Requests", "31 awaiting advisor"], ["Claims Open", "12 in progress"]]
    }},
    policy_cards: {{
      title: "Policy Cards",
      summary: "Clean policy cards for premium, coverage, renewal date, and claim readiness.",
      cards: [["Health Protect", `${{MONEY.serviceMedium}}/mo renewal`], ["Vehicle Shield", "Quote pending"], ["Term Life Secure", "Nominee verified"]]
    }},
    quote_builder: {{
      title: "Quote Builder",
      summary: "A trust-focused quote form for customer details, policy type, date, and advisor notes.",
      formType: "enquiry",
      serviceOptions: ["Health Policy", "Vehicle Insurance", "Term Life"]
    }},
    claim_tracker: {{
      title: "Claim Tracker",
      summary: "Timeline-style cards for submitted documents, review status, advisor action, and payout stage.",
      cards: [["Documents", "Received"], ["Review", "Advisor assigned"], ["Settlement", "Awaiting approval"]]
    }},
    advisor_contacts: {{
      title: "Advisor Contacts",
      summary: "Advisor cards keep contact and follow-up visible without a dark generic CRM feel.",
      cards: [["Meera Kapoor", "Health policies"], ["Rohan Sethi", "Vehicle claims"], ["Aisha Khan", "Renewals"]]
    }},
    renewals: {{
      title: "Renewals",
      summary: "Upcoming policy renewals and quote reminders for the finance team.",
      cards: [["Health Protect", "Due in 14 days"], ["Vehicle Shield", "Quote sent"], ["Term Secure", "Call scheduled"]]
    }},
    admin_dashboard: {{
      title: "Admin Dashboard",
      summary: "Finance admin view for policies, quotes, claims, and advisor workload.",
      cards: [["Policies", "248"], ["Claims", "12"], ["Renewals", "44"]]
    }}
  }},
  mutual_fund_advisor: {{
    dashboard: {{
      title: "Mutual Fund Dashboard",
      summary: "Investors, SIP customers, advisor leads, KYC pending items, and portfolio summaries in one clean finance app.",
      cards: [["SIP Amount", `${{MONEY.sipAmount}}/mo`], ["Portfolio Value", `${{MONEY.portfolioValue}}`], ["Advisory Leads", "28 enquiries"]]
    }},
    funds: {{
      title: "Mutual Fund Categories",
      summary: "Category cards help investors review equity, hybrid, and debt funds with risk-aware advisor guidance.",
      cards: [["Equity Funds", "Estimated growth view"], ["Hybrid Funds", "Balanced risk profile"], ["Debt Funds", "Lower volatility category"]]
    }},
    compare: {{
      title: "Compare Funds",
      summary: "Compare fund categories, NAV context, risk profile fit, and portfolio suitability without promising returns.",
      cards: [["Large Cap Fund", "NAV summary"], ["Balanced Advantage", "Risk profile fit"], ["Short Duration Debt", "Portfolio allocation"]]
    }},
    sip: {{
      title: "SIP Calculator",
      summary: "Estimate SIP growth scenarios from monthly investment, duration, and risk profile inputs.",
      formType: "sip",
      serviceOptions: ["Monthly SIP", "Step-up SIP", "Goal-based SIP"]
    }},
    portfolio: {{
      title: "Portfolio Tracker",
      summary: "Portfolio summary cards show current value, monthly investment, allocation, and advisor follow-up.",
      cards: [["Portfolio Value", `${{MONEY.portfolioValue}}`], ["Monthly Investment", `${{MONEY.monthlyInvestment}}`], ["Review", "Advisor guidance due"]]
    }},
    kyc: {{
      title: "KYC Upload",
      summary: "Document upload readiness screen for PAN, address proof, bank proof, and pending checks. No fake KYC approval is shown.",
      cards: [["PAN", "Pending upload"], ["Address Proof", "Review needed"], ["Bank Proof", "Checklist ready"]]
    }},
    risk: {{
      title: "Risk Profile",
      summary: "Risk profile form preview for investor goals, horizon, volatility comfort, and advisor guidance.",
      formType: "risk",
      serviceOptions: ["Conservative", "Moderate", "Aggressive"]
    }},
    advisor: {{
      title: "Advisor Booking",
      summary: "Book advisor calls for portfolio review, SIP guidance, KYC help, and customer enquiry follow-up.",
      formType: "booking",
      serviceOptions: ["Portfolio Review", "SIP Guidance", "KYC Help"]
    }},
    reminders: {{
      title: "SIP Reminders",
      summary: "Upcoming SIP reminders and customer follow-up cards for investors and advisor teams.",
      cards: [["Priya Sharma", `${{MONEY.sipAmount}} due Friday`], ["Arjun Mehta", "Step-up reminder"], ["Neha Rao", "Portfolio review call"]]
    }},
    enquiry: {{
      title: "Customer Enquiry",
      summary: "Capture investor enquiry details for advisor guidance and broker admin follow-up.",
      formType: "enquiry",
      serviceOptions: ["New SIP", "Fund Comparison", "Portfolio Review"]
    }},
    admin: {{
      title: "Admin Dashboard",
      summary: "Broker admin view for advisory leads, KYC pending items, SIP reminders, and portfolio review workload.",
      cards: [["Advisory Leads", "28"], ["KYC Pending", "12"], ["SIP Reminders", "24"]]
    }}
  }},
  car_detailing: {{
    dashboard: {{
      title: "Dashboard",
      summary: "Daily bookings, revenue, leads, and payment status for the detailing business.",
      cards: [["Daily Bookings", "18 scheduled services"], ["Revenue", `${{MONEY.revenueWeekly}}`], ["Customer Leads", "7 callback requests"]]
    }},
    service_packages: {{
      title: "Service Packages",
      summary: "Customers compare detailing packages and choose the service that matches their vehicle.",
      cards: [["Express Wash", `${{MONEY.serviceSmall}} quick exterior care`], ["Interior Deep Clean", `${{MONEY.serviceMedium}} cabin reset`], ["Premium Ceramic Detail", `${{MONEY.serviceLarge}} finish protection`]]
    }},
    doorstep_booking: {{
      title: "Doorstep Booking",
      summary: "A realistic booking preview with customer, mobile, date, service, and message fields.",
      formType: "booking",
      serviceOptions: ["Express Wash", "Interior Deep Clean", "Premium Ceramic Detail"]
    }},
    before_after_gallery: {{
      title: "Before-After Gallery",
      summary: "Proof-focused visual sections for exterior shine, interior reset, wheel detail, and ceramic finish.",
      cards: [["Exterior Shine", "Paint-safe foam wash result"], ["Interior Reset", "Seats, mats, and dashboard"], ["Ceramic Finish", "Premium gloss outcome"]]
    }},
    booking_calendar: {{
      title: "Booking Calendar",
      summary: "Upcoming doorstep slots and service status for the operations team.",
      cards: [["Today 4:30 PM", "SUV ceramic detail"], ["Tomorrow 10:00 AM", "Interior deep clean"], ["Friday 2:00 PM", "Express wash route"]]
    }},
    payment_status: {{
      title: "Payment Status",
      summary: "Payment and invoice states stay visible before the real backend payment proxy is connected.",
      cards: [["Express wash", "Paid"], ["Ceramic detail", "Invoice sent"], ["Interior clean", "Awaiting payment"]]
    }},
    admin_dashboard: {{
      title: "Admin Dashboard",
      summary: "Admin view for bookings, revenue, lead follow-up, and service completion.",
      cards: [["Bookings", "18 active"], ["Revenue", `${{MONEY.revenueShort}}`], ["Leads", "7 open"]]
    }}
  }},
  gym: {{
    dashboard: {{
      title: "Dashboard",
      summary: "Fitness studio snapshot for members, attendance, class bookings, and revenue.",
      cards: [["Member Records", "286 active"], ["Class Bookings", "34 today"], ["Attendance", "91% this week"]]
    }},
    membership_plans: {{
      title: "Membership Plans",
      summary: "Members can compare starter, transformation, and elite coaching plans.",
      cards: [["Starter Plan", `${{MONEY.basic}}/mo gym access`], ["Transformation Plan", `${{MONEY.serviceMedium}}/mo trainer match`], ["Elite Coaching", `${{MONEY.serviceLarge}}/mo premium sessions`]]
    }},
    trainer_profiles: {{
      title: "Trainer Profiles",
      summary: "Trainer cards highlight coaching type, availability, and consultation options.",
      cards: [["Riya Kapoor", "Strength and HIIT"], ["Kabir Mehta", "Mobility and yoga"], ["Neha Singh", "Diet consultation"]]
    }},
    class_booking: {{
      title: "Class Booking",
      summary: "A realistic class booking preview with member, mobile, date, class, and message fields.",
      formType: "booking",
      serviceOptions: ["HIIT Class", "Yoga Session", "Strength Coaching"]
    }},
    attendance_tracking: {{
      title: "Attendance Tracking",
      summary: "Track check-ins, weekly attendance rate, and missed-session follow-ups.",
      cards: [["Ananya Rao", "Checked in"], ["Karan Singh", "HIIT at 7 PM"], ["Weekly Rate", "91%"]]
    }},
    diet_consultation: {{
      title: "Diet Consultation",
      summary: "Preview diet consultation requests and trainer follow-up notes.",
      cards: [["Consultation", "Follow-up due"], ["Goal", "Fat loss plan"], ["Coach Note", "Review on Friday"]]
    }},
    payment_dashboard: {{
      title: "Payment Dashboard",
      summary: "Membership payments, trainer add-ons, and pending invoices in one screen.",
      cards: [["Monthly Revenue", `${{MONEY.monthlyRevenue}}`], ["Paid Members", "248"], ["Pending", "18 invoices"]]
    }}
  }},
  wedding_venue: {{
    dashboard: {{
      title: "Dashboard",
      summary: "Booking lead, package, enquiry, and date-hold overview for the venue manager.",
      cards: [["Booking Leads", "24 this week"], ["Date Holds", "8 active"], ["Package Revenue", `${{MONEY.weddingPipeline}}`]]
    }},
    wedding_packages: {{
      title: "Wedding Packages",
      summary: "Families compare Haldi, Mehendi, lawn booking, banquet package, and full wedding options.",
      cards: [["Haldi Theme", `${{MONEY.weddingPackage}} outdoor decor`], ["Mehendi Theme", `${{MONEY.weddingPremium}} family lounge`], ["Royal Wedding", `${{MONEY.weddingRoyal}} full venue`]]
    }},
    haldi_theme: {{
      title: "Haldi Theme",
      summary: "Theme screen for marigold decor, turmeric palette, lawn setup, and welcome drinks.",
      cards: [["Decor", "Marigold entry"], ["Lawn", "Outdoor ceremony"], ["Guest Flow", "Welcome drinks"]]
    }},
    mehendi_theme: {{
      title: "Mehendi Theme",
      summary: "Theme screen for stage seating, artist corner, photo wall, and lounge setup.",
      cards: [["Stage", "Family seating"], ["Artist Corner", "Mehendi stations"], ["Photo Wall", "Guest memories"]]
    }},
    gallery: {{
      title: "Gallery",
      summary: "Visual gallery sections for Haldi, Mehendi, lawn booking, and banquet package setups.",
      cards: [["Haldi Theme", "Yellow lawn setup"], ["Mehendi Theme", "Artist corner"], ["Lawn Booking", "Outdoor venue"], ["Banquet Package", "Premium indoor stage"]]
    }},
    booking_calendar: {{
      title: "Booking Calendar",
      summary: "Calendar preview for date holds, site visits, and confirmed events.",
      cards: [["24 Feb 2027", "Royal wedding hold"], ["02 Mar 2027", "Site visit"], ["15 Apr 2027", "Mehendi confirmed"]]
    }},
    enquiry_form: {{
      title: "Enquiry Form",
      summary: "A realistic enquiry preview with name, mobile, date, package, and message fields.",
      formType: "enquiry",
      serviceOptions: ["Haldi Theme", "Mehendi Theme", "Royal Wedding", "Lawn Booking", "Banquet Package"]
    }},
    admin_lead_dashboard: {{
      title: "Admin Lead Dashboard",
      summary: "Booking Lead status, quotations, site visits, and package interest for venue staff.",
      cards: [["Aarav & Meera", "Royal Wedding site visit"], ["Kapoor Family", "Banquet Package date hold"], ["Nisha Events", "Haldi Theme quotation"]]
    }}
  }},
  restaurant: {{
    dashboard: {{
      title: "Owner Dashboard",
      summary: "Orders, table reservations, kitchen queue, and revenue for today's service.",
      cards: [["Today Orders", "86 orders"], ["Reservations", "18 tables"], ["Revenue", `${{MONEY.dailyRevenue}}`]]
    }},
    menu: {{
      title: "Menu",
      summary: "Customer-facing menu cards with popular dishes, prices, and add-to-order actions.",
      cards: [["Chef Thali", `${{MONEY.serviceSmall}} lunch combo`], ["Paneer Tikka Bowl", `${{MONEY.basic}} bestseller`], ["Family Dinner Pack", `${{MONEY.serviceMedium}} bundle`]]
    }},
    food_ordering: {{
      title: "Food Ordering",
      summary: "A realistic order preview with customer, mobile, date, item, and notes.",
      formType: "order",
      serviceOptions: ["Chef Thali", "Paneer Tikka Bowl", "Family Dinner Pack"]
    }},
    table_booking: {{
      title: "Table Booking",
      summary: "Reservation screen for party size, preferred slot, and confirmation status.",
      formType: "booking",
      serviceOptions: ["Table for 2", "Table for 4", "Family table"]
    }},
    kitchen_queue: {{
      title: "Kitchen Queue",
      summary: "Live-style preparation cards for kitchen staff and owners.",
      cards: [["Order #2184", "Preparing"], ["Table 6", "Ready in 8 min"], ["Takeaway #2190", "Packed"]]
    }},
    payment_dashboard: {{
      title: "Payment Dashboard",
      summary: "Paid, pending, and refunded order states before real payment proxy wiring.",
      cards: [["Paid Orders", "72"], ["Pending", "9"], ["UPI Settled", `${{MONEY.settled}}`]]
    }},
    admin_dashboard: {{
      title: "Admin Dashboard",
      summary: "Owner view for reservations, sales records, popular dishes, and staff workload.",
      cards: [["Popular Dish", "Chef Thali"], ["Reservations", "18"], ["Repeat Customers", "41"]]
    }}
  }},
  clinic: {{
    dashboard: {{
      title: "Clinic Dashboard",
      summary: "Appointments, doctor schedule, queue status, follow-ups, and payments.",
      cards: [["Appointments", "42 today"], ["Queue", "8 waiting"], ["Open Slots", "11"]]
    }},
    appointments: {{
      title: "Appointments",
      summary: "A calm appointment form for patient details, doctor, date, and visit reason.",
      formType: "appointment",
      serviceOptions: ["General Consultation", "Dental Checkup", "Health Package"]
    }},
    doctor_schedule: {{
      title: "Doctor Schedule",
      summary: "Doctor availability, booked visits, and open consultation slots.",
      cards: [["Dr. Kapoor", "3 open slots"], ["Dr. Shah", "Fully booked"], ["Dental Wing", "2 slots"]]
    }},
    patients: {{
      title: "Patients",
      summary: "Patient enquiry and record preview for clinic staff.",
      cards: [["Meera Shah", "Checked in"], ["Ravi Jain", "Waiting"], ["Aditi Rao", "Follow-up due"]]
    }},
    queue_status: {{
      title: "Queue Status",
      summary: "Reception-ready queue board for waiting, checked-in, and completed visits.",
      cards: [["Waiting", "8 patients"], ["In consultation", "3"], ["Completed", "31"]]
    }},
    follow_ups: {{
      title: "Follow-ups",
      summary: "Follow-up reminders and care notes before notification proxy integration.",
      cards: [["Health Package", "Tomorrow"], ["Dental Review", "Friday"], ["Lab Report", "Call patient"]]
    }},
    admin_dashboard: {{
      title: "Admin Dashboard",
      summary: "Admin schedule, payments, queue, and daily clinic operations.",
      cards: [["Collections", `${{MONEY.collections}}`], ["Pending Bills", "6"], ["Reminders", "16"]]
    }}
  }},
  school: {{
    dashboard: {{
      title: IS_TUTOR_MODE ? "Tutor Dashboard" : "Parent Dashboard",
      summary: IS_TUTOR_MODE
        ? "Student batches, class schedule, attendance, homework, fees pending, and parent messages."
        : "Attendance, notices, homework, fees, exam results, and teacher contact.",
      cards: IS_TUTOR_MODE
        ? [["Student Batches", "6 active"], ["Attendance", "92%"], ["Fees Pending", "12 dues"]]
        : [["Attendance", "92%"], ["Homework", "3 due"], ["Fees", "Term 2 pending"]]
    }},
    students: {{
      title: "Students",
      summary: "Tutor-ready student records with batch, progress, and fee status.",
      cards: [["Aarohi Sharma", "Batch A"], ["Vivaan Mehta", "Fees pending"], ["Riya Patel", "Progress updated"]]
    }},
    classes: {{
      title: IS_TUTOR_MODE ? "Student Batches" : "Classes",
      summary: IS_TUTOR_MODE
        ? "Batch-wise view for tutoring groups, subject focus, and upcoming sessions."
        : "Class and section overview for school coordination.",
      cards: IS_TUTOR_MODE
        ? [["Batch A", "Math revision"], ["Batch B", "Science practice"], ["One-to-one", "English grammar"]]
        : [["Class 5A", "24 students"], ["Class 6B", "Homework pending"], ["Class 8", "Exam prep"]]
    }},
    schedule: {{
      title: "Class Schedule",
      summary: "Upcoming tutoring sessions, reschedules, and parent-visible timing updates.",
      cards: [["4:00 PM", "Batch A Math"], ["5:30 PM", "Science practice"], ["7:00 PM", "Parent review call"]]
    }},
    parent_portal: {{
      title: "Parent Portal",
      summary: "Parent-facing view with child status, notices, and teacher remarks.",
      cards: [["Aarohi Sharma", "Class 5A"], ["Teacher Remark", "Good progress"], ["Notice", "Sports day"]]
    }},
    attendance: {{
      title: "Attendance",
      summary: "Daily and monthly attendance view for parents and school admins.",
      cards: [["Today", "Present"], ["This Month", "92%"], ["Late Marks", "1"]]
    }},
    homework: {{
      title: "Homework",
      summary: "Homework assignments, due dates, and completion status.",
      cards: [["Math", "Due tomorrow"], ["Science", "Submitted"], ["English", "Reading task"]]
    }},
    fees: {{
      title: IS_TUTOR_MODE ? "Fees Pending" : "Fees",
      summary: IS_TUTOR_MODE
        ? "Pending fees, receipts, monthly dues, and reminder status for tutor collections."
        : "Fee status, receipts, reminders, and admin follow-up states.",
      cards: IS_TUTOR_MODE
        ? [["Aarohi Sharma", "Pending"], ["Batch B", "Paid"], ["July Reminder", "Ready"]]
        : [["Term 2", "Pending"], ["Transport", "Paid"], ["Receipt", "Ready"]]
    }},
    parent_messages: {{
      title: "Parent Messages",
      summary: "Tutor-to-parent updates for attendance, homework, and progress follow-up.",
      cards: [["Homework reminder", "Sent to 12 parents"], ["Attendance note", "3 pending replies"], ["Fee reminder", "Ready to send"]]
    }},
    student_progress: {{
      title: "Student Progress",
      summary: "Track concept coverage, weak topics, and tutor remarks for each student.",
      cards: [["Fractions", "Improving"], ["Reading", "Needs revision"], ["Weekly score", "82%"]]
    }},
    test_results: {{
      title: "Test Results",
      summary: "Recent test marks, batch comparisons, and follow-up coaching notes.",
      cards: [["Math Test", "18/20"], ["Science Quiz", "16/20"], ["Revision Test", "Scheduled"]]
    }},
    notes_assignments: {{
      title: "Notes & Assignments",
      summary: "Share notes, assignments, and homework follow-ups for each batch.",
      cards: [["Fractions worksheet", "Assigned"], ["Grammar notes", "Shared"], ["Science revision", "Due tomorrow"]]
    }},
    payment_reminders: {{
      title: "Payment Reminders",
      summary: "Payment reminder queue for overdue monthly tuition and coaching fees.",
      cards: [["Batch A", "3 reminders"], ["Riya Patel", "Due tomorrow"], ["Auto reminders", "Ready"]]
    }},
    parent_notices: {{
      title: "Parent Notices",
      summary: "School notices and announcements sent to parents.",
      cards: [["Sports Day", "Saturday"], ["PTM", "March 2"], ["Holiday", "Monday"]]
    }},
    exam_results: {{
      title: "Exam Results",
      summary: "Exam result cards with subject marks and teacher notes.",
      cards: [["Math", "88%"], ["Science", "91%"], ["English", "84%"]]
    }},
    teacher_contact: {{
      title: "Teacher Contact",
      summary: "Contact and meeting request preview for parents.",
      formType: "enquiry",
      serviceOptions: ["Class Teacher", "Math Teacher", "Admin Office"]
    }}
  }},
  retail: {{
    dashboard: {{
      title: "Inventory Dashboard",
      summary: "Stock cards, low-stock alerts, sales records, revenue, and product movement.",
      cards: [["Products", "312 SKUs"], ["Low Stock", "14 alerts"], ["Revenue", `${{MONEY.retailRevenue}}`]]
    }},
    product_catalog: {{
      title: "Product Catalog",
      summary: "Product cards with SKU, pricing, and stock context.",
      cards: [["Wireless Earbuds", "48 in stock"], ["Travel Backpack", "12 left"], ["Smart Watch", "PO pending"]]
    }},
    inventory: {{
      title: "Inventory",
      summary: "A stock update preview for product, SKU, quantity, and notes.",
      formType: "stock",
      serviceOptions: ["Wireless Earbuds", "Travel Backpack", "Smart Watch"]
    }},
    low_stock: {{
      title: "Low Stock",
      summary: "Low-stock alerts and reorder signals for store teams.",
      cards: [["Travel Backpack", "12 left"], ["Phone Stand", "6 left"], ["Water Bottle", "9 left"]]
    }},
    sales_records: {{
      title: "Sales Records",
      summary: "Recent sales, customer enquiries, payment status, and order records.",
      cards: [["Order #8841", "Paid"], ["Order #8842", "Pending"], ["Customer Enquiry", "Callback"]]
    }},
    revenue_dashboard: {{
      title: "Revenue Dashboard",
      summary: "Revenue, margin, and fast-moving product overview.",
      cards: [["Today Revenue", `${{MONEY.retailRevenue}}`], ["Top SKU", "Earbuds"], ["Margin", "31%"]]
    }},
    admin_dashboard: {{
      title: "Admin Dashboard",
      summary: "Admin operations for stock, orders, purchases, and payments.",
      cards: [["Purchase Orders", "7 open"], ["Supplier Updates", "4"], ["Low Stock", "14"]]
    }}
  }},
  agriculture: {{
    dashboard: {{
      title: "Farmer Dashboard",
      summary: "Crop health, weather, mandi prices, satellite intelligence, farmer profile, farm records, and AI chat.",
      cards: [["Crop Health", "86% stable"], ["Weather", "Low risk"], ["Mandi Rate", `${{MONEY.mandiRate}}`]]
    }},
    crop: {{
      title: "Crop Health",
      summary: "Field cards for crop condition, scouting priority, and disease risk.",
      cards: [["North Field", "Wheat healthy"], ["Soil Moisture", "Good"], ["Scout Priority", "Medium"]]
    }},
    weather: {{
      title: "Weather",
      summary: "Weather cards for rain window, temperature, and irrigation planning.",
      cards: [["Rain Window", "Low chance"], ["Temperature", "29 C"], ["Irrigation", "Tomorrow"]]
    }},
    mandi: {{
      title: "Mandi Prices",
      summary: "Mandi price cards and buyer signals for farmers and FPO teams.",
      cards: [["Wheat", `${{MONEY.mandiRate}}`], ["Soybean", `${{MONEY.mandiSoybean}}`], ["Buyer Interest", "3 calls"]]
    }},
    satellite: {{
      title: "Satellite Intelligence",
      summary: "Satellite intelligence cards for NDVI-style field health and action planning.",
      cards: [["Vegetation", "Stable"], ["Risk", "Low"], ["Task", "Scout west patch"]]
    }},
    profile: {{
      title: "Farmer Profile",
      summary: "Farmer profile with crop, acreage, advisory state, and contact readiness.",
      cards: [["Ramesh Patel", "8 acres"], ["Crop", "Wheat"], ["Advisory", "Sent"]]
    }},
    records: {{
      title: "Farm Records",
      summary: "Farm records for acreage, crop history, soil health, irrigation, and advisory notes.",
      cards: [["North Farm", "8 acres"], ["Soil Health", "Good"], ["Irrigation", "Tomorrow"]]
    }},
    chat: {{
      title: "AI Chat",
      summary: "AI chat button and advisory form for crop, date, field status, and next action.",
      formType: "stock",
      serviceOptions: ["Crop Health Update", "Weather Advisory", "Mandi Follow-up"]
    }},
    admin: {{
      title: "Admin Dashboard",
      summary: "Admin dashboard for farmer records, alerts, recommendations, and FPO team follow-up.",
      cards: [["Farmers", "128"], ["Alerts", "9"], ["Recommendations", "24"]]
    }}
  }},
  government: {{
    dashboard: {{
      title: "Civic Dashboard",
      summary: "Citizen services, officer reviews, application status, audit cards, and department metrics.",
      cards: [["Citizen Services", "74 active"], ["Officer Reviews", "18 pending"], ["Audit Status", "96% verified"]]
    }},
    citizen_services: {{
      title: "Citizen Services",
      summary: "Official service cards for certificates, requests, scheme applications, and status.",
      cards: [["Certificate", "Officer review"], ["Water Request", "In progress"], ["Scheme Form", "Verified"]]
    }},
    officer_dashboard: {{
      title: "Officer Dashboard",
      summary: "Officer workload, pending applications, SLA status, and next review actions.",
      cards: [["Ward 12", "11 pending"], ["SLA", "4 near due"], ["Reviews", "18 today"]]
    }},
    application_tracker: {{
      title: "Application Tracker",
      summary: "Status tracker for citizen applications and department routing.",
      cards: [["CERT-4821", "Officer review"], ["MUNI-2098", "Assigned"], ["SCHEME-112", "Verified"]]
    }},
    audit_status: {{
      title: "Audit Status",
      summary: "Audit cards show verification, officer trail, and official status.",
      cards: [["Verified", "96%"], ["Needs Review", "4 files"], ["Officer Trail", "Complete"]]
    }},
    service_request: {{
      title: "Service Request",
      summary: "A civic service request form for citizen details, service type, date, and notes.",
      formType: "enquiry",
      serviceOptions: ["Certificate", "Municipal Request", "Scheme Application"]
    }},
    department_metrics: {{
      title: "Department Metrics",
      summary: "Department-level metrics for services, officer workload, and audit status.",
      cards: [["Services", "74"], ["Officers", "18"], ["Pending", "11"]]
    }}
  }}
}};

SCREEN_CONFIG.generic = {{
  dashboard: {{
    title: {json.dumps(plan["app_name"])},
    summary: {json.dumps(plan["preview_summary"])},
    cards: {json.dumps([[item, "Registry-backed screen"] for item in plan["screens"][:6]], ensure_ascii=False)}
  }}
}};
if (!SCREEN_CONFIG[APP_DOMAIN]) {{
  SCREEN_CONFIG[APP_DOMAIN] = SCREEN_CONFIG.generic;
}}
SCREEN_CONFIG[APP_DOMAIN] = Object.assign({{}}, SCREEN_CONFIG[APP_DOMAIN] || {{}}, BLUEPRINT_SCREEN_CONFIG);

const SCREEN_ALIASES = {{
  dashboard: "dashboard",
  preview: "dashboard",
  view_packages: APP_DOMAIN === "wedding_venue" ? "wedding_packages" : APP_DOMAIN === "gym" ? "membership_plans" : "service_packages",
  send_enquiry: APP_DOMAIN === "wedding_venue" ? "enquiry_form" : APP_DOMAIN === "mutual_fund_advisor" ? "enquiry" : "teacher_contact",
  gallery: APP_DOMAIN === "car_detailing" ? "before_after_gallery" : "gallery",
  admin: APP_DOMAIN === "wedding_venue" ? "admin_lead_dashboard" : APP_DOMAIN === "agriculture" || APP_DOMAIN === "mutual_fund_advisor" ? "admin" : "admin_dashboard",
  trainers: "trainer_profiles",
  payments: APP_DOMAIN === "gym" ? "payment_dashboard" : "payment_status",
  book_package: "service_packages",
  compare_package: "wedding_packages",
  choose_plan: "membership_plans",
  book_class: "class_booking",
  submit_booking: "doorstep_booking",
  add_to_order: "food_ordering",
  send_order: "food_ordering",
  order_food: "food_ordering",
  book_table: "table_booking",
  book_visit: "appointments",
  confirm_appointment: "appointments",
  book_appointment: "appointments",
  doctor_schedule: "doctor_schedule",
  view_module: "parent_portal",
  send_notice: "parent_notices",
  parent_messages: "parent_messages",
  student_progress: "student_progress",
  test_results: "test_results",
  notes_assignments: "notes_assignments",
  payment_reminders: "payment_reminders",
  parent_portal: "parent_portal",
  attendance: "attendance",
  save_stock: "inventory",
  update_stock: "inventory",
  sales_dashboard: "revenue_dashboard",
  view_quote: "quote_builder",
  quote_builder: "quote_builder",
  policy_cards: "policy_cards",
  claim_tracker: "claim_tracker",
  advisor_contacts: "advisor_contacts",
  compare_funds: "compare",
  compare: "compare",
  mutual_fund_categories: "funds",
  fund_categories: "funds",
  funds: "funds",
  sip_calculator: "sip",
  sip: "sip",
  sip_reminders: "reminders",
  reminders: "reminders",
  portfolio_tracker: "portfolio",
  portfolio: "portfolio",
  kyc_upload: "kyc",
  kyc_document_upload: "kyc",
  kyc: "kyc",
  risk_profile: "risk",
  risk: "risk",
  advisor_booking: "advisor",
  book_advisor: "advisor",
  customer_enquiry: "enquiry",
  enquiry: "enquiry",
  crop: "crop",
  crop_health: "crop",
  weather: "weather",
  mandi: "mandi",
  mandi_prices: "mandi",
  satellite_intelligence: "satellite",
  satellite: "satellite",
  farmer_profile: "profile",
  profile: "profile",
  farm_records: "records",
  records: "records",
  ai_chat: "chat",
  chat: "chat",
  admin_dashboard: APP_DOMAIN === "agriculture" || APP_DOMAIN === "mutual_fund_advisor" ? "admin" : "admin_dashboard",
  view_field: "crop",
  save_update: "chat",
  citizen_services: "citizen_services",
  officer_dashboard: "officer_dashboard",
  track_status: "application_tracker",
  audit_status: "audit_status",
  submit_request: "service_request"
}};

Object.assign(SCREEN_ALIASES, REGISTRY_SCREEN_ALIASES);

// TODO: Add API key billing layer before enabling paid runtime services.
// TODO: Add runtime usage metering for every backend proxy call.
// TODO: Route all third-party keys through the backend safety gateway before public launch.
// TODO: Add illegal-usage blocking before API key issuance.
function slugFromLabel(label) {{
  return String(label || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}}

function cardMarkup(cards) {{
  return `<div class="screen-card-grid">${{(cards || []).map(([title, detail]) => `
    <article class="screen-card" role="button" tabindex="0" data-screen="${{slugFromLabel(title)}}"><strong>${{title}}</strong><span>${{detail}}</span></article>
  `).join("")}}</div>`;
}}

function formMarkup(screen) {{
  const options = (screen.serviceOptions || ["Service Package"]).map((option) => `<option>${{option}}</option>`).join("");
  const actions = {{
    appointment: "Confirm Appointment",
    booking: "Submit Booking",
    enquiry: "Send Enquiry",
    order: "Send Order",
    stock: "Save Stock",
    sip: "Estimate SIP",
    risk: "Save Risk Profile"
  }};
  const action = actions[screen.formType] || "Submit";
  return `
    <form class="screen-form" data-local-form>
      <label>Name<input name="name" value="Priya Sharma"></label>
      <label>Mobile<input name="mobile" value="+91 98765 43210"></label>
      <label>Date<input name="date" type="date" value="2027-02-24"></label>
      <label>Service / Package<select name="service">${{options}}</select></label>
      <label>Message<textarea name="message">Please confirm availability and next steps.</textarea></label>
      <button type="submit">${{action}}</button>
      <span class="form-success" role="status"></span>
    </form>
  `;
}}

function renderScreen(screenKey, shouldScroll = true) {{
  const config = SCREEN_CONFIG[APP_DOMAIN] || {{}};
  const key = SCREEN_ALIASES[screenKey] || screenKey || "dashboard";
  const screen = config[key] || config.dashboard;
  const panel = document.querySelector(".interactive-screen-panel");
  if (!panel || !screen) return;
  const showClose = key !== "dashboard";
  panel.innerHTML = `
    <div class="section-heading-row">
      <div class="section-heading">
        <span class="eyebrow">Active screen</span>
        <h2>${{screen.title}}</h2>
      </div>
      <button type="button" class="screen-panel-close" data-screen-close="dashboard" ${{showClose ? "" : "hidden"}}>Close</button>
    </div>
    <p>${{screen.summary}}</p>
    ${{screen.formType ? formMarkup(screen) : cardMarkup(screen.cards)}}
  `;
  document.querySelectorAll("[data-screen]").forEach((button) => {{
    const candidate = SCREEN_ALIASES[button.dataset.screen] || button.dataset.screen;
    button.classList.toggle("is-active", candidate === key);
  }});
  if (shouldScroll) {{
    panel.scrollIntoView({{ behavior: "smooth", block: "start" }});
  }}
}}

document.addEventListener("click", (event) => {{
  const closeButton = event.target.closest("[data-screen-close]");
  if (closeButton) {{
    renderScreen(closeButton.dataset.screenClose || "dashboard", false);
    return;
  }}
  const target = event.target.closest("button, .screen-card, .package-card, .metric-grid article, .gallery-grid span, .feature-card, .screen-section");
  if (!target) return;
  target.dataset.clicked = "true";
  const screenKey = target.dataset.screen || slugFromLabel(target.textContent);
  renderScreen(screenKey);
}});

document.addEventListener("keydown", (event) => {{
  if (!["Enter", " "].includes(event.key)) return;
  const target = event.target.closest(".screen-card, .package-card, .metric-grid article, .gallery-grid span, .feature-card, .screen-section");
  if (!target) return;
  event.preventDefault();
  target.dataset.clicked = "true";
  renderScreen(target.dataset.screen || slugFromLabel(target.textContent));
}});

document.addEventListener("submit", (event) => {{
  const form = event.target.closest("[data-local-form]");
  if (!form) return;
  event.preventDefault();
  const success = form.querySelector(".form-success");
  if (success) {{
    success.textContent = "Saved locally for preview. Backend submission will use a runtime proxy later.";
  }}
}});

renderScreen("dashboard", false);

window.generatedAppRuntime = {{
  appId: APP_ID,
  apiProxyPlaceholders: API_PROXY_PLACEHOLDERS,
  secretsInFrontend: false,
}};
"""
    return _strip_inactive_domain_aliases(_strip_universal_screen_config(script), domain)


def generate_static_app(plan: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_product_plan(plan)
    from backend.blueprint_ui_adapter import apply_blueprint_to_generated_plan as _phase33c_apply_blueprint
    normalized = _phase33c_apply_blueprint(normalized, user_text=str(plan.get('source_prompt_hint') or plan.get('user_text') or ''))
    app_id = f"{_slugify(normalized['app_name'])}-{uuid4().hex[:8]}"
    visual_theme = select_visual_theme(normalized, app_id)
    normalized["visual_theme"] = visual_theme
    if visual_theme.get("image_guided_design_note"):
        normalized["design_inspiration_note"] = visual_theme["image_guided_design_note"]
    backend_dir = BACKEND_GENERATED_APPS_DIR / app_id
    files = {
        "index.html": _build_html(normalized, app_id),
        "style.css": _build_css(),
        "app.js": _build_js(app_id, normalized),
        "manifest.json": json.dumps(
            {
                "app_id": app_id,
                "app_name": normalized["app_name"],
                "app_type": normalized["app_type"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "preview_url": f"/generated-apps/{app_id}/index.html",
                "source": "phase-32a-visual-theme-generator",
                "sector_id": normalized.get("sector_id"),
                "sector_confidence": normalized.get("sector_confidence"),
                "sector_reasons": normalized.get("sector_reasons"),
                "theme_family": normalized.get("theme_family") or visual_theme.get("family"),
                "layout_family": normalized.get("layout_family") or visual_theme.get("layout_variant"),
                "currency_code": normalized.get("currency_code"),
                "currency_symbol": normalized.get("currency_symbol"),
                "currency_locale": normalized.get("currency_locale"),
                "country_hint": normalized.get("country_hint"),
                "input_mode": "image-guided" if normalized.get("image_guided") else "text-only",
                "image_guided": bool(normalized.get("image_guided")),
                "reference_image": normalized.get("reference_image") if normalized.get("image_guided") else None,
                "visual_theme": visual_theme,
                "design_inspiration_note": normalized.get("design_inspiration_note"),
                "quality": quality_notes_for_generated_app(normalized),
                "plan": normalized,
            },
            indent=2,
        ),
    }

    backend_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (backend_dir / name).write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "app_id": app_id,
        "preview_url": f"/generated-apps/{app_id}/index.html",
        "files": [str(backend_dir / name) for name in files],
        "plan": normalized,
    }

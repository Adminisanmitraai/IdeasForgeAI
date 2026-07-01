import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from backend.core.project_paths import PROJECT_ROOT


BACKEND_GENERATED_APPS_DIR = PROJECT_ROOT / "backend" / "generated_apps"


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


DOMAIN_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
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
        "keywords": ["gym", "fitness", "trainer", "membership"],
        "app_name": "Fit Membership Hub",
        "app_type": "gym membership and trainer booking app",
        "target_users": ["gym owners", "members", "trainers", "front desk admins"],
        "core_features": ["membership plans", "trainer booking", "class schedule", "attendance tracking", "payment status", "admin dashboard"],
        "screens": ["Home", "Membership Plans", "Trainer Booking", "Class Schedule", "Attendance", "Payment Status", "Admin Dashboard"],
        "data_needs": ["member name", "mobile number", "membership plan", "trainer", "class time", "payment status"],
        "api_needs": ["membership signup via backend proxy", "payment status via backend proxy", "optional SMS reminders via backend proxy"],
        "monetization": ["monthly gym subscription", "trainer session fees", "premium membership upsell"],
        "preview_summary": "Manage memberships, trainer bookings, class schedules, attendance, and payments in one gym app.",
    },
    "wedding_venue": {
        "keywords": ["wedding", "venue", "lawn", "event", "haldi", "mehendi", "banquet", "marriage"],
        "app_name": "Wedding Venue Booking",
        "app_type": "wedding venue booking app",
        "target_users": ["couples", "families", "wedding planners", "venue managers"],
        "core_features": [
            "venue packages",
            "photo/video gallery",
            "enquiry form",
            "booking lead capture",
            "package comparison",
            "admin dashboard",
            "enquiry management",
            "event date tracking",
        ],
        "screens": ["Home", "Packages", "Gallery", "Enquiry", "Booking Leads", "Admin Dashboard"],
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
        "preview_summary": "Manage packages, gallery, enquiries, and booking leads from one mobile-first app.",
    },
    "restaurant": {
        "keywords": ["restaurant", "menu", "table", "order", "food", "tiffin", "cafe"],
        "app_name": "Restaurant Order Hub",
        "app_type": "restaurant ordering app",
        "target_users": ["restaurant owners", "kitchen staff", "customers"],
        "core_features": ["menu catalog", "order capture", "table enquiries", "daily specials", "kitchen dashboard"],
        "screens": ["Home", "Menu", "Orders", "Reservations", "Admin Dashboard"],
        "data_needs": ["dish name", "price", "category", "order status", "customer mobile"],
        "api_needs": ["order submission via backend proxy", "payment gateway via backend proxy"],
        "monetization": ["monthly restaurant subscription", "online order fees", "premium menu listing"],
        "preview_summary": "Take menu orders, enquiries, and reservations from one mobile-first restaurant app.",
    },
    "school": {
        "keywords": ["school", "parents", "homework", "fees", "attendance", "education", "student", "teacher"],
        "app_name": "School Parent Connect",
        "app_type": "school parent communication and attendance app",
        "target_users": ["school admins", "teachers", "parents", "students"],
        "core_features": ["attendance tracking", "homework updates", "fee status", "parent notices", "class dashboard"],
        "screens": ["Home", "Attendance", "Homework", "Fees", "Parent Notices", "Admin Dashboard"],
        "data_needs": ["student name", "class", "attendance status", "homework", "fee status", "parent mobile"],
        "api_needs": ["parent notification via backend proxy", "fee status via backend proxy"],
        "monetization": ["monthly school subscription", "per-student communication plan"],
        "preview_summary": "Track attendance, homework, fees, and parent updates in one school communication app.",
    },
    "retail": {
        "keywords": ["shop", "inventory", "retail", "stock", "store", "catalog", "ecommerce"],
        "app_name": "Retail Inventory Hub",
        "app_type": "retail inventory app",
        "target_users": ["store owners", "sales staff", "inventory managers"],
        "core_features": ["product catalog", "inventory tracking", "sales dashboard", "customer enquiries"],
        "screens": ["Home", "Products", "Inventory", "Orders", "Admin Dashboard"],
        "data_needs": ["product name", "SKU", "price", "stock", "customer mobile"],
        "api_needs": ["inventory sync via backend proxy", "payment gateway via backend proxy"],
        "monetization": ["monthly store subscription", "premium catalog listing"],
        "preview_summary": "Track products, stock, sales, and customer enquiries from one retail dashboard.",
    },
    "clinic": {
        "keywords": ["clinic", "doctor", "dental", "patient", "appointment", "health"],
        "app_name": "Clinic Appointment Hub",
        "app_type": "clinic appointment app",
        "target_users": ["doctors", "clinic staff", "patients"],
        "core_features": ["appointment booking", "patient enquiries", "doctor schedule", "admin dashboard"],
        "screens": ["Home", "Appointments", "Patients", "Schedule", "Admin Dashboard"],
        "data_needs": ["patient name", "mobile", "appointment date", "doctor", "status"],
        "api_needs": ["appointment submission via backend proxy", "notification service via backend proxy"],
        "monetization": ["monthly clinic subscription", "appointment credits"],
        "preview_summary": "Manage appointments, patient enquiries, and schedules in a mobile-first clinic app.",
    },
}


def _detect_domain(text: str) -> str:
    lower_text = text.lower()
    tokens = set(re.findall(r"[a-z0-9]+", lower_text))
    for domain, blueprint in DOMAIN_BLUEPRINTS.items():
        for keyword in blueprint["keywords"]:
            normalized_keyword = keyword.lower()
            if " " in normalized_keyword:
                if normalized_keyword in lower_text:
                    return domain
            elif normalized_keyword in tokens:
                return domain
    return "generic"


def _domain_from_plan(plan: Dict[str, Any]) -> str:
    values = []
    for value in plan.values():
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return _detect_domain(" ".join(values))


def create_product_plan(idea: str) -> Dict[str, Any]:
    clean_idea = _clean_text(idea, "A useful mobile-first product")
    lower_idea = clean_idea.lower()
    domain = _detect_domain(clean_idea)

    if domain in DOMAIN_BLUEPRINTS:
        blueprint = DOMAIN_BLUEPRINTS[domain]
        return {
            "idea": clean_idea,
            "app_name": blueprint["app_name"],
            "app_type": blueprint["app_type"],
            "target_users": list(blueprint["target_users"]),
            "core_features": list(blueprint["core_features"]),
            "screens": list(blueprint["screens"]),
            "data_needs": list(blueprint["data_needs"]),
            "api_needs": list(blueprint["api_needs"]),
            "monetization": list(blueprint["monetization"]),
            "preview_summary": blueprint["preview_summary"],
            "next_action": "approve_generate",
        }

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
    elif any(word in lower_idea for word in ["student", "school", "course", "learn", "teacher"]):
        app_type = "education workflow app"
        target_users = ["students", "teachers", "parents"]
        data_needs = ["courses", "assignments", "progress", "resources"]
        api_needs = ["content library", "calendar reminders"]
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

    return {
        "idea": clean_idea,
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
        "next_action": "approve_generate",
    }


def normalize_product_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    idea = _clean_text(plan.get("idea") or plan.get("source_idea") or plan.get("preview_summary") or plan.get("product_name"))
    domain_text = " ".join(
        str(item)
        for value in plan.values()
        for item in (value if isinstance(value, list) else [value])
    )
    idea_domain = _detect_domain(idea) if idea else "generic"
    plan_domain = _domain_from_plan(plan)
    normalized = create_product_plan(idea if idea_domain != "generic" else domain_text or idea or "Generated app prototype")
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


def _render_metric_cards(domain: str) -> str:
    metrics = {
        "car_detailing": [
            ("Daily Bookings", "18"),
            ("Revenue", "$4.6k"),
            ("Payment Status", "7 pending"),
            ("Completed Details", "42"),
        ],
        "gym": [("Active Members", "286"), ("Trainer Sessions", "34"), ("Renewals Due", "19"), ("Monthly Revenue", "$12.4k")],
        "wedding_venue": [
            ("Total Enquiries", "128"),
            ("Pending Bookings", "24"),
            ("Popular Package", "Royal"),
            ("Gallery Views", "4.8k"),
        ],
        "restaurant": [("Today Orders", "86"), ("Pending Tables", "12"), ("Top Item", "Chef Special"), ("Repeat Guests", "41%")],
        "school": [("Attendance", "92%"), ("Homework Due", "38"), ("Fees Pending", "17"), ("Parent Updates", "19")],
        "retail": [("Total Products", "312"), ("Low Stock", "14"), ("Today Orders", "57"), ("Revenue", "$8.2k")],
        "clinic": [("Appointments", "42"), ("Waiting", "8"), ("Follow-ups", "16"), ("Open Slots", "11")],
    }.get(domain, [("Active Records", "1,248"), ("Open Tasks", "36"), ("New Leads", "18"), ("Completion", "82%")])

    return "\n".join(
        f"<article><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></article>"
        for label, value in metrics
    )


def _render_wedding_venue_sections() -> str:
    packages = [
        ("Silver Wedding Package", "$2,499", "Up to 150 guests with decor starter kit"),
        ("Premium Wedding Package", "$4,999", "Up to 300 guests with catering and photo zones"),
        ("Royal Wedding Package", "$8,999", "Full venue, premium decor, VIP support, and event desk"),
    ]
    package_cards = "\n".join(
        f"""
        <article class="package-card">
          <span>{html.escape(price)}</span>
          <h3>{html.escape(name)}</h3>
          <p>{html.escape(detail)}</p>
          <button type="button">Compare Package</button>
        </article>"""
        for name, price, detail in packages
    )
    leads = [
        ("Aarav & Meera", "Premium Wedding Package", "Site visit booked"),
        ("Kapoor Family", "Royal Wedding Package", "Date hold pending"),
        ("Nisha Events", "Silver Wedding Package", "Quotation sent"),
    ]
    lead_rows = "\n".join(
        f"<li><strong>{html.escape(name)}</strong><span>{html.escape(package)}</span><em>{html.escape(status)}</em></li>"
        for name, package, status in leads
    )
    return f"""
    <section class="content-block">
      <div class="section-heading">
        <span class="eyebrow">Packages</span>
        <h2>Wedding venue packages</h2>
      </div>
      <div class="package-grid">{package_cards}</div>
    </section>

    <section class="content-block gallery-panel">
      <div class="section-heading">
        <span class="eyebrow">Gallery</span>
        <h2>Photo and video showcase</h2>
      </div>
      <div class="gallery-grid">
        <span>Mandap Decor</span>
        <span>Banquet Hall</span>
        <span>Outdoor Lawn</span>
        <span>Reception Stage</span>
      </div>
    </section>

    <section class="content-block enquiry-admin-grid">
      <article class="enquiry-card">
        <span class="eyebrow">Enquiry form preview</span>
        <h2>Capture booking leads</h2>
        <label>Customer name<input value="Priya Sharma" readonly></label>
        <label>Event date<input value="24 Feb 2027" readonly></label>
        <label>Guest capacity<input value="300 guests" readonly></label>
        <button type="button">Send Enquiry</button>
      </article>
      <article class="admin-card">
        <span class="eyebrow">Admin dashboard preview</span>
        <h2>Lead status list</h2>
        <ul>{lead_rows}</ul>
      </article>
    </section>"""


def _render_car_detailing_sections() -> str:
    packages = [
        ("Express Wash", "$29", "Exterior foam wash, tyre shine, and quick interior vacuum"),
        ("Interior Deep Clean", "$79", "Seats, mats, dashboard, odor treatment, and stain care"),
        ("Premium Ceramic Detail", "$249", "Paint polish, ceramic coating prep, and premium finish protection"),
    ]
    package_cards = "\n".join(
        f"""
        <article class="package-card">
          <span>{html.escape(price)}</span>
          <h3>{html.escape(name)}</h3>
          <p>{html.escape(detail)}</p>
          <button type="button">Book Package</button>
        </article>"""
        for name, price, detail in packages
    )
    bookings = [
        ("Doorstep Booking", "SUV ceramic detail", "Today 4:30 PM"),
        ("Booking Calendar", "Interior deep clean", "Tomorrow 10:00 AM"),
        ("Payment Status", "Express wash", "Paid"),
        ("Admin Dashboard", "Daily Bookings", "Revenue $4.6k"),
    ]
    booking_rows = "\n".join(
        f"<li><strong>{html.escape(name)}</strong><span>{html.escape(detail)}</span><em>{html.escape(status)}</em></li>"
        for name, detail, status in bookings
    )
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
        <span>Exterior Shine</span>
        <span>Interior Reset</span>
        <span>Wheel Detail</span>
        <span>Ceramic Finish</span>
      </div>
    </section>

    <section class="content-block enquiry-admin-grid">
      <article class="enquiry-card">
        <span class="eyebrow">Doorstep Booking</span>
        <h2>Customer enquiry form</h2>
        <label>Customer name<input value="Rohan Mehta" readonly></label>
        <label>Vehicle type<input value="Premium SUV" readonly></label>
        <label>Booking date<input value="Today, 4:30 PM" readonly></label>
        <button type="button">Submit Booking</button>
      </article>
      <article class="admin-card">
        <span class="eyebrow">Admin Dashboard</span>
        <h2>Booking calendar and revenue</h2>
        <ul>{booking_rows}</ul>
      </article>
    </section>"""


def _render_domain_sections(domain: str, plan: Dict[str, Any]) -> str:
    if domain == "car_detailing":
        return _render_car_detailing_sections()

    if domain == "wedding_venue":
        return _render_wedding_venue_sections()

    return f"""
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


def _build_html(plan: Dict[str, Any]) -> str:
    app_name = html.escape(plan["app_name"])
    app_type = html.escape(plan["app_type"])
    summary = html.escape(plan["preview_summary"])
    domain = _domain_from_plan(plan)
    if domain == "wedding_venue":
        primary_action = "View Packages"
        secondary_action = "Send Enquiry"
    elif domain == "car_detailing":
        primary_action = "Service Packages"
        secondary_action = "Doorstep Booking"
    else:
        primary_action = "Start workflow"
        secondary_action = "View dashboard"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{app_name}</title>
  <link rel="manifest" href="./manifest.json">
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <main class="app-shell">
    <header class="hero">
      <nav class="top-nav" aria-label="Prototype navigation">
        <strong>{app_name}</strong>
        <button type="button">Preview</button>
      </nav>
      <section class="hero-content">
        <span class="eyebrow">{app_type}</span>
        <h1>{app_name}</h1>
        <p>{summary}</p>
        <div class="hero-actions">
          <button type="button">{html.escape(primary_action)}</button>
          <button type="button" class="ghost-button">{html.escape(secondary_action)}</button>
        </div>
      </section>
    </header>

    <section class="metric-grid" aria-label="Dashboard metrics">
      {_render_metric_cards(domain)}
    </section>

    {_render_domain_sections(domain, plan)}

    <section class="content-block data-panel">
      <div>
        <span class="eyebrow">Data model</span>
        <h2>Placeholder data needs</h2>
        <ul>{_render_list(plan["data_needs"])}</ul>
      </div>
      <div>
        <span class="eyebrow">API ready</span>
        <h2>Backend proxy placeholders</h2>
        <ul>{_render_list([f"/api/runtime/{{app_id}}/{_slugify(service)}" for service in plan["api_needs"]] or ["/api/runtime/{app_id}/future-service"])}</ul>
      </div>
      <div>
        <span class="eyebrow">Monetization</span>
        <h2>Business model</h2>
        <ul>{_render_list(plan["monetization"] if isinstance(plan["monetization"], list) else [plan["monetization"]])}</ul>
      </div>
    </section>
  </main>
  <script src="./app.js"></script>
</body>
</html>
"""


def _build_css() -> str:
    return """:root {
  color-scheme: light;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f6f7fb;
  color: #171923;
}

* { box-sizing: border-box; }
body { margin: 0; background: #f6f7fb; }
button { border: 0; font: inherit; cursor: pointer; }
.app-shell { min-height: 100svh; padding: 14px; }
.hero { overflow: hidden; border-radius: 28px; background: linear-gradient(135deg, #171923, #314159); color: #fff; }
.top-nav { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 16px; }
.top-nav strong { overflow-wrap: anywhere; font-size: 15px; }
.top-nav button, .hero-actions button, .screen-section button { min-height: 42px; border-radius: 999px; padding: 0 15px; background: #fff; color: #171923; font-weight: 800; }
.hero-content { display: grid; gap: 16px; padding: 42px 18px 28px; }
.eyebrow, .screen-kicker { color: #6d5dfc; font-size: 11px; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }
.hero .eyebrow { color: #b9d6ff; }
h1, h2, h3, p { margin: 0; }
h1 { max-width: 720px; font-size: clamp(34px, 8vw, 68px); line-height: .96; letter-spacing: 0; }
.hero p { max-width: 620px; color: rgba(255,255,255,.78); font-size: 16px; line-height: 1.55; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.hero-actions .ghost-button { background: rgba(255,255,255,.12); color: #fff; outline: 1px solid rgba(255,255,255,.25); }
.metric-grid, .feature-grid, .package-grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); margin-top: 14px; }
.metric-grid article, .feature-card, .screen-section, .data-panel, .package-card, .enquiry-card, .admin-card, .gallery-panel { border: 1px solid #e4e7ef; border-radius: 18px; background: #fff; box-shadow: 0 14px 34px rgba(36,42,66,.08); }
.metric-grid article { display: grid; gap: 6px; padding: 16px; }
.metric-grid span { color: #697184; font-size: 12px; font-weight: 750; }
.metric-grid strong { font-size: 28px; }
.content-block { display: grid; gap: 14px; margin-top: 26px; }
.section-heading { display: grid; gap: 6px; }
.section-heading h2, .data-panel h2 { font-size: 24px; line-height: 1.1; }
.feature-card { display: grid; gap: 12px; min-height: 168px; padding: 18px; }
.feature-card span { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 14px; background: #f0edff; color: #6d5dfc; font-weight: 900; }
.feature-card h3 { font-size: 18px; line-height: 1.2; }
.feature-card p, .screen-section p { color: #697184; font-size: 14px; line-height: 1.5; }
.screen-list { display: grid; gap: 12px; }
.screen-section { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px; }
.screen-section button { flex: 0 0 auto; background: #171923; color: #fff; }
.data-panel { display: grid; gap: 18px; padding: 18px; }
.data-panel ul { display: grid; gap: 8px; margin: 10px 0 0; padding-left: 18px; color: #3c4354; }
.package-card { display: grid; gap: 12px; padding: 18px; }
.package-card span { color: #6d5dfc; font-size: 22px; font-weight: 900; }
.package-card button, .enquiry-card button { min-height: 42px; border-radius: 999px; background: #171923; color: #fff; font-weight: 850; }
.gallery-panel { padding: 18px; }
.gallery-grid { display: grid; gap: 10px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 12px; }
.gallery-grid span { display: grid; min-height: 110px; place-items: end start; padding: 14px; border-radius: 16px; background: linear-gradient(135deg, #fff2f6, #edf4ff); color: #33394a; font-weight: 850; }
.enquiry-admin-grid { display: grid; gap: 14px; }
.enquiry-card, .admin-card { display: grid; gap: 12px; padding: 18px; }
.enquiry-card label { display: grid; gap: 6px; color: #5f6677; font-size: 13px; font-weight: 750; }
.enquiry-card input { width: 100%; min-height: 42px; border: 1px solid #e4e7ef; border-radius: 12px; padding: 0 12px; color: #171923; font: inherit; }
.admin-card ul { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
.admin-card li { display: grid; gap: 3px; padding: 12px; border-radius: 14px; background: #f7f8fc; }
.admin-card li span { color: #697184; font-size: 13px; }
.admin-card li em { color: #6d5dfc; font-size: 12px; font-style: normal; font-weight: 850; }
@media (max-width: 640px) {
  .app-shell { padding: 72px 10px 10px; }
  .hero { border-radius: 22px; }
  .screen-section { align-items: flex-start; flex-direction: column; }
  .screen-section button { width: 100%; }
}
@media (min-width: 860px) {
  .app-shell { max-width: 1160px; margin: 0 auto; padding: 20px; }
  .hero-content { padding: 72px 42px 46px; }
  .data-panel { grid-template-columns: 1fr 1fr; }
  .enquiry-admin-grid { grid-template-columns: 1fr 1fr; }
}
"""


def _build_js(app_id: str, plan: Dict[str, Any]) -> str:
    api_services = [_slugify(service) for service in plan["api_needs"]] or ["future-service"]
    return f"""const APP_ID = {json.dumps(app_id)};
const API_PROXY_PLACEHOLDERS = {json.dumps([f"/api/runtime/{app_id}/{service}" for service in api_services])};

// TODO: Add API key billing layer before enabling paid runtime services.
// TODO: Add runtime usage metering for every backend proxy call.
// TODO: Route all third-party keys through the backend safety gateway before public launch.
// TODO: Add illegal-usage blocking before API key issuance.
document.querySelectorAll("button").forEach((button) => {{
  button.addEventListener("click", () => {{
    button.dataset.clicked = "true";
  }});
}});

window.generatedAppRuntime = {{
  appId: APP_ID,
  apiProxyPlaceholders: API_PROXY_PLACEHOLDERS,
  secretsInFrontend: false,
}};
"""


def generate_static_app(plan: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_product_plan(plan)
    app_id = f"{_slugify(normalized['app_name'])}-{uuid4().hex[:8]}"
    backend_dir = BACKEND_GENERATED_APPS_DIR / app_id
    files = {
        "index.html": _build_html(normalized).replace("{app_id}", app_id),
        "style.css": _build_css(),
        "app.js": _build_js(app_id, normalized),
        "manifest.json": json.dumps(
            {
                "app_id": app_id,
                "app_name": normalized["app_name"],
                "app_type": normalized["app_type"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "preview_url": f"/generated-apps/{app_id}/index.html",
                "source": "phase-29b-static-prototype",
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

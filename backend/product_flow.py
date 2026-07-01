import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from backend.core.project_paths import PROJECT_ROOT


BACKEND_GENERATED_APPS_DIR = PROJECT_ROOT / "backend" / "generated_apps"
MAX_REFERENCE_IMAGE_TEXT_LENGTH = 1200
REFERENCE_IMAGE_KEYS = {"referenceImage", "reference_image", "imageReference", "image_metadata"}


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
        "keywords": ["school", "parents", "homework", "fees", "attendance", "education", "student", "teacher"],
        "app_name": "School Parent Connect",
        "app_type": "school parent communication and attendance app",
        "target_users": ["school admins", "teachers", "parents", "students"],
        "core_features": ["attendance tracking", "homework updates", "fee status", "parent notices", "teacher remarks", "student records", "class dashboard"],
        "screens": ["Home", "Parent Portal", "Attendance", "Homework", "Fees", "Parent Notices", "Student Records", "Admin Dashboard"],
        "data_needs": ["student name", "class", "attendance status", "homework", "fee status", "parent mobile", "teacher remarks"],
        "api_needs": ["parent notification via backend proxy", "fee status via backend proxy", "attendance sync via backend proxy"],
        "monetization": ["monthly school subscription", "per-student communication plan", "premium analytics for administrators"],
        "preview_summary": "Give parents a clear portal for attendance, homework, fee status, notices, teacher remarks, and student records.",
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
        "keywords": ["clinic", "doctor", "dental", "patient", "appointment", "health"],
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


def create_product_plan(idea: str, reference_image: Dict[str, Any] | None = None) -> Dict[str, Any]:
    clean_idea = _clean_text(idea, "A useful mobile-first product")
    lower_idea = clean_idea.lower()
    domain = _detect_domain(clean_idea)
    reference_image = reference_image or {}

    if domain in DOMAIN_BLUEPRINTS:
        blueprint = DOMAIN_BLUEPRINTS[domain]
        return _apply_image_guidance({
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
        }, reference_image)

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

    return _apply_image_guidance({
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
    }, reference_image)


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


def _render_metric_cards(domain: str) -> str:
    metrics = {
        "car_detailing": [
            ("Daily Bookings", "18"),
            ("Revenue", "$4.6k"),
            ("Payment Status", "7 pending"),
            ("Customer Leads", "31"),
        ],
        "gym": [("Member Records", "286"), ("Class Bookings", "34"), ("Attendance", "91%"), ("Payment Dashboard", "$12.4k")],
        "wedding_venue": [
            ("Total Enquiries", "128"),
            ("Booking Leads", "24"),
            ("Lawn Bookings", "17"),
            ("Package Revenue", "₹84L"),
        ],
        "restaurant": [("Today Orders", "86"), ("Kitchen Queue", "12"), ("Table Bookings", "18"), ("Revenue", "$6.8k")],
        "school": [("Attendance", "92%"), ("Homework Due", "38"), ("Fees Pending", "17"), ("Parent Updates", "19")],
        "retail": [("Total Products", "312"), ("Low Stock", "14"), ("Today Orders", "57"), ("Revenue", "$8.2k")],
        "clinic": [("Appointments", "42"), ("Queue Status", "8 waiting"), ("Follow-ups", "16"), ("Open Slots", "11")],
    }.get(domain, [("Workflow Items", "1,248"), ("Approvals Due", "36"), ("New Requests", "18"), ("Completion", "82%")])

    return "\n".join(
        f"<article><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></article>"
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


def _domain_screen_labels(domain: str, plan: Dict[str, Any]) -> List[str]:
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


def _domain_theme_class(domain: str) -> str:
    return f"theme-{domain.replace('_', '-')}" if domain != "generic" else "theme-generic"


def _render_app_visual(domain: str) -> str:
    visual = {
        "car_detailing": ("Detail route", "Ceramic SUV", "Paid", ["Foam wash", "Interior reset", "Coating prep"]),
        "gym": ("Tonight", "HIIT 7 PM", "34 booked", ["Strength", "Yoga", "Diet consult"]),
        "wedding_venue": ("Date hold", "Royal Lawn", "Visit booked", ["Haldi", "Mehendi", "Reception"]),
        "restaurant": ("Kitchen", "Order #2184", "8 min", ["Thali", "Table 6", "Paid"]),
        "clinic": ("Queue", "Dr. Kapoor", "3 slots", ["Checked in", "Follow-up", "Invoice"]),
        "school": ("Parent view", "Class 5A", "92%", ["Homework", "Fees", "Notice"]),
        "retail": ("Stock desk", "Backpack", "12 left", ["Low stock", "Sales", "PO sent"]),
    }.get(domain, ("Workspace", "Live preview", "82%", ["Intake", "Review", "Dashboard"]))
    title, focus, status, chips = visual
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


def _render_wedding_venue_sections() -> str:
    packages = [
        ("Haldi Theme", "₹2.49L", "Outdoor lawn booking, marigold decor, turmeric color palette, and welcome drinks"),
        ("Mehendi Theme", "₹4.99L", "Stage seating, artist corner, photo wall, and family lounge setup"),
        ("Royal Wedding", "₹8.99L", "Full venue, banquet package, premium decor, catering coordination, and VIP support desk"),
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


def _render_car_detailing_sections() -> str:
    packages = [
        ("Express Wash", "$29", "Exterior foam wash, tyre shine, and quick interior vacuum"),
        ("Interior Deep Clean", "$79", "Seats, mats, dashboard, odor treatment, and stain care"),
        ("Premium Ceramic Detail", "$249", "Paint polish, ceramic coating prep, and premium finish protection"),
    ]
    package_cards = _render_package_cards(packages, "Book Package")
    bookings = [
        ("Doorstep Booking", "SUV ceramic detail", "Today 4:30 PM"),
        ("Booking Calendar", "Interior deep clean", "Tomorrow 10:00 AM"),
        ("Payment Status", "Express wash", "Paid"),
        ("Admin Dashboard", "Daily Bookings", "Revenue $4.6k"),
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


def _render_gym_sections() -> str:
    plans = [
        ("Starter Plan", "$39/mo", "Gym floor access, progress check-in, and monthly attendance summary"),
        ("Transformation Plan", "$89/mo", "Personal trainer profile match, class booking, and diet consultation"),
        ("Elite Coaching", "$149/mo", "Premium trainer sessions, weekly diet review, and payment dashboard access"),
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


def _render_restaurant_sections() -> str:
    menu_items = [
        ("Chef Thali", "$12", "Best-selling lunch combo with dal, curry, rice, roti, and dessert"),
        ("Paneer Tikka Bowl", "$9", "Fast ordering item with add-on beverage and spice preference"),
        ("Family Dinner Pack", "$34", "Four-person bundle with payment status and kitchen queue tracking"),
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


def _render_clinic_sections() -> str:
    services = [
        ("General Consultation", "$25", "Appointment booking with visit reason and queue status"),
        ("Dental Checkup", "$40", "Doctor schedule slot with follow-up reminder"),
        ("Health Package", "$99", "Patient records, payment status, and admin dashboard review"),
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


def _render_school_sections() -> str:
    modules = [
        ("Parent Portal", "$2/student", "Attendance, notices, homework, and teacher remarks in one parent view"),
        ("Class Dashboard", "$79/mo", "Teacher workload, class attendance, and assignment status"),
        ("Fee Desk", "$129/mo", "Fee status, reminders, receipts, and school admin overview"),
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


def _render_retail_sections() -> str:
    items = [
        ("Wireless Earbuds", "$49", "SKU EB-204, 48 in stock, high reorder velocity"),
        ("Travel Backpack", "$39", "SKU BG-118, 12 in stock, low-stock alert active"),
        ("Smart Watch", "$89", "SKU SW-331, supplier purchase order pending"),
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


def _render_domain_sections(domain: str, plan: Dict[str, Any]) -> str:
    if domain == "car_detailing":
        return _render_car_detailing_sections()

    if domain == "wedding_venue":
        return _render_wedding_venue_sections()

    if domain == "gym":
        return _render_gym_sections()

    if domain == "restaurant":
        return _render_restaurant_sections()

    if domain == "clinic":
        return _render_clinic_sections()

    if domain == "school":
        return _render_school_sections()

    if domain == "retail":
        return _render_retail_sections()

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
    screen_labels = _domain_screen_labels(domain, plan)
    actions = {
        "car_detailing": ("Service Packages", "Doorstep Booking"),
        "gym": ("Membership Plans", "Class Booking"),
        "wedding_venue": ("Wedding Packages", "Send Enquiry"),
        "restaurant": ("Order Food", "Book Table"),
        "clinic": ("Book Appointment", "Doctor Schedule"),
        "school": ("Parent Portal", "Attendance"),
        "retail": ("Update Stock", "Sales Dashboard"),
    }
    primary_action, secondary_action = actions.get(domain, ("Open Workflow", "View Dashboard"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{app_name}</title>
  <link rel="manifest" href="./manifest.json">
  <link rel="stylesheet" href="./style.css">
</head>
<body class="{html.escape(_domain_theme_class(domain))}{' is-image-guided' if plan.get('image_guided') else ''}">
  <main class="app-shell">
    <header class="hero">
      <nav class="top-nav" aria-label="Prototype navigation">
        <strong>{app_name}</strong>
        <button type="button" data-screen="dashboard">Preview</button>
      </nav>
      <section class="hero-content">
        <div class="hero-copy">
          <span class="eyebrow">{app_type}</span>
          <h1>{app_name}</h1>
          <p>{summary}</p>
          <div class="hero-actions">
            <button type="button" data-screen="{html.escape(_screen_slug(primary_action))}">{html.escape(primary_action)}</button>
            <button type="button" class="ghost-button" data-screen="{html.escape(_screen_slug(secondary_action))}">{html.escape(secondary_action)}</button>
          </div>
        </div>
        {_render_app_visual(domain)}
      </section>
    </header>

    <section class="app-screen-nav" aria-label="Generated app screens">
      {_render_screen_nav(screen_labels)}
    </section>

    <section class="metric-grid" aria-label="Dashboard metrics">
      {_render_metric_cards(domain)}
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
.metric-grid article { position: relative; display: grid; gap: 7px; overflow: hidden; padding: 17px; }
.metric-grid article::after { content: ""; position: absolute; inset: auto 14px 14px auto; width: 34px; height: 34px; border-radius: 12px; background: color-mix(in srgb, var(--accent) 16%, transparent); }
.metric-grid span { color: var(--muted); font-size: 12px; font-weight: 750; }
.metric-grid strong { font-size: 28px; line-height: 1; overflow-wrap: anywhere; }
.content-block { display: grid; gap: 14px; margin-top: 26px; }
.interactive-screen-panel { display: grid; gap: 14px; margin-top: 14px; padding: 18px; background: linear-gradient(180deg, var(--surface-strong), color-mix(in srgb, var(--accent-soft) 46%, var(--surface-strong))); }
.interactive-screen-panel p { color: var(--muted); font-size: 14px; line-height: 1.5; }
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
  .app-shell { padding: 72px 10px max(108px, calc(env(safe-area-inset-bottom) + 88px)); }
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
    return f"""const APP_ID = {json.dumps(app_id)};
const API_PROXY_PLACEHOLDERS = {json.dumps([f"/api/runtime/{app_id}/{service}" for service in api_services])};
const APP_DOMAIN = {json.dumps(domain)};

const SCREEN_CONFIG = {{
  car_detailing: {{
    dashboard: {{
      title: "Dashboard",
      summary: "Daily bookings, revenue, leads, and payment status for the detailing business.",
      cards: [["Daily Bookings", "18 scheduled services"], ["Revenue", "$4.6k this week"], ["Customer Leads", "7 callback requests"]]
    }},
    service_packages: {{
      title: "Service Packages",
      summary: "Customers compare detailing packages and choose the service that matches their vehicle.",
      cards: [["Express Wash", "$29 quick exterior care"], ["Interior Deep Clean", "$79 cabin reset"], ["Premium Ceramic Detail", "$249 finish protection"]]
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
      cards: [["Bookings", "18 active"], ["Revenue", "$4.6k"], ["Leads", "7 open"]]
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
      cards: [["Starter Plan", "$39/mo gym access"], ["Transformation Plan", "$89/mo trainer match"], ["Elite Coaching", "$149/mo premium sessions"]]
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
      cards: [["Monthly Revenue", "$12.4k"], ["Paid Members", "248"], ["Pending", "18 invoices"]]
    }}
  }},
  wedding_venue: {{
    dashboard: {{
      title: "Dashboard",
      summary: "Booking lead, package, enquiry, and date-hold overview for the venue manager.",
      cards: [["Booking Leads", "24 this week"], ["Date Holds", "8 active"], ["Package Revenue", "₹38L pipeline"]]
    }},
    wedding_packages: {{
      title: "Wedding Packages",
      summary: "Families compare Haldi, Mehendi, lawn booking, banquet package, and full wedding options.",
      cards: [["Haldi Theme", "₹2.49L outdoor decor"], ["Mehendi Theme", "₹4.99L family lounge"], ["Royal Wedding", "₹8.99L full venue"]]
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
      cards: [["Today Orders", "86 orders"], ["Reservations", "18 tables"], ["Revenue", "$6.8k"]]
    }},
    menu: {{
      title: "Menu",
      summary: "Customer-facing menu cards with popular dishes, prices, and add-to-order actions.",
      cards: [["Chef Thali", "$12 lunch combo"], ["Paneer Tikka Bowl", "$9 bestseller"], ["Family Dinner Pack", "$34 bundle"]]
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
      cards: [["Paid Orders", "72"], ["Pending", "9"], ["UPI Settled", "$5.9k"]]
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
      cards: [["Collections", "$2.8k"], ["Pending Bills", "6"], ["Reminders", "16"]]
    }}
  }},
  school: {{
    dashboard: {{
      title: "Parent Dashboard",
      summary: "Attendance, notices, homework, fees, exam results, and teacher contact.",
      cards: [["Attendance", "92%"], ["Homework", "3 due"], ["Fees", "Term 2 pending"]]
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
      title: "Fees",
      summary: "Fee status, receipts, reminders, and admin follow-up states.",
      cards: [["Term 2", "Pending"], ["Transport", "Paid"], ["Receipt", "Ready"]]
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
      cards: [["Products", "312 SKUs"], ["Low Stock", "14 alerts"], ["Revenue", "$8.2k"]]
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
      cards: [["Today Revenue", "$8.2k"], ["Top SKU", "Earbuds"], ["Margin", "31%"]]
    }},
    admin_dashboard: {{
      title: "Admin Dashboard",
      summary: "Admin operations for stock, orders, purchases, and payments.",
      cards: [["Purchase Orders", "7 open"], ["Supplier Updates", "4"], ["Low Stock", "14"]]
    }}
  }}
}};

const SCREEN_ALIASES = {{
  preview: "dashboard",
  view_packages: APP_DOMAIN === "wedding_venue" ? "wedding_packages" : APP_DOMAIN === "gym" ? "membership_plans" : "service_packages",
  send_enquiry: APP_DOMAIN === "wedding_venue" ? "enquiry_form" : "teacher_contact",
  gallery: APP_DOMAIN === "car_detailing" ? "before_after_gallery" : "gallery",
  admin: APP_DOMAIN === "wedding_venue" ? "admin_lead_dashboard" : "admin_dashboard",
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
  parent_portal: "parent_portal",
  attendance: "attendance",
  save_stock: "inventory",
  update_stock: "inventory",
  sales_dashboard: "revenue_dashboard"
}};

// TODO: Add API key billing layer before enabling paid runtime services.
// TODO: Add runtime usage metering for every backend proxy call.
// TODO: Route all third-party keys through the backend safety gateway before public launch.
// TODO: Add illegal-usage blocking before API key issuance.
function slugFromLabel(label) {{
  return String(label || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}}

function cardMarkup(cards) {{
  return `<div class="screen-card-grid">${{(cards || []).map(([title, detail]) => `
    <article class="screen-card"><strong>${{title}}</strong><span>${{detail}}</span></article>
  `).join("")}}</div>`;
}}

function formMarkup(screen) {{
  const options = (screen.serviceOptions || ["Service Package"]).map((option) => `<option>${{option}}</option>`).join("");
  const actions = {{
    appointment: "Confirm Appointment",
    booking: "Submit Booking",
    enquiry: "Send Enquiry",
    order: "Send Order",
    stock: "Save Stock"
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
  panel.innerHTML = `
    <div class="section-heading">
      <span class="eyebrow">Active screen</span>
      <h2>${{screen.title}}</h2>
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
  const button = event.target.closest("button");
  if (!button) return;
  button.dataset.clicked = "true";
  const screenKey = button.dataset.screen || slugFromLabel(button.textContent);
  renderScreen(screenKey);
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
                "source": "phase-30a-output-quality-engine",
                "input_mode": "image-guided" if normalized.get("image_guided") else "text-only",
                "image_guided": bool(normalized.get("image_guided")),
                "reference_image": normalized.get("reference_image") if normalized.get("image_guided") else None,
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

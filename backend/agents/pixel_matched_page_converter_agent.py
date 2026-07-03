from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class PixelMatchedPageConverterAgent(BaseAgent):
    name = "PixelMatchedPageConverterAgent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        app_slug = (
            context.get("app_slug")
            or context.get("project_slug")
            or context.get("app_name")
            or "IdeasForgeAIProduct"
        )
        has_image = bool(context.get("image_provided"))
        image_name = context.get("image_name") or ""
        target_base = f"generated-apps/{app_slug}/frontend"

        data = {
            "detected_layout": "Placeholder: upload or paste a screenshot to detect layout regions."
            if not has_image
            else "Placeholder analysis: hero/header, primary content, cards, forms, and navigation regions.",
            "components": []
            if not has_image
            else [
                "Navigation",
                "Hero/Header",
                "Content Cards",
                "Primary Action Buttons",
                "Responsive Sections",
            ],
            "color_palette": []
            if not has_image
            else ["#07120f", "#102019", "#52d273", "#3bb4c1", "#f3fff6"],
            "typography": {
                "heading": "Placeholder heading stack",
                "body": "Placeholder body stack",
                "notes": "Real font detection will be added in a later phase.",
            },
            "html_file": f"{target_base}/converted-page.html",
            "css_file": f"{target_base}/converted-page.css",
            "responsive_notes": [
                "Current phase is safe placeholder mode.",
                "No external image analysis APIs are called.",
                "Future mode will map screenshot regions into responsive HTML/CSS.",
                "Target breakpoints: mobile, tablet, desktop.",
            ],
            "image_name": image_name,
            "image_provided": has_image,
            "mode": "placeholder",
        }

        if not has_image:
            return self.success(
                summary="Placeholder ready. Upload or paste a screenshot to begin pixel-matched conversion.",
                data=data,
            )

        return self.success(
            summary="Safe placeholder conversion prepared. Real image analysis is not enabled yet.",
            data=data,
        )


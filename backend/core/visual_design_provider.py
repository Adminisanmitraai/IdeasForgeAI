from abc import ABC, abstractmethod
from typing import Any, Dict


class VisualDesignProvider(ABC):
    name = "visual_design_provider"

    @abstractmethod
    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class PlaceholderVisualDesignProvider(VisualDesignProvider):
    name = "placeholder_visual_design_provider"

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        project_name = context.get("app_name") or "IdeasForgeAIProduct"
        idea = context.get("idea") or "Agriculture management platform"
        slug = context.get("app_slug") or project_name.lower().replace(" ", "-")

        return {
            "mode": "placeholder",
            "provider": self.name,
            "project_name": project_name,
            "idea": idea,
            "asset_root": "frontend/assets/generated",
            "brand_kit": {
                "brand_name": project_name,
                "logo_placeholder": f"frontend/assets/generated/logos/{slug}-logo-placeholder.png",
                "app_icon_placeholder": f"frontend/assets/generated/icons/{slug}-app-icon-placeholder.png",
                "primary_color": "#168A52",
                "secondary_color": "#0E9FB1",
                "accent_color": "#F2B84B",
                "typography": "Inter for product UI, Merriweather Sans for warm editorial accents",
            },
            "logo_workflow": {
                "status": "awaiting_approval",
                "actions": ["AI Logo Generation", "Regenerate", "Upload Logo", "Approve Logo"],
                "notes": "No external AI provider is connected in this phase.",
            },
            "app_icon_workflow": [
                {"name": "Rounded icon", "size": "1024x1024", "path": f"frontend/assets/generated/icons/{slug}-rounded.png"},
                {"name": "Square icon", "size": "1024x1024", "path": f"frontend/assets/generated/icons/{slug}-square.png"},
                {"name": "Play Store icon", "size": "512x512", "path": f"frontend/assets/generated/icons/{slug}-play-store.png"},
                {"name": "Apple icon", "size": "1024x1024", "path": f"frontend/assets/generated/icons/{slug}-apple.png"},
            ],
            "ui_mockups": [
                {"name": "Desktop", "orientation": "Landscape", "path": f"frontend/assets/generated/mockups/{slug}-desktop.png"},
                {"name": "Tablet", "orientation": "Landscape", "path": f"frontend/assets/generated/mockups/{slug}-tablet.png"},
                {"name": "Mobile", "orientation": "Portrait", "path": f"frontend/assets/generated/mockups/{slug}-mobile.png"},
                {"name": "Dashboard", "orientation": "Responsive", "path": f"frontend/assets/generated/mockups/{slug}-dashboard.png"},
                {"name": "Landing Page", "orientation": "Responsive", "path": f"frontend/assets/generated/mockups/{slug}-landing.png"},
            ],
            "screen_gallery": ["Homepage", "Login", "Dashboard", "Profile", "Settings"],
            "pipeline": [
                "Understanding Idea",
                "Brand Creation",
                "Logo",
                "App Icon",
                "Color Palette",
                "Typography",
                "UI Mockups",
                "Approval Ready",
            ],
            "approval": {
                "status": "pending",
                "frontend_generation_allowed": False,
                "actions": ["Approve Design", "Regenerate Design", "Edit Design"],
            },
            "future_hooks": ["OpenAI image models", "Other image providers"],
        }


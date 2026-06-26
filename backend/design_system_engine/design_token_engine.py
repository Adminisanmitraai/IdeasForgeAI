from typing import Dict, List


class DesignTokenEngine:
    def generate(self, context: Dict) -> Dict:
        return {
            "typography_rules": {
                "font_style": "Clean readable sans-serif",
                "page_title": "Clear, strong, and not oversized",
                "section_title": "Bold, compact, and easy to scan",
                "card_title": "Short labels with calm hierarchy",
                "body": "Founder-friendly body text with comfortable line height",
                "status": "Human-readable status text, never raw booleans or technical codes",
            },
            "color_rules": {
                "background": "Soft white or light green-white",
                "surface": "White or pale green-white cards",
                "primary": "Deep green or teal for important actions and approval",
                "secondary": "Muted green-gray for supportive UI",
                "text": "Dark green-black or charcoal",
                "border": "Soft green-gray borders",
                "success": "Green for ready, saved, approved, and running safely",
                "warning": "Amber for missing information or approval needed",
                "error": "Red only for real blocking issues",
            },
            "spacing_rules": [
                "Use generous card padding",
                "Keep sections visually separated",
                "Use consistent gaps between cards, labels, inputs, and actions",
                "Keep mobile screens scrollable and uncluttered",
            ],
            "layout_rules": [
                "Keep Studio V3 chat-first",
                "Keep Create Mode and Product Preview Mode full-screen",
                "Group product intelligence into clear cards",
                "Stack cards on mobile and use two columns carefully on desktop",
                "Keep the bottom input simple and unchanged",
            ],
        }

    def do_not_do_rules(self) -> List[str]:
        return [
            "Do not redesign Studio V3",
            "Do not generate final frontend code in Phase 6",
            "Do not generate backend code in Phase 6",
            "Do not create database schema",
            "Do not connect Supabase",
            "Do not add authentication",
            "Do not deploy",
            "Do not show raw JSON, booleans, stack traces, or technical failure text",
            "Do not turn the product into a form builder or dense admin dashboard",
        ]

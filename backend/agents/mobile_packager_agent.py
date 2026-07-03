from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class MobilePackagerAgent(BaseAgent):
    name = "mobile_packager_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        return self.success(
            summary="Prepared mobile packaging strategy.",
            data={
                "mobile_targets": [
                    "android_apk",
                    "android_aab",
                    "ios_project",
                ],
                "recommended_approach": "Generate responsive web first, then package using Capacitor or Expo depending on product type.",
                "future_steps": [
                    "Create app icon",
                    "Create splash screen",
                    "Generate mobile shell",
                    "Connect web build",
                    "Prepare store metadata",
                ],
            },
        )

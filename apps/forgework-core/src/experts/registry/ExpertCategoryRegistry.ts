import type { ExpertCategory } from "../types/ExpertCategory";

export const DEFAULT_EXPERT_CATEGORIES: ExpertCategory[] = [
  {
    id: "design-engineering",
    name: "Design & Engineering",
    description: "Cross-disciplinary design, spatial planning, engineering logic, and technical concept development.",
    parentCategory: null,
    defaultPriority: 80,
    allowedOutputTypes: ["plan", "layout", "technical-spec", "visual-brief", "client-presentation"]
  },
  {
    id: "architecture-construction",
    name: "Architecture & Construction",
    description: "Architecture, interiors, construction, lighting, landscape, and technical planning experts.",
    parentCategory: "design-engineering",
    defaultPriority: 80,
    allowedOutputTypes: ["plan", "layout", "technical-spec", "visual-brief", "client-presentation"]
  },
  {
    id: "creative-production",
    name: "Creative Production",
    description: "Creative experts for visuals, branding, presentations, photo, video, and media production.",
    parentCategory: null,
    defaultPriority: 75,
    allowedOutputTypes: ["creative-brief", "image-brief", "video-brief", "presentation", "brand-guide"]
  },
  {
    id: "software-engineering",
    name: "Software Engineering",
    description: "Experts for architecture analysis, coding strategy, debugging, testing, safe editing, and deployment planning.",
    parentCategory: null,
    defaultPriority: 90,
    allowedOutputTypes: ["architecture-plan", "code-plan", "diff-plan", "test-plan", "deployment-plan"]
  },
  {
    id: "business-marketing",
    name: "Business & Marketing",
    description: "Business strategy, marketing, launch planning, positioning, copy, campaigns, and customer intelligence.",
    parentCategory: null,
    defaultPriority: 75,
    allowedOutputTypes: ["strategy", "campaign-plan", "copy", "report", "dashboard-spec"]
  },
  {
    id: "finance-accounting",
    name: "Finance & Accounting",
    description: "Finance, accounting, spreadsheet modelling, projections, analysis, and business calculations.",
    parentCategory: null,
    defaultPriority: 80,
    allowedOutputTypes: ["financial-model", "spreadsheet", "report", "calculation", "risk-summary"]
  },
  {
    id: "legal-compliance",
    name: "Legal & Compliance",
    description: "Legal research, compliance planning, document review, policy logic, and risk identification.",
    parentCategory: null,
    defaultPriority: 85,
    allowedOutputTypes: ["legal-summary", "risk-summary", "checklist", "document-review", "policy-draft"]
  },
  {
    id: "healthcare",
    name: "Healthcare",
    description: "Medical information organization, patient education, healthcare workflows, and safety-aware triage support.",
    parentCategory: null,
    defaultPriority: 85,
    allowedOutputTypes: ["health-summary", "education-note", "workflow", "risk-summary"]
  },
  {
    id: "education-training",
    name: "Education & Training",
    description: "Teaching, curriculum planning, lesson design, assessments, tutoring, and learning support.",
    parentCategory: null,
    defaultPriority: 75,
    allowedOutputTypes: ["lesson-plan", "worksheet", "rubric", "explanation", "training-plan"]
  },
  {
    id: "research-intelligence",
    name: "Research & Intelligence",
    description: "Research planning, source analysis, synthesis, market intelligence, and professional investigation.",
    parentCategory: null,
    defaultPriority: 85,
    allowedOutputTypes: ["research-brief", "analysis", "source-map", "report", "recommendation"]
  },
  {
    id: "office-productivity",
    name: "Office Productivity",
    description: "Documents, presentations, spreadsheets, process notes, reports, and administrative productivity.",
    parentCategory: null,
    defaultPriority: 70,
    allowedOutputTypes: ["document", "spreadsheet", "presentation", "report", "template"]
  },
  {
    id: "media-production",
    name: "Media Production",
    description: "Video, photo, audio, editing strategy, creative media production, and publishing workflows.",
    parentCategory: "creative-production",
    defaultPriority: 75,
    allowedOutputTypes: ["video-brief", "photo-brief", "shot-list", "editing-plan", "content-plan"]
  },
  {
    id: "general-professional",
    name: "General Professional",
    description: "General senior-professional reasoning for tasks that do not map to a specialized category yet.",
    parentCategory: null,
    defaultPriority: 60,
    allowedOutputTypes: ["plan", "summary", "checklist", "document", "recommendation"]
  }
];

export class ExpertCategoryRegistry {
  private readonly categoriesById = new Map<string, ExpertCategory>();

  constructor(categories: ExpertCategory[] = DEFAULT_EXPERT_CATEGORIES) {
    for (const category of categories) {
      this.categoriesById.set(category.id, category);
    }
  }

  listCategories(): ExpertCategory[] {
    return [...this.categoriesById.values()];
  }

  getCategory(id: string): ExpertCategory | null {
    return this.categoriesById.get(id) ?? null;
  }

  hasCategory(id: string): boolean {
    return this.categoriesById.has(id);
  }
}

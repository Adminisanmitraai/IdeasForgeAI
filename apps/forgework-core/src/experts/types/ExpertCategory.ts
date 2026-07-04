export interface ExpertCategory {
  id: string;
  name: string;
  description: string;
  parentCategory: string | null;
  defaultPriority: number;
  allowedOutputTypes: string[];
}

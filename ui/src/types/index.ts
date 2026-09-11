export type ResearchStatusType = {
  step: string;
  message: string;
};

export type ResearchOutput = {
  summary: string;
  details: {
    report: string;
  };
};

export type Evidence = {
  claim: string;
  source_urls: string[];
  confidence: number;
};

export type OpportunityAssessment = {
  executive_summary: string;
  pain_points: Array<{
    title: string;
    description: string;
    priority: string;
    evidence: Evidence[];
  }>;
  score: {
    need_fit: number;
    business_value: number;
    urgency: number;
    delivery_feasibility: number;
    evidence_quality: number;
    total: number;
  };
  recommended_solutions: Array<{
    name: string;
    target_problem: string;
    workflow: string[];
    tools_and_data: string[];
    expected_value: string;
    human_approval_points: string[];
    risks: string[];
    source_urls: string[];
  }>;
  discovery_questions: string[];
  limitations: string[];
};

export type TaskDraft = {
  id: number;
  title: string;
  details: Record<string, unknown>;
  status: string;
};

export type EnrichmentCounts = {
  company: { total: number; enriched: number };
  industry: { total: number; enriched: number };
  financial: { total: number; enriched: number };
  news: { total: number; enriched: number };
};

export type GlassStyle = {
  base: string;
  card: string;
  input: string;
};

export type AnimationStyle = {
  fadeIn: string;
  writing: string;
};

export type ResearchStatusProps = {
  status: ResearchStatusType | null;
  error: string | null;
  isComplete: boolean;
  currentPhase: 'search' | 'enrichment' | 'briefing' | 'complete' | null;
  isResetting: boolean;
  glassStyle: GlassStyle;
  loaderColor: string;
  statusRef: React.RefObject<HTMLDivElement>;
};

export type ResearchQueriesProps = {
  queries: Array<{
    text: string;
    number: number;
    category: string;
  }>;
  streamingQueries: {
    [key: string]: {
      text: string;
      number: number;
      category: string;
      isComplete: boolean;
    };
  };
  isExpanded: boolean;
  onToggleExpand: () => void;
  isResetting: boolean;
  glassStyle: string;
};

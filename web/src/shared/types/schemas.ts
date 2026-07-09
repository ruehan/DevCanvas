/** 백엔드 Pydantic 스키마를 미러하는 공용 타입 (ADR-0014). */

export type ScreenType = "admin" | "dashboard" | "internal_tool";
export type Tone = "b2b" | "minimal" | "enterprise" | "startup" | "friendly";
export type ScreenKind = "list" | "detail" | "dashboard";

export interface GenerationRequest {
  prompt: string;
  screen_type: ScreenType;
  service_type: string;
  role: string;
  data_fields: string[];
  tone: Tone;
  stack: string;
}

export interface GenerationInput extends GenerationRequest {}

export interface RequirementSpec {
  features: string[];
  users: string[];
  screens: string[];
  data_entities: string[];
}

export interface ScreenSpec {
  name: string;
  purpose: string;
  kind: ScreenKind;
  components: string[];
  data_columns: string[];
  filters: string[];
  actions: string[];
}

export interface ScreenState {
  loading: string;
  empty: string;
  error: string;
  permission: string;
  mobile: string;
}

export interface UXPlan {
  screens: ScreenSpec[];
  flows: string[];
  states: Record<string, ScreenState>;
}

export interface DesignTokens {
  colors: Record<string, string>;
  spacing: Record<string, string>;
  radius: Record<string, string>;
  typography: Record<string, string>;
  shadows: Record<string, string>;
}

export interface DesignSystem {
  tokens: DesignTokens;
}

export interface ScreenLayout {
  screen: string;
  layout: string;
  kind: ScreenKind;
  component_tree: string[];
}

export interface UIGeneration {
  layouts: ScreenLayout[];
}

export interface CodeFile {
  path: string;
  content: string;
  language: "tsx" | "ts" | "css" | "json" | "md";
}

export interface ReviewFinding {
  severity: "P1" | "P2";
  category: string;
  message: string;
}

export interface HandoffDoc {
  file_tree: string[];
  install_commands: string[];
  todos: string[];
  guide_md: string;
}

export interface GenerationResult {
  input: GenerationInput;
  requirement: RequirementSpec;
  ux_plan: UXPlan;
  design_system: DesignSystem;
  ui: UIGeneration;
  code: CodeFile[];
  review: ReviewFinding[];
  handoff: HandoffDoc;
}

// ---- 세션/대화 (ADR-0017) ----

export type MessageRole = "user" | "agent";

export interface Message {
  role: MessageRole;
  content: string;
  steps: string[];
  created_at?: string;
}

export interface Session {
  id: string;
  created_at?: string;
  messages: Message[];
  current_result: GenerationResult | null;
}

export interface PostMessageResponse {
  agent_message: Message;
  result: GenerationResult;
  session_id: string;
}

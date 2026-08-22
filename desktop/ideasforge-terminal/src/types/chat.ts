export type ChatRole = "user" | "assistant" | "system";

export type ChatRequestStatus =
  | "idle"
  | "sending"
  | "completed"
  | "error"
  | "cancelled";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
  route?: string;
  source?: string;
  error?: boolean;
}

export interface HomeChatRequest {
  message: string;
  page: string;
  mode: string;
  role: string;
  source: string;
}

export interface HomeChatResponse {
  ok: boolean;
  answer: string;
  route?: string;
  page?: string;
  mode?: string;
  source?: string;
  error_detail?: string | null;
  suggestions?: string[];
}

export interface ChatState {
  messages: ChatMessage[];
  suggestions: string[];
  status: ChatRequestStatus;
  editingMessageId?: string;
  activeRequestId?: string;
  errorMessage?: string;
}

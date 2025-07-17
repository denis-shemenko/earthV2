export interface Question {
    question: string;
    options: string[];
    correct_answer: string;
    session_id: string;
  }

  export interface QuestionOption {
    text: string[];
    is_correct: boolean;
  }

export interface GraphNode {
  id: string;
  label: string;
  type: "home" | "question" | "answer" | "topic" | "session";
  isCurrent?: boolean;
  question: string;
  selected: boolean;
  topic?: boolean; // Add optional topic property
}

export interface GraphLink {
  source: string;
  target: string;
  label?: string;
}

export interface KnowledgeGraph {
  nodes: GraphNode[];
  links: GraphLink[];
}
  
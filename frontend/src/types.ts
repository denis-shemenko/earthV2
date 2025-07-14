export interface Question {
    question: string;
    options: string[];
    correct_answer: string;
    session_id: string;
  }

export interface GraphNode {
  id: string;
  label: string;
  type: "home" | "question" | "answer" | "topic" | "session";
  isCurrent?: boolean;
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
  
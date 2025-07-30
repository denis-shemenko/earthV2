export type Trait = "Любопытный" | "Безрассудный" | "Точный" | "Забывчивый" | "Поддерживающий";

export type KnowledgeArea = "Физика" | "История" | "Музыка" | "Математика" | "Биология"
  | "Спорт" | "Кино" | "Животные" | "Литература" | "Технологии" | "Природа" | "Философия";

export interface CrewMember {
  id: string;
  name: string;
  specialty: KnowledgeArea;
  traits: Trait[];
}

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
  correct?: boolean;
  x?: number;
  y?: number;
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
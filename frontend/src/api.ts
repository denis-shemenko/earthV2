import axios from "axios";
import type { Question, KnowledgeGraph } from "./types";

const API = axios.create({
  baseURL: "http://localhost:8000", // меняется при деплое
});

export const fetchStart = async (): Promise<Question> => {
  const res = await API.get<Question>("/start");
  return res.data;
};

export const sendAnswer = async (
  session_id: string,
  chosen_answer: string,
  question_text: string
): Promise<Question> => {
  const res = await API.post<Question>("/answer", {
    session_id,
    chosen_answer,
    question_text,
  });
  return res.data;
};

export const getGraphBySession = async (sessionId: string): Promise<KnowledgeGraph> => {
  const res = await fetch(`http://localhost:8000/graph/${sessionId}`);
  if (!res.ok) throw new Error("Failed to fetch graph");
  return await res.json();
};
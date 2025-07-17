import axios from "axios";
import type { Question, KnowledgeGraph } from "./types";

const API = axios.create({
  baseURL: "http://localhost:8000", // меняется при деплое
});

export const fetchStart = async (): Promise<Question> => {
  const res = await API.post<Question>("/start-session");
  return res.data;
};

export const postFirstQuestion = async (
  session_id: string,
  topic: string,
): Promise<Question> => {
  const res = await API.post<Question>("/first-question", {
    session_id,
    topic
  });
  return res.data;
};

export const getGraphBySession = async (sessionId: string): Promise<KnowledgeGraph> => {
  const res = await fetch(`http://localhost:8000/graph/${sessionId}`);
  if (!res.ok) throw new Error("Failed to fetch graph");
  return await res.json();
};
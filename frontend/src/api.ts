import axios from "axios";
import type { Question } from "./types";

const API = axios.create({
  baseURL: "http://localhost:8000", // меняется при деплое
});

export const fetchStart = async (): Promise<Question> => {
  const res = await API.get<Question>("/start");
  return res.data;
};

export const sendAnswer = async (
  session_id: string,
  chosen_answer: string
): Promise<Question> => {
  const res = await API.post<Question>("/answer", {
    session_id,
    chosen_answer,
  });
  return res.data;
};

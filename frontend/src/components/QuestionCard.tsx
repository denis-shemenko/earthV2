import { useState } from "react";
import classNames from "classnames";
import type { Question } from "../types";

interface Props {
  data: Question;
  onAnswer: (answer: string) => void;
  disabled: boolean;
  selected: string | null;
}

export default function QuestionCard({ data, onAnswer, disabled, selected }: Props) {
  const handleClick = (option: string) => {
    if (!disabled) onAnswer(option);
  };

  return (
    <div className="max-w-xl mx-auto bg-white shadow-xl rounded-2xl p-6">
      <h2 className="text-xl font-semibold mb-4">{data.question}</h2>
      <div className="grid grid-cols-1 gap-3">
        {data.options.map((opt) => {
          const isCorrect = selected && opt === data.correct_answer;
          const isWrong = selected && opt === selected && opt !== data.correct_answer;

          return (
            <button
              key={opt}
              onClick={() => handleClick(opt)}
              disabled={disabled}
              className={classNames(
                "px-4 py-2 rounded-lg border text-left transition-colors",
                {
                  "bg-green-200 border-green-600": isCorrect,
                  "bg-red-200 border-red-600": isWrong,
                  "hover:bg-gray-100": !selected,
                  "cursor-not-allowed": disabled,
                }
              )}
            >
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}

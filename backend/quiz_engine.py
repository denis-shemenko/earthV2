import os
from tabnanny import verbose
from dotenv import load_dotenv
from typing import List
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain.globals import set_verbose

load_dotenv()

# Конфигурация модели
llm = ChatOpenAI(
    model="gpt-4",  # легко заменить на gpt-3.5-turbo, Claude, Mistral и т.д.
    temperature=0.7
)

llmGemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    thinking_budget=0,
    # other params...
)

# JSON-парсер
parser = JsonOutputParser()

# Шаг 1: Генерация нового связанного топика
next_topic_prompt = PromptTemplate(
    input_variables=["previous_answer", "avoid"],
    template="""
Ты создаешь уникальный путь знаний для игрока. У игрока предыдущий ответ был: "{previous_answer}".
Твоя задача — придумать одну новую, логически связанную, но при этом из другой области знаний, 
или которая требует креативного, ассоциативного прыжка.
Это должен быть не очевидный, но интересный прыжок между темами, для расширения кругозора игрока.

Примеры таких прыжков:
- Space -> Greek Mythology (через имена планет)
- История -> Кулинария (через традиционные блюда эры)

Избегай повторного использования этих тем: {avoid}.

Верни только одну тему без пояснений.
"""
)

next_topic_chain = next_topic_prompt | llmGemini

# Шаблон промпта
next_question_template = """
Ты — генератор интеллектуальных викторин. На вход ты получаешь тему и должен сгенерировать интересный, 
краткий вопрос на эту тему, с 4 вариантами ответа.

Формат вывода должен строго соответствовать следующей JSON-структуре:

  "question": "строка — сам вопрос",
  "options": [
    "text": "вариант ответа 1", "isCorrect": true/false "",
    "text": "вариант ответа 2", "isCorrect": true/false "",
    "text": "вариант ответа 3", "isCorrect": true/false "",
    "text": "вариант ответа 4", "isCorrect": true/false ""
  ]

⚠️ Только один из вариантов должен иметь "isCorrect": true.

Пример:

  "question": "Кто первым высадился на Луне?",
  "options": [
    "text": "Нил Армстронг", "isCorrect": true "",
    "text": "Юрий Гагарин", "isCorrect": false "",
    "text": "Базз Олдрин", "isCorrect": false "",
    "text": "Майкл Коллинз", "isCorrect": false ""
  ]

Тема: {next_topic}

Правильный ответ должен быть связан с темой, но не должен повторяться из следующего списка: {avoid}.

Следи за разнообразием и корректностью. Варианты ответов должны быть правдоподобны, но только один — правильный.
"""

next_question_prompt = PromptTemplate(
    input_variables=["next_topic", "avoid"],
    template=next_question_template
)

# English without OPTIONS!
# prompt = PromptTemplate(
#     input_variables=["topic"],
#     template=(
#         "You are an AI-powered quiz generator for a curiosity-driven game.\n"
#         "Generate a single multiple-choice question on the topic: '{topic}'.\n"
#         "Return exactly 4 answer options — one correct and three plausible but incorrect ones.\n"
#         "Respond ONLY in strict JSON format with the following fields:\n"
#         "  - question: string\n"
#         "  - options: array of 4 strings\n"
#         "  - correct_answer: string\n"
#         "Do not include any explanations or extra text."
#     )
# )

# Сборка цепочки
#next_question_chain = next_question_prompt | llmGemini | parser 
next_question_chain = (
    next_question_prompt 
    | llmGemini 
    | parser
)

def log_next_topic(inputs):
    print(f"[DEBUG] Next topic generated: {inputs['next_topic']}")
    return inputs

def log_next_question_prompt(x):
    prompt = next_question_prompt.format(
        next_topic=x["next_topic"],
        avoid=x["avoid"]
    )
    print("[DEBUG] Next question prompt sent to LLM:\n", prompt)
    return x

#set_verbose(True)

question_generator_chain = (
    RunnablePassthrough.assign(
        next_topic=lambda x: next_topic_chain.invoke({
            "previous_answer": x["previous_answer"],
            "avoid": x["avoid"]
        }).content
    )
    #| log_next_topic
    #| log_next_question_prompt
    | RunnablePassthrough.assign(
        question_json=lambda x: next_question_chain.invoke({
            "next_topic": x["next_topic"],
            "avoid": x["avoid"]
        })
    )
)

# Основная функция генерации
def generate_question(topic: str, previous_answers: List[str]) -> dict:
    try:
      result = question_generator_chain.invoke({
          "previous_answer": topic,
          "avoid": ", ".join(previous_answers)
      })
      #result = question_generator_chain.invoke({"previous_answer": topic})
      return result["question_json"]
    except Exception as e:
        print(f"[AI error] {e}")
        return {
            "question": f"Что-то пошло не так при генерации вопроса по теме '{topic}'.",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }

# Функция генерации первого вопроса по топику
def generate_first_question(topic: str) -> dict:
    try:
      result = next_question_chain.invoke({
            "next_topic": topic,
            "avoid": ""
        })
      return result
    except Exception as e:
        print(f"[AI error] {e}")
        return {
            "question": f"Что-то пошло не так при генерации вопроса по теме '{topic}'.",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }
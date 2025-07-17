import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
#from langchain_core.chains import LLMChain

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

# Шаблон промпта
system_prompt_template = """
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

Тема: {topic}
"""
prompt = PromptTemplate(
    input_variables=["topic"],
    template=system_prompt_template
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
chain = prompt | llmGemini | parser

# Основная функция генерации
def generate_question(topic: str) -> dict:
    try:
        result = chain.invoke({"topic": topic})
        return result
    except Exception as e:
        print(f"[AI error] {e}")
        return {
            "question": f"Что-то пошло не так при генерации вопроса по теме '{topic}'.",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }

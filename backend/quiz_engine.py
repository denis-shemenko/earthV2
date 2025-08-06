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
    input_variables=["previous_answer", "possible_topics", "avoid"],
    template="""
Ты создаешь уникальный путь знаний для игрока. У игрока предыдущий ответ был: "{previous_answer}".
Твоя задача — придумать от одной до четырех новых тем, логически связанных, 
но при этом из другой области знаний, или которая требует креативного, ассоциативного прыжка.
Это должен быть не очевидный, но интересный прыжок между темами, для расширения кругозора игрока.
Список возможных тем на данный момент ограничен следующим списком: {possible_topics}

Примеры таких прыжков:
- Space -> Greek Mythology (через имена планет)
- История -> Кулинария (через традиционные блюда эры)
- Biology -> Music (through natural rhythms and patterns)
- Technology -> Art (through creative applications)

Избегай повторного использования этих тем: {avoid}.

Верни от одной до четырех (случайно выбери как много) тем, каждую на новой строке, без пояснений.
"""
)

# Сборка цепочки для генерации тем
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

# Сборка цепочки для генерации вопросов
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

# Функция генерации новых тем (Шаг 1)
def generate_next_topics(previous_answer: str, possible_topics: List[str], previous_answers: List[str]) -> List[str]:
    """
    Generate 1-4 new topics based on the player's previous answer.
    This is Step 1 of the two-step process.
    """
    try:
        result = next_topic_chain.invoke({
            "previous_answer": previous_answer,
            "possible_topics": ", ".join(possible_topics),
            "avoid": ", ".join(previous_answers)
        })
        
        # Parse the response to get individual topics
        topics_text = result.content.strip()
        topics = [topic.strip() for topic in topics_text.split('\n') if topic.strip()]
        
        return topics
    except Exception as e:
        print(f"[AI error] {e}")
        return ["General Knowledge", "Science", "History", "Technology"]

# Функция генерации вопроса по выбранной теме (Шаг 2)
def generate_question_for_topic(chosen_topic: str, previous_answers: List[str]) -> dict:
    """
    Generate a question for the chosen topic.
    This is Step 2 of the two-step process.
    """
    try:
        result = next_question_chain.invoke({
            "next_topic": chosen_topic,
            "avoid": ", ".join(previous_answers)
        })
        return result
    except Exception as e:
        print(f"[AI error] {e}")
        return {
            "question": f"Что-то пошло не так при генерации вопроса по теме '{chosen_topic}'.",
            "options": [
                {"text": "A", "isCorrect": True},
                {"text": "B", "isCorrect": False},
                {"text": "C", "isCorrect": False},
                {"text": "D", "isCorrect": False}
            ]
        }

# Основная функция генерации (legacy - теперь используйте две отдельные функции выше)
def generate_question(topic: str, previous_answers: List[str]) -> dict:
    """
    Legacy function - use generate_next_topics() and generate_question_for_topic() instead
    """
    try:
        # First generate topics
        topics = generate_next_topics(topic, [], previous_answers)
        if topics:
            # Then generate question for the first topic
            return generate_question_for_topic(topics[0], previous_answers)
        else:
            raise Exception("No topics generated")
    except Exception as e:
        print(f"[AI error] {e}")
        return {
            "question": f"Что-то пошло не так при генерации вопроса по теме '{topic}'.",
            "options": [
                {"text": "A", "isCorrect": True},
                {"text": "B", "isCorrect": False},
                {"text": "C", "isCorrect": False},
                {"text": "D", "isCorrect": False}
            ]
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
            "options": [
                {"text": "A", "isCorrect": True},
                {"text": "B", "isCorrect": False},
                {"text": "C", "isCorrect": False},
                {"text": "D", "isCorrect": False}
            ]
        }
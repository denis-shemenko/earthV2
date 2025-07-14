````markdown
# 🧠 E.A.R.T.H. — AI-викторина нового поколения

**"Путь Знаний"** — это бесконечная интеллектуальная викторина, где каждый следующий вопрос связан с выбранным ответом. Игра создаёт уникальный маршрут обучения, формируя персонализированную ветку знаний для каждого игрока.

---

## 🚀 Функционал MVP

- Генерация вопросов с помощью GPT-4 (через Langchain)
- 4 варианта ответа: 1 верный и 3 правдоподобных
- После выбора — новый вопрос на основе предыдущего ответа
- Подсветка правильного/неправильного варианта
- Ведение пользовательской сессии (in-memory)
- Frontend на React + Vite + Tailwind (по желанию)

---

## 🛠️ Технологии

- **Frontend:** React + Vite + TypeScript
- **Backend:** FastAPI + Langchain + OpenAI GPT
- **Session Store:** Python in-memory store
- **LLM Layer:** Langchain (позволяет гибко менять провайдеров: OpenAI, Claude, Gemini и др.)

---

## 📦 Установка и запуск

### 🔧 Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # или .\venv\Scripts\activate
pip install -r requirements.txt

# Добавь свой OpenAI API ключ в файл `.env`
echo "OPENAI_API_KEY=sk-..." > .env

# Запусти сервер
uvicorn main:app --reload
````

### 🌐 Frontend

```bash
cd quiz-frontend
npm install
npm run dev
```

* Открой: [http://localhost:5173](http://localhost:5173)
* API работает на: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔄 API Эндпоинты

* `GET /start` — сгенерировать стартовый вопрос
* `POST /answer` — передать выбранный ответ и получить следующий вопрос

---

## 🧩 Пример запроса / ответа

```json
POST /answer
{
  "session_id": "abc123",
  "chosen_answer": "Альберт Эйнштейн"
}

Ответ:
{
  "question": "Где Эйнштейн разработал E=mc²?",
  "options": ["Берлин", "Цюрих", "Прага", "Вена"],
  "correct_answer": "Берлин",
  "session_id": "abc123"
}
```

---

## 📍 Планы развития

* Визуализация "пути знаний" игрока (графовая структура)
* Авторизация и сохранение истории
* Режимы игры: Тематический / Случайный
* Мобильное приложение (React Native)
* Кэширование и повторное использование вопросов
* Интеграция в Telegram или Discord

---

## 👨‍💻 Автор

Разработано с ❤️ by DannyShu
CTO & Game Designer with a passion for AI and learning systems

---

## 📄 Лицензия

MIT License // TODO
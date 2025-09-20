import os
from openai import OpenAI
from config import SCIBOX_API_KEY, SCIBOX_BASE_URL, SCIBOX_MODEL
import asyncio

class SciBoxService:
    def __init__(self):
        self.client = OpenAI(
            api_key=SCIBOX_API_KEY, 
            base_url=SCIBOX_BASE_URL
        )
    
    async def generate_career_plan(self, user_data: dict) -> str:
        """Генерация структурированного карьерного плана"""
        
        # Формируем описание навыков
        skills_text = ""
        
        if user_data.get('languages'):
            skills_text += "🌍 Языки: " + ", ".join([lang['language'] for lang in user_data['languages']]) + "\n"
        
        if user_data.get('programming'):
            skills_text += "💻 Программирование: " + ", ".join([prog['language'] for prog in user_data['programming']]) + "\n"
        
        if user_data.get('skills'):
            skills_text += "🔧 Навыки: " + ", ".join([skill['skill'] for skill in user_data['skills']])

        prompt = f"""
        Создай краткий и структурированный карьерный план. Используй эмодзи для наглядности.

        Данные сотрудника:
        Имя: {user_data.get('name', 'Не указано')}
        Цель: {user_data.get('career_goal', 'Не указана')}
        Навыки: {skills_text}

        Структура ответа:
        🎯 Текущий уровень и цель
        ✅ Сильные стороны (3 пункта)
        📈 Что развивать (3 пункта)
        🚀 План на 3 месяца (по месяцам)
        📚 Ресурсы (2-3 курса/книги)
        ⏱️ Сроки и метрики

        Будь кратким! Максимум 15 предложений. Только самое важное.
        """
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.chat.completions.create(
                    model=SCIBOX_MODEL,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Ты создаешь краткие и структурированные карьерные планы. Используй эмодзи, буллиты, будь конкретным. Максимум 300 слов."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    top_p=0.8
                )
            )
            
            return self._format_response(response.choices[0].message.content)
            
        except Exception as e:
            return "❌ Не удалось сгенерировать план. Попробуйте позже."

    def _format_response(self, text: str) -> str:
        """Форматирование ответа для лучшей читаемости"""
        # Добавляем отступы и переносы для структуры
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip() and not line.startswith(('•', '🎯', '✅', '📈', '🚀', '📚', '⏱️')):
                formatted_lines.append(f"• {line}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

# Синглтон instance
scibox_service = SciBoxService()
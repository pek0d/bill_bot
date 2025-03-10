# Используем официальный образ Python
FROM python:3.12

# Устанавливаем рабочую директорию в контейнере
WORKDIR /bot

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота
CMD ["python", "main.py"]

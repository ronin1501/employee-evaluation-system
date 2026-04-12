/hr_assessment_system
│── app.py                # Запуск приложения и роутинг
│── database.py           # Работа с БД (отдельный слой)
│── models.py             # Логика оценки и генерация графиков (модель автоматизации)
│── database.db           # БД SQLite
├── /static
│   └── /charts           # Папка для сохранения сгенерированных графиков
└── /templates
    ├── base.html         # Общий шаблон (Layout)
    ├── index.html        # Главная (список сотрудников)
    └── assessment.html   # Форма оценки
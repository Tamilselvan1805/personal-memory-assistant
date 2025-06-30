# 🧠 Personal Memory Assistant

A simple AI-powered memory assistant that allows users to log memories and ask questions about past events using natural language queries. Built with Flask, SQLite, and integrated with Gemini AI.

## 🚀 Features

- Log personal events with date, title, and details
- Ask questions about your memory log using a Gemini model
- AI responds contextually based on logged data
- Clean and responsive frontend using HTML/CSS/JS
- .env-based secure API key handling

## 📸 Screenshots

![Homepage](./static/images/screenshot-home.png)
![AI Query](./static/images/screenshot-query.png)

## 🛠 Tech Stack

- Python (Flask)
- SQLite
- Google Generative AI (Gemini)
- HTML / CSS / JavaScript
- dotenv for environment variables

## 📦 Installation

```bash
git clone https://github.com/<your-username>/personal-memory-assistant.git
cd personal-memory-assistant
python3 -m venv memoryENV
source memoryENV/bin/activate  # On Windows: memoryENV\Scripts\activate
pip install -r requirements.txt

Create a .env file in the root directory:
GOOGLE_API_KEY=your_api_key_here

File Structure:

personal-memory-assistant/
│
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── script.js
├── app.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md


INSTALLATION GUIDE:
1: Clone the Repository
    git clone https://github.com/YourUsername/personal-memory-assistant.git
    cd personal-memory-assistant

 2: Set Up a Virtual Environment
    source memoryENV/bin/activate   # Linux or macOS
    # OR
    memoryENV\Scripts\activate      # Windows

3: Install Dependencies
    pip install -r requirements.txt

4: Add Your API Key
    touch .env
    # Paste the following inside .env:
    GOOGLE_API_KEY=your-gemini-api-key-here

 5: Run the Flask App
    python app.py
    Visit http://127.0.0.1:5000 in your browser.

Future Improvements :

    User authentication system

    Export memories as PDF or CSV

    LLM fine-tuning or memory optimization




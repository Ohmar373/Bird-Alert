# 🐦 BirdAlert

BirdAlert is a community-driven birdwatching web application built with **Python** and **Django**. It allows birdwatchers to log sightings, upload photos or descriptions, and record when and where birds are observed. By sharing verified sightings, Bird-Alert helps users discover proven birdwatching locations and identify observation patterns over time.

This project is developed as a **Computer Science senior project** with an emphasis on full-stack web development, database design, and real-world data sharing.

---

## 🚀 Features

* User account creation and authentication
* Secure login and logout functionality
* Create and manage bird sighting posts
* Upload bird photos or written descriptions
* Record sighting details:

  * Location
  * Date
  * Time
* View sightings submitted by other users
* Community-driven data sharing for birdwatching insights

---

## 🛠️ Tech Stack

* **Backend:** Python, Django
* **Frontend:** HTML, CSS, Django Templates (future support for JS frameworks)
* **Database:** SQLite (development), PostgreSQL (planned)
* **Authentication:** Django Auth System
* **Version Control:** Git & GitHub

---

## 📂 Project Structure

```text
Bird-Alert/
│
├── bird_alert/          # Main Django project settings
├── sightings/           # App handling bird sighting logic
├── users/               # User authentication and profiles
├── media/               # Uploaded images
├── static/              # CSS, JS, and static assets
├── templates/           # HTML templates
├── manage.py
└── README.md
```

---

## 🧠 Project Motivation

Birdwatching often relies on word-of-mouth or scattered online forums to locate birds in specific regions. BirdAlert centralizes this information into a single platform where users can contribute verified sightings, making birdwatching more accessible, collaborative, and data-driven.

---

## 📌 Learning Objectives

This project focuses on applying core computer science and software engineering concepts, including:

* Full-stack web application development
* MVC/MVT architecture using Django
* Relational database design
* User authentication and authorization
* File uploads and media handling
* Clean code practices and documentation

---

## 🔮 Future Enhancements

* Interactive map visualization of sightings
* Bird species filtering and search
* Commenting and discussion on sightings
* Admin moderation tools
* Mobile-friendly UI
* AI-based bird image classification

---

## ⚙️ Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/Bird-Alert.git
   ```

2. Navigate into the project directory:

   ```bash
   cd Bird-Alert
   ```

3. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Open your browser and visit:

   ```text
   http://127.0.0.1:8000/
   ```

---

## 👤 Author

**Omar Alanis**
Computer Science Student
Senior Project – 2025–2026

---

## 📜 License

This project is for academic and educational purposes. License details may be added in the future.

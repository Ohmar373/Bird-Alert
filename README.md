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
* **Frontend:** HTML, CSS, Django Templates, JavaScript
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

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.10+** ([Download here](https://www.python.org/downloads/))
- **Git** ([Download here](https://git-scm.com/))
- A terminal/command prompt

### Step 1: Clone the Repository

```bash
git clone https://github.com/Ohmar373/Bird-Alert.git
cd Bird-Alert/Bird-Alert
```

### Step 2: Create a Virtual Environment

Create an isolated Python environment for the project:

```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root (same directory as `manage.py`):

```bash
touch .env  # On Windows: type nul > .env
```

Add the following to your `.env` file:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

### Step 6: Load Bird Species Data

The application includes a comprehensive database of **10,000+ bird species** from the eBird/Clements checklist. Load this data:

```bash
python manage.py import_birds bird_alert/data/BirdSpeciesList.csv
```

**Note:** This may take 2-3 minutes to complete. You'll see progress updates as the import runs.

### Step 7: Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account. You'll use this to access the admin panel.

### Step 8: Run the Development Server

```bash
python manage.py runserver
```

### Step 9: Access the Application

Open your browser and visit:
```
http://127.0.0.1:8000/
```

To access the admin panel:
```
http://127.0.0.1:8000/admin/
```

---

## 🎯 First Steps After Setup

1. **Create an Account:** Register a new user at the home page
2. **Log In:** Use your credentials to access the app
3. **Add a Sighting:** Click "Add Sighting" to log a bird observation
4. **Use Autocomplete:** Start typing a bird's common name to see suggestions from the database

---

## 📚 Project Features

### Bird Species Search
- Autocomplete search with 10,000+ bird species
- Shows both common names and scientific names
- Fast, responsive search as you type

### Sighting Logging
- Record location via map click
- Log weather conditions
- Add optional notes/descriptions
- View all your past sightings

### User Authentication
- Secure login/logout
- User registration
- Password protection

---

## 🔧 Development Commands

```bash
# Run the development server
python manage.py runserver

# Create a superuser (admin)
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Make migrations
python manage.py makemigrations

# Access Django shell
python manage.py shell

# Import bird species from CSV
python manage.py import_birds bird_alert/data/BirdSpeciesList.csv
```

---

## 📁 Project Structure

```text
Bird-Alert/
├── bird_alert/                    # Main Django project settings
│   ├── settings.py               # Project configuration
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # Production server config
│
├── sightings/                     # Bird sightings app
│   ├── models.py                 # BirdSpecies and Sighting models
│   ├── views.py                  # View logic
│   ├── forms.py                  # Form definitions
│   ├── urls.py                   # App-specific URLs
│   ├── management/commands/      # Custom Django commands
│   │   └── import_birds.py       # Import bird data from CSV
│   └── templates/                # HTML templates
│
├── user/                          # User authentication app
│   ├── models.py                 # User models
│   ├── views.py                  # Auth views
│   └── templates/                # Auth templates
│
├── data/                          # Data files
│   └── BirdSpeciesList.csv       # Comprehensive bird species database
│
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🔒 Security Notes

- **Never commit `.env` file** - It's already in `.gitignore`
- **Keep `SECRET_KEY` private** - Generate a new one for production
- **Debug mode:** Only enable `DEBUG=True` during development
- For production, update `ALLOWED_HOSTS` in `settings.py`

---

## 👤 Author

**Omar Alanis**,
**Adam Garcia**,
**Alejandro Barragan**
Computer Science Students
Senior Project – 2025–2026

---

## 📜 License

This project is for academic and educational purposes. License details may be added in the future.

---
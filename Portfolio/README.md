# My Portfolio Website

Welcome to my portfolio website! This project showcases my work, skills, and experiences in a responsive and aesthetic way. The website is built using the Fastapi framework in Python.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [License](#license)
- [Contact](#contact)

## Project Overview
This is a personal portfolio website designed to present my projects, skills, and experiences. It includes various sections like an about page, portfolio gallery, and a contact form. The site is fully responsive and includes some 3D elements to enhance the visual appeal.

## Features
- **Responsive Design:** Works seamlessly on desktop, tablet, and mobile devices.
- **Modern Aesthetic:** Clean, professional design with smooth animations and 3D elements.
- **Portfolio Showcase:** A dedicated section to display my projects with descriptions and links.
- **Contact Form:** Allows visitors to get in touch with me directly from the website.

## Technologies Used
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Bootstrap, Custom CSS
- **3D Elements:** 
- **Other Tools:** 

## Setup Instructions
To set up the project locally, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/portfolio-website.git
    cd portfolio-website
    ```

2. **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment:**
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

4. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5. **Run the application:**
    ```bash
    python run.py
    ```

6. **Access the website:**
    Open your web browser and go to `http://0.0.0.0:8000/`.

## Usage
Once the server is running, you can navigate through the various sections of the website:
- **Home:** Overview of who I am and what I do.
- **Portfolio:** Gallery of my projects with descriptions and links.
- **Contact:** A form to send me a message directly.

## Project Structure
```plaintext
portfolio-website/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
|   |
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── portfolio.html
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py
|   |
│   ├── __init__.py
│   ├── routes.py
│   └── models.py
|
├── config.py
├── main.py
├── requirements.txt
└── README.md

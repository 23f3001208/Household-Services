# Household Services Application

## Description

A multi-user application connecting customers, service professionals, and administrators to manage household services effectively. Built with Flask, Jinja2, Bootstrap, and SQLite, the app provides role-based functionalities for admins, customers, and service professionals.

## Features

### Admin:

- Manage users and services.
- Approve/reject service professionals.
- Monitor service requests and reviews.

### Customer:

- Register/login, create service requests, and review services.
- Search services by name or location.

### Service Professional:

- Accept/reject service requests.
- Manage assigned services and update status.

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Jinja2, Bootstrap
- **Database**: SQLite

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/23f3001208/Household-Services.git
   cd Household-Services
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   flask run
   ```
4. **Access the app at http://127.0.0.1:5000**

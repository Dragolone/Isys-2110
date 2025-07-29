# Death Star Management System

This project is a visual management system simulating the operation of the Empire's Death Star. It supports resource management, mission scheduling, planet information, alert monitoring, and more. Suitable for course projects, demonstrations, and learning purposes.

## Features
- Login/Registration system
- Resource management
- Mission management
- Planet management
- Alerts and reports
- Modern, beautiful UI with multi-user support

## Technologies Used
- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, Jinja2 templates
- **Data Storage:** JSON files (for demo; can be extended to use a database)
- **Other:** Bootstrap (optional), Google Fonts

## Deployment

### Local Deployment (Recommended for Evaluators)
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the application:**
   ```bash
   python app.py
   ```
4. **Open your browser and visit:**
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Production Deployment (Optional)
- You can deploy this Flask app to any WSGI-compatible server (e.g., Gunicorn, uWSGI) behind Nginx or Apache.
- For cloud deployment, platforms like Heroku, PythonAnywhere, or AWS Elastic Beanstalk are supported.
- Make sure to set a secure `app.secret_key` in production and use a persistent database if needed.

## Default Accounts
- Email: admin@example.com  Password: 123456
- Email: test@example.com  Password: 654321

You can also create a new account via the Sign Up page.

## Usage Instructions for Evaluators
- Visiting the home page will redirect you to the login screen if you are not logged in.
- After logging in, you will be taken to the Dashboard where you can manage all system features (resources, missions, planets, alerts, etc.).
- To log out, click the logout button or visit `/logout`.
- You can test registration, login, and all management features directly from the web interface.

---
For any questions, please contact the developers or team members.

```
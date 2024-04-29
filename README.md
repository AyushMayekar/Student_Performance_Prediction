
## Student Performance Prediction System (PERFORMX)

Welcome to the Student Performance Prediction System repository! This project aims to predict the future academic performance of students based on various factors such as study habits, screen time, and sleep patterns. By analyzing past performance data and current lifestyle choices, the system provides insights and recommendations to help students improve their academic outcomes.

### Features

- **CGPA Prediction**: The system predicts the Cumulative Grade Point Average (CGPA) for future semesters based on historical performance data.
  
- **Daily Schedule Analysis**: Analyzes the daily schedule of students, including study hours, screen time, sleep duration, and other activities, to identify areas for improvement.

- **Personalized Recommendations**: Provides personalized tips and strategies to help students align their daily routines with ideal schedules for better academic performance.

- **Visualizations**: Generates visualizations such as pie charts and trend graphs to illustrate the student's current schedule and predicted academic performance.


## Tech Stack

**Python**: Used for backend development, integrating a Large Language Model (Google Gemini LLM), integrating a Machine Learning Model (Linear Regression), overall connectivity.

**HTML, CSS, Javascript**: Used for creating user interface and designing the website

**Firebase**: Used for maintaining the database, Authentication and user information

### How it Works

1. **Data Collection**: The system collects data on past academic performance, study habits, and lifestyle choices from the user.

2. **Analysis**: Using machine learning algorithms, the system analyzes the data to predict future academic performance and identify areas for improvement in the student's daily schedule.

3. **Recommendations**: Based on the analysis, the system provides personalized recommendations and tips to help the student optimize their daily routine for better academic outcomes.

### Installation

To use the Student Performance Prediction System, follow these steps:

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/yourusername/student-performance-prediction.git
   ```

2. Create a firebase project, Create Firestore Database with document users and generate a private service key of the project for integration with python at [Firebase Official Website](https://firebase.google.com/)

3. Generate a Google Gemini API key at  [Google's Official Website](https://aistudio.google.com/app/apikey) and save it in a .env file

4. Install other required dependencies

6. Change the Paths in the files accordingly 

7. Change the Database Credentials in the files accordingly 

8. Run the Backend application (app.py) from the terminal:
   ```
   waitress-serve --listen=*:5000 app:app
   ```

9. Run the Frontend application (homepage.html):
   ```
   Ctrl+f5
   ```

### Working

Check out this YouTube video for a working of the Student Performance Prediction System in action

[![Watch the video](https://img.youtube.com/vi/HMUlhZm2rI8/maxresdefault.jpg)](https://youtu.be/HMUlhZm2rI8) 

### Screenshots

![1.](https://github.com/AyushMayekar/Student_Performance_Prediction/blob/main/static/Screenshot%202024-04-24%20105439.png)
![2.](https://github.com/AyushMayekar/Student_Performance_Prediction/blob/main/static/Screenshot%202024-04-24%20105452.png)


### Contact

For more information about the Student Performance Prediction System, you can reach out to the project creator on [LinkedIn](https://www.linkedin.com/in/ayush-mayekar-b9b883284).



Thank you for using the Student Performance Prediction System! We hope it helps you achieve academic success.

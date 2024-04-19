import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify,render_template,redirect,url_for
from flask_cors import CORS
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression



app = Flask(__name__)
CORS(app)
load_dotenv()
# Configure Flask to serve static files from the 'static' directory
app.static_url_path = '/static'
app.static_folder = 'static'


# Generate a random string of 32 characters for the secret key
secret_key = os.urandom(32)
app.secret_key = secret_key

# Configure Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")
genai.configure(api_key=gemini_api_key)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(r"C:\Users\afnan_sdcddxx\Student_Performance_Prediction\config_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to retrieve selected subjects from Firestore
def get_selected_subjects(user_id):
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            selected_subjects = user_doc.get('selectedSubjects')
            if selected_subjects:
                selected_subjects_list = [subject for subject in selected_subjects]
                return selected_subjects_list
            else:
                return []
        else:
            print(f"User document with ID {user_id} does not exist.")
            return []
    except Exception as e:
        print(f"Error retrieving selected subjects: {e}")
        return []

def get_selected_Cgpa(user_id):
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            selected_cgpa = user_doc.get('Cgpa')
            if selected_cgpa:
                selected_cgpa_list = [float(item['cgpa']) for item in selected_cgpa if item.get('cgpa') != ''] 
                return selected_cgpa_list
            else:
                return []
        else:
            print(f"User document with ID {user_id} does not exist.")
            return []
    except Exception as e:
        print(f"Error retrieving cgpa: {e}")
        return []
    

def predict_future_cgpa(selected_cgpa_list):
    num_semesters = len(selected_cgpa_list)
    X = np.arange(1, num_semesters + 1).reshape(-1, 1)
    y = np.array(selected_cgpa_list)

    model = LinearRegression()
    model.fit(X, y)

    future_semesters = np.arange(num_semesters + 1, min(num_semesters + 6, 9)).reshape(-1, 1)
    predicted_cgpa = model.predict(future_semesters)
    predicted_cgpa = np.minimum(predicted_cgpa, 10)
    return predicted_cgpa


def retrieve_other_info(user_id):
        try:
             user_ref = db.collection('users').document(user_id)
             user_doc = user_ref.get()

             if user_doc.exists:
                 other_info={}
                 data=user_doc.to_dict()
                 if 'sleepingHours' in data:
                    other_info['sleepingHours'] = data['sleepingHours']
                 if 'studyHours' in data:
                    other_info['studyHours'] = data['studyHours']
                 if 'screenTime' in data:
                    other_info['screenTime'] = data['screenTime']
                 if 'learningStyle' in data:
                    other_info['learningStyle'] = data['learningStyle']

                 return other_info
             else :
                 return f'doc {user_id} does not exist'
        except Exception as e:
            print(f"Error retreiving other info: {e}")     


# Route to handle user requests
@app.route('/user', methods=['POST'])
def receive_user_id():
    try:
        user_id = request.json.get('userId')
        if user_id:
            output = get_selected_subjects(user_id)
            piechart=retrieve_other_info(user_id)
            if output and piechart is not None:
                piechart_data = {key: value for key, value in piechart.items() if key != 'learningStyle'}
                total_hours = 24
                screen_time = int(piechart_data.get('screenTime', 0))
                study_time = int(piechart_data.get('studyHours', 0))
                sleep_hours = int(piechart_data.get('sleepingHours', 0))
                other_activities_hours = total_hours - (screen_time + study_time + sleep_hours)
                piechart_data['Other Activities'] = other_activities_hours
                kt_tips = generate_output(output)
                comparison=generate_comparison(piechart_data)
                create_piechart(user_id,piechart_data)
                if kt_tips and comparison :
                    user_ref = db.collection('users').document(user_id)
                    user_ref.update({'kt_tips': kt_tips,'comparison': comparison})
                    return redirect(url_for('display_kt_output',user_id=user_id))
                else:
                    return 'Error in generating LLM response', 200
            else:
                return 'User data not found', 404
        else:
            return 'User ID not provided', 400
    except Exception as e:
        print('Error:', e)
        return 'Internal Server Error', 500



# Function to generate response using GenerativeAI model
def generate_output(selected_subjects_list):
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt_2 = f"""Semester and Subjects: ({selected_subjects_list})

Goal: Develop effective strategies to improve academic performance in the above given subjects.

Request: Please provide concise and professional bullet points on achieving these goals for each subject listed.

Additionally:

Focus on actionable strategies that can be implemented immediately.
Prioritize clear and easy-to-understand explanations."""  
        response_2 = model.generate_content(prompt_2)
        return response_2.text
    except Exception as e:
        error_message = f"Error generating response: {e}"
        return error_message
    


def generate_comparison(piechart_data):
    try:
        model = genai.GenerativeModel("gemini-pro")
        ideal_data={'Max_ScreenTime':2, 'Enough_SleepHours':8, 'Min-StudyTime':2,'Other_Activities':12}
        prompt_2 = f"""Task: Compare a student's current daily schedule with an ideal daily schedule and provide strategies to align them.

Instructions:

Given the current daily schedule of the student and an ideal daily schedule, provide comparative strategies to help the student achieve a schedule closer to the ideal one.
Present the strategies in concise bullet points, maintaining a professional tone and avoiding the use of bold formatting.
Prompt:
"Student's Current Daily Schedule: ({piechart_data})
Ideal Daily Schedule: ({ideal_data})

Compare the student's current daily schedule with the ideal daily schedule and provide comparative strategies to achieve alignment. Offer concise bullet-point recommendations for adjusting the student's schedule to better match the ideal one. Ensure the strategies are practical, actionable, and presented in a professional manner without using bold formatting."""

        response = model.generate_content(prompt_2)
        return response.text
    except Exception as e:
        error_message = f"Error generating response: {e}"
        return error_message


def create_piechart(user_id,piechart_data):
    labels = list(piechart_data.keys())
    values = list(piechart_data.values())
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    plt.pie(values, labels=labels,colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('PIECHART OF YOUR DAILY SCHEDULE')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    piechart_filename=f"static/{user_id}_performance_piechart.png"
    plt.savefig(piechart_filename)
    plt.clf()    
    return 'Piechart saved'


@app.route('/cgpa', methods=['POST'])
def receive_user_id_cgpa():
    try:
        user_id = request.json.get('userId')
        if user_id:
            output = get_selected_Cgpa(user_id)
            piechart=retrieve_other_info(user_id)
            if output and piechart is not None:
                piechart_data = {key: value for key, value in piechart.items() if key != 'learningStyle'}
                total_hours = 24
                screen_time = int(piechart_data.get('screenTime', 0))
                study_time = int(piechart_data.get('studyHours', 0))
                sleep_hours = int(piechart_data.get('sleepingHours', 0))
                other_activities_hours = total_hours - (screen_time + study_time + sleep_hours)
                piechart_data['Other Activities'] = other_activities_hours
                cgpa = predict_future_cgpa(output)
                if cgpa is not None:
                   tips=generate_tips(output,cgpa)
                   create_piechart(user_id,piechart_data)
                   Create_Graph(output,cgpa,user_id)
                   comparison=generate_comparison(piechart_data)
                   if user_id and tips and comparison:
                       user_ref = db.collection('users').document(user_id)
                       user_ref.update({'tips': tips,'comparison': comparison})
                       return redirect(url_for('display_output',user_id=user_id))
                   else:
                        return 'User ID or tips not generated', 500
                else:
                    return 'Error in generating Graph', 200
            else:
                return 'User data not found', 404
        else:
            return 'User ID not provided', 400
    except Exception as e:
        print('Error:', e)
        return 'Internal Server Error', 



def generate_tips(selected_cgpa_list,predicted_cgpa):
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt_2 = f"""Given your historical CGPA records:({selected_cgpa_list}) and the predicted future CGPAs:({predicted_cgpa}), provide tailored strategies to either address a declining trend or capitalize on an inclining trend in academic performance(only one) compulsorily checking only from left to right in the given data collectively. Ensure the output offers clear and actionable advice suitable for the identified trend, maintaining a professional and easily understandable structure without using any bold formatting."""

        response_2 = model.generate_content(prompt_2)
        return response_2.text
    except Exception as e:
        error_message = f"Error generating response: {e}"
        return error_message
    

def create_piechart(user_id,piechart_data):
    labels = list(piechart_data.keys())
    values = list(piechart_data.values())
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    plt.pie(values, labels=labels,colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('PIECHART OF YOUR DAILY SCHEDULE')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    piechart_filename=f"static/{user_id}_performance_piechart.png"
    plt.savefig(piechart_filename)
    plt.clf()    
    return 'Piechart saved'


def Create_Graph(output,cgpa,user_id):
     num_semesters = len(output)
     future_semesters = np.arange(num_semesters + 1, min(num_semesters + 6, 9))
     plt.figure(figsize=(8, 6))
     plt.plot(future_semesters, cgpa, linestyle='dashed', color='green')  # Line for predicted CGPAs
     plt.scatter(np.arange(1, num_semesters + 1), output, color='blue', label='Past CGPA')
     plt.scatter(future_semesters, cgpa, color='green', label='Predicted CGPA')
     plt.title('CGPA Prediction for Future Semesters')
     plt.xlabel('Semester Number')
     plt.ylabel('CGPA')
     plt.xlim(0,9)
     plt.ylim(0, 11)
     plt.subplots_adjust(top=0.9,bottom=0.1)
     plt.legend()
     plt.grid(True)
     filename=f"static/{user_id}_performance_graph.png"
     plt.savefig(filename)
     plt.clf()
     return "Image Saved Successfully!"


def generate_comparison(piechart_data):
    try:
        model = genai.GenerativeModel("gemini-pro")
        ideal_data={'Max_ScreenTime':2, 'Enough_SleepHours':8, 'Min-StudyTime':2,'Other_Activities':12}
        prompt_2 = f"""Task: Compare a student's current daily schedule with an ideal daily schedule and provide strategies to align them.

Instructions:

Given the current daily schedule of the student and an ideal daily schedule, provide comparative strategies to help the student achieve a schedule closer to the ideal one.
Present the strategies in concise bullet points, maintaining a professional tone and avoiding the use of bold formatting.
Prompt:
"Student's Current Daily Schedule: ({piechart_data})
Ideal Daily Schedule: ({ideal_data})

Compare the student's current daily schedule with the ideal daily schedule and provide comparative strategies to achieve alignment. Offer concise bullet-point recommendations for adjusting the student's schedule to better match the ideal one. Ensure the strategies are practical, actionable, and presented in a professional manner without using bold formatting."""

        response = model.generate_content(prompt_2)
        return response.text
    except Exception as e:
        error_message = f"Error generating response: {e}"
        return error_message

       

@app.route('/output/<string:user_id>')
def display_output(user_id):
       return render_template("output.html", user_id=user_id)


@app.route('/kt_output/<string:user_id>')
def display_kt_output(user_id):
    return render_template("kt-output.html", user_id=user_id)


    

# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)
    

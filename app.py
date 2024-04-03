import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
load_dotenv()

# Configure Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")
genai.configure(api_key=gemini_api_key)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(r"C:\Users\ayush\OneDrive\Desktop\Student Performance Prediction\config_key.json")
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
                selected_cgpa_list = [cgpa for cgpa in selected_cgpa]
                return selected_cgpa_list
            else:
                return []
        else:
            print(f"User document with ID {user_id} does not exist.")
            return []
    except Exception as e:
        print(f"Error retrieving cgpa: {e}")
        return []
    

# Route to handle user requests
@app.route('/user', methods=['POST'])
def receive_user_id():
    try:
        user_id = request.json.get('userId')
        if user_id:
            output = get_selected_subjects(user_id)
            if output is not None:
                tips = generate_output(output)
                if tips is not None:
                    print(tips)
                    return jsonify({'tips': tips}), 200
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
        prompt_2 = f"""semester and subjects:{selected_subjects_list}."""  
        response_2 = model.generate_content(prompt_2)
        return response_2.text
    except Exception as e:
        error_message = f"Error generating response: {e}"
        return error_message


@app.route('/cgpa', methods=['POST'])
def receive_user_id_cgpa():
    try:
        user_id = request.json.get('userId')
        if user_id:
            output = get_selected_Cgpa(user_id)
            if output is not None:
                cgpa = generate_output_cgpa(output)
                if cgpa is not None:
                    print(cgpa)
                    return jsonify({'cgpa': cgpa}), 200
                else:
                    return 'Error in generating LLM response', 200
            else:
                return 'User data not found', 404
        else:
            return 'User ID not provided', 400
    except Exception as e:
        print('Error:', e)
        return 'Internal Server Error', 
# Function to generate response using GenerativeAI model
def generate_output_cgpa(selected_cgpa_list):
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt_2 = f"""just display cgpa:{selected_cgpa_list}."""  
        response_2 = model.generate_content(prompt_2)
        return response_2.text
    except Exception as e:
        error_message = f"Error generating response: {e}"
        return error_message
    

# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)

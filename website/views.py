from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note,File
from . import db
import json
from openai import OpenAI
import os
import uuid

import boto3, botocore
from dotenv import load_dotenv
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png'}



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

views = Blueprint('views', __name__)

s3 = boto3.client('s3')
s3 = boto3.resource(
    service_name="s3",
    region_name="ap-south-1",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)



load_dotenv()
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPEN_API_KEY"),
)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)





@views.route('/chatbot', methods=['POST'])
def chatbot():





    user_input = request.form.get("message")

   # Use the OpenAI API to generate a response
    prompt = f"User: {user_input}\nChatbot: " 
    chat_history = []
    response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": user_input,
        }
    ],
    model="gpt-3.5-turbo",
)
    print(response)


    # Extract the response text from the OpenAI API result
    response_json = response.json()


    bot_response = response.choices[0].message.content
    #render the chatbot tempalte with the repose text 
    chat_history.append(f"User: {user_input}\nChatbot: {bot_response}")



    return render_template("chatbot.html", user_input = user_input, bot_response=bot_response,user=current_user)    
      




@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
        if request.method == "POST":
            uploaded_file = request.files["file-to-save"]
            if not allowed_file(uploaded_file.filename):
                return "FILE NOT ALLOWED!"

            new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()

            bucket_name = "bevops"
            s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)

            file = File(original_filename=uploaded_file.filename, filename=new_filename,
                bucket=bucket_name, region="ap-south-1",user_id = current_user.id)

            db.session.add(file)
            db.session.commit()

            #return redirect(url_for("upload.html"))

        files = File.query.filter_by(user_id = current_user.id).all()

        return render_template("upload.html", user=current_user, files=files)






"""
    response = openai.Completion.create(
    engine="text-davinci-002",
     prompt=prompt,
     temperature=0.5,
     max_tokens=60,
     top_p=1,
     frequency_penalty=0,
     stop= ["\nUser: ", "\nChatbot: "])  """
     
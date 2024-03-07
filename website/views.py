from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from openai import OpenAI
import os
import boto3
from dotenv import load_dotenv

views = Blueprint('views', __name__)

s3 = boto3.client('s3')




load_dotenv()
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPEN_API_KEY"),
)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

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
      











"""
    response = openai.Completion.create(
    engine="text-davinci-002",
     prompt=prompt,
     temperature=0.5,
     max_tokens=60,
     top_p=1,
     frequency_penalty=0,
     stop= ["\nUser: ", "\nChatbot: "])  """
     
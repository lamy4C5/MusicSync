from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from googleapiclient.discovery import build
from openai import OpenAI
import os
import requests


app = Flask(__name__)

@app.after_request
def set_headers(response):
    response.headers["Referrer-Policy"] = 'no-referrer'
    return response

# Load environment variables
load_dotenv()
# Set OpenAI API key
#openai.api_key = os.getenv("GPT_API_KEY")
client = OpenAI()

# Set YouTube API key
ytapikey = os.getenv("YOUTUBE_API_KEY")

# YouTube API client
#youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


@app.route("/")
def home():
    return render_template("index.html")  # Serve the HTML file

@app.route('/queryai/',methods=['GET','POST'])

def queryai():
    if request.method == 'POST':
        mood = request.form.get('mood', '')
        activity = request.form.get('activity', '')

        # Validate input
        if not mood or not activity:
            return render_template("index.html", error="Mood and activity are required!")

        prompt = "I am currently feeling: "+mood+", and the activity I am currently doing is: "+activity+". Find a youtube video (without lyrics) that would play as background music if my life was an epic movie, based on my current mood and activity. RESPOND ONLY WITH A PROMPT FOR THE YOUTUBE SEARCH TO PULL UP A RELEVANT VIDEO OF MUSIC."
        aiResponse = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Responds to queries with only the necessary information and nothing more."},
                {
                    "role": "user",
                    "content":prompt
                }
            ],
            temperature=0.3
        )
        
        ytprompt = aiResponse.choices[0].message.content
        result = get_youtube_video_id(ytprompt)
        
        
        print(ytprompt)
        print(result)
        
        
        chosenurl = result
        chosenurl = "https://www.youtube.com/embed/" + chosenurl
        # Pass the YouTube URL to the template
        return render_template("index.html", yturl=chosenurl)

    # For GET requests, just show the form
    return render_template("index.html")

def get_youtube_video_id(search_query):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': search_query,
        'key': ytapikey,
        'maxResults': 1,
        'type': 'video'
    }
    
    response = requests.get(search_url, params=params)
    results = response.json()
    print(results)
    
    if 'items' in results and len(results['items']) > 0:
        video_id = results['items'][0]['id']['videoId']
        return video_id
    else:
        return None
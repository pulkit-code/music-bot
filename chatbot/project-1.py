from flask import Flask, render_template, request, redirect, url_for
import nltk
from textblob import TextBlob
import webbrowser
from pytube import Search

app = Flask(__name__)

def analyze_mood(text):
    blob = TextBlob(text)
    sentiment_polarity = blob.sentiment.polarity
    
    if sentiment_polarity > 0.5:
        return "excited"
    elif sentiment_polarity > 0.2 and sentiment_polarity <= 0.5:
        return "happy"
    elif sentiment_polarity > 0 and sentiment_polarity <= 0.2:
        return "content"
    elif sentiment_polarity < 0 and sentiment_polarity >= -0.2:
        return "sad"
    elif sentiment_polarity < -0.2 and sentiment_polarity >= -0.5:
        return "depressed"
    elif sentiment_polarity < -0.5:
        return "angry"
    else:
        return "neutral"

def recommend_music(mood, music_type, language, attempt=0, preference=None):
    if preference:
        search_query = preference
    else:
        search_query = f"{music_type} songs in {language} for when you are feeling {mood}"
    search = Search(search_query)
    video_url = search.results[attempt].watch_url
    return video_url

@app.route("/", methods=["GET", "POST"])
def index():
    print(f"Request method: {request.method}")
    if request.method == "POST":
        user_input = request.form["user_input"]
        print(f"User input: {user_input}")
        if not hasattr(index, 'mood'):
            index.mood = analyze_mood(user_input)
            print(f"Analyzed mood: {index.mood}")
            return render_template("index.html", message=f"You seem to be feeling {index.mood}. What type of music would you like to listen to (e.g., pop, rock, classical)?")
        elif not hasattr(index, 'music_type'):
            index.music_type = user_input
            print(f"Selected music type: {index.music_type}")
            return render_template("index.html", message="Great! Now, what language do you prefer for your music?")
        elif not hasattr(index, 'language'):
            index.language = user_input
            index.attempt = 0
            index.preference = None
            print(f"Selected language: {index.language}")
            return redirect(url_for("recommendation"))
        elif hasattr(index, 'waiting_for_feedback') and index.waiting_for_feedback:
            index.waiting_for_feedback = False
            if user_input.lower() in ["no", "nah", "nope"]:
                print("User did not like the recommendation")
                index.attempt += 1  # Try the next recommendation
                return redirect(url_for("recommendation"))
            else:
                print("User liked the recommendation")
                delattr(index, 'mood')
                delattr(index, 'music_type')
                delattr(index, 'language')
                return render_template("index.html", message="Great! Enjoy your music.")
        elif hasattr(index, 'waiting_for_preference') and index.waiting_for_preference:
            index.waiting_for_preference = False
            index.preference = user_input
            index.attempt = 0
            print(f"User preference: {index.preference}")
            return redirect(url_for("recommendation"))
    return render_template("index.html", message="Hi, I am Jarvis. I am your music assistant and I will help you find the perfect music. How are you feeling today?")

@app.route("/recommendation")
def recommendation():
    try:
        recommendation = recommend_music(index.mood, index.music_type, index.language, index.attempt, index.preference)
        webbrowser.open(recommendation)
        index.waiting_for_feedback = True
        print(f"Music recommendation: {recommendation}")
        return render_template("index.html", message=f"Here's some {index.language} music for you: {recommendation}. Did you like it?")
    except IndexError:
        # If no more recommendations are available
        return render_template("index.html", message="I'm out of suggestions for now. Would you like to tell me your favorite song or artist?")

if __name__ == "__main__":
    app.run(debug=True)

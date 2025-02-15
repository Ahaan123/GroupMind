from flask import Flask, render_template, request, jsonify
from reddit_scaper import *
from summarizer import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        subreddit_name = request.form['subreddit']
        posts = get_top_posts(subreddit_name)
        all_text = " ".join([post['title'] + " " + post['selftext'] + " " + " ".join(post['comments']) for post in posts])
        summary = generate_summary(all_text)
        return render_template('index.html', summary=summary, subreddit=subreddit_name)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

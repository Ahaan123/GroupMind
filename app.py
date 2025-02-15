import prawcore
from flask import Flask, render_template, request, jsonify, Response, json
import praw
import openai
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Reddit API credentials
REDDIT_CLIENT_ID = 'ITL3QHc_Ik9oJFA3ZwcTmA'
REDDIT_CLIENT_SECRET = '4yzZfX8BTljM_J4KfjyAaMG1n4D5Sg'
REDDIT_USER_AGENT = 'GroupMind'

# OpenAI API key
OPENAI_API_KEY = ''

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)
openai.api_key = OPENAI_API_KEY


def scrape_subreddit(subreddit_name, limit=100):
    """Scrape text-only posts from a subreddit."""
    posts = []

    try:
        subreddit = reddit.subreddit(subreddit_name)

        # Validate subreddit existence
        try:
            subreddit.id  # Raises an exception if subreddit does not exist
        except prawcore.exceptions.NotFound:
            yield json.dumps({"error": f"Subreddit '{subreddit_name}' not found. Please enter a valid subreddit."})
            return
        except prawcore.exceptions.Forbidden:
            yield json.dumps({"error": f"Subreddit '{subreddit_name}' is private or restricted. Cannot access data."})
            return

        for i, post in enumerate(subreddit.new(limit=limit)):
            if post.selftext.strip():  # Only include text posts
                posts.append(post.selftext)

            # Stream progress updates
            yield json.dumps({"progress": (i + 1) / limit * 100, "message": f"Scraping post {i + 1} of {limit}..."})
            time.sleep(0.25)  # Prevent hitting rate limits

        # Train chatbot with collected posts
        chatbot_response = train_chatbot(posts, subreddit_name)
        yield json.dumps({"progress": 100, "message": "Scraping complete!", "response": chatbot_response})

    except prawcore.exceptions.RequestException as e:
        yield json.dumps({"error": f"Network error while accessing subreddit: {str(e)}"})
    except Exception as e:
        yield json.dumps({"error": f"Unexpected error: {str(e)}"})


def train_chatbot(posts, subreddit_name):
    """Train a chatbot using OpenAI's API."""
    if not posts:
        return "No relevant posts found to train the chatbot."

    # Limit to first 10 posts to avoid exceeding OpenAI's max token limit
    formatted_posts = "\n\n".join(posts[:10])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "You are a chatbot that mimics the behavior of the average user of a subreddit."},
                {"role": "user",
                 "content": f"The following are posts from r/{subreddit_name}. Mimic the average user:\n\n{formatted_posts}"}
            ]
        )
        return response['choices'][0]['message']['content']

    except openai.error.OpenAIError as e:
        return f"OpenAI API error: {str(e)}"
    except Exception as e:
        return f"Unexpected error in AI training: {str(e)}"


@app.route('/analyze', methods=['POST'])
def analyze_subreddit():
    """Handle subreddit analysis request."""
    print('Received /analyze request')

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    subreddit_name = data.get('subreddit')

    if not subreddit_name:
        return jsonify({"error": "Subreddit name is required"}), 400
    ret = Response(scrape_subreddit(subreddit_name), mimetype='application/json')
    print(ret.json)
    return ret


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)



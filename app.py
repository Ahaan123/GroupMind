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
chat_sessions = {}

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)
openai.api_key = OPENAI_API_KEY

def scrape_subreddit(subreddit_name, limit=100):
    """Scrape text-only posts from a subreddit with streaming updates."""
    posts = []

    try:
        subreddit = reddit.subreddit(subreddit_name)

        # Check if the subreddit exists
        try:
            subreddit.id  # Raises exception if subreddit does not exist
        except prawcore.exceptions.NotFound:
            print("not a subreddit!")
            yield json.dumps(
                {"error": f"Subreddit '{subreddit_name}' not found. Please enter a valid subreddit."}) + "\n"
            return
        except prawcore.exceptions.Forbidden:
            print("restricted!")
            yield json.dumps(
                {"error": f"Subreddit '{subreddit_name}' is private or restricted. Cannot access data."}) + "\n"
            return

        # Fetch and process posts
        for i, post in enumerate(subreddit.new(limit=limit)):
            print(post.title)
            if post.title.strip():  # Only include text posts
                posts.append(post.title)
                print("hey!")

            # Stream progress updates
            yield json.dumps(
                {"progress": (i + 1) / limit * 100, "message": f"Scraping post {i + 1} of {limit}..."}) + "\n"
            time.sleep(0.25)  # Prevent API rate limit

        # Train chatbot with collected posts
        chatbot_response = train_chatbot(posts, subreddit_name)
        chat_sessions[subreddit_name] = [
            {"role": "system",
             "content": f"You are a chatbot that mimics the behavior of users from r/{subreddit_name}."},
            {"role": "assistant", "content": chatbot_response}
        ]

        yield json.dumps({"progress": 100, "message": "Scraping complete!", "response": chatbot_response}) + "\n"

    except prawcore.exceptions.RequestException as e:
        yield json.dumps({"error": f"Network error while accessing subreddit: {str(e)}"}) + "\n"
    except Exception as e:
        yield json.dumps({"error": f"Unexpected error: {str(e)}"}) + "\n"


def train_chatbot(posts, subreddit_name):
    """Train a chatbot using OpenAI's API."""
    print("called!")
    if not posts:
        print("no posts!")
        return "No relevant posts found to train the chatbot."

    # Limit to first 10 posts, truncate each post to 500 characters
    formatted_posts = "\n\n".join(post[:500] for post in posts[:10])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a chatbot that mimics the behavior of the average user of a subreddit."},
                {"role": "user",
                 "content": f"The following are posts from r/{subreddit_name}. Mimic the average user:\n\n{formatted_posts}"}
            ]
        )
        print("yo we got a response!")
        return response['choices'][0]['message']['content']

    except openai.OpenAIError as e:
        print(e)
        return f"OpenAI API error: {str(e)}"
    except Exception as e:
        print("other error!")
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
    ret = Response(scrape_subreddit(subreddit_name, 10), content_type='application/json')
    print(ret.status_code)
    return ret


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with the trained subreddit chatbot."""
    print('Received /chat request')

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_message = data.get('message')
    subreddit_name = data.get('subreddit')

    if not user_message or not subreddit_name:
        return jsonify({"error": "Both 'message' and 'subreddit' fields are required"}), 400

    if subreddit_name not in chat_sessions:
        return jsonify({"error": "No trained chatbot found for this subreddit. Please analyze it first."}), 400

    # Append user message to chat history
    chat_sessions[subreddit_name].append({"role": "user", "content": user_message})

    try:
        # Get chatbot response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_sessions[subreddit_name]
        )

        chatbot_reply = response['choices'][0]['message']['content']

        # Append chatbot response to chat history
        chat_sessions[subreddit_name].append({"role": "assistant", "content": chatbot_reply})

        return jsonify({"response": chatbot_reply})

    except openai.error.OpenAIError as e:
        return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)




import praw
import math

# Reddit API credentials
client_id =  'ITL3QHc_Ik9oJFA3ZwcTmA'
client_secret = '4yzZfX8BTljM_J4KfjyAaMG1n4D5Sg'
user_agent = 'GroupMind'

# Initialize PRAW
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

def get_top_posts(subreddit_name, limit=500):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    for post in subreddit.top(limit=limit):
        post_data = {
            'title': post.title,
            'selftext': post.selftext,
            'comments': get_top_comments(post)
        }
        posts.append(post_data)
    
    return posts

def get_top_comments(post, top_percentage=0.2):
    post.comments.replace_more(limit=0)
    all_comments = post.comments.list()
    top_n = math.ceil(len(all_comments) * top_percentage)
    
    sorted_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)
    top_comments = [comment.body for comment in sorted_comments[:top_n]]
    
    return top_comments

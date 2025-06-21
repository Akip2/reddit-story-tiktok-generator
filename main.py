from config import CLIENT_ID, PASSWORD, REDDIT_USERNAME, CLIENT_SECRET
from voice_maker import create_audio
from video_editor import generate_video_from_audio
import praw, asyncio

ATTRACTIVE_POST_LENGTH = 800
POST_LIMIT = None

SUBS = [
    "stories",
    "RedditStoryTime",
    "tifu",
    "LetsNotMeet",
    "TrueOffMyChest"
]

def calculate_score(post) -> float:
    ratio = post.upvote_ratio
    num_comments = post.num_comments
    text = post.selftext
    
    score = 0
    # Valorizing posts with extreme ratio
    if ratio >= 0.5:
        score += ratio * 10
    else:
        score += (1 - ratio) * 10
        
    score += num_comments # Valorizing posts with lots of comments
    
    postLenDif = max(abs(ATTRACTIVE_POST_LENGTH - len(text)), 1)
    score += (1 / postLenDif) * 30 # Valorizing posts with a number of chars close to the one we want
    
    return score

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=PASSWORD,
    user_agent='script:test-bot:v1.0 (by u/' + REDDIT_USERNAME + ')'
)

print("Connected as :", reddit.user.me())

for sub_name in SUBS:
    subreddit = reddit.subreddit(sub_name)

    best_post = None
    best_score = 0
    for post in subreddit.new(limit=POST_LIMIT):
        if not post.is_self:
            continue

        score = calculate_score(post)

        if (score > best_score):
            best_score = score
            best_post = post
     
    print(best_post.title + "("+best_post.url+")\n")
    print(best_post.selftext)
    
    audio_file = asyncio.run(create_audio(best_post.selftext))
    generate_video_from_audio(audio_file)
    
    print("----------------------------------------------------------")
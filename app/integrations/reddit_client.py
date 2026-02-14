"""Reddit API integration — trending discussions and community signals."""

import praw
from config.settings import settings

_client = None


def _get_client() -> praw.Reddit:
    global _client
    if _client is None:
        _client = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
        )
    return _client


def get_trending_posts(query: str, limit: int = 20, sort: str = "relevance", time_filter: str = "month") -> list:
    """Search Reddit for trending posts related to a topic."""
    reddit = _get_client()

    posts = []
    for submission in reddit.subreddit("all").search(query, sort=sort, time_filter=time_filter, limit=limit):
        posts.append({
            "title": submission.title,
            "subreddit": str(submission.subreddit),
            "score": submission.score,
            "num_comments": submission.num_comments,
            "url": submission.url,
            "selftext": submission.selftext[:500] if submission.selftext else "",
            "created_utc": submission.created_utc,
        })

    return posts


def get_comments(post_url: str, limit: int = 20) -> list:
    """Get top comments from a Reddit post."""
    reddit = _get_client()

    submission = reddit.submission(url=post_url)
    submission.comments.replace_more(limit=0)

    comments = []
    for comment in submission.comments[:limit]:
        comments.append({
            "body": comment.body[:500],
            "score": comment.score,
        })

    return comments


def get_subreddit_trending(subreddit_name: str, limit: int = 10) -> list:
    """Get hot posts from a specific subreddit."""
    reddit = _get_client()

    posts = []
    for submission in reddit.subreddit(subreddit_name).hot(limit=limit):
        posts.append({
            "title": submission.title,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "selftext": submission.selftext[:300] if submission.selftext else "",
        })

    return posts

import praw
import database
import confparser


class RedditScraper():

    def __init__(self, subreddit: str, limit: int):
        self.sub = subreddit
        self.limit = limit
        self.config = confparser.get("config.json")

        self.reddit = praw.Reddit(client_id=self.config.reddit_id,
                                    client_secret=self.config.reddit_secret,
                                    password=self.config.reddit_password,
                                    user_agent=self.config.reddit_useragent,
                                    username=self.config.reddit_username)
        self.database = database.DB()
        self.db_ids = self.database.get_all_pasta_id()

    def get_posts(self):
        subreddit = self.reddit.subreddit(self.sub)
        hot_posts = subreddit.hot(limit=self.limit)

        post_data = []
        for post in hot_posts:
            if post.is_self and post.score >= 1:
                data = {
                    "title": post.title,
                    "url": "https://reddit.com" + post.permalink,
                    "id": post.id,
                    "text": post.selftext,
                    "upvote_count": post.score,
                }
                post_data.append(data)
        return post_data

    def scrape(self):
        reddit_posts = self.get_posts()
        for p in reddit_posts:
            self.add_to_db(p)

    def add_to_db(self, post):
        if not post['id'] in self.db_ids:
            self.database.add_pasta(post)
            self.db_ids.append(post['id'])


if __name__ == "__main__":
    rs = RedditScraper("kopyamakarna", limit=50000)
    rs.scrape()

    ids = rs.database.get_all_pasta_id()
    print(f"{len(rs.db_ids)} records before scrape")
    print(f"{len(ids)} records after scrape")

    '''
    rs = RedditScraper("kopyamakarna", limit=50000)
    posts = rs.get_posts()

    # writes all to a json
    with codecs.open("posts/posts.json", "w+", "utf-8") as json_file:
        json.dump(posts, json_file, ensure_ascii=False)
    '''
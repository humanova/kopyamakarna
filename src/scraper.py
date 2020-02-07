import praw
import database
import confparser
from logger import logging


class RedditScraper:

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
                    "upvote": post.score,
                    "timestamp": post.created}
                post_data.append(data)
        return post_data

    def scrape(self):
        logging.info("[Scraper] Trying to scrape new posts")
        reddit_posts = self.get_posts()
        new_posts = list()
        tb_updated_posts = list()

        for p in reddit_posts:
            if not p['id'] in self.db_ids:
                new_posts.append(p)
                self.db_ids.append(p['id'])
            else:
                tb_updated_posts.append(p)

        if len(new_posts) > 0:
            logging.info(f"[Scraper] Scraped {len(new_posts)} new post(s)")
            self.add_posts_to_db(new_posts)

        self.update_scraped_posts_to_db(tb_updated_posts)

    def add_posts_to_db(self, posts):
        self.database.add_pastas(posts)

    def add_post_to_db(self, post):
        self.database.add_pasta(post)

    def update_scraped_posts_to_db(self, posts):
        self.database.update_pastas(posts)

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
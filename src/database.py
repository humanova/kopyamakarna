from peewee import *
import time
import math
from logger import logging



db = SqliteDatabase("posts/posts.db")


class BaseModel(Model):
    class Meta:
        database = db


class Pasta(BaseModel):
    id = CharField(unique=True)
    title = CharField()
    url = CharField()
    upvote = IntegerField()
    text = CharField()
    timestamp = DateTimeField()
    index_score = FloatField()


class FrontpagePasta(Pasta):
    pass

class DB:

    def __init__(self):
        self.connected = False
        self.create_tables()

    def create_tables(self):
        try:
            db.create_tables([Pasta, FrontpagePasta])
        except Exception as e:
            logging.exception(f"[DB] Couldn't create tables, it may already exist in db : {e})")

    def connect(self):
        try:
            db.connect()
            self.connected = True
        except Exception as e:
            logging.exception(f"[DB] Couldn't connect to db : {e}")

    def update_tables(self):
        logging.info(f'[DB] Updating index scores')
        self.update_pasta_indexes()
        logging.info(f'[DB] Updating frontpage')
        self.update_frontpage()

    def add_pastas(self, post_list):
        try:
            for p in post_list:
                self.add_pasta(p)
            logging.info(f'[DB] {len(post_list)} new pasta(s) has been added to Pasta table')
        except Exception as e:
            logging.exception(f'[DB] Error while adding pasta_list : {e}')

    def add_pasta(self, post):
        try:
            with db.atomic():
                pasta = Pasta.create(
                    id= post['id'],
                    title= post['title'],
                    url= post['url'],
                    upvote= post['upvote_count'],
                    text= post['text'],
                    timestamp= post['timestamp'],
                    index_score= 0
                )
                #logging.info(f"new pasta -> : {post['id']}")
                return pasta
        except Exception as e:
            logging.exception(f'[DB] Error while adding pasta : {e}')

    def add_frontpage_pasta(self, pasta):
        try:
            with db.atomic():
                fp_pasta = FrontpagePasta.create(
                    id= pasta.id,
                    title= pasta.title,
                    url= pasta.url,
                    upvote= pasta.upvote,
                    text= pasta.text,
                    timestamp= pasta.timestamp,
                    index_score= pasta.index_score
                )
                return fp_pasta
        except Exception as e:
            logging.exception(f'[DB] Error while adding frontpage_pasta : {e}')

    def search_pasta_by_text(self, text):
        pasta_list = list()
        pasta_list.append(Pasta.select().where(Pasta.title.contains(text)))
        for p in Pasta.select().where(Pasta.text.contains(text)):
            if p not in pasta_list:
                pasta_list.append(p)
        pasta_list.remove(pasta_list[0])
        return pasta_list

    def get_pasta_by_id(self, pasta_id):
        try:
            pasta = Pasta.select().where(Pasta.id == pasta_id).get()
            return pasta
        except:
            return None

    def get_all_pasta_id(self):
        ids = [pasta.id for pasta in Pasta.select()]
        return ids

    def get_all_pasta(self):
        return [pasta for pasta in Pasta.select()]

    def get_all_frontpage_pasta(self):
        return [fp_pasta for fp_pasta in FrontpagePasta.select()]

    def update_pasta_indexes(self):
        pastas = self.get_all_pasta()
        for pasta in pastas:
            seconds = pasta.timestamp - 1540771200
            order = math.log(pasta.upvote, 10)
            pasta.index_score = round(order + seconds / 45000, 7)

            pasta.save(only=[Pasta.index_score])

    # call update_pasta_indexes first
    def update_frontpage(self):
        FrontpagePasta.delete().execute()
        # sort Pasta table and update FrontpagePasta
        for pasta in Pasta.select().order_by(Pasta.index_score.desc())[:30]:
            self.add_frontpage_pasta(pasta)


from peewee import *

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


class DB:

    def __init__(self):
        self.connected = False
        self.create_tables()

    def create_tables(self):
        try:
            db.create_tables([Pasta])
        except Exception as e:
            print("Couldn't create tables, it may already exist in db...")
            print(e)

    def connect(self):
        try:
            db.connect()
            self.connected = True
        except Exception as e:
            print(f"Couldn't connect to db")
            print(e)

    def add_pasta(self, post):
        try:
            with db.atomic():
                word = Pasta.create(
                    id= post['id'],
                    title= post['title'],
                    url= post['url'],
                    upvote= post['upvote_count'],
                    text= post['text']
                )
                print(f"[DB] new pasta -> : {post['id']}")
                return word
        except Exception as e:
            print(f'Error while adding pasta : {e}')

    def search_pasta_by_text(self, text):
        pasta_list = []
        pasta_list.append(Pasta.select().where(Pasta.title.contains(text)))
        for p in Pasta.select().where(Pasta.text.contains(text)):
            if p not in pasta_list:
                pasta_list.append(p)
        pasta_list.remove(pasta_list[0])
        return pasta_list

    def get_pasta_by_id(self, id):
        try:
            pasta = Pasta.select().where(Pasta.id == id).get()
            return pasta
        except:
            return None

    def get_all_pasta_id(self):
        ids = [pasta.id for pasta in Pasta.select()]
        return ids

    def get_all_pasta(self):
        return [pasta for pasta in Pasta.select()]
from flask import Flask, url_for, render_template
import database
import random

db = database.DB()
app = Flask("kopyamakarna", template_folder="src/templates")


@app.route('/')
def index():
    #ids = db.get_ids()
    pastas = db.get_all_pasta()
    return render_template('index.html', pastas=pastas)


@app.route('/pasta/<pasta_id>')
def pasta(pasta_id):
    try:
        pasta = db.get_pasta_by_id(pasta_id)
        pasta.text = pasta.text.replace("\n", "<br>")
        random_pastas = get_random_pasta(limit=10)
        return render_template('pasta.html', pasta=pasta, random_pastas=random_pastas)
    except Exception as e:
        return render_template('404.html')

def get_random_pasta(limit=10):
    return random.sample(db.get_all_pasta(), limit)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

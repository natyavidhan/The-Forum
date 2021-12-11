from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from authlib.integrations.flask_client import OAuth
import config
from loginpass import create_flask_blueprint, GitHub
import databases

app = Flask(__name__)
app.config.from_pyfile(filename='config.py')

oauth = OAuth(app)
database = databases.Database()
backends = [GitHub]

@app.route('/')
def home():
    if 'user' in session:
        session['user'] = database.getUserWithId(session['user']['_id'])
        questions = database.getMostUpvotedQuestions()
        for question in questions:
            question['user'] = database.getUserWithId(question['user'])
        return render_template('home.html', user=session['user'], questions=questions)
    return render_template('index.html')

@app.route('/changeName', methods=['POST'])
def changeName():
    if 'user' not in session:
        return abort(404)
    name = request.form.get('name')
    if name == '':
        return 'please enter a valid username'
    elif len(name) > 20:
        return 'username too long'
    user = session['user']
    user['username'] = name
    session['user'] = user
    database.updateName(user['email'], name)
    return "Updated!"

@app.route('/new', methods=['GET', 'POST'])
def new():
    if 'user' in session:
        if request.method == 'GET':
            return render_template('new.html')
        else:
            question = request.form.get('question')
            explaination = request.form.get('explaination')
            tags = request.form.get('tags').split(',')
            database.postQuestion(session['user']['email'], question, explaination, tags)
        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/question/<id>', methods=['GET'])
def question(id):
    if 'user' in session:
        question = database.getQuestion(id)
        if question is None:
            return abort(404)
        question['user'] = database.getUserWithId(question['user'])
        return render_template('question.html', user=session['user'], question=question)
    return redirect(url_for('home'))

@app.route('/upvote/<id>', methods=['POST'])
def upvote(id):
    if 'user' in session:
        result = database.upvoteQuestion(id, session['user']['_id'])
        if not result:
            database.removeUpvote(id, user=session['user']['_id'])
        return "ok"
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('home'))

def handle_authorize(remote, token, user_info):
    if not database.userExists(user_info['email']):
        database.addUser(user_info['email'])
    session['user'] = database.getUser(user_info['email'])
    return redirect(url_for('home'))

bp = create_flask_blueprint(backends, oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)


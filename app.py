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
        return render_template('home.html', user= session['user'])
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
    
def handle_authorize(remote, token, user_info):
    if not database.userExists(user_info['email']):
        database.addUser(user_info['email'])
    session['user'] = database.getUser(user_info['email'])
    return redirect(url_for('home'))

bp = create_flask_blueprint(backends, oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)


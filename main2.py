# main2.py

from flask import Blueprint, render_template, redirect, url_for, session

app2 = Blueprint('app2', __name__)

@app2.route('/elements')
def elements():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('elements.html')

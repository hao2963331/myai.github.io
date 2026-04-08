# Assuming the file is a Python Flask app

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        command = request.form['command']
        # Process the command here
        return render_template('index.html', name=name, command=command, hide_name=True)
    return render_template('index.html', hide_name=False)

if __name__ == '__main__':
    app.run(debug=True)
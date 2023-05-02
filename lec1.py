from flask import Flask , render_template

app = Flask(__name__)

@app.route("/")
def main_page():
    return render_template('index.html')


@app.route("/about")
def suraj():
    myname = "suraj" 
    return render_template('about.html', name = myname)

app.run(debug = True)
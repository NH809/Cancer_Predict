from flask import Flask, render_template, request, redirect, session
import os

# ==============================
# APP SETUP
# ==============================

app = Flask(__name__)
app.secret_key = "secret123"

# ==============================
# CONFIGURATION
# ==============================

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ==============================
# ROUTES
# ==============================

# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simple demo login
        if username == "admin" and password == "admin123":
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid Credentials"

    return render_template('login.html')


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# 🏠 HOME
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')


# 🧠 PREDICT (DEMO MODE)
@app.route('/predict', methods=['POST'])
def predict():

    if 'user' not in session:
        return redirect('/login')

    if 'file' not in request.files:
        return redirect('/')

    file = request.files['file']

    if file.filename == '':
        return redirect('/')

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # 🔁 DEMO RESULT (since no TensorFlow on Render)
    result = "Cancer Detected"
    confidence = 95

    return render_template(
        'index.html',
        prediction=result,
        confidence=confidence,
        image=file.filename
    )


# 📁 HISTORY (DEMO DATA)
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/login')

    data = [
        (1, "image1.jpg", "Cancer Detected", "2026-04-20"),
        (2, "image2.jpg", "No Cancer", "2026-04-20")
    ]

    return render_template('history.html', data=data)


# 📊 STATS (DEMO DATA)
@app.route('/stats')
def stats():
    if 'user' not in session:
        return redirect('/login')

    labels = ["Cancer", "No Cancer"]
    values = [5, 3]

    return render_template('stats.html', labels=labels, values=values)


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
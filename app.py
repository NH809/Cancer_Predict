from flask import Flask, render_template, request, redirect, session
import os
from tensorflow.keras.models import load_model
from predict import predict_image
import mysql.connector

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

# Create folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load ML model
model = load_model('model.h5', compile=False)

# ==============================
# DATABASE CONNECTION
# ==============================

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Nikita@2005",   # 🔁 change if needed
    database="cancer_db"
)

cursor = db.cursor()

# ==============================
# ROUTES
# ==============================

# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
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


# 🧠 PREDICT
@app.route('/predict', methods=['POST'])
def predict():

    if 'user' not in session:
        return redirect('/login')

    if 'file' not in request.files:
        return redirect('/')

    file = request.files['file']

    if file.filename == '':
        return redirect('/')

    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Prediction
    result, confidence = predict_image(filepath, model)

    # Save to DB
    cursor.execute(
        "INSERT INTO predictions (image_name, result) VALUES (%s, %s)",
        (file.filename, result)
    )
    db.commit()

    return render_template(
        'index.html',
        prediction=result,
        confidence=confidence,
        image=file.filename
    )


# 📁 HISTORY
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    data = cursor.fetchall()

    return render_template('history.html', data=data)


# 📊 STATS (CHART)
@app.route('/stats')
def stats():
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("SELECT result, COUNT(*) FROM predictions GROUP BY result")
    data = cursor.fetchall()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template('stats.html', labels=labels, values=values)


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
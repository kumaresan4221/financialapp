from flask import Flask, render_template, request, redirect, session, url_for
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = 'ec0922348a2ac922064cd70829fbb07c'  # You can regenerate this if needed

# 🔥 Firebase Admin Setup
cred = credentials.Certificate("firebase.json")  # Make sure this file exists
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://finance-c2952-default-rtdb.firebaseio.com/'
})

# 📍 Home redirect to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# 🧾 Dashboard - Show customer list
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    uid = session['user']
    ref = db.reference(f'users/{uid}/customers')
    customers = ref.get() or {}
    return render_template('dashboard.html', customers=customers)

# ➕ Add Customer (POST only)
@app.route('/add', methods=['POST'])
def add_customer():
    if 'user' not in session:
        return redirect(url_for('login'))

    uid = session['user']
    reg_no = request.form.get('reg_no')
    name = request.form.get('name')
    amount = request.form.get('amount')

    # ✅ Check all fields
    if not reg_no or not name or not amount:
        return "Missing data. Please fill all fields.", 400

    try:
        amount_float = float(amount)
    except ValueError:
        return "Amount must be a number", 400

    try:
        ref = db.reference(f'users/{uid}/customers')
        ref.child(reg_no).set({
            'reg_no': reg_no,
            'name': name,
            'amount': amount_float
        })
        return redirect('/dashboard')
    except Exception as e:
        return f"Error saving data: {str(e)}", 500

# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return "Email required", 400

        session['user'] = email.replace('.', '_')  # Firebase-safe key
        return redirect('/dashboard')

    return render_template('login.html')

# 🔓 Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ✅ Run app
if __name__ == '__main__':
    app.run(debug=True)

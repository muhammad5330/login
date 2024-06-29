from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import plotly.graph_objs as go
import plotly.offline as pyo
from datetime import datetime
from biology import get_random_questions_bio
from chemistry import get_random_questions_chem
from physics import get_random_questions_phy
from logical import get_random_questions_logical
from english import get_random_questions_eng

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to the CSV files
CSV_FILE_PATH_bio = 'biology.csv'
CSV_FILE_PATH_chem = 'chemistry.csv'
CSV_FILE_PATH_eng = 'english.csv'
CSV_FILE_PATH_logical = 'logical.csv'
CSV_FILE_PATH_phy = 'physics.csv'

# Database connection
db = mysql.connector.connect(
    host="us-cluster-east-01.k8s.cleardb.net",
    # port=3306,
    user="b8cd5c22abd5cb",
    password="c9646ecf",
    database="heroku_06bc75ebcf9d933"
)
cursor = db.cursor(dictionary=True)

#*********************************LOGIN/SIGNUP*********************************************************
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['user_id'] = user['ID']  # Assuming 'ID' is the column name for the user ID
            return redirect(url_for('home'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        try:
            cursor.execute("INSERT INTO user (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            db.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Error: {err}"
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

#*********************************BIOLOGY**************************************************************
@app.route('/BiologyQuiz')
def BIO():
    return render_template('BiologyQuiz.html')

@app.route('/BIO_questions', methods=['GET'])
def BIO_get_questions():
    random_questions = get_random_questions_bio(CSV_FILE_PATH_bio, 20)
    return jsonify(random_questions)

@app.route('/BIO_submit', methods=['POST'])
def BIO_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']

    questions = get_random_questions_bio(CSV_FILE_PATH_bio, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    response = {"correct": is_correct}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

@app.route('/save_score', methods=['POST'])
def bio_save_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        score = data.get('score')

        try:
            cursor.execute("SELECT * FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                cursor.execute("UPDATE SubjScore SET Biology=%s WHERE ID=%s", (score, user_id))
            else:
                cursor.execute("INSERT INTO SubjScore (ID, Biology) VALUES (%s, %s)", (user_id, score))

            cursor.execute("UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s", (user_id,))
            db.commit()
            return jsonify({"message": "Score saved successfully"})
        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 500
    return jsonify({"error": "User not logged in"}), 401

#*********************************CHEMISTRY************************************************************
@app.route('/ChemistryQuiz')
def CHEM():
    return render_template('ChemistryQuiz.html')

@app.route('/CHEM_questions', methods=['GET'])
def CHEM_get_questions():
    random_questions = get_random_questions_chem(CSV_FILE_PATH_chem, 20)
    return jsonify(random_questions)

@app.route('/CHEM_submit', methods=['POST'])
def CHEM_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']
    
    questions = get_random_questions_chem(CSV_FILE_PATH_chem, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    response = {"correct": is_correct}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

@app.route('/save_chemistry_score', methods=['POST'])
def chemistry_save_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        score = data.get('score')

        try:
            cursor.execute("SELECT * FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                cursor.execute("UPDATE SubjScore SET Chemistry=%s WHERE ID=%s", (score, user_id))
            else:
                cursor.execute("INSERT INTO SubjScore (ID, Chemistry) VALUES (%s, %s)", (user_id, score))

            cursor.execute("UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s", (user_id,))
            db.commit()
            return jsonify({"message": "Chemistry score saved successfully"})
        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 500
    return jsonify({"error": "User not logged in"}), 401

#*********************************PHYSICS**************************************************************
@app.route('/PhysicsQuiz')
def PHY():
    return render_template('PhysicsQuiz.html')

@app.route('/PHY_questions', methods=['GET'])
def PHY_get_questions():
    random_questions = get_random_questions_phy(CSV_FILE_PATH_phy, 20)
    return jsonify(random_questions)

@app.route('/PHY_submit', methods=['POST'])
def PHY_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']
    
    questions = get_random_questions_phy(CSV_FILE_PATH_phy, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    response = {"correct": is_correct}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

@app.route('/save_physics_score', methods=['POST'])
def save_physics_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        score = data.get('score')

        try:
            cursor.execute("SELECT * FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                cursor.execute("UPDATE SubjScore SET Physics=%s WHERE ID=%s", (score, user_id))
            else:
                cursor.execute("INSERT INTO SubjScore (ID, Physics) VALUES (%s, %s)", (user_id, score))

            cursor.execute("UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s", (user_id,))
            db.commit()
            return jsonify({"message": "Physics score saved successfully"})
        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 500
    return jsonify({"error": "User not logged in"}), 401

#*********************************LOGICAL**************************************************************
@app.route('/LogicalQuiz')
def LOGICAL():
    return render_template('LogicalQuiz.html')

# API endpoint to get a random set of questions
@app.route('/LOGICAL_questions', methods=['GET'])
def LOGICAL_get_questions():
    random_questions = get_random_questions_chem(CSV_FILE_PATH_logical, 20)
    return jsonify(random_questions)

# API endpoint to submit an answer and get the next question or score
@app.route('/submit', methods=['POST'])
def LOGICAL_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']
    
    questions = get_random_questions_chem(CSV_FILE_PATH_logical, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    if is_correct:
        response = {"correct": True}
    else:
        response = {"correct": False}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

#---------------
@app.route('/save_logical_score', methods=['POST'])
def save_logical_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        score = data.get('score')
        print(f"Saving logical score for user {user_id}: {score}")  # Debug print

        try:
            # Check if the user already has a record in SubjScore
            cursor.execute("SELECT * FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                # Update the existing Physics score
                cursor.execute(
                    "UPDATE SubjScore SET Logical=%s WHERE ID=%s",
                    (score, user_id)
                )
            else:
                # Insert a new record with the Physics score
                cursor.execute(
                    "INSERT INTO SubjScore (ID, Logical) VALUES (%s, %s)",
                    (user_id, score)
                )

            # Update the Total field to sum all subjects for the user
            cursor.execute(
                "UPDATE SubjScore SET Total =COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s",
                (user_id,)
            )

            db.commit()
            return jsonify({"message": "Physics score saved successfully"})
        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # Debug print
            return jsonify({"error": str(err)}), 500
    else:
        print("User not logged in")  # Debug print
        return jsonify({"error": "User not logged in"}), 401

#******************************************************************************************************
#*********************************ENGLISH**************************************************************
# Serve the HTML page
@app.route('/EnglishQuiz')
def ENG():
    return render_template('EnglishQuiz.html')

# API endpoint to get a random set of questions
@app.route('/ENG_questions', methods=['GET'])
def ENG_get_questions():
    random_questions = get_random_questions_chem(CSV_FILE_PATH_eng, 20)
    return jsonify(random_questions)

# API endpoint to submit an answer and get the next question or score
@app.route('/submit', methods=['POST'])
def ENG_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']
    
    questions = get_random_questions_chem(CSV_FILE_PATH_eng, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    if is_correct:
        response = {"correct": True}
    else:
        response = {"correct": False}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)
#-------------
@app.route('/save_english_score', methods=['POST'])
def save_english_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        score = data.get('score')
        print(f"Saving logical score for user {user_id}: {score}")  # Debug print

        try:
            # Check if the user already has a record in SubjScore
            cursor.execute("SELECT * FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                # Update the existing Physics score
                cursor.execute(
                    "UPDATE SubjScore SET English=%s WHERE ID=%s",
                    (score, user_id)
                )
            else:
                # Insert a new record with the Physics score
                cursor.execute(
                    "INSERT INTO SubjScore (ID, English) VALUES (%s, %s)",
                    (user_id, score)
                )

            # Update the Total field to sum all subjects for the user
            cursor.execute(
                "UPDATE SubjScore SET Total =COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s",
                (user_id,)
            )

            db.commit()
            return jsonify({"message": "Physics score saved successfully"})
        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # Debug print
            return jsonify({"error": str(err)}), 500
    else:
        print("User not logged in")  # Debug print
        return jsonify({"error": "User not logged in"}), 401

#*********************************MOCK EXAM************************************************************
# Function to insert quiz result into database
def insert_quiz_result(total_score):
    if 'user_id' not in session:
        return "User not logged in"
    
    user_id = session['user_id']
    current_datetime = datetime.now()
    query = 'INSERT INTO MockTests (ID, Marks, Timestamp) VALUES (%s, %s, %s)'
    
    try:
        cursor.execute(query, (user_id, total_score, current_datetime))
        db.commit()
    except mysql.connector.Error as err:
        return f"Error: {err}"

# Function to read MCQs from CSV file
def read_mcqs(filename, count):
    mcqs = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)[:count]  # Read exactly 'count' number of rows
        for row in rows:
            mcq = {
                'Question': row['Questions'],
                'Option A': row['A'],
                'Option B': row['B'],
                'Option C': row['C'],
                'Option D': row['D'],
                'Correct Answer': row['Correct Option'],
                'is_correct': None  # Initialize is_correct key
            }
            mcqs.append(mcq)
    return mcqs

# Read specified number of MCQs from each CSV file
biology_mcqs = read_mcqs('biology.csv', 68)
chemistry_mcqs = read_mcqs('chemistry.csv', 54)
physics_mcqs = read_mcqs('physics.csv', 54)
english_mcqs = read_mcqs('english.csv', 18)
logical_reasoning_mcqs = read_mcqs('logical.csv', 6)

# Combine all MCQs into a single list
all_mcqs = biology_mcqs + chemistry_mcqs + physics_mcqs + english_mcqs + logical_reasoning_mcqs

# Function to calculate results
def calculate_results(mcqs):
    total_mcqs = len(mcqs)
    total_correct = 0
    subject_wise_correct = {'Biology': 0, 'Chemistry': 0, 'Physics': 0, 'English': 0, 'Logical Reasoning': 0}
    
    for mcq in mcqs:
        if mcq['is_correct']:
            total_correct += 1
            if mcq in biology_mcqs:
                subject_wise_correct['Biology'] += 1
            elif mcq in chemistry_mcqs:
                subject_wise_correct['Chemistry'] += 1
            elif mcq in physics_mcqs:
                subject_wise_correct['Physics'] += 1
            elif mcq in english_mcqs:
                subject_wise_correct['English'] += 1
            elif mcq in logical_reasoning_mcqs:
                subject_wise_correct['Logical Reasoning'] += 1
    
    insert_quiz_result(total_correct)
    
    return total_mcqs, total_correct, subject_wise_correct

# Generate bar chart using Plotly
def generate_bar_chart(subject_wise_correct):
    subjects = list(subject_wise_correct.keys())
    correct_counts = list(subject_wise_correct.values())

    bar_data = [go.Bar(x=subjects, y=correct_counts, marker=dict(color=['blue', 'green', 'orange', 'red', 'purple']))]
    layout = go.Layout(title='Subject-wise Correct MCQs', xaxis=dict(title='Subjects'), yaxis=dict(title='Number of Correct MCQs'))
    fig = go.Figure(data=bar_data, layout=layout)
    bar_chart_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return bar_chart_div

# Generate pie chart using Plotly
def generate_pie_chart(total_mcqs, total_correct):
    incorrect_count = total_mcqs - total_correct
    labels = ['Correct MCQs', 'Incorrect MCQs']
    sizes = [total_correct, incorrect_count]
    colors = ['green', 'red']

    pie_data = [go.Pie(labels=labels, values=sizes, marker=dict(colors=colors))]
    layout = go.Layout(title='Correct vs Incorrect MCQs')
    fig = go.Figure(data=pie_data, layout=layout)
    pie_chart_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return pie_chart_div

# Generate pie chart for subject-wise distribution using Plotly
def generate_subject_pie_chart(subject_wise_correct):
    labels = list(subject_wise_correct.keys())
    values = list(subject_wise_correct.values())
    colors = ['blue', 'green', 'orange', 'red', 'purple']

    pie_data = [go.Pie(labels=labels, values=values, marker=dict(colors=colors))]
    layout = go.Layout(title='Subject-wise Correct MCQs Distribution')
    fig = go.Figure(data=pie_data, layout=layout)
    subject_pie_chart_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return subject_pie_chart_div

# Home route to display start page
@app.route('/MockExam')
def index():
    return render_template('MockExam.html')

# Quiz route to handle MCQs
@app.route('/quiz', methods=['POST', 'GET'])
def quiz():
    if request.method == 'POST':
        # Check answers
        for mcq in all_mcqs:
            user_answer = request.form.get(mcq['Question'])
            correct_answer = mcq['Correct Answer']
            
            if user_answer == correct_answer:
                mcq['is_correct'] = True
            else:
                mcq['is_correct'] = False
                mcq['user_answer'] = user_answer
        
        # Recalculate results after answering
        total_mcqs, total_correct, subject_wise_correct = calculate_results(all_mcqs)

        # Generate charts after answering
        bar_chart_div = generate_bar_chart(subject_wise_correct)
        pie_chart_div = generate_pie_chart(total_mcqs, total_correct)
        subject_pie_chart_div = generate_subject_pie_chart(subject_wise_correct)
        
        return render_template('result.html', all_mcqs=all_mcqs, total_correct=total_correct, 
                               subject_wise_correct=subject_wise_correct, bar_chart_div=bar_chart_div, 
                               pie_chart_div=pie_chart_div, subject_pie_chart_div=subject_pie_chart_div)

    # GET request: Display quiz form
    return render_template('quiz.html', all_mcqs=all_mcqs)

#*********************************SCOREBOARD***********************************************************
@app.route('/Scoreboard')
def scoreboard():
    if 'user_id' in session:
        user_id = session['user_id']
        try:
            cursor.execute("SELECT username, Biology, Chemistry, English, Logical, Physics, Total FROM SubjScore JOIN user ON SubjScore.ID = user.ID WHERE SubjScore.ID=%s", (user_id,))
            user_scores = cursor.fetchone()

            cursor.execute("SELECT username, Biology, Chemistry, English, Logical, Physics, Total FROM SubjScore JOIN user ON SubjScore.ID = user.ID ORDER BY Total DESC")
            all_scores = cursor.fetchall()

            return render_template('Scoreboard.html', user_scores=user_scores, all_scores=all_scores)
        except mysql.connector.Error as err:
            return f"Error: {err}"
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

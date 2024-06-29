 # questions.py
import csv
import random

def load_questions_from_csv(file_path):
    questions = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = {
                "question": row["Questions"],
                "answers": [
                    {"text": row["A"], "correct": row["Correct Option"] == "A"},
                    {"text": row["B"], "correct": row["Correct Option"] == "B"},
                    {"text": row["C"], "correct": row["Correct Option"] == "C"},
                    {"text": row["D"], "correct": row["Correct Option"] == "D"}
                ]
            }
            questions.append(question)
    return questions

def get_random_questions_eng(file_path, num_questions=20):
    all_questions = load_questions_from_csv(file_path)
    return random.sample(all_questions, num_questions)

# Example usage: get 20 random questions from the CSV
random_questions = get_random_questions_eng('english.csv', 10)

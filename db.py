from pymongo import MongoClient
from bson import ObjectId

# Connect to the MongoDB server (make sure MongoDB is running)
client = MongoClient('mongodb://localhost:27017')

# Select the database
exam_db = client.get_database('ExamApp')

# Define collections
topics_collection = exam_db.get_collection('topics')
student_answers_collection = exam_db.get_collection('student_answers')

# Function to retrieve a topic by its ID
def get_topic(topic_id):
    topic = topics_collection.find_one({'_id': ObjectId(topic_id)})
    return topic if topic else None

# Function to create a new topic
def create_topic(topic_data):
    topics_collection.insert_one({
        'subject': topic_data['subject'],
        'topic_class': topic_data['topic_class'],
        'topic_name': topic_data['topic_name'],
        'level': topic_data['level'],
        'no_of_questions': topic_data['no_of_questions'],
        'assigned_time': topic_data['assigned_time'],
        'instruction': topic_data['instruction'],
        'learning': topic_data['learning'],
        'eligibility': topic_data['eligibility'],
        'questions': []  # Initialize with an empty list of questions
    })

# Function to update a topic
def update_topic(topic_id, updated_data):
    topics_collection.update_one(
        {'_id': ObjectId(topic_id)},
        {'$set': updated_data}
    )

# Function to delete a topic by its ID
def delete_topic(topic_id):
    topics_collection.delete_one({'_id': ObjectId(topic_id)})

# Function to add questions to a topic with image support
def update_topic_questions(topic_id, questions):
    topics_collection.update_one(
        {'_id': ObjectId(topic_id)},
        {'$set': {'questions': questions}}
    )

# Function to calculate the student's score based on the answers
def calculate_score(topic, student_answers):
    questions = topic.get('questions', [])
    correct_answers = 0

    for question in questions:
        question_no = question.get('question_no')
        correct_answer = question.get('answer')
        student_answer = student_answers.get(str(question_no))

        if student_answer == correct_answer:
            correct_answers += 1

    # Calculate the score (you can define your own scoring mechanism)
    total_questions = len(questions)
    score = (correct_answers / total_questions) * 100

    return score
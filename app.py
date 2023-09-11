from bson import ObjectId
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os

from db import create_topic, delete_topic, get_topic, get_topics, update_topic, update_topic_questions

app = Flask(__name__)
app.secret_key = 'secertkey'

@app.route('/')
def home():
    return 'Home page!'

@app.route('/get_topic/<topic_id>')
def get_topic_function(topic_id):
    topic = get_topic(topic_id)
    if topic:
        topic['_id'] = str(topic['_id'])
        return jsonify(topic), 200
    else:
        return jsonify({'msg': 'Topic not found!!'}), 404
    
@app.route('/get_topics', methods=['GET'])
def get_topics_function():
    topics = get_topics()
    if topics:
        return jsonify(topics), 200
    else:
        return jsonify({'error': 'There are no topics!!'}), 404
    

@app.route('/create_topic', methods=['GET', 'POST'])
def create_topic_function():
    subject = request.json.get('subject', '')
    topic_class = request.json.get('topic_class', '')
    topic_name = request.json.get('topic_name', '')
    level = request.json.get('level', '')
    no_of_questions = int(request.json.get('no_of_questions', ''))
    assigned_time = int(request.json.get('assigned_time', ''))
    instruction = request.json.get('instruction', '')
    learning = request.json.get('learning', '')
    eligiblity = request.json.get('eligiblity', '')

    topic = {
        'subject': subject,
        'topic_class': topic_class,
        'topic_name': topic_name,
        'level': level,
        'no_of_questions': no_of_questions,
        'assigned_time': assigned_time,
        'instruction': instruction,
        'learning': learning,
        'eligiblity': eligiblity
    }

    create_topic(topic)
    
    return jsonify(topic), 201

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/create_questions/<topic_id>', methods=['GET', 'POST'])
def create_questions_function(topic_id):
    topic = get_topic(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found!!'}), 404
    
    type = ["mcq", "fill_up", 'true_or_false']
    fetched_questions = request.json.get('questions', [])

    no_of_questions = topic['no_of_questions']
    count_no_questions = 0
    questions = []
    for q in fetched_questions:
        if (count_no_questions >= no_of_questions):
            print("Questions count is not equal!!")
            break

        question_type = fetched_questions[q]['question_type']
        question_text = fetched_questions[q]['question_text']
        answer = fetched_questions[q]['answer']
        if question_type not in type:
            return jsonify({'error': 'Invalid question type!!'}), 400

        if question_type == 'true_or_false':
            if answer not in ['true', 'false']:
                return jsonify({'error': 'Invalid answer for true/false question!!'}), 400
        elif question_type == 'mcq':
            options = {}
            question_choices = fetched_questions[q]['question_choices']
            for choice in question_choices:
                option = {
                    choice: question_choices[choice]
                }
                options.update(option)

        questions.append({
            'questions_no': q,
            'question_type': question_type,
            'question_text': question_text,
            'options': options if question_type == 'mcq' else None,
            'answer': answer
        })

        count_no_questions += 1

    update_topic_questions(topic_id, questions)

    return jsonify(questions), 201

@app.route('/update_topic/<topic_id>', methods=['POST', 'PUT'])
def update_topic_function(topic_id):
    topic = get_topic(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found!!'}), 404

    subject = request.json.get('subject', topic.get('subject', ''))
    topic_class = request.json.get('topic_class', topic.get('topic_class', ''))
    topic_name = request.json.get('topic_name', topic.get('topic_name', ''))
    level = request.json.get('level', topic.get('level', ''))
    no_of_questions = int(request.json.get('no_of_questions', topic.get('no_of_questions', '')))
    assigned_time = int(request.json.get('assigned_time', topic.get('assigned_time', '')))
    instruction = request.json.get('instruction', topic.get('instruction', ''))
    learning = request.json.get('learning', topic.get('learning', ''))
    eligiblity = request.json.get('eligiblity', topic.get('eligiblity', ''))

    fetched_questions = request.json.get('questions', topic.get('questions', []))
    type = ["mcq", "fill_up", 'true_or_false']

    count_no_questions = 0
    questions = []
    for q in fetched_questions:
        if (count_no_questions >= no_of_questions):
            print("Questions count is not equal!!")
            break

        question_type = fetched_questions[q]['question_type']
        question_text = fetched_questions[q]['question_text']
        answer = fetched_questions[q]['answer']
        if question_type not in type:
            return jsonify({'error': 'Invalid question type!!'}), 400
        
        if question_type == 'true_or_false':
            if answer not in ['true', 'false']:
                return jsonify({'error': 'Invalid answer for true/false question!!'}), 400
        elif question_type == 'mcq':
            options = {}
            question_choices = fetched_questions[q]['question_choices']
            for choice in question_choices:
                option = {
                    choice: question_choices[choice]
                }
                options.update(option)

        questions.append({
            'questions_no': q,
            'question_type': question_type,
            'question_text': question_text,
            'options': options if question_type == 'mcq' else None,
            'answer': answer
        })
        count_no_questions += 1


    new_topic = {
        'subject': subject,
        'topic_class': topic_class,
        'topic_name': topic_name,
        'level': level,
        'no_of_questions': no_of_questions,
        'assigned_time': assigned_time,
        'instruction': instruction,
        'learning': learning,
        'eligiblity': eligiblity,
        'questions': questions
    }

    update_topic(topic_id, new_topic)

    return jsonify(new_topic)

@app.route('/delete_topic/<topic_id>', methods=['DELETE'])
def delete_topic_function(topic_id):
    topic = get_topic(topic_id)
    if topic:
        delete_topic(topic_id)
        return jsonify({'message': 'Topic deleted successfully'})
    else:
        return jsonify({'error': 'Topic not found!!'}), 404


if __name__ == '__main__':
    app.run(debug=True)
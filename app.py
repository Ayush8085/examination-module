from flask import Flask, jsonify, request,send_file
import os
from bson import Binary, ObjectId

from db import create_topic, get_topic, update_topic, update_topic_questions, delete_topic, calculate_score, student_answers_collection

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])



# Function to save an uploaded image and return its filename
def save_uploaded_image(file):
    if file.filename == '':
        return None

    filename = f"{ObjectId()}.{file.filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename


@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = save_uploaded_image(file)

    return jsonify({'message': 'Image uploaded successfully', 'filename': filename}), 200

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/')
def home():
    return 'Home page!'

@app.route('/get_topic/<topic_id>', methods=['GET'])
def get_topic_function(topic_id):
    topic = get_topic(topic_id)
    if topic:
        topic['_id'] = str(topic['_id'])
        return jsonify(topic)
    else:
        return jsonify({'error': 'Topic not found!!'}), 404

@app.route('/create_topic', methods=['POST'])
def create_topic_function():
    topic_data = request.json
    image_filename = save_uploaded_image(request.files.get('image'))

    # Convert image data to binary format
    image_data = store_image(image_filename)

    # Add the image data to the topic_data
    topic_data['question_image'] = image_data

    create_topic(topic_data)
    return jsonify(topic_data), 201


@app.route('/create_questions/<topic_id>', methods=['POST'])
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
        if count_no_questions >= no_of_questions:
            print("Questions count is not equal!!")
            break

        question_type = fetched_questions[q]['question_type']
        question_text = fetched_questions[q]['question_text']
        answer = fetched_questions[q]['answer']

        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            image_filename = save_uploaded_image(image)

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
            'question_image': image_filename,
            'options': options if question_type == 'mcq' else None,
            'answer': answer
        })

        count_no_questions += 1

    # Update the topic with the new questions
    update_topic_questions(topic_id, questions)

    return jsonify(questions), 201



# Function to store the uploaded image in the database
def store_image(image_filename):
    if image_filename:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], image_filename), 'rb') as image_file:
            image_data = Binary(image_file.read())
        return image_data
    return None


@app.route('/update_topic/<topic_id>', methods=['PUT'])
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
    eligibility = request.json.get('eligibility', topic.get('eligibility', ''))

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

    # Get and store the image data
    image_filename = save_uploaded_image(request.files.get('image'))
    image_data = store_image(image_filename)

    new_topic = {
        'subject': subject,
        'topic_class': topic_class,
        'topic_name': topic_name,
        'level': level,
        'no_of_questions': no_of_questions,
        'assigned_time': assigned_time,
        'instruction': instruction,
        'learning': learning,
        'eligibility': eligibility,
        'questions': questions,
        'question_image': image_data  # Store the image data
    }

    # Update the topic with the new data
    update_topic(topic_id, new_topic)

    return jsonify(new_topic)



@app.route('/read_topic/<topic_id>', methods=['GET'])
def read_topic_function(topic_id):
    topic = get_topic(topic_id)
    if topic:
        topic['_id'] = str(topic['_id'])
        return jsonify(topic)
    else:
        return jsonify({'error': 'Topic not found!!'}), 404

@app.route('/delete_topic/<topic_id>', methods=['DELETE'])
def delete_topic_function(topic_id):
    topic = get_topic(topic_id)
    if topic:
        delete_topic(topic_id)
        return jsonify({'message': 'Topic deleted successfully'})
    else:
        return jsonify({'error': 'Topic not found!!'}), 404
    

@app.route('/take_exam/<topic_id>', methods=['POST'])
def take_exam(topic_id):
    student_answers = request.json.get('answers', {})
    topic = get_topic(topic_id)
    
    if not topic:
        return jsonify({'error': 'Topic not found!!'}), 404

    questions = topic['questions']
    total_questions = len(questions)
    correct_answers = 0

    results = []

    for question in questions:
        question_type = question['question_type']
        question_no = question['question_no']
        correct_answer = question['answer']
        student_answer = student_answers.get(str(question_no), "").strip()

        if question_type == 'mcq':
            is_correct = student_answer == correct_answer
        elif question_type == 'fill_up':
            is_correct = student_answer.lower() == correct_answer.lower()
        elif question_type == 'true_or_false':
            is_correct = student_answer.lower() == correct_answer.lower()

        results.append({
            'question_no': question_no,
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'student_answer': student_answer
        })

        if is_correct:
            correct_answers += 1

    # Calculate student's score and percentage
    score = correct_answers
    percentage = (correct_answers / total_questions) * 100

    # Save student's answers and score to the "student_answers" collection
    student_answers_collection.insert_one({
        'topic_id': ObjectId(topic_id),
        'student_answers': student_answers,
        'score': score
    })

    return jsonify({
        'results': results,
        'score': score,
        'percentage': percentage
    })

@app.route('/submit_exam/<topic_id>', methods=['POST'])
def submit_exam(topic_id):
    student_answers = request.json.get('answers', {})
    student_id = request.json.get('student_id', '')

    # Find the topic based on the provided topic_id
    topic = get_topic(topic_id)

    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    # Calculate the student's score
    score = calculate_score(topic, student_answers)

    # Save student's answers and score to the "student_answers" collection
    student_answers_collection.insert_one({
        'topic_id': ObjectId(topic_id),
        'student_id': student_id,
        'answers': student_answers,
        'score': score
    })

    return jsonify({'message': 'Exam submitted successfully', 'score': score})


if __name__ == '__main__':
    app.run(debug=True)
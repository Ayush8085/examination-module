from bson import ObjectId
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
exam_db = client.get_database('ExamApp')

topics_collection = exam_db.get_collection('topics')
questions_collection = exam_db.get_collection('questions')

def get_topics():
    topics = list(topics_collection.find({}))
    for topic in topics:
        topic['_id'] = str(topic['_id'])
    return topics if topics else None

def get_topic(topic_id):
    topic = topics_collection.find_one({'_id': ObjectId(topic_id)})
    return topic if topic else None

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
        'eligiblity': topic_data['eligiblity']
    })

def update_topic(topic_id, topic):
    topics_collection.update_one(
        {'_id': ObjectId(topic_id)},
        {'$set': {
            'subject': topic['subject'],
            'topic_class': topic['topic_class'],
            'topic_name': topic['topic_name'],
            'level': topic['level'],
            'no_of_questions': topic['no_of_questions'],
            'assigned_time': topic['assigned_time'],
            'instruction': topic['instruction'],
            'learning': topic['learning'],
            'eligiblity': topic['eligiblity'],
            'questions': topic['questions']
        }}
    )

def delete_topic(topic_id):
    topics_collection.delete_one({'_id': ObjectId(topic_id)})

def update_topic_questions(topic_id, questions):
    topics_collection.update_one(
        {'_id': ObjectId(topic_id)},
        {'$set': {
            'questions': questions
        }}
    )


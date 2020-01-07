import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_password = "admin"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', self.database_password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Which hockey team did Wayne Gretzky play for in the 80s?',
            'answer': 'Edmonton Oilers',
            'difficulty': 2,
            'category': 6 
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    def test_get_all_questions_paginated(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['current_category']))
        self.assertTrue(len(data['categories']))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000', json={'category': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        question = Question.query.filter_by(id=2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['all_questions']))
        self.assertEqual(question, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/question/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['all_questions']))

    def test_422_if_question_creation_fails(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)        
        pass

    def test_search_questions(self):
        res = self.client().post('/questions', json={
            'searchTerm': 'title'
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_422_if_question_search_fails(self):
        res = self.client().post('/questions', json={
            'searchTerm': 'title'
        })
        data = json.loads(res.data)        
        pass

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['current_category']))
    
    def test_404_get_questions_by_category_fails(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)        
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_422_get_questions_by_category_fails(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)        
        pass

    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': 1,
                'type': 'Science'
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_play_quiz_fails(self):
        res = self.client().post('/quizzed', json={
            'quiz_category': {
                'id': 1000,
            }
        })
        data = json.loads(res.data)        
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_422_play_quiz_fails(self):
        res = self.client().post('/quizzed', json={
            'quiz_category': {
                'id': 1,
            }
        })
        data = json.loads(res.data)        
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
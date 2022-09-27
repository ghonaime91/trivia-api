
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flaskr import create_app, paginate_questions
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.db_user = 'postgres'
        self.db_pwd = 'postgres'
        self.db_host = 'localhost:5432'
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.db_user,
            self.db_pwd,
            self.db_host,
            self.database_name
            )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # """
    # Write at least one test for each test for successful operation and for expected errors.
    # """

    def test_get_all_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['categories']),0)

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_404_sent_requesting_non_existing_category(self):
        res = self.client().get('/api/categories/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_get_paginated_questions(self):
        res = self.client().get('/api/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_404_sent_requesting_questions_beyond_valid_page(self):
        res = self.client().get('/api/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")

    #-----------------------------------------------------------
    #-----------------------------------------------------------
    
    def test_delete_question(self):
        # adding a new question to database
        new_question = Question(
            question='new Question',
            answer='new Answer',
            category=1,
            difficulty=1
            )
        new_question.insert()
        question_id = new_question.id
        # test the deletion
        res = self.client().delete(f'/api/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data['deleted'], question_id)

    #-----------------------------------------------------------
    #-----------------------------------------------------------
    
    def test_422_sent_deleting_non_existing_question(self):
        res = self.client().delete("/api/questions/50000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],'unprocessable')

    #-----------------------------------------------------------
    #-----------------------------------------------------------
    
    def test_post_new_question(self):
        new_question={
            "question":"another new question?",
            "answer" : "another new answer",
            "difficulty":1,
            "category":1
        }
        total_questions_before_add = len(
            Question.query.all()
        )
        res = self.client().post('/api/questions', json=new_question)
        data = json.loads(res.data)

        total_questions_after = len(
            Question.query.all()
        )

        self.assertEqual(res.status_code,200)
        self.assertGreater(
            total_questions_after ,
            total_questions_before_add
            )
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

    #-----------------------------------------------------------
    #-----------------------------------------------------------
    
    def test_422_post_new_question(self):
        new_question={
            "question":"another new question?",
            "difficulty":1,
            "category":1
        }
        res = self.client().post('/api/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "unprocessable")

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_search_questions(self):
        new_search = {'searchTerm': 'a'}
        res = self.client().post('/api/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_404_search_question(self):
        new_search = {
            'searchTerm': '',
        }
        res = self.client().post('/api/questions/search', json=new_search)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_get_questions_per_category(self):
        res = self.client().get('/api/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_404_get_questions_per_category(self):
        res = self.client().get('/api/categories/a/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_play_quiz(self):
        new_quiz_round = {
            'previous_questions': [],
            'quiz_category': {'type': 'Entertainment', 'id': 5}
            }
        res = self.client().post('/api/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    #-----------------------------------------------------------
    #-----------------------------------------------------------

    def test_404_play_quiz(self):
        new_quiz_round = {'previous_questions': []}
        res = self.client().post('/api/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")







# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
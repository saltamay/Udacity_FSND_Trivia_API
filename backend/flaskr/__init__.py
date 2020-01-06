import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins. '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''Set Access-Control-Allow'''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''Handle GET requests for all available categories.'''
  @app.route('/categories', methods=['GET'])
  def get_all_categories():
    categories = Category.query.all()
    categories = [category.format() for category in categories]
    
    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'all_categories': categories,
      'total_categories': len(categories)
    })

  ''' 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  BOOKS_PER_PAGE = 10

  def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_PAGE
    end = start + BOOKS_PER_PAGE

    questions = [question.format() for question in questions]
    current_questions = questions[start:end]

    return current_questions


  @app.route('/questions', methods=['GET'])
  def get_all_questions():
    categories = Category.query.all()
    categories = [category.format() for category in categories]

    current_category = request.args.get('category', 0, type=int)

    if current_category != 0:
      questions = Question.query.filter_by(category=current_category).all()
      current_category = Category.query.get(current_category)
      current_category = [{
        'id': current_category.id,
        'type': current_category.type
      }]
    else:
      questions = Question.query.all()
      current_category = categories
    
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'all_questions': current_questions,
      'total_questions': len(current_questions),
      'current_category': current_category,
      'all_categories': categories
    })

  '''
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter_by(id=question_id).one_or_none()
    
      if question is None:
        abort(404)

      question.delete()

      questions = Question.query.all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
      'success': True,
      'deleted': question_id,
      'all_questions': current_questions,
      'total_questions': len(current_questions)
      })

    except:
      abort(422) 

  def create_question():
    
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)

    if 'category' in body:
      new_category = int(body.get('category'))
    else:
      new_category = None
    
    if 'difficulty' in body:
      new_difficulty = int(body.get('difficulty'))
    else:
      new_difficulty = None

    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      print(question)

      question.insert()

      questions = Question.query.all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'created': question.id,
        'all_questions': current_questions,
        'total_questions': len(current_questions)
      })
    
    except:
      abort(422)
  
  def search_questions():
    search_term = request.args.get('search', None, type=str)
    
    if search_term is None:
      abort(400)

    try:
      results = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
      results = [result.format() for result in results]

      return jsonify({
        'success': True,
        'total_results': len(results),
        'all_results': results
      })
    
    except:
      abort(422)
  
  @app.route('/questions', methods=['POST'])
  def handle_post():
    '''
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    if 'search' in request.args:
      return search_questions()
    else:
      '''
      Create an endpoint to POST a new question, 
      which will require the question and answer text, 
      category, and difficulty score.

      TEST: When you submit a question on the "Add" tab, 
      the form will clear and the question will appear at the end of the last page
      of the questions list in the "List" tab.  
      '''
      return create_question()
  
  '''
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    
    try:
      
      questions = Question.query.filter_by(category=category_id).all()
      current_questions = paginate_questions(request, questions)
      
      current_category = Category.query.filter(Category.id == category_id).one_or_none()

      current_category = [{
        'id': current_category.id,
        'type': current_category.type
      }]

      if len(current_questions) == 0:
        abort(404)
      
      return jsonify({
        'success': True,
        'all_questions': current_questions,
        'total_questions': len(current_questions),
        'current_category': current_category
      })
    
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    
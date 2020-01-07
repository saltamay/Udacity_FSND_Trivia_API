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
      'categories': categories,
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
    '''Get and format all categories'''
    categories = Category.query.all()
    categories = [category.format() for category in categories]

    current_category = request.args.get('category', None)

    '''If category provided, get questions for that particular category'''
    if isinstance(current_category, int):
      questions = Question.query.filter_by(category=current_category).all()
      current_category = Category.query.get(current_category)
      current_category = [{
        'id': current_category.id,
        'type': current_category.type
      }]
    else:
      '''Get all questions and categories'''
      questions = Question.query.all()
      current_category = categories    
    
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'current_category': current_category,
      'categories': categories
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
      '''If question invalid, abort with 404'''
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

  def create_question(body):
    
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
  
  def search_questions(body):
    search_term = body.get('searchTerm', None)

    try:
      results = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
      results = [result.format() for result in results]

      return jsonify({
        'success': True,
        'total_questions': len(results),
        'questions': results
      })
    
    except:
      abort(422)
  
  @app.route('/questions', methods=['POST'])
  def handle_post():
    body = request.get_json()
    '''
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    if 'searchTerm' in body:
      return search_questions(body)
    else:
      '''
      Create an endpoint to POST a new question, 
      which will require the question and answer text, 
      category, and difficulty score.

      TEST: When you submit a question on the "Add" tab, 
      the form will clear and the question will appear at the end of the last page
      of the questions list in the "List" tab.  
      '''
      return create_question(body)
  
  '''
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    
    questions = Question.query.filter_by(category=category_id).all()
    
    '''Abort if category id does not exist'''
    if len(questions) == 0:
      abort(404)

    try:

      current_questions = paginate_questions(request, questions)
      
      current_category = Category.query.filter(Category.id == category_id).one_or_none()
      
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'current_category': current_category.format()
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
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():

    body = request.get_json()
    
    category = body.get('quiz_category', None)

    try:
      questions = Question.query.filter(Question.category == category['id']).all()
      
      if len(questions) == 0:
        abort(404)

      question_ids = []
      for question in questions:
        question_ids.append(question.id)
    
      '''Filter out all questions in that category that are already answered'''
      if 'previous_questions' in body:
        previous_questions = body.get('previous_questions', [])
        filtered_questions_list = [id for id in question_ids if id not in previous_questions]

        if filtered_questions_list:
          question = Question.query.get(filtered_questions_list[0]).format()
        else:
          question = None
      
      return jsonify({
        'success': True,
        'question': question
      })
    
    except:
      abort(422)

  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(500)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "internal server error"
      }), 500
  
  return app

    
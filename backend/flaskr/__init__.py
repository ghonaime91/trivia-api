
import sys, random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10



# function to paginate questions 
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions




def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  


  #Set up CORS. Allow '*' for origins.
  CORS(app, resources={r'/api/*':{'origins':'*'}})


  # Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
      response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization,true'
      )
      response.headers.add(
        'Access-Control-Allow-Methods',
        'GET,PUT,POST,DELETE,OPTIONS'
      )
      return response




  # Create an endpoint to handle GET requests 
  # for all available categories.
  @app.route('/api/categories')
  def all_categories():
    categories = Category.query.order_by(Category.type).all()

    if len(categories) == 0:
      abort(404)      

    return jsonify({
      'success': True,
      'categories':
      {category.id: category.type for category in categories }
    })



  # Create an endpoint to handle GET requests for questions, 
  # including pagination (every 10 questions). 
  # This endpoint should return a list of questions, 
  # number of total questions, current category, categories. 
  # TEST: At this point, when you start the application
  # you should see questions and categories generated,
  # ten questions per page and pagination at the bottom of the screen for three pages.
  # Clicking on the page numbers should update the questions. 

  @app.route('/api/questions')
  def all_questions():
    questions = Question.query.order_by(Question.id).all()
    currentQuestions = paginate_questions(request,questions)
    categories = Category.query.order_by(Category.type).all()

    if len(currentQuestions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions':currentQuestions,
      'total_questions':len(questions),
      'categories':{category.id:category.type for category in categories},
      'current_category':None
      })





  # Create an endpoint to DELETE question using a question ID. 
  # TEST: When you click the trash icon next to a question, the question will be removed.
  # This removal will persist in the database and when you refresh the page. 

  @app.route('/api/questions/<int:question_id>',
  methods=['DELETE'] )
  def delete_question(question_id):

    del_question = Question.query.filter(
      Question.id == question_id
      ).one_or_none()

    if del_question is None:
      abort(422)
    try:
      del_question.delete()
      return jsonify({
        'success':True,
        'deleted':question_id
        })
    except:
      print(sys.exc_info())
      db.session.rollback()
      abort(422)
    finally:
      db.session.close()




  # Create an endpoint to POST a new question, 
  # which will require the question and answer text, 
  # category, and difficulty score.
  # TEST: When you submit a question on the "Add" tab, 
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.  

  @app.route('/api/questions', methods=['POST'])
  def post_new_question():
    data = request.get_json()

    if not (
      'question' in data
       and 'answer' in data 
       and 'difficulty' in data
       and 'category' in data
        ) or not (
          data['question'] and 
          data['answer'] and
          data['difficulty'] and 
          data['category'] 
          ):
            abort(422)

    try:
      new_question = Question(
        question=data['question'],
        answer=data['answer'],
        difficulty=data['difficulty'],
        category=data['category']
        )
      new_question.insert()

      return jsonify({
        'success':True,
        'created': new_question.id,
        })
    except:
       print(sys.exc_info())
       db.session.rollback()
       abort(422)
    finally:
      db.session.close()



 
  # Create a POST endpoint to get questions based on a search term. 
  # It should return any questions for whom the search term 
  # is a substring of the question. 
  # TEST: Search by any phrase. The questions list will update to include 
  # only question that include that string within their question. 
  # Try using the word "title" to start. 

  @app.route('/api/questions/search', methods=['POST'])
  def search_question():
    search_term = request.get_json()['searchTerm']
    if search_term == '':
      abort(404)

    result = Question.query.filter(
      Question.question.ilike(f'%{search_term}%')
      ).all()
    questions_list = [question.format() for question in result ]
    return jsonify({
      "success":True,
      "questions":questions_list,
      "total_questions":len(result),
      "current_category":None
      })




  # Create a GET endpoint to get questions based on category. 
  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 

  @app.route('/api/categories/<int:category_id>/questions')
  def get_question_by_category(category_id):
    questions_by_category = Question.query.filter(
      Question.category == category_id
      ).all() 
    totalQuestions = len(questions_by_category)

    if totalQuestions == 0:
      abort(404)

    currentQuestions = paginate_questions(
      request,questions_by_category
      )
    categoryName = Category.query.get(category_id)
    currentCategory = categoryName.type

    return jsonify({
      "success":True,
      'questions':currentQuestions,
      'total_questions':totalQuestions,
      'current_category':currentCategory
    })




  # Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions. 
  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not. 

  @app.route('/api/quizzes', methods=['POST'])
  def quizzes():
    data = request.get_json()
    if not ('quiz_category' in data and 'previous_questions' in data):
      abort(422)
      
    previous_questions = data['previous_questions']
    category = data['quiz_category']

    if category['type'] == 'click':
        available_questions = Question.query.filter(
            Question.id.notin_((previous_questions))
            ).all()
    else:
        available_questions = Question.query.filter_by(
            category=category['id']).filter(
              Question.id.notin_((previous_questions))
              ).all()

    new_question = available_questions[random.randrange(
        0, len(available_questions)
        )].format()if len(available_questions) > 0 else None

    return jsonify({
        'success': True,
        'question': new_question
    })





  # Create error handlers for all expected errors 
  # including 404 and 422. 
  
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
  def server_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal Server Error"
      })


  return app

    
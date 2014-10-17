###########################################################################
#
#   File Name      Date          Owner            Description
#   ----------    -------      ----------       ----------------
#   views.py      7/8/2014   Archana Bahuguna  View fns for qzngn APIs
#
#  Handles HTTP requests/JSON for a qzengine restful API service using
#  Flask/SQLAlchemy. 
#  Flask session, basic authentication, role (admin/user permisions) are 
#  implemented , Flask bcrypt is used for password encryption.
#
###########################################################################

import os, logging
from flask import Flask, request, json, jsonify, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.bcrypt import Bcrypt
import models 
import utls 
import role
import basicauth 
import logs 

app = Flask(__name__)
bcrypt = Bcrypt(app)
api = Api(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

class InvalidUsageException(Exception):
    """ Handles exceptions not caught by framework and sends response
    """
    status_code = 404

    def __init__(self, message, status_code=None, payload=None):
        super(InvalidUsageException,self).__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsageException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logs.info_ (response)
    return response
    
class AdmnQuizzesAPI(Resource):
    """ Class that defines methods for processing get/post requests 
        for /api/quizzes endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, required=True, 
                                   help="No title given for quiz", 
                                   location='json')
        self.reqparse.add_argument("difficulty_level", type=str, required=True,
                                   help="No difficulty level given for quiz", 
                                   location='json')
        self.reqparse.add_argument("text", type=str, required=True,
                                   help="Quiz text not provided", 
                                   location='json')
        super(AdmnQuizzesAPI, self).__init__()


    # GET /admin/quizzes
    @basicauth.login_required
    @role.admin_required
    def get(self):
        """Get all quizzes"""
        logs.debug_ ("_______________________________________________")
        logs.debug_ ("QuizzesAPI get fn: %s" %(request))

        # Query quizzes for this admin from quiz table
        # Should that be the case or should admin be able to see
        # other quizzes as well
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Quiz.query.filter_by(userid=userid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                                ('Error: No quizzes found', status_code=404))
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                              ('Error: No active session for this user found',
                               status_code=404))
            return response

        # Return response
        resource_fields = {}
        resource_fields['qzid'] =fields.Integer 
        resource_fields['title']=fields.String 
        resource_fields['difficulty_level'] =fields.String 
        resource_fields['text'] =fields.String 
        resource_fields['no_ques']=fields.Integer 

        quizzes = marshal(query_obj, resource_fields)
        response = jsonify(quizzes=quizzes)
        response.status_code = 200
        logs.info_(response)
        utls.display_tables()
        return response

    # POST /admin/quizzes
    @basicauth.login_required
    @role.admin_required
    def post(self):
        """Add new quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuizzesAPI post fn: %s\nJson Request\n=============\n %s"
                     %(request, request.json))

        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                                ('Error: No active session for this user found', 
                                 status_code=404))
            
            return response

        # Get values from request
        args = self.reqparse.parse_args()
        for key, value in args.iteritems():
            if value is not None:
                if (key == 'title'):
                    title = request.json['title']
                if (key == 'difficulty_level'):
                    difficulty_level = request.json['difficulty_level']
                if (key == 'text'):
                    text = request.json['text']

        # Update tables
        quiz_obj = models.Quiz(title, difficulty_level, text, userid)
        models.db.session.add(quiz_obj)
        models.db.session.commit()
        
        # Return response
        location = "/quizzes/%s" % quiz_obj.qzid
        query_obj = models.Quiz.query.filter_by(qzid=quiz_obj.qzid).all()

        resource_fields =  {'qzid':fields.Integer, 
                           'title':fields.String,
                           'difficulty_level':fields.String,
                           'text':fields.String,
                           'no_ques':fields.Integer
                          }
                            
        quiz = marshal(query_obj, resource_fields)
        response = jsonify(quiz=quiz)
        response.status_code = 201
        response.location = location
        logs.info_(response)
        utls.display_tables()
        return response

class AdmnQuizAPI(Resource):
    """ Class that defines methods for processing get/patch/del requests 
        for /api/quizzes/<qzid> endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, 
                             help="No title given", location='json')
        self.reqparse.add_argument("difficulty_level", type=str,
                             help="No difficulty level set", location='json')
        self.reqparse.add_argument("text", type=str, 
                             help="text", location='json')
        super(AdmnQuizAPI, self).__init__()

    # GET  /admin/quizzes/{qzid}
    @basicauth.login_required
    @role.admin_required
    def get(self, qzid):
        """Get quiz details"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuizAPI get fn: %s" %(request))

        # Check if user is auth to get details of this quiz
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Quiz.query.filter_by(qzid=qzid).first()
        if (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                       ('Error: Unauthorized Username for this quiz', \
                        status_code=401))
            
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                         status_code=404))
            return response

        # Query from quiz table
        query_obj = models.Quiz.query.filter_by(qzid = qzid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                    ('Error: Quiz not found', status_code=404))
            return response

        # Return response
        resource_fields =  {'qzid':fields.Integer, 
                           'title':fields.String,
                           'difficulty_level':fields.String,
                           'text':fields.String,
                           'no_ques':fields.Integer
                          }
                            
        quiz = marshal(query_obj, resource_fields)
        response = jsonify(quiz=quiz)
        response.status_code = 200
        logs.info_(response)
        return response

    # PATCH /admin/quizzes/{qzid}
    @basicauth.login_required
    @role.admin_required
    def patch(self, qzid):
        """Edit quiz details"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuizAPI patch fn: %s \nJson Request\n=============\n %s" 
                 %(request, request.json)) 
        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                       ('Error: No active session for this user found', 
                        status_code=404))
            
            return response

        # Get values from req
        args = self.reqparse.parse_args()
        cols = {}
        no_data = True
        for key, value in args.iteritems():
            if value is not None:
                no_data = False
                cols[key] = request.json[key]

        # Check if user is auth to update this quiz
        query_obj = models.Quiz.query.filter_by(qzid=qzid).first()
        if  (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: Unauthorized Username for this quiz', \
                         status_code=401))
            
            return response

        # If no input in patch request, return 400
        if no_data:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No input data provided in Patch req', 
                         status_code=400))
            return response

        # Update tables
        models.Quiz.query.filter_by(qzid=qzid).update(cols)
        models.db.session.commit()

        # Return response
        query_obj = models.Quiz.query.filter_by(qzid=qzid).all()
        resource_fields =  {'qzid':fields.Integer, 
                           'title':fields.String,
                           'difficulty_level':fields.String,
                           'text':fields.String,
                           'no_ques':fields.Integer
                          }
                            
        quiz = marshal(query_obj, resource_fields)
        response = jsonify(quiz=quiz)
        response.status_code = 200
        logs.info_(response)
        utls.display_tables()
        return response

    # DELETE  /admin/quizzes/{qzid}
    @basicauth.login_required
    @role.admin_required
    def delete(self, qzid):
        """Delete quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuizAPI delete fn: %s" %(request))

        # Check if user is auth to delete this quiz
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Quiz.query.filter_by(qzid=qzid).first()
        if  (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                             ('Error: Unauthorized Username for this quiz', \
                              status_code=401
                              )
                             )
            
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                       ('Error: No active session for this user found', 
                        status_code=404))
            return response
     
        # Delete all questions table entries for the quiz
        models.Question.query.join(models.Quiz).filter(models.Question.qzid == qzid).\
                delete()
        
        # Delete all Ans choices table entries for quiz
        models.Anschoice.query.join(models.Quiz).filter(models.Anschoice.qzid == qzid).\
                delete()

        # Delete quiz
        models.Quiz.query.filter(models.Quiz.qzid == qzid).delete()
        models.db.session.commit()
        
        # Return response
        utls.display_tables()
        return 204

class AdmnQuestionsAPI(Resource):
    """ Class that defines methods for processing get/post requests 
        for /api/quizzes/<qzid>/questions endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("ques_text", type=str, required=True,
                             help="No ques text provided", location='json')
        self.reqparse.add_argument("ans_text", type=str, required=True,
                             help="No ans given", location='json')
        self.reqparse.add_argument("anschoices", type=list, required=True,
                             help="No choices given", location='json')
        super(AdmnQuestionsAPI, self).__init__()


    # GET /admin/questions/{qzid}/questions
    @basicauth.login_required
    @role.admin_required
    def get(self, qzid):
        """Get all questions for quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuestionisAPI get fn: %s" %(request))

        # Check if user is auth to get details of this ques
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Quiz.query.filter_by(qzid=qzid).first()
        if  (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                    ('Error: Unauthorized Username for this quiz', \
                     status_code=401))
            
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                       ('Error: No active session for this user found', 
                        status_code=404))
            return response

        # Query from questions table
        query_obj = models.Question.query.join(models.Quiz).join(models.Anschoice).\
                      filter(models.Quiz.qzid == qzid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No question for quiz found', 
                         status_code=404))
            
            return response

        # Return response
        ans_fields = {'ans_choice':fields.String,
                      'correct':fields.Boolean
                     }
        resource_fields =  {'qid':fields.Integer, 
                           'ques_text':fields.String,
                           'ans_text':fields.String,
                           'qzid':fields.Integer,
                           'anschoices':fields.Nested(ans_fields)
                          }
                            
        questions = marshal(query_obj, resource_fields)
        response = jsonify(questions=questions)
        response.status_code = 200
        utls.display_tables()
        logs.info_(response)
        return response

    # POST /admin/quizzes/{qzid}/questions
    @basicauth.login_required
    @role.admin_required
    def post(self, qzid):
        """Add question to quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuestionsAPI post fn: %s \nJson Request\n=============\n %s" 
                      %(request, request.json))

        # Get userid from hdr
        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                         status_code=404))
            return response

        # Get data from req
        args = self.reqparse.parse_args()
        for key, value in args.iteritems():
            if value is not None:
                if (key == 'ques_text'):
                    ques_text = request.json['ques_text']
                if (key == 'ans_text'):
                    ans_text = request.json['ans_text']
                if (key == 'anschoices'):
                    anschoices = request.json['anschoices']

        # Post new data to table
        qn_obj = models.Question(ques_text, ans_text, qzid, userid)
        models.db.session.add(qn_obj)

        # Update correspnoding relationship tables 
        #Quiz table
        L = models.Quiz.query.filter_by(qzid = qzid).first()
        models.Quiz.query.filter_by(qzid = qzid).update(dict(no_ques=
                                                      (L.no_ques+1)))

        # Ans choices table 
        ansidL = []
        for choice in range(len(anschoices)):
            ans_obj = models.Anschoice(qzid,
                                     qn_obj.qid,
                                     anschoices[choice]["answer"], 
                                     anschoices[choice]["correct"]
                                    )
            models.db.session.add(ans_obj)
        models.db.session.commit()

        # Return response
        location = "/quizzes/%s/questions/%s" % (qzid, qn_obj.qid)
        query_obj = models.Question.query.join(models.Anschoice).\
                         filter(models.Question.qid == qn_obj.qid).all()
        qid = qn_obj.qid
        ans_fields = {'ans_choice':fields.String,
                      'correct':fields.Boolean
                     }
        resource_fields =  {'ques_text':fields.String,
                           'ans_text':fields.String,
                           'qzid':fields.Integer,
                           'qid':fields.Integer,
                           'anschoices':fields.Nested(ans_fields)
                          }
                            
        question = marshal(query_obj, resource_fields)
        response = jsonify(question=question)
        response.location = location
        response.status_code = 201
        logs.info_(response)
        utls.display_tables()
        return response

class AdmnQuestionAPI(Resource):
    """ Class that defines methods for processing get/patch/del requests 
        for /api/quizzes/<qzid>/questions/<qid> endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('ques_text', type=str, required=True,
                             help='No title given', location='json')
        self.reqparse.add_argument('ans_text', type=str, default="",
                             help='No ans provided', location='json')
        self.reqparse.add_argument('anschoices', type=str, default="",
                             help='No anschoices provided', location='json')
        super(AdmnQuestionAPI, self).__init__()

    # GET  /admin/quizzes/{qzid}/questions/{qid}
    @basicauth.login_required
    @role.admin_required
    def get(self, qzid, qid):
        """Get question qid for quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuestionAPI get fn: %s" %(request))

        # Check if user is auth to get details of this ques
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Question.query.filter_by(qid=qid).first()
        if (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                         ('Error: Unauthorized Username for this quiz', \
                          status_code=401))
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                          ('Error: No active session for this user found', 
                            status_code=404))
            
            return response

        # Query Question table
        query_obj = models.Question.query.join(models.Anschoice).filter(
                     models.Question.qid == qid,models.Question.qzid == qzid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                       ('Error: Question not found', status_code=404))
            return response

        # Return response
        ans_fields = {'ans_choice':fields.String,
                      'correct':fields.Boolean
                     }
        resource_fields =  {'qid':fields.Integer,
                           'ques_text':fields.String,
                           'ans_text':fields.String,
                           'qzid':fields.Integer,
                           'anschoices':fields.Nested(ans_fields)
                          }
                            
        question = marshal(query_obj, resource_fields)
        response = jsonify(question=question)
        response.status_code = 200
        logs.info_(response)
        utls.display_tables()
        return response

    # PATCH /admin/quizzes/{qzid}/questions/{qid}
    @basicauth.login_required
    @role.admin_required
    def patch(self, qzid, qid):
        """Add question to quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuestionAPI patch fn: %s \nJson Request\n=============\n %s" 
                     %(request, request.json))

        # Check if user is auth to update this ques
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Question.query.filter_by(qid=qid).first()
        if  (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: Unauthorized Username for this ques', \
                         status_code=401))
            
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                         status_code=404))
            
            return response

        # Check if question qid exists for qzid, raise error
        query_obj = models.Question.query.filter(models.Question.qid == qid,models.Question.qzid == qzid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                           ('Error: Question to edit not found for ques', 
                            status_code=400))
            return response

        args = self.reqparse.parse_args()
        for key, value in args.iteritems():
            if value is not None:
                if (key == 'ques_text'):
                    ques_text = request.json['ques_text']
                if (key == 'ans_text'):
                    ans_text = request.json['ans_text']
                if (key == 'anschoices'):
                    anschoices = request.json['anschoices']


        # Update all table entries with input data
        models.Question.query.filter_by(qid = qid).\
                update(dict(ques_text=ques_text, ans_text=ans_text))

        # Updating correspnoding relationship tables
        # Ans choices table 
        query_obj = models.Anschoice.query.filter_by(qid = qid)
        index = 0
        for choice in query_obj:
            ansid = query_obj[index].ansid
            ans_choice = anschoices[index]["answer"]
            correct    = anschoices[index]["correct"]
            models.Anschoice.query.filter_by(ansid = ansid).\
                  update(dict(ans_choice = ans_choice, correct = correct))  
            index += 1
        models.db.session.commit()

        # Return response
        query_obj = models.Question.query.join(models.Anschoice).filter(
                                         models.Question.qid == qid).all()
        ans_fields = {'ans_choice':fields.String,
                      'correct':fields.Boolean
                     }
        resource_fields =  {'qid':fields.Integer,
                           'ques_text':fields.String,
                           'ans_text':fields.String,
                           'qzid':fields.Integer,
                           'anschoices':fields.Nested(ans_fields)
                          }
                            
        question = marshal(query_obj, resource_fields)
        response = jsonify(question=question)
        response.status_code = 200
        logs.info_(response)
        utls.display_tables()
        return response

    # DELETE  /admin/quizzes/{qzid}/questions/{qid}
    @basicauth.login_required
    @role.admin_required
    def delete(self, qzid, qid):
        """Delete question"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuestionAPI del fn: %s" %(request.url))

        # Check if user is auth to del this ques
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Question.query.filter_by(qid=qid).first()
        if  (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: Unauthorized Username for this ques', \
                         status_code=401))
            
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                        status_code=404))
            return response


        # Updating no_ques col in quiz table
        L = models.Quiz.query.filter_by(qzid = qzid).first()
        models.Quiz.query.filter_by(qzid = qzid).\
                         update(dict(no_ques= (L.no_ques-1)))

        # Deleting Ans choices table entries for qid
        models.Anschoice.query.filter(models.Anschoice.qid == qid).delete()

        # Finally deleting entries from Question table
        models.Question.query.filter_by(qid = qid).delete()
        models.db.session.commit()

        # Return response
        response = jsonify(qid=qid)
        response.status_code = 204
        logs.info_(response)
        utls.display_tables()
        return response


class UsersAPI(Resource):
    """ Class that defines methods for processing post requests 
        for /users endpoint. This endpoint can either be requested
        directly from the client side or can be a result of control 
        reaching here once the send_authenticate_req function is 
        processed.
        Flask session is created once the user is created(post) or 
        logs in(get).
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str, required=True,
                             help="No username provided", location='json')
        self.reqparse.add_argument("password", type=str, required=True,
                             help="No password given", location='json')
        self.reqparse.add_argument("role", type=str, required=True,
                             help="No role given", location='json')
        super(UsersAPI, self).__init__()

    # POST /users
    def post(self):
        """Login already existing user or add new user"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("UserAPI post fn: %s\nJson Request\n=============\n %s" %(request, request.json))

        # Get values from request
        args = self.reqparse.parse_args()
        for key, value in args.iteritems():
            if value is not None:
                if (key == 'username'):
                    username = request.json['username']
                if (key == 'password'):
                    password = request.json['password']
                if (key == 'role'):
                    role = request.json['role']

        if ((role != 'admin') and  (role != 'user')):
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: Role should be admin or user', \
                         status_code=400))
            return response

        # Check and Update tables
        # This is implemented as if we are processing get /users
        user_obj = models.User.query.filter_by(username=username).all()
        user_index = None
        for i in range(len(user_obj)):
            if username in user_obj[i].username:
                user_index = i
        if user_index is not None:
            #match encrypted password with one in table 
            if not bcrypt.check_password_hash(user_obj[user_index].password, 
                    password):
                response = handle_invalid_usage(InvalidUsageException
                           ('Error: Password for user does not match', 
                            status_code=401))
                return response

        else:
            # Add new user
            user_obj = models.User(username, 
                                 bcrypt.generate_password_hash(password), 
                                 role)
            models.db.session.add(user_obj)
            models.db.session.commit()

        # Create flask session here with secret key based on username
#        if 'username' not in session:
#            session['username'] = username

        # Return response
        location = "/users/%s" % user_obj.userid
        query_obj = models.User.query.filter_by(userid=user_obj.userid).all()
        resource_fields = {'userid':fields.Integer}
        user = marshal(query_obj, resource_fields)
        response = jsonify(user=user)
        response.status_code = 201
        response.location = location
        logs.info_(response)
        utls.display_tables()
        return response

class UsrQuizzesAPI(Resource):
    """ Class that defines methods for processing get/post requests 
        for /api/quizzes endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """
    # GET /user/quizzes
    @basicauth.login_required
    def get(self):
        """Get all quizzes"""
        logs.debug_ ("_______________________________________________")
        logs.debug_ ("QuizzesAPI get fn: %s" %(request))

        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                         status_code=404))
            
            return response

        # Query from quiz table
        query_obj = models.Quiz.query.order_by(models.Quiz.qzid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No quizzes found', status_code=404))
            return response

        # Return response
        resource_fields =  {'qzid':fields.Integer,
                            'title':fields.String
                            }
        user = marshal(query_obj, resource_fields)
        response = jsonify(user=user)
        response.status_code = 200
        logs.info_(response)
        utls.display_tables()
        return response

class UsrQuizAPI(Resource):
    """ Class that defines methods for processing get/patch/del requests 
        for /api/quizzes/<qzid> endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """

    # GET  /user/quizzes/{qzid}
    @basicauth.login_required
    def get(self, qzid):
        """Get quiz details"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuizAPI get fn: %s" %(request))

        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                         status_code=404))
            return response

        # Query from quiz table
        query_obj = models.Quiz.query.filter_by(qzid=qzid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                         ('Error: Quiz not found', status_code=404))
            return response

        # Return response
        resource_fields =  {'qzid':fields.Integer,
                            'title':fields.String,
                            'difficulty_level':fields.String,
                            'text':fields.String,
                            'no_ques':fields.Integer
                            }
        quiz = marshal(query_obj, resource_fields)
        response = jsonify(quiz=quiz)
        utls.display_tables()
        response.status_code = 200
        logs.info_(response)
        return response

class UsrQuizRtAPI(Resource):

    # GET /user/quizzes/{qzid}/result
    @basicauth.login_required
    def get(self, qzid):
        """Get result for taker of this  quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("UsrQuizRtAPI get fn: %s" %(request))

        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                         status_code=404))
            return response

        # Find quiz result for session
        query_obj = models.User.query.filter_by(userid=userid).first()
        result = query_obj.qzscore

        # Return response
        logs.debug_ ("Json response")
        logs.debug_ ("=============\n")
        logs.debug_ ("{\'result\':%s}\n" %(result))
        response = jsonify (result=result)
        response.status_code = 200
        utls.display_tables()
        logs.info_(response)
        return response

class UsrQuestionAPI(Resource):
    """ Class that defines methods for processing get/patch/del requests 
        for /api/quizzes/<qzid>/questions/<qid> endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('anschoices', type=str, required=True,
                             help='No ans choice provided', location='json')
        super(UsrQuestionAPI, self).__init__()

    # GET  /user/quizzes/{qzid}/questions/{qid}
    @basicauth.login_required
    def get(self, qzid, qid):
        """Get question qid for quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuestionAPI get fn: %s" %(request))

        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException(
                         'Error: No active session for this user found', 
                          status_code=404))
            return response

        # Query Question table
        query_obj = models.Question.query.join(models.Anschoice).filter\
                         (models.Question.qid == qid,models.Question.qzid == qzid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                         ('Error: Question not found', status_code=404))
            return response

        # Return response
        ans_fields = {'ans_choice':fields.String,
                      'correct':fields.Boolean
                     }
        resource_fields =  {'qid':fields.Integer,
                            'ques_text':fields.String,
                            'anschoices':fields.Nested(ans_fields)
                           }
        question = marshal(query_obj, resource_fields)
        response = jsonify(question=question)
        response.status_code = 200
        logs.info_(response)
        utls.display_tables()
        return response

    @basicauth.login_required
    # POST  /user/quizzes/{qzid}/questions
    def post(self, qzid, qid):
        """Answer question of quiz"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("QuestionAPI patch fn: %s \nJson Request\n=============\n %s" 
                    %(request, request.json))

        # Check if cookie user_session exists
        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException(
                            'Error: No active session found for this user', 
                             status_code=404))
            return response

        # Check if question qid exists for qzid, raise error
        query_obj = models.Question.query.filter(
                     models.Question.qid == qid,models.Question.qzid == qzid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                           ('Error: Question to edit not found for ques', 
                            status_code=400))
            return response

        args = self.reqparse.parse_args()
        for key, value in args.iteritems():
            if value is not None:
                if (key == 'anschoices'):
                    anschoices = request.json['anschoices']

        # Comparing quiz taker answers with actual ans choices in db
        correct = True
        query_obj = models.Anschoice.query.filter_by(qid=qid).all()

        index = 0
        for choice in query_obj:
            if (unicode(query_obj[index].correct) != 
                                  anschoices[index]["correct"]):
                correct = False
            index += 1
        if correct:
            #update the user table in the database
            query_obj = models.User.query.filter_by(userid=userid).all()
            cur_qzscore= query_obj[0].qzscore  #get current quiz score
            #increment quiz score
            models.User.query.filter_by(userid=userid).\
                                  update(dict(qzscore=cur_qzscore+1))

        query_obj = models.Question.query.join(models.Anschoice).filter\
                          (models.Question.qid == qid).all()
        location = "/quizzes/<int:qzid>/result %s" % qzid

        # Return response
        ans_fields = {'ans_choice':fields.String,
                      'correct':fields.Boolean
                     }
        resource_fields =  {'qid':fields.Integer,
                            'ques_text':fields.String,
                            'ans_text':fields.String,
                            'qzid':fields.Integer,
                            'anschoices':fields.Nested(ans_fields)
                           }
        question = marshal(query_obj, resource_fields)
        response = jsonify(question=question)
        response.status_code = 200
        response.location = location
        logs.info_(response)
        utls.display_tables()
        return response

class SessionAPI(Resource):
    """ Class that defines methods for processing del requests 
        for /session endpoint -mainly to delete sessions
    """

    # DELETE  /session (used to delete sessions)
    @basicauth.login_required
    def delete(self):
        """Delete session"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("SessionAPI del fn: %s" %(request.url))

        # Pop user from session
        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            logs.debug_("User already not in session")
        else:
            session.pop('username', None)

        # Return response
        utls.display_tables()
        return 204

api.add_resource(AdmnQuizzesAPI, '/admin/quizzes')
api.add_resource(AdmnQuizAPI, '/admin/quizzes/<int:qzid>')
api.add_resource(AdmnQuestionsAPI, '/admin/quizzes/<int:qzid>/questions')
api.add_resource(AdmnQuestionAPI, '/admin/quizzes/<int:qzid>/questions/<int:qid>')

api.add_resource(UsrQuizzesAPI, '/user/quizzes')
api.add_resource(UsrQuizAPI, '/user/quizzes/<int:qzid>')
api.add_resource(UsrQuizRtAPI, '/user/quizzes/<int:qzid>/result')
api.add_resource(UsrQuestionAPI, '/user/quizzes/<int:qzid>/questions/<int:qid>')

api.add_resource(UsersAPI, '/users')
api.add_resource(SessionAPI, '/session')

if __name__ == '__main__':

    #Initial config for db, this can be disabled
    models.db_init()

    utls.display_tables()
    app.debug = True

    app.run('192.168.33.10', 5001)


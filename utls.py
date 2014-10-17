###########################################################################
#
#   File Name      Date        Owner           Description
#   ---------    -------     ---------        ------------
#   utls.py     7/8/2014   Archana Bahuguna  Utility fuctions for 
#                                            qzengine restful APIs
#
###########################################################################

from collections import OrderedDict
from flask import request
import models
import logs

def get_user_from_hdr():
    auth = request.headers.get('Authorization')
    username = auth.split()[1].split(':')[0]
    user_obj = models.User.query.filter_by(username=username).first()
    userid = user_obj.userid
    return userid, username

def serialize_to_json(fields, query_result, a=0):
    """
    Serialize the query results into dict format so it can be
    converted to json format using jsonify fn
    """
    result = []
    for i in query_result:
        record = OrderedDict()
        for field in fields:
            if (field['relnshp']):
                x = getattr(i, field['name'])
                record[field['name']] = serialize_to_json(
                                              field['subfields'], 
                                              x)
            else:
                record[field['name']] = getattr(i, field['name'])
        result.append(record)

    return result

def display_tables():
    """ Displays db table entries after processing request """
    prompt = '__________________________________________\n'\
             'To view tables enter Yes/yes/y/No/no/n:'
    #i = raw_input(prompt)
    i = "yes"
    if i.lower() in ('yes','y'):
        import os
        os.system('clear')
        qry = models.User.query.all()
        logs.debug_ ('User Table\n=============:\nUserid  Username'\
                     '     Pwd     Role     QzScore\n')
        for i in qry:
            logs.debug_ (i)
        logs.debug_ ('\n------------------------------------------'\
                     '-----------------')

        qry = models.Quiz.query.all()
        logs.debug_ ('Quiz Table\n=============:\nQzid  Title     '\
                 '    Difficulty Level   Text                Userid  No Ques\n')
        for i in qry:
            logs.debug_ (i)
        logs.debug_ ('\n--------------------------------------------'
                '--------------')

        qry = models.Question.query.all()
        logs.debug_ ('Questions Table\n================:\nQid Qzid      QText'\
                      'Ans Text   Userid\n')
        for i in qry:
            logs.debug_ (i)
        logs.debug_ ('\n------------------------------------------------------')

        qry = models.Anschoice.query.all()
        logs.debug_ ('Ans Choices Table\n================:\nAnsid  Qzid'
                     '  Qid         Choices                          Correct\n')
        for i in qry:
            logs.debug_ (i)
        logs.debug_ ('\n------------------------------------------------------')
    else:
        pass
    return None


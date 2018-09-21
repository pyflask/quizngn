###########################################################################
#
#   File Name      Date          Owner              Description
#   ---------      ----          ----               -----------
#   client.py  7/8/2014   Archana Bahuguna    Simulates HTTP client requests
#                                             Used for testing qzengine
#
###########################################################################

import json
import requests
url = 'http://192.168.33.10:5001/users'
headers = {'Content-Type': 'application/json'} 

#url = 'http://192.168.33.10:5001/user/quizzes/1/result'

#url = 'http://192.168.33.10:5001/admin/quizzes'
#url = 'http://192.168.33.10:5001/session'
#headers = {'Content-Type': 'application/json', 'Authorization': 'Basic Archana:mypwd role:admin'} 
#headers = {'Content-Type': 'application/json', 'Authorization': 'Basic Archana:mypwd role:admin', 'Cookie': 'session=eyJ1c2VybmFtZSI6IkFyY2hhbmEifQ.Bp8e4A.l40yxekkA0RR_8Zyebq226FBrkM; HttpOnly; Path=/'}

# Make a POST request to create a user in the database.
#With Auth
data = dict(username = "Archana", password="mypwd", role="admin")
#data = dict(username = "Sridevi", password="herpwd", role="user")

# Make a POST request to create a quiz in the database.
#data = dict(title = "New quiz", difficulty_level="Difficult", text="Very good")
#response = requests.patch(url, data=json.dumps(data), headers=headers)
response = requests.post(url, data=json.dumps(data), headers=headers)

# Make a POST request to create a question in the database.
#data = dict(ques_text = "New question?", ans_text="New ANswer .", anschoices=[{"answer":"a. correct answer ", "correct":False}, {"answer":"b. Second answer ", "correct":False}, {"answer":"c. Third modified ", "correct":True}])                                
#response = requests.post(url, data=json.dumps(data), headers=headers)

# Make a POST request to answer questions as a quiz taker
#data = dict(anschoices=dict(ans_choice= '1. This is correct', correct='True'))

#url = 'http://192.168.33.10:5001/user/quizzes/1/questions/1'
#data = dict(anschoices=[dict(ans_choice= '1. This function does nothing', correct='True'), dict(ans_choice= '2. This function returns a fn pass', correct='False'), dict(ans_choice= '3. This function is not yet defined', correct='False')])
#response = requests.post(url, data=json.dumps(data), headers=headers)

#url = 'http://192.168.33.10:5001/user/quizzes/1/questions/2'
#data = dict(anschoices=[dict(ans_choice= '1. Yes Python is object oriented   ', correct='True'), dict(ans_choice= '2. No Python is not object oriented', correct='False'), dict(ans_choice= '3. Python may not be used as OOP 1 ', correct='True')])
#response = requests.post(url, data=json.dumps(data), headers=headers)

# Make a GET request for the entire collection.
#response = requests.get(url, headers=headers)

#response = requests.delete(url, headers=headers)
'''
# Make a DEL request for the entire collection.
response = requests.delete(url, headers=headers)
'''
   #print '\n_____________________Response received___________________\n'
   #print '\nJson response:\n==============\n Status code:%i  Reason: %s' %(response.status_code, response.reason)
   #print '\nResponse:\n==============\n%s' %(response.json())
   #print '\nHeader:\n==============\n%s\n' %(response.headers)
   #print '\n_________________________________________________________\n'

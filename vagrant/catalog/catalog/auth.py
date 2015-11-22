import random, string
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response, flash

CLIENT_ID = json.loads(
    open('client_secret.json','r').read())['web']['client_id']

credentials = None

def createResponse(res, status):
    response = make_response(json.dumps(res), status)
    response.headers['Content-Type'] = 'application/json'
    return response

def UpgradeCode(request):
    if request.args.get('state') != login_session['state']:
        return createResponse('Invalid state parameter.', 401)

    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json',scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        return createResponse('Failed to upgrade the authorization code.', 401)

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        return createResponse(result.get('error'), 50)

    gplus_id = credentials.id_token['sub']

    if result['user_id'] != gplus_id:
        return createResponse("Token's User ID doesn't match given user ID.", 401)

    if result['issued_to'] != CLIENT_ID:
        print "Token's Client ID does not match app's."
        return createResponse("Token's Client ID does not match app's.")

    # Is the user already logged in?
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return createResponse('Current User is already connected.', 200)

    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get User info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
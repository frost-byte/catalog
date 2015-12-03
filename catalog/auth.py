import httplib2
import json
import requests
import random
import string


from oauth2client.client import (
    flow_from_clientsecrets,
    FlowExchangeError,
    OAuth2Credentials as Creds,
    TokenRevokeError
)

from flask import session as login_session
from flask import (
    make_response,
    flash,
    redirect,
    url_for,
    Response,
    jsonify
)
from .models import User
from .database import session

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']

credentials = None


def getUserInfo(user_id):
    user = User.query.filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = User.query.filter_by(email=email).one()
        return user.id

    except:
        return None


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )

    session.add(newUser)
    session.commit()
    user = User.query.filter_by(email=login_session['email']).one()

    return user.id


def isActiveSession():
    if 'username' not in login_session:
        return False
    else:
        return True


def canAlter(userID):
    if 'user_id' not in login_session:
        return False

    sessID = login_session['user_id']

    print "(suID, uID) = ( {0}, {1} )".format(sessID, userID)

    if sessID == userID:
        return True
    else:
        return False


def getSessionUserInfo():
    info = {
        'id': login_session['user_id'],
        'name': login_session['username'],
        'photo': login_session['picture']
    }
    return info


def getLoginSessionState():
    if 'state' not in login_session:
        login_session['state'] = ''.join(
            random.choice(
                string.ascii_uppercase + string.digits
            ) for x in range(32)
        )

    return login_session['state']


def createResponse(res, status):
    response = make_response(json.dumps(res), status)
    response.headers['Content-Type'] = 'application/json'
    return response


def ConnectGoogle(request):
    if request.args.get('state') != login_session['state']:
        return createResponse('Invalid state parameter.', 401)

    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
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

    # Check for User ID mismatch.
    if result['user_id'] != gplus_id:
        return createResponse(
            "Token's User ID doesn't match given user ID.",
            401
        )

    # Validate Client ID
    if result['issued_to'] != CLIENT_ID:
        print "Token's Client ID does not match app's."
        return createResponse("Token's Client ID does not match app's.")

    # Is the user already logged in?
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return createResponse('Current User is already connected.', 200)

    # This is a new Login, so store all pertinent info.
    login_session['access_token'] = credentials.access_token
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

    # Check to see if the user exists
    user_id = getUserID(data['email'])

    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " class="gplus_img"> '
    flash("you are now logged in as %s" % login_session['username'])

    data = {
        'name': login_session['username'],
        'picture': login_session['picture']
    }

    print "done!"
    return jsonify(data)


# Disconnect from Google
def DisconnectGoogle():
    if 'credentials' not in login_session:
        print "Invalid Credentials"
        return redirect(url_for('listItem'))

    credentials = Creds.from_json(login_session['credentials'])
    access_token = credentials.access_token

    print "access_token = %s" % access_token
    print 'User name is: %s' % login_session['username']

    http = httplib2.Http()
    http = credentials.authorize(http)

    try:
        credentials.revoke(http)

    except TokenRevokeError as e:
        print "Unable to revoke Token %s" % e
        # Clear login_session
        del login_session['credentials']
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        print "login_session cleared after invalid token.."

        return createResponse("Unable to revoke Token %s" % e, 200)

    # Successfully Disconnected from Google
    del login_session['credentials']
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    print "login_session deleted."
    return createResponse('Successfully disconnected.', 200)

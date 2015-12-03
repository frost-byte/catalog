'''
This is the auth, or Authorization module for the Catalog app.
The module provides methods for Authorizing the app to connect/disconnect
to/from a user's Google+ profile.

Attributes:
    CLIENT_ID:  The Client Secret for the Catalog App.  This file is
        generated from the app's credentials using the Google Development Console.
        It is not included with the repository for the purpose of security.
        Running the app will require the creation of the client secret using the
        previously mentioned Development Console.  The client_secret.json file
        needs to be in the same directory as this module.
'''
import httplib2
import json
import requests
import random
import string
from binascii import hexlify
from os import urandom


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
    request,
    Response,
    jsonify
)
from sqlalchemy.orm.exc import NoResultFound

from app import app
from models import User
from database import session


CLIENT_ID = json.loads(
    open(app.config['APP_CLIENT_SECRET'], 'r').read())['web']['client_id']

credentials = None

@app.before_request
def csrf_protect():
    '''Protect form submissions using a CSRF token.

    If the token is found and validated, then the request will proceed.

    Notes:
        This function is applied to a POST request before it is processed by
        any of the routes that would receive a POST.

        The only POST request that can be made for an unauthenticated user is
        to connect to their Google+ profile.

    Returns:
        In the event that a token is invalid the user will be sent a notice.
    '''
    if request.method == 'POST':

        rule = request.url_rule
        print "csrf_protect: rule = " + rule.rule

        if 'gconnect' in rule.rule:
            # Don't check for a CSRF token when connecting to Google for
            # user authorization.
            return

        token = login_session.pop("_csrf_token", None)

        # Validate the token and make sure it's contained in the form.
        if not token or token != request.form.get('_csrf_token'):
            flash("Invalid form submission!")
            return redirect(url_for('listItem'))
    else:
        return


def generate_random_string():
    '''Create a 16 character long string containing randomly generated
    characters.

    Returns:
        string: The Randomized string.

    '''
    result = hexlify(urandom(16))
    return result

def generate_csrf_token():
    """Generate A CSRF token for the User's login session


    Returns:
        string: Returns a the csrf_token for the currently logged in user.

    """

    if '_csrf_token' not in login_session:
        # Add a new token to the login session.
        login_session['_csrf_token'] = generate_random_string()

    return login_session['_csrf_token']

# Make token generation available to the templating engine.
app.jinja_env.globals['csrf_token'] = generate_csrf_token


def getUserInfo(user_id):
    """Retrieve a User record from the Database via their User id.

    Note:
        Any information regarding usage or something the caller of the function
        should know when using it.

    Args:
        user_id (int): The key/primary key in the User table

    Returns:
        User: returns an instance of the models.User class populated with
            the user's information.

        If no user is found, None is returned.

    Raises:
        NoResultFound: No user was found with the given user id.

    """
    try:
        user = User.query.filter_by(id=user_id).one()

    except NoResultFound as e:
        return e

    return user


def getUserID(email):
    """Retrieve a User record from the Database via their User id.

    Note:
        Any information regarding usage or something the caller of the function
        should know when using it.

    Args:
        user_id (int): The key/primary key in the User table

    Returns:
        User: returns an instance of the models.User class populated with
            the user's information.

    Raises:
        NoResultFound: No user was found with the given email.

    """
    try:
        user = User.query.filter_by(email=email).one()

    except NoResultFound as e:
        print "No Result Found"
        return None

    return user.id


def createUser(login_session):
    """Add a User to the database using the current information stored in the
    login session.

    Args:
        login_session (dict): Dictionary containing information about the current
        login session, including the user's profile information from Google+

    Returns:
        int: The user_id from the newly created record in the User table in
            the database.

    """
    print "Creating User"
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )

    session.add(newUser)
    session.flush()
    session.commit()

    return newUser.id


def isActiveSession():
    """Determine if the current session is active by checking if a username is
    associated with the session.

    Returns:
        True if the session is active, otherwise False for an inactive session.

    """
    if 'username' not in login_session:
        return False
    else:
        return True


def canAlter(userID):
    """Confirms that the user specified by the given user id is the one currently
    in the login_session.


    Args:
        userID (int): An ID corresponding to a User record in the database.

    Returns:
        True if the specified user is also the currently authorized user in the
        login_session.  False if it is a different user.

    """
    if 'user_id' not in login_session:
        return False

    sessID = login_session['user_id']

    if sessID == userID:
        return True
    else:
        return False


def getSessionUserInfo():
    """Return profile information for the user currently logged in.

    Note:
        The profiles for the User records generated using the populator module
        obviously won't have valid information related to Google+.

    Returns:
        dict: Basic profile information for the login_session user.
            Including:
            user_id: Their User record in the database.
            name: Their name (from their Google+ Profile)
            email: Their email (also taken from their Google+ Profile)

    """
    info = {
        'id': login_session['user_id'],
        'name': login_session['username'],
        'photo': login_session['picture']
    }

    return info


def getLoginSessionState():
    """ Retrieve the Login Session's state.

    The State is assigned to the Login Session when a user logs in to the App.
    This is a specific string used to validate the session.

    Returns:
        string: The state is generated upon user login and added to the login
            session and returned.

    """
    if 'state' not in login_session:
        login_session['state'] = ''.join(
            random.choice(
                string.ascii_uppercase + string.digits
            ) for x in range(32)
        )

    return login_session['state']


def createResponse(res, status):
    """Create a response to a Request to one of the App's endpoints.

    When the routes for connecting/disconnecting to Google+ are called,
    this function will be used to send various responses to those requests.

    Args:
        res (object): A response with information pertinent to a request for
            Connect and Disconnect to and from Google+

        status (int): Depending upon the result of processing the request, this
            will indicate whether or not the request was successful.

    Returns:
        Response: A response in json format containing the data passed in via
        the res and status arguments.

    """
    response = make_response(json.dumps(res), status)
    response.headers['Content-Type'] = 'application/json'

    return response


def ConnectGoogle(request):
    """Process the Request to the App for logging in to Google+.

    Args:
        request (Request): Contains the information for requesting login
            to Google+

    Returns:
        Response: returnValues

        Detailed Description of the possible values of the returned variable.
        Describe contents and format of returned values.
        Describe Usage.

    Raises:
        FlowExchangeError:  The flow exchange setup establishing authorization
        with the Google+ failed.

    Examples:
        (optional) Describe how the function is used by providing examples here.

    """

    # Make sure that the session state in the request matches the current state
    # for this login session.
    if request.args.get('state') != login_session['state']:
        return createResponse('Invalid state parameter.', 401)

    # Code required for obtaining credentials via OAuth
    code = request.data

    try:
        # Establish the OAuth Flow Exchange
        oauth_flow = flow_from_clientsecrets(app.config['APP_CLIENT_SECRET'], scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        return createResponse('Failed to upgrade the authorization code.', 401)

    # Authorize access to Google+ via Oauth2
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)

    # Request Authorization
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # Authorization Request Error occurred.
    if result.get('error') is not None:
        return createResponse(result.get('error'), 50)

    # Authorization via OAuth2 succeeded, now confirm that the user for this session
    # matches the specified user_id
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
        print "Already connected!"
        return createResponse('Current User is already connected.', 200)

    # This is a new Login, so store all pertinent info.
    login_session['access_token'] = credentials.access_token
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get User info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    # Convert the response data to a usable form.
    data = answer.json()

    # Store the User's Google profile information in the current login session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check to see if the user exists
    user_id = getUserID(data['email'])

    # This is a new user, so add them to the Database.
    if user_id is None:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    # Create the welcome message to be displayed in the Client User's browser.
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " class="gplus_img"> '
    flash("You are now logged in as %s" % login_session['username'])

    data = {
        'name': login_session['username'],
        'picture': login_session['picture']
    }

    print "done!"
    # Return some of the user information to be displayed in the Navbar
    return jsonify(data)


def DisconnectGoogle():
    """Disconnect from Google by Revoking access to a User's Google Profile

    Returns:
        Response: A varying response depending upon the success or failure in
            revoking the app's usage of the logged in user's Google Profile.

    Raises:
        TokenRevokeError: Google was unable to revoke the connection between this
            app and their Google profile.

    """
    # Credentials must be in the login session in order for the Revocation
    # to succeed.
    if 'credentials' not in login_session:
        print "Invalid Credentials"
        return redirect(url_for('listItem'))

    # Retrieve the OAuth2 credentials and Access Token from the Login Session.
    credentials = Creds.from_json(login_session['credentials'])
    access_token = credentials.access_token


    # Authorize an HTTP Request using the Credentials and then attempt to
    # revoke the app's connection.
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

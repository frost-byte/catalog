'''
A module for populating the database for the Catalog app.

Creates a variety of Items, Users and Category records and associates them.
Random creation dates from the last 18 months are assigned to Categories and Items.


Attributes:
    item_names (strings):           Names of items.
    item_images (strings):          Local Urls to images for each item.
    item_descriptions (strings):    Descriptions of each item.
    category_names (strings):       Names of each Category.
    user_male_names (strings):      Male User Names.
    user_female_names (strings):    Female User Names.

    parser (Parser):                The command-line parser that populates the
                                    database when give the -r option.

    args (list):                    The list of arguments passed to the parser.

'''
if __name__ == '__main__' and '__package__' is None:
    from os import sys, path
    sys.path.append(path.dirname(path.abspath(__file__)))

from random import randint
import datetime
import random
import argparse

from database import init_db, session
from models import Category, Item, User

item_names = [
    "Snowboard",
    "Bicycle",
    "Stick",
    "Shinguards",
    "Frisbee",
    "Bat",
    "Jersey",
    "Cleats",
    "Goggles"
]


item_images = [
    "images/snowboard.png",
    "images/racing-bicycle.png",
    "images/ice-hockey-stick.png",
    "images/shinguards.png",
    "images/frisbee.png",
    "images/baseball-bat.png",
    "images/jersey.png",
    "images/cleats.jpg",
    "images/goggles.jpg"
]


item_descriptions = [
    '''Best for any terrain and conditions.  All-mountain snowboards perform
    anywhere on a mountain - groomed runs, backcountry, or even park and pipe.
    They may be directional (meaning downhill only) or twin-tip (for riding
    switch, meaning either direction).  Most boarders ride all-mountain boards.
    Because of their versatility, all-mountain boards are good for beginners
    who are still learning what terrain they like.''',
    '''Bii cycle, biii cycle, bicycle.  I want to ride my Bii cycle, I want to
    ride my bike. I want to ride my bicycle, I want to ride it where I
    like.''',
    '''The number one tool to bring to a boxing match on an ice rink.  If you want
    to start a totally unnecessary fight, just hook an opposing player or trip
    them up. Your missing teeth will thank you in no time!''',
    '''Shinguards are an integral part of maintaining your ability to walk.  After
    an overly aggressive day of attacking the enemie's end of the pitch, your
    shins will greatly appreciate your concern for their well-being.''',
    '''What flies through the air, and really doesn't care? Frisbee!  What
    bonks your dog in the beak and makes him incredibly weak? Frisbee!''',
    '''When your baseball career comes to an end, you'll still be able to
    rely upon your trusty bat.  In an unexpected riot? Bat is there when
    you need it.''',
    '''Aside from being named for a corrupt State in the USA, jersey is
    a key part in representing your team.  No need to gesticulate with your
    fingers to indicate which side of town your gang is from.  Just don your
    jersey and everyone of your hooligan fans will know who you
    represent.''',
    '''Cleats will keep you well grounded.  See an opposing player without
    shinguards? That poor sod!  The only downside is that you won't be able to
    use them for hockey.''',
    '''Goggles, not to be confused with the search engine, are designed to
    shield your eyes from that stray snowball or spray of powder when your
    skiing friend, Jacque, decides to give your face a good dusting of snow.
    Otherwise, they're bound to help improve your visibility just enough to see
    that impending pine tree, right before it crushes your body.'''
]


# Categories
category_names = [
    "Snowboarding",
    "Cycling",
    "Hockey",
    "Soccer",
    "Frisbee",
    "Baseball",
    "Basketball",
    "Rock Climbing",
    "Foosball",
    "Skating"
]

# Users
user_male_names = [
    "George Tanaka",
    "Johnny Utah",
    "Troy Armstong",
    "Tennessee Williams",
    "Garet Jax",
    "Gandalf the Grey",
    "Saruman the White",
]

user_female_names = [
    "Meryl Streep",
    "Kim Bigassian",
    "Sarah Failin",
    "Amy Adams",
    "Keira Knightley",
    "Jessica Chastain",
    "Jennifer Lawrence"
]


def randomCreationDate():
    '''Randomly choose a date for an Item or Category's creation from within
    the last 18 months at the time the module is executed.

    Returns:
        datetime: A random date from the previous 540 days at the time
            the function was executed.
    '''

    today = datetime.date.today()
    days_old = randint(0, 540)
    created = today - datetime.timedelta(days=days_old)
    return created


def CreateItem(name, category, user_id, description, picture):
    '''Create an Item.

    Notes:
        Doesn't add or commit the Item to the database.

    Args:
        name (string):          The Item's name.
        category (Category):    The Category record of the item.
        user_id (int):          The user_id of the person who created the item.
        description (string):   The Description of the Item.
        picture (string):       Local Url to the Image of the item.

    Returns:
        A new Item instance.
    '''
    new_item = Item(
        name=name,
        cat_id=category,
        description=description,
        dateCreated=randomCreationDate(),
        picture=picture,
        user_id=user_id
    )
    return new_item


def generateEmail(name):
    '''Create an email address with the gmail.com Domain from a user name.

    Args:
        name (string):  The User's name.

    Returns:
        string: The User's gmail address.
    '''
    domain = "@gmail.com"
    firstName = name.split(' ')[0].lower()
    return firstName + domain


class ItemPopulator(object):
    '''Populates Item records into the Catalog Database.

    Attributes:
        users (list):       The users generated and added to the database.
        categories (list):  The categories generated and added to the database.
    '''

    def __init__(self):
        '''Initialize the Database connection.'''
        init_db()
        self.users = []
        self.categories = []


    def findCategoryByName(self, name):
        '''Find a Category by its name.

        Notes:
            Doesn't refer directly to Categories in the database.

        Args:
            name (string): The Category name to find.

        Returns:
            A Category in this instance that has the specified name.

        '''
        for c in self.categories:
            if c.name == name:
                return c

    def chooseUser(self):
        '''Randomly choose a User from the list of users.

        Notes:
            Doesn't refer directly to users in the database.

        Returns:
            int: The id of a User from the list in this instance.

        '''
        user = random.choice(self.users)
        return user.id

    def numCategorys(self):
        '''The Number of Categories in the database.'''
        return len(Category.query.all())

    def populate(self):
        '''Populate the Database with Users, Categories and Items.'''
        # Add Male Users
        for name in user_male_names:
            user = User(
                name=name,
                email=generateEmail(name),
                picture="images/male_avatar.png"
            )
            session.add(user)
            session.commit()
            self.users.append(user)

        # Add Female Users
        for name in user_female_names:
            user = User(
                name=name,
                email=generateEmail(name),
                picture="images/female_avatar.png"
            )
            session.add(user)
            session.commit()
            self.users.append(user)

        # Add Categories
        for name in category_names:
            category = Category(name=name, user_id=self.chooseUser())
            session.add(category)
            session.commit()
            self.categories.append(category)

        # Add Items
        snowboard = Item(
            cat_id=self.findCategoryByName("Snowboarding").id,
            user_id=self.chooseUser(),
            picture=item_images[0],
            name=item_names[0],
            description=item_descriptions[0],
            dateCreated=randomCreationDate()
        )
        session.add(snowboard)
        session.commit()

        bicycle = Item(
            cat_id=self.findCategoryByName("Cycling").id,
            user_id=self.chooseUser(),
            picture=item_images[1],
            name=item_names[1],
            description=item_descriptions[1],
            dateCreated=randomCreationDate()
        )
        session.add(bicycle)
        session.commit()

        stick = Item(
            cat_id=self.findCategoryByName("Hockey").id,
            user_id=self.chooseUser(),
            picture=item_images[2],
            name=item_names[2],
            description=item_descriptions[2],
            dateCreated=randomCreationDate()
        )
        session.add(stick)
        session.commit()

        shinguards = Item(
            cat_id=self.findCategoryByName("Soccer").id,
            user_id=self.chooseUser(),
            picture=item_images[3],
            name=item_names[3],
            description=item_descriptions[3],
            dateCreated=randomCreationDate()
        )
        session.add(shinguards)
        session.commit()

        frisbee = Item(
            cat_id=self.findCategoryByName("Frisbee").id,
            user_id=self.chooseUser(),
            picture=item_images[4],
            name=item_names[4],
            description=item_descriptions[4],
            dateCreated=randomCreationDate()
        )
        session.add(frisbee)
        session.commit()

        bat = Item(
            cat_id=self.findCategoryByName("Baseball").id,
            user_id=self.chooseUser(),
            picture=item_images[5],
            name=item_names[5],
            description=item_descriptions[5],
            dateCreated=randomCreationDate()
        )
        session.add(bat)
        session.commit()

        jersey = Item(
            cat_id=self.findCategoryByName("Soccer").id,
            user_id=self.chooseUser(),
            picture=item_images[6],
            name=item_names[6],
            description=item_descriptions[6],
            dateCreated=randomCreationDate()
        )
        session.add(jersey)
        session.commit()

        cleats = Item(
            cat_id=self.findCategoryByName("Soccer").id,
            user_id=self.chooseUser(),
            picture=item_images[7],
            name=item_names[7],
            description=item_descriptions[7],
            dateCreated=randomCreationDate()
        )
        session.add(cleats)
        session.commit()

        goggles = Item(
            cat_id=self.findCategoryByName("Snowboarding").id,
            user_id=self.chooseUser(),
            picture=item_images[8],
            name=item_names[8],
            description=item_descriptions[8],
            dateCreated=randomCreationDate()
        )
        session.add(goggles)
        session.commit()


# Only run the Database Population Functions when specified on the
# command line by using the run argument
parser = argparse.ArgumentParser(
    description="Populate records in the puppies database.")

parser.add_argument(
    '-r',
    '--run',
    action='store_true',
    dest='populate',
    default='store_false',
    help='Run the population funcitons.'
)

args = parser.parse_args()

'''
The run argument was specified, so we populate the database.
This is done so that when other modules import this one, it doesn't
populate the database again.
(The tables of strings can be used in other modules.)
'''
if args.populate is True:
    init_db()
    p = ItemPopulator()
    p.populate()

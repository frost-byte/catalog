from random import randint
import datetime
import random
import argparse

from database import init_db, Base, session
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
    "images/shinguards.jpg",
    "images/frisbee.png",
    "images/baseball-bat.png",
    "images/jersey.png",
    "images/cleats.jpg",
    "images/goggles.jpg"
]

# Descriptions
item_descriptions = [
    "Best for any terrain and conditions.  All-mountain snowboards perform anywhere on"
    " a mountain - groomed runs, backcountry, or even park and pipe. They may be"
    "directional (meaning downhill only) or twin-tip (for riding switch, meaning"
    " either direction).  Most boarders ride all-mountain boards.  Because of their "
    "versatility, all-mountain boards are good for beginners who are still learning what"
    " terrain they like.",
    "Biii cycle, biii cycle, bicycle.  I want to ride my Bii cycle, I want to ride my"
    "bike. I want to ride my bicycle, I want to ride it where I like.",
    "The number one tool to bring to a boxing match on an ice rink.  If you want to"
    " start a totally unnecessary fight, just hook an opposing player or trip them up."
    "Your missing teeth will thank you in no time!",
    "Shinguards are an integral part of maintaining your ability to walk.  After an "
    "over aggressive day of attacking the enemies end of the pitch, your chins will"
    " greatly appreciate your concern for their well-being.",
    "What flies through the air, and really don't care? Frisbee!  What bonks your dog "
    " in the beak and makes him incredibly weak? Frisbee!",
    "When your baseball career comes to an end, you'll still be able to rely upon your"
    " trusty bat.  In an unexpected riot? Bat is there when you need it.",
    "Aside from being named for a worthless State in the USA, jersey is a key "
    " part in representing your team.  No need to gesticulate with your fingers to "
    "indicate which side of town your gang is from.  Just don your jersey and everyone "
    " of your hooligan fans will know who you represent.",
    "Cleats will keep you well grounded.  See an opposing player without shinguards? "
    " That poor sod!  The only downside is that you won't be able to use them for "
    "hockey.",
    "Goggles, not to be confused with the search engine, are designed to shield your eyes"
    " from that stray snowball or spray of powder when your skiing friend, Jacque, "
    " decides to give your face a good dusting of snow.  Otherwise, they're bound to "
    "help improve your visibility just enough to see that impending pine tree, right "
    "before it crushes your body."
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

# Adopters
user_names = [
    "George Tanaka",
    "Bill Witherspoon",
    "Johnny Football",
    "Johnny Utah",
    "John Wick",
    "Meryl Streep",
    "Jacob Dylan",
    "Troy Armstong",
    "Tennessee Williams",
    "Billy Bob McNugget",
    "Kim Bigassian",
    "Sarah Failin",
    "Garet Jax",
    "Gandalf the Grey",
    "Saruman the White",
    "Nathan Barnes",
    "Amy Adams",
    "Keira Knightley",
    "Jessica Chastain",
    "Jennifer Lawrence"
]

def removeUserName(name):
    if name in user_names:
        user_names.remove(name)


#This method will make the creation date for an item somewhere in the last 0-18 months(approx.) from the day the algorithm was run.
def randomCreationDate():
    today = datetime.date.today()
    days_old = randint(0,540)
    created = today - datetime.timedelta(days = days_old)
    return created


def CreateItem(name, category, user_id, description, picture):
    new_item = Item(
        name = name,
        cat_id = category,
        description = description,
        dateCreated = randomCreationDate(),
        picture= picture,
        user_id = user_id
    )
    return new_item


class ItemPopulator(object):

    def __init__(self):
        init_db()
        self.users = []
        self.categories = []


    def findCategoryByName(self, name):
        for c in self.categories:
            if c.name == name:
                return c


    def ChooseUser(self):
        user = random.choice(self.users)
        return user.id


    def numCategorys(self):
        return len(Category.query.all())


    def populate(self):

        #Add Categories
        for name in category_names:
            category = Category(name = name)
            session.add(category)
            session.commit()
            self.categories.append(category)


        # Add Users
        for name in user_names:
            user = User(name = name)
            session.add(user)
            session.commit()
            self.users.append(user)


        #Add Items
        snowboard = Item(
            cat_id = self.findCategoryByName("Snowboarding").id,
            user_id = self.ChooseUser(),
            picture = item_images[0],
            name = item_names[0],
            description = item_descriptions[0],
            dateCreated = randomCreationDate()
        )
        session.add(snowboard)
        session.commit()

        bicycle = Item(
            cat_id = self.findCategoryByName("Cycling").id,
            user_id = self.ChooseUser(),
            picture = item_images[1],
            name = item_names[1],
            description = item_descriptions[1],
            dateCreated = randomCreationDate()
        )
        session.add(bicycle)
        session.commit()


        stick = Item(
            cat_id = self.findCategoryByName("Hockey").id,
            user_id = self.ChooseUser(),
            picture = item_images[2],
            name = item_names[2],
            description = item_descriptions[2],
            dateCreated = randomCreationDate()
        )
        session.add(stick)
        session.commit()


        shinguards = Item(
            cat_id = self.findCategoryByName("Soccer").id,
            user_id = self.ChooseUser(),
            picture = item_images[3],
            name = item_names[3],
            description = item_descriptions[3],
            dateCreated = randomCreationDate()
        )
        session.add(shinguards)
        session.commit()


        frisbee = Item(
            cat_id = self.findCategoryByName("Frisbee").id,
            user_id = self.ChooseUser(),
            picture = item_images[4],
            name = item_names[4],
            description = item_descriptions[4],
            dateCreated = randomCreationDate()
        )
        session.add(frisbee)
        session.commit()


        bat = Item(
            cat_id = self.findCategoryByName("Baseball").id,
            user_id = self.ChooseUser(),
            picture = item_images[5],
            name = item_names[5],
            description = item_descriptions[5],
            dateCreated = randomCreationDate()
        )
        session.add(bat)
        session.commit()


        jersey = Item(
            cat_id = self.findCategoryByName("Soccer").id,
            user_id = self.ChooseUser(),
            picture = item_images[6],
            name = item_names[6],
            description = item_descriptions[6],
            dateCreated = randomCreationDate()
        )
        session.add(jersey)
        session.commit()

        cleats = Item(
            cat_id = self.findCategoryByName("Soccer").id,
            user_id = self.ChooseUser(),
            picture = item_images[7],
            name = item_names[7],
            description = item_descriptions[7],
            dateCreated = randomCreationDate()
        )
        session.add(cleats)
        session.commit()

        goggles = Item(
            cat_id = self.findCategoryByName("Snowboarding").id,
            user_id = self.ChooseUser(),
            picture = item_images[8],
            name = item_names[8],
            description = item_descriptions[8],
            dateCreated = randomCreationDate()
        )
        session.add(goggles)
        session.commit()


# Only run the Database Population Functions when specified on the
# command line by using the run argument
parser = argparse.ArgumentParser(description="Populate records in the puppies database.")
parser.add_argument(
    '-r',
    '--run',
    action='store_true',
    dest='populate',
    default='store_false',
    help='Run the population funcitons.'
)
args = parser.parse_args()

# The run argument was specified, so we populate the database.
# This is done so that when other moodules import this one, it doesn't
# populate the database again. (The tables of strings are used in other modules.)
if args.populate == True:
    init_db()
    p = ItemPopulator()
    p.populate()

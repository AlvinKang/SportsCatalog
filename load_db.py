from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine("sqlite:///catalog.db")

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create users
user1 = User(name="Heather Weber", email="heatherweber1983@gmail.com")
session.add(user1)

user2 = User(name="Jesse Walker", email="jessewalker1983@gmail.com")
session.add(user2)

session.commit()

# Create baseball category
category = Category(name="Baseball")
session.add(category)
session.commit()

# Create items for baseball
item1 = Item(user_id=1, category_name="Baseball", name="Youth Bat",
	description="Youth Bat is a good option for players who value the traditional feel of a one-piece bat and the classic ping off a durable aluminum barrel.")
session.add(item1)

item2 = Item(user_id=1, category_name="Baseball", name="Classic Baseball Glove", description="Classic Baseball Glove is built to be strong and sturdy for maximum ball control, yet becomes soft and pliable once broken-in. Made with pride in the USA.")
session.add(item2)

item3 = Item(user_id=1, category_name="Baseball", name="Retro Baseball Cleats", description="Retro Baseball Cleats feature a synthetic leather upper with overlays throughout that deliver enhanced durability and fit while a full-length Phylon midsole and heel Air-Sole unit combine to provide maximum impact protection and a smooth comfortable ride.")
session.add(item3)

session.commit()

# Create basketball category
category = Category(name="Basketball")
session.add(category)
session.commit()

# Create items for basketball
item1 = Item(user_id=2, category_name="Basketball", name="Official Basketball",
	description="Official Basketball is constructed with a composite leather casing for the best feel and durability on indoor hardwood or outdoor pavement.")
session.add(item1)

item2 = Item(user_id=2, category_name="Basketball", name="Basketball Shoes",
	description="Designed for high-performing athletes and packed with serious technology, these low-top shoes make sure you have a solid foundation for your best moves.")
session.add(item2)

item3 = Item(user_id=2, category_name="Basketball", name="Basketball Sleeves",
	description="Stay strong from the first minute through the last in the Basketball Sleeves. Made with moisture-wicking fabric in a form-fitting design, these compression sleeves keep your muscles supported and engaged without overheating.")
session.add(item3)

session.commit()

# Create soccer category
category = Category(name="Soccer")
session.add(category)
session.commit()

# Create items for soccer
item1 = Item(user_id=1, category_name="Soccer", name="Pitch Soccer Ball",
	description="Built for intense training sessions and improving your footwork, the Pitch Soccer Ball features a machine-stitched TPU casing and reinforced butyl bladder that ensures consistent shape retention and enhanced protection against tears and abrasions.")
session.add(item1)

item2 = Item(user_id=1, category_name="Soccer", name="Soccer Shin Socks",
	description="Designed to provide incredible protection, convenience and comfort for youth players, the Soccer Shin Socks are an essential for your future pro. Manufactured with unyielding shin and ankle padding, these shin socks are sure to keep players safe out on the field.")
session.add(item2)

item3 = Item(user_id=1, category_name="Soccer", name="Goalie Gloves",
	description="Made for heavy duty performance that's designed for consistency in all weather conditions, the Goalie Gloves' positive cut palm offers a greater surface area to enhance cushioning and protection, while making sure you make solid contact with each shot attempt.")
session.add(item3)

session.commit()

# Create tennis category
category = Category(name="Tennis")
session.add(category)
session.commit()

# Create items for tennis
item1 = Item(user_id=2, category_name="Tennis", name="Bam Tennis Racquet",
	description="Add power to your game with the graphite construction of this moderate swinging racquet. The breakthrough frame reduces twisting for ultimate control so you can return every volley with perfection.")
session.add(item1)

item2 = Item(user_id=2, category_name="Tennis", name="Official Tennis Balls",
	description="The official ball of USTA League Tennis, these balls feature natural rubber for reliable feel and reduced shock. Interlocked wool fiber provides durability along with deep-elastic seams that reduce cracking.")
session.add(item2)

item3 = Item(user_id=2, category_name="Tennis", name="Tennis Bag",
	description="The Tennis Bag has the room you need for a day at the tennis court. This tennis bag's main compartment either fits up to three full sized tennis racquets or one tennis racquet plus other gear, like towels or tennis shoes-you decide. Smaller items and accessories fit nicely and are easily accessed in the bag's outer side pocket.")
session.add(item3)

session.commit()

# Create football category
category = Category(name="Football")
session.add(category)
session.commit()

# Create items for football
item1 = Item(user_id=1, category_name="Football", name="Junior Football",
	description="Watch your player develop their spiral under center or track down lobs on the sideline with the Junior Football. Engineered to guide your player toward excellent form when tossing the ball downfield, its extruded lace system and textured stripes ensure they maintain solid grip during harsh conditions.")
session.add(item1)

item2 = Item(user_id=1, category_name="Football", name="Youth Football Helmet",
	description="Inflatable padding at the back, side and jaw pads can be inflated to provide a customized support system tailored to fit the size of each players specific head shape. The high impact shell offers protection against impact, with an overliner that enhances comfort for players so they can focus on the action.")
session.add(item2)

item3 = Item(user_id=1, category_name="Football", name="Turf Football Cleats",
	description="Flyknit upper with a fused durable skin provides exceptional flexibility, support, unbeatable breathability and stability while a cushioning system delivers maximum padding for ultimate comfort. The Turf Football Cleats have a rubber outsole pattern that's designed to provide traction, speed and performance on every down.")
session.add(item3)

session.commit()

# Create golf category
category = Category(name="Golf")
session.add(category)
session.commit()

# Create items for golf
item1 = Item(user_id=2, category_name="Golf", name="XR Driver",
	description="Speed up your tee game with the XR Driver. R technology reduces face weight and lowers Center of Gravity by 17% to create a blend of increased ball speeds and playability.")
session.add(item1)

item2 = Item(user_id=2, category_name="Golf", name="X-Carry Stand Bag",
	description="Transport your clubs in comfort and style with the X-Carry Stand Bag. A 6-way top with 3 full-length dividers provides exceptional club separation and protection. 6 strategically-placed pockets, including a velour-lined valuables pockets and full-length apparel pocket, provide numerous storage options.")
session.add(item2)

item3 = Item(user_id=2, category_name="Golf", name="Command Golf Shoes",
	description="Achieve next-level performance on the course with Command Golf Shoes. Performance textile uppers equipped with a waterproof membrane, articulated tongue and technology provide complete support, protection and comfort in any playing condition.")
session.add(item3)

session.commit()

print "Database loaded with users, categories, items!"
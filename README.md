# Simple Idle Game
#### To run the game use command "flask run", make sure you read requirements.txt
#### NOTE: Game does not look very pretty at the moment, my main focus was functionality. This game is still being developed.
#### Description:
This is a Simple Idle Game that was written in Python and HTML. This project is using Flask, Bootstrap, CSS, Sqlite3, jQuery and Jinja.
This program lets user make a secured account (secured by Werkzeug Security) which data is stored in data.db table called users. Password itself is not stored but the hash generated.
Creating account requirements are that username entered must be unique. Password must be at least 6 characters long and there must be 1 letter in password. Passwords must match.

Upon creating account, table called buildings in data.db is generating new entries. Each new user registered automatically get's assigned 4 rows in buildings database. 
This database's function is to keep track of each building in a way that allows user to upgrade building's level and deconstruct building.

If user has built a building, if that building is not busy it will generate money in generator.py. 
In generator.py are 2 functions, first function generates income every 5 seconds for each building built.
Second function is checking every 5 seconds if building status should be changed from busy to not busy(1 or 0).
In generator.py there's a lot of spam with lock.aquire(True) and lock.release(), this is used because threading functions tend to execute
at exactly same time, which causes a lot of errors, using lock function ensures that one is being executed after another, not mixing it up.


Helpers.py file contains the following functions: login_required - which makes sure that user is logged in if accessing something when function is applied.
usd - this function formats value as USD
error - this function renders a message as error message to user.
building_name - This function takes building type as input and return building name
building_price and building_time - these functions take building type and building level as input and return price and time needed to build/upgrade.
my_timedelta and get_sec - these functions are not in use and I'm currently figuring out the way to implement them, but they are connected to formating time.

app.py is a main python file where code is executed. 
building_income() and update_busy_status() is being executed near start of program, trigerring these two function will start a forever loop on them.
"/" route is default route, in this case it's home screen where user has short gets a welcome message and if they are logged in it will show message: You are logged in! Go to Map
and if user is not logged in they will only have option to log in.

"/login" route is where user logs in their existing account, if user enters wrong username or password they will not be able to login.

"/register" route is covered in 4th line.

"/logout" route logs user out, and redirects them to home page.

"/map" route is where user will see their game map. It shows buildings they have build, along with building's level and if building is busy it shows time
remaining until building finishes upgrading/building. From here users can also click on each building they have and they will be redirected
to "/b/<b_id>"
map.html contains 1 modal from bootstrap which appears when user wants to build a new building.

"/b/<b_id>" is a dynamic route that allows user to upgrade or deconstruct building.
b.html contains 2 modals from bootstrap, one for upgrade and one for deconstruct.

"/upgrade", "/deconstruct", "/build" are routes that are POST only, their functions are to upgrade,deconstruct and build new buildings. They heavily rely on changing content of buildings and user database.

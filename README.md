# Board Game Tools
#### Video Demo:  <URL HERE>
#### Description: 
For my final project for CS50x 2024, I have created a web application called Board Game Tools.
## Concept
The concept originated from frustrations with not having the correct tools when playing various board games, maybe because you lost a timer, or a die, or maybe just from a desire to not scribble scores down on scrap paper. Here I have created the beginnings of a website that acts as a compendium for tools, both generic and game-specific, to assist and support gamers while playing board games.

## Installation & Usage
1. Clone the repository.
2. Navigate to the project directory.
3. Install the required dependencies in `requirements.txt`.
4. Run the application using `flask run`.
5. Open your web browser and go to `http://localhost:5000`.

## Features
- **Homepage**: A stylised homepage to welcome the user to the site.
- **Account**: Register for an account and log in to enable tracking between sessions, and view statistics.
- **Directories**: Pages to show all games and tools available.
- **Tools**
    - **Dice**: Choose multiple dice from a standard role-playing set and randomly roll them.
    - **Scores**: Tally up points on a scoreboard for multiple players .
    - **Timer**: A countdown timer with sound effects.
- **Games**
    - **Monopoly**: Implemented save states for Monopoly games, to allow you to stop mid-game and pick up where you left off.
    - **Scrabble**: Using an API, check whether a word is valid in Scrabble, and if so, how many points it will score.
    - **Poker**: A visual reminder of scoring hands in poker and their ranking.

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript, Bootstrap.
- **Backend**: Python, Flask.
- **Database**: SQLite3, CS50's SQL Python implementation based on SQLAlchemy.

## Web Design
For the design of the site, I used various elements and components from bootstrap. I have a consistent nav bar at the top of the page with a logo matchin the one found on the home page, which folds down into a burger menu at smaller screen sizes to allow for responsive design. I went with a dark theme.\
To match this, I implemented a footer with the same colouring that always floats at the bottom of the page. This gives the effect of having a closed environment to surface page content within, giving consistency to the website.\
Between the nav bar and the footer, the page content sits in the middle with a small margin to both sides, meaning that all page content follows the same maximum width rules at any screen size.\
On any pages that take an input to set up (such as `/tools/timer`), or have 'player cards' to display different players or sections of the game or tool (such as `/games/scrabble`) I created a `frosted` class, which adds a gradient colouring, rounded border, drop/box shadow, and styles input fields, to again provide a consistent styling accross the site and to make important interactive parts of the site stand out.\
The two Directory pages use a different style of card, which features a hover over effect that scales the object, to imitate picking up each card in a sense.\
Tables throughout the site are styled in standard bootstrap dark striped styling, and in the `/account` page, they are held within custom styled accordion components.\
Some pages use custom fonts, such as `/tools/timer` and `/tools/dice`. The latter has different font characters representing the faces of various sided dice, so I created a helper python file `translate_dice.py` to take the output from the random number generation, and translate it into the ascii character that corresponds to the symbol needed to show that dice, (whilst also storing the integer of course in the database and to perform calculations on).

## Validation
Throughout the site, I have used client-side validation on forms to prevent submission of invalid inputs, and to indicate minimum and maximums for each tool, however bypassing these restrictions in a lot of cases would not completely break the site, and would only result in slightly ugly UI, so I have not built any further protections against this type of validation. An example of this can be seen in `/games/monopoly`, where bypassing client-side validation and not providing a name for each player would just render each card nameless, and therefore is not the end of the world.\
Some forms require an input that the user should not be able to easily change, so where this is needed, to avert (but not completely prevent) the user from tampering with this, I have used `<input>` elements with the styling property `display: hidden`.\
In other places, it is paramount that protection is in place, so on the login and register pages, password complexity limits and unique usernames are checked client side and errors are passed back in flash messages.\
Also, During setup for `/games/monopoly` and `/tools/scoreboard`, the player count input is prevented from submission by the select button triggering a Javascript script to check the player number is greater than 1, and alerting and preventing submission if not.

## History
In certain areas of the site (namely; `/games/scrabble`, `/tools/dice`, `/account`, and `/games/monopoly/load`), upon page load, the database is queried for history of submissions and results, and presents these in various tables. Where sensible, the database query limits the results to 5 to fit on the screen nicely, and in other areas, the full table is shown.\
One issue I ran into was that each player is stored as a seperate line in the database in the `monopoly` table. Upon loading these saves, it was impossible to distingusish which save/session each line belonged to. To solve this, I created a further table in the database `monopoly_sessions`, whose purpose is to store an incrementing number each time a session is saved, and also edited the `monopoly table` to store this number as a column for each row. This way, when querying for the saves, I only present a load button when the session ID number changes, and use that button to load every save with that session ID, thereby seperating each save session.\
There are also if statements at each place where histories are displayed to check firstly whether the user is logged in or not, and secondly whether they have any history for that particular function, and instead display instructional information in the place of the history.

## API

## Database Choices

## Timer in JS

##
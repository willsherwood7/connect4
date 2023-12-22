To explain the design of our code, we will break it into three sections: the back end (Python), the front end (HTML), and the visual appearance (CSS). We chose to run the game with python, then dynamically display the state of the board using HTML and Jinja. We felt more comfortable doing this as opposed to having the entire game run with JavaScript.

The backend of our game was broken up into four different python files: app.py, helpers.py, game.py, and ai.py. The app.py contains the core functionality of our website, just like app.py did for Finance.

The purpose of our helpers.py file is to have functions that are not used in the actual running of the game and do not render one of our HTML pages. We have reused the apology function that displays an apology message if the user does not execute something correctly. Also in our helpers.py file, we have the “update_elo” and “update_stats” functions. The “update_elo” function returns the value that must be added to the players elo rating based on that player’s rating, their opponent’s rating, the result, and how many games the player has played. Our algorithm places more weight on the earlier matches in the players history so that they can more quickly adjust to their accurate elo range. This means that the first game in the players history will have a larger impact on their elo than their second game. The games become less and less impactful to their rating up until their 10th game, when it becomes just the standard change in rating. The “update_stats” function updates the database when a match is played. In connect4.db, we created a users table (stores username, id, hashed password, rating, wins, losses, and ties) and a games table (stores the player1_id, player2_id, result, and time). After every match is played, both tables are updated in the “update_stats” function. This serves as the database for our project and allows us to store different users and their individual histories.

Moving to our game.py file, this file contains all the required functions that run the game play as well as the easy, medium, and hard bots. The Connect 4 board is stored as a 2d list with 7 rows and 6 columns. This is represented with “board”, a list of 6 lists each with length 7. When starting a new game, the board is cleared with all 0 values. When attempting a move, the functions in game.py can ensure that the column is indeed valid by making sure the column is not already full. This is used in app.py to make ensure valid input. To simulate pieces falling with gravity, game.py has a function that finds the lowest open row in a given column to insert the piece. The functions that check whether or not the game has been won on each move are also in our game.py file. They loop through the entire array checking for 4 in a row in the verticals, horizontals, and diagonals separately. We also use a function to check if the game has been tied. Our programmed computer bots are also written in the “game.py” file. Our easy bot just obtains all the valid moves and randomly chooses a move from those possibilities. Our medium bot is a little more advanced. The medium bot will recognize a winning spot and move there, will see if the human can win and block them if they can, and will not go somewhere if the user can win right above it. Otherwise, this bot will move randomly. Our hard bot is more advanced. The idea behind our hard bot is that it does everything the medium bot does, but it also generally tries to move near other pieces and the middle of the board with some randomness. A point system is created so that each valid move will be allotted points based on the closeness to the middle of the board and points for how many pieces will be touching that hypothetical move. The bot then makes a random move out of the potential moves that have the maximum or one less than the maximum number of points.


To create our insane bot, we repurposed the minimax algorithm from this website: (https://roboticsproject.readthedocs.io/en/latest/ConnectFourAlgorithm.html). We tried a number of times to use our own minimax algorithm with the help of ChatGPT, but found that it was prone to making mistakes. We knew we wanted to include a CPU that uses some semblance of artificial intelligence, so we decided we would rather use this code than not have an AI CPU altogether. Before we could use their code, we needed to convert the board we were using in game.py to one that ai.py could understand. The people who built the algorithm had the board flipped upside down, so we needed to do that before passing the board to the minimax function. The minimax algorithm creates decision trees for possible moves and scores each move based on the state of the game it leads to. The number of moves the bot looks ahead depends on the depth of the minimax algorithm. When we tried running the code with depth 5, it took over two seconds for each move to be made. This created an awkward phenomenon where it felt like the website had timed out. Using depth 4 almost always takes under a second, which made it more optimal for our game. Since the people who built this algorithm used a much higher depth than we did (they probably had better computing power), we had to make some changes to the way the function scored boards so that it would be harder to beat. Eventually, we came up with unique scores in evaluate_window for connecting four, three, and two pieces as well as blocking the opponent. Tweaking these numbers changed the way the computer “made decisions” by weighting different states of the game—sometimes it would be too focused on blocking that it ignored an easy win, and sometimes it would forget to block the human altogether. The numbers we came up with were the result of a few hours playing the bot, trying to make it as difficult as possible to beat using only depth 4. Interestingly, this algorithm leads to much less random games than our hard bot, since it will calculate the same “optimal” move for the same board state.

Lastly, the app.py file is where the routes that render the HTML pages are located. The history, stats, index, login, register, play_again, logout, play1, and play2 functions are in this file. The history and stats functions both retrieve data from the database and then return those values so they can be used in their respective HTML files.

The register route makes sure that that the username inputted has not been used and that the password and the confirmation match. The register page also inputs the username and hashed password value into the users table in the database. The login route ensures that a valid username and password are inputted in the text boxes before storing their information in the session. The logout route just clears the session logs the user out of their account.

The index route obtains whether the user would like to play a 1 or 2 player game and then ensures that the second account is valid if they selected the 2 player mode. If the route is accessed with a GET method it displays the survey, and if it’s accessed with a POST request it will use the data to start the game. If the single player mode is selected then it redirects to the play1 function with the correct difficulty and if the if the 2 player mode is selected then the index function redirects to the play2 function. The play2 and play1 functions are very similar. Their difference is that play2 prompts for the second users move and play1 automatically calls the function that generates the computer bot’s move as the second move. Both of these routes call the functions in the game.py file that check if the game has ended/will end and verify if moves are valid. Once the move has been made (the route is accessed with a POST request), these functions render the current board status, who’s turn it is to make a move, and whether or not the game is over to the HTML files so that they can be used to alter the display on the screen.

The play_again route is used so that after a game ends, the board can be reset back to all zeros and game_over set to False without losing track of the number of players and the login information or cpu difficulty.


The basis for our visual design is in the layout.html file. This file defines what the screen looks like and creates the buttons in the top section of our webpage. This layout is extended to our other pages to have the same visual components and prevent repetition in our code. The login page displays text boxes that takes in a username and password and then logs the user into their account. The register page displays username, password, and confirmation text boxes for the user to enter in to create an account. The stats and history HTML pages loop through the data that is returned from the functions in app.py to display these data on the screen.

The index.html file is used mainly to prompt the user for the game settings. This required a little bit of JavaScript to make certain inputs only appear when previous inputs were selected. We didn’t want CPU difficulty to be an option if the user selected 2 players, and we didn’t want the second users username and password to be required if someone was playing singleplayer, so we made these conditional inputs using JavaScript. If 1 player was clicked, the CPU difficulty question would be styled to become visible, and if 2 players was clicked, the username and password was styled to become visible. We also added a DALLE generated image of John Harvard playing Connect 4 on the homepage.

The play.html file takes in the board state passed from app.py and renders it by making a table and painting the cells red, yellow, or white based on the state of that slot in the game. This is done using Jinja to loop through and print dynamic HTML. The play.html also makes buttons appear on the top of the table that are used to select a specific column while playing. Clicking one of these buttons will send a POST request to the correct play route with the column of the intended move. If there are two players, the backend and frontend are keeping track of whose move it is so that the correct text can be displayed above the board. Game.py is able to know who should be moving since players alternate so we can reuse the make move functionality of the play route each time. Calling it twice will make it automatically go back and forth from player 1 moving to player 2 moving. When there’s one player, the play2 route will automatically make the CPUs move after the player moves by clicking the button. It’s not exactly ideal that both player1’s move and the CPU’s response show up at the second game, but delaying the CPU’s move would have required making some way of showing the human that the move is in process. If we were to start over, we would ideally design a better way of doing this so that the human could go both first and second and that the CPU’s move didn’t appear immediately. Routing and keeping track of who is player1 for stats and history is something that made this more difficult.

The CSS file uses a lot of classes and ids to specifically style different attributes and buttons. Mainly, there’s a different styling for the board table, and the tables that contain the stats and history information. The rest was used to fix the spacing and add visual cues as to who’s turn it is. For example, we made a colored circle follow the cursor of whoever’s turn it was. Lastly, we added a favicon with a connect4 board to make the tab appear prettier in our browser.
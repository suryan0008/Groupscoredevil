from telegram.ext import Updater, CommandHandler
import logging
import pymongo
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(name)

# MongoDB configuration
MONGO_URI = os.environ.get('MONGO_URI')
MONGO_DB = "game_scores"
MONGO_COLLECTION = "scores"

# Establish MongoDB connection
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Define the start function
def start(update, context):
    update.message.reply_text('Welcome to the devil x score bot!')


# Define the function to get the score of a game
def get_score(update, context):
    game = context.args[0]  # assuming the first argument is the game name
    score_data = collection.find_one({"game": game})
    if score_data:
        score = score_data["score"]
        update.message.reply_text(f'The score for {game} is {score}')
    else:
        update.message.reply_text(f'No score found for {game}')


# Define the function to display the scoreboard
def scoreboard(update, context):
    scoreboard_text = ""
    for score_data in collection.find():
        scoreboard_text += f"{score_data['game']}: {score_data['score']}\n"
    update.message.reply_text('Scoreboard:\n' + scoreboard_text)


# Define the function to add score for a game
def add_score(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("You are not authorized to use this command.")
        return
    args = context.args
    if len(args) != 2:
        update.message.reply_text("Usage: /addscore <game_name> <score>")
        return
    game = args[0]
    score = int(args[1])
    collection.update_one({"game": game}, {"$inc": {"score": score}}, upsert=True)
    update.message.reply_text(f"Score added for {game}")


# Define the function to subtract score for a game
def minus_score(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("You are not authorized to use this command.")
        return
    args = context.args
    if len(args) != 2:
        update.message.reply_text("Usage: /minusscore <game_name> <score>")
        return
    game = args[0]
    score = int(args[1])
    collection.update_one({"game": game}, {"$inc": {"score": -score}}, upsert=True)
    update.message.reply_text(f"Score subtracted for {game}")


# Function to check if the user is an admin
def is_admin(user_id):
    # Replace this with your admin user IDs check
    return user_id in [6846608545]  # Example admin user IDs


# Function to restrict commands to members only
def restricted(func):
    def wrapper(update, context):
        user_id = update.effective_user.id
        if user_id not in [6929596322]:  # Example member user IDs
            update.message.reply_text("You are not authorized to use this command.")
            return
        return func(update, context)
    return wrapper


def main():
    # Create the Updater and pass it your bot's token
    updater = Updater("7106919597:AAEInwr4HGYQT9PNipJC7acL0pWliR-XVYY", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("score", get_score))
    dp.add_handler(CommandHandler("scoreboard", scoreboard))
    dp.add_handler(CommandHandler("addscore", restricted(add_score)))
    dp.add_handler(CommandHandler("minusscore", restricted(minus_score)))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if name == 'main':
    main()

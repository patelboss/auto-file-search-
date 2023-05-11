# import telegram
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# # Initialize the Telegram bot with your API token
# bot = telegram.Bot('YOUR_API_TOKEN')

# # Define a dictionary to store the list of movies in the database
# movie_database = {}

# # Define a function to handle incoming messages
# def handle_message(update, context):
#     # Get the message text and user ID
#     message_text = update.message.text
#     user_id = update.message.chat_id
    
#     # Check if the movie is in the database
#     if message_text in movie_database:
#         # If the movie is found, send a message to the user
#         context.bot.send_message(chat_id=user_id, text=f"𝐘𝐨𝐮𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐞𝐝 𝐦𝐨𝐯𝐢𝐞 '{message_text}' 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐢𝐧 𝐨𝐮𝐫 𝐝𝐚𝐭𝐚𝐛𝐚𝐬𝐞.")
#     else:
#         # If the movie is not found, notify the user and send a message to the log channel with a "Notify user" button
#         context.bot.send_message(chat_id=user_id, text=f"𝐒𝐨𝐫𝐫𝐲, 𝐲𝐨𝐮𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐞𝐝 𝐦𝐨𝐯𝐢𝐞 '{message_text}' 𝐢𝐬 𝐧𝐨𝐭 𝐢𝐧 𝐨𝐮𝐫 𝐝𝐚𝐭𝐚𝐛𝐚𝐬𝐞. 𝐖𝐞'𝐥𝐥 𝐭𝐫𝐲 𝐭𝐨 𝐚𝐝𝐝 𝐢𝐭 𝐬𝐨𝐨𝐧!")
        
#         # Send a message to the log channel with the movie name and user ID
#         log_message = f"𝐌𝐨𝐯𝐢𝐞 '{message_text}'𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐞𝐝 𝐛𝐲 𝐮𝐬𝐞𝐫 {user_id}."
#         keyboard = [[InlineKeyboardButton("Notify user", callback_data=f"notify:{user_id}:{message_text}")]]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=log_message, reply_markup=reply_markup)

# # Define a function to handle the "Notify user" button callback
# def handle_notify_callback(update, context):
#     # Get the user ID and movie name from the callback data
#     callback_data = update.callback_query.data
#     user_id, movie_name = callback_data.split(':')[1:]
    
#     # Update the movie database with the new movie
#     movie_database[movie_name] = True
    
#     # Send a message to the user to notify them that their requested movie has been added
#     context.bot.send_message(chat_id=user_id, text=f"𝐘𝐨𝐮𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐞𝐝 𝐦𝐨𝐯𝐢𝐞 '{movie_name}' 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐚𝐝𝐝𝐞𝐝 𝐭𝐨 𝐨𝐮𝐫 𝐝𝐚𝐭𝐚𝐛𝐚𝐬𝐞. 𝐄𝐧𝐣𝐨𝐲!")
    
#     # Delete the "Notify user" button from the log message
#     context.bot.edit_message_reply_markup(chat_id=LOG_CHANNEL_ID, message_id=update.callback_query.message.message_id, reply_markup=None)

# # Start the bot and set up the message handlers
# updater = telegram.Updater('YOUR_API_TOKEN', use_context=True)
# updater.dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_message))
# updater.dispatcher.add_handler(telegram.ext.CallbackQueryHandler(handle_notify_callback))
# updater.start_polling()
# updater.idle()









# # ///////////////////////////
# from telethon import Button

# async def handle_movie_request(client, message):
#     requested_movie = message.text.strip()
#     user_id = message.from_user.id
#     log_channel_id = 123456789 # Replace with the ID of your log channel
#     database = ["Movie 1", "Movie 2", "Movie 3"] # Replace with your movie database
    
#     if requested_movie not in database:
#         # Notify user that movie is not in database
#         await client.send_message(message.chat_id, f"𝐒𝐨𝐫𝐫𝐲, 𝐲𝐨𝐮𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐞𝐝 𝐦𝐨𝐯𝐢𝐞 '{message_text}' 𝐢𝐬 𝐧𝐨𝐭 𝐢𝐧 𝐨𝐮𝐫 𝐝𝐚𝐭𝐚𝐛𝐚𝐬𝐞. 𝐖𝐞'𝐥𝐥 𝐭𝐫𝐲 𝐭𝐨 𝐚𝐝𝐝 𝐢𝐭 𝐬𝐨𝐨𝐧!")
#         # Send message to log channel
#         button_data = f"notify_user:{user_id}:{requested_movie}"
#         notify_button = Button.inline("Notify User", data=button_data)
#         await client.send_message(log_channel_id, f"User {user_id} requested {requested_movie}.", buttons=notify_button)
#     else:
#         # Movie is in database, do nothing
#         return
    
# async def handle_callback(client, callback_query):
#     data = callback_query.data
#     if data.startswith("notify_user"):
#         _, user_id, movie = data.split(":")
#         # Send message to user
#         await client.send_message(int(user_id), f"𝐘𝐨𝐮𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐞𝐝 𝐦𝐨𝐯𝐢𝐞 {movie} 𝐢𝐬 𝐧𝐨𝐰 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐢𝐧 𝐨𝐮𝐫 𝐝𝐚𝐭𝐚𝐛𝐚𝐬𝐞!")
#         # Delete callback query message
#         await callback_query.answer()
#         await callback_query.delete()

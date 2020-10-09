import discord
from discord.ext import commands
import json
import random
import os
import users
import helpercmds

token = os.environ['TOKEN']
client = commands.Bot(command_prefix=".")
subjects = ["chem", "phys"]
questions = users.questions
question_ongoing = False

# just for my convenience
correct_emoji = ":white_check_mark:"
wrong_emoji = ":no_entry_sign:"

@client.event
async def on_ready():
    global question_ongoing
    print("cum")
    question_ongoing = False # this variable helps to prevent duplicate qns
    players = users.read_from_dontpad()


def generate_question(question_list, subject):
    question_generated = random.choice(question_list)
    question_list.remove(question_generated)
    if len(question_list) == 0:
        question_list = questions["questions"][0][subject]
    return question_generated, question_list


@client.command()
async def question(ctx, subject=None, duration=None):
    global question_ongoing
    if not question_ongoing:

        # check if subject is valid
        if subject not in subjects:
            await ctx.send("Please input a valid subject!")
            return
        
        # check if duration is valid
        if duration is not None:
            try: 
                duration = int(duration)
                num_questions = duration
                original_author = ctx.author 
            except: # this will trigger if duration cannot be turned into an int (i.e. it is invalid)
                await ctx.send("Please input a valid duration!")
                return

        question_ongoing = True 
        questions_list = questions["questions"][0][subject]
        correct_answers = 0
        question_counter = 1

        while question_ongoing:

            answer_submitted = False
            question_generated, questions_list = generate_question(questions_list, subject)

            await ctx.send(f"Question **{question_counter}:**\n{question_generated['image']}")

            while not answer_submitted:
                msg = await client.wait_for('message', check=lambda message: message.author != client.user)
                answer = msg.content.upper().strip(" ")

                if answer == ".EXIT":
                    question_ongoing = False
                    await ctx.send("Session ended. Thanks for using the bot!")
                    break

                if not answer[0] == ".":
                    continue # only accept commands with "." in the name. this is separate to avoid spamming the channel with "Invalid answers!"
                
                if not helpercmds.answer_validator(subject, answer):
                    if ".QUESTION" not in answer: # edge case: someone asks for a question while a question is ongoing
                        await ctx.send("Invalid answer!")
                    continue

                if duration is not None: # do a check for duration
                    if not msg.author == original_author:
                        await ctx.send("A private session is ongoing! Please wait for it to end first.")
                        continue
                
                # now start to check the answer
                answer_submitted = True
                question_counter += 1

                await ctx.send(f"You answered **{answer[1:]}**!")

                if answer[1:] == question_generated["correct"]:
                    await ctx.send(f"{correct_emoji} You were correct! {correct_emoji}")
                    question_correct = 1
                    
                else:
                    await ctx.send(f"{wrong_emoji} You were wrong! {wrong_emoji}\nThe answer was **{question_generated['correct']}**.")
                
                correct_answers += question_correct

                # data storage
                player_id = msg.author.id
                users.add_player_score(player_id, subject, question_generated["tags"], question_correct == 1)
                users.write_to_dontpad()


                if duration is not None: # slowly count down
                    duration -= 1
                    if duration == 0:
                        score = correct_answers / num_questions * 100 # format as percentage
                        # stop the session
                        await ctx.send(f"Session done!\n**{num_questions}** questions answered.\n**{correct_answers}** correct answers.\nScore: **{score:.2f}**\nJiayou!")
                        question_ongoing = False
                        break

    else:
        await ctx.send("A session is currently ongoing!\nDo **.exit** to quit the current session.")
        return


def emoji(percentage):
    if 75 <= percentage and percentage <= 100:
        return ":green_circle:"
    elif 50 <= percentage and percentage <= 100:
        return ":yellow_circle:"
    elif 0 <= percentage  and percentage <= 50:
        return ":red_circle:"


@client.command()
async def stats(ctx):
    player_id = ctx.author.id
    player_stats = users.get_stats(player_id)

    if player_stats is None:
        await ctx.send("You have not answered any questions yet!")
        return
    
    # get the string
    # save it as a list then join with an "\n"
    string_list = [f"Stats for **{ctx.message.author.display_name}**"]
    for subject in player_stats:
        string_list.append(f"**{subject}**:")
        for topic in player_stats[subject]:
            percentage = topic['right']/ (topic['right'] + topic['wrong']) * 100 # percentage of questions in the topic that you got right
            emojis = emoji(percentage)
            string_list.append(f"{topic['tag']}: {emojis}  **{percentage:.2f}**%")
    await ctx.send("\n".join(string_list))

client.run(token)

import discord
from discord.ext import commands
import json
import random
import os
import users
import helpercmds

token = 'NzYwODM4MDQ4MzAwMjY5NTg4.X3R3pg.wruoiMk68xFfLe_qTjDAAMi3Qto' # os.environ['TOKEN']
client = commands.Bot(command_prefix=".")
subjects = ["chem", "phys", "bio"]
questions = users.questions
question_ongoing = False

# just for my convenience
correct_emoji = ":white_check_mark:"
wrong_emoji = ":no_entry_sign:"

@client.event
async def on_ready():
    global question_ongoing
    print("Ready.")
    question_ongoing = False # this variable helps to prevent duplicate qns


def generate_question(questions_list, subject, tag=None):
    warning = False
    question_generated = random.choice(questions_list)
    questions_list.remove(question_generated)
    if len(questions_list) == 0:
        questions_list = questions["questions"][0][subject]
        if tag is not None:
            warning = True
            questions_list = [question for question in questions["questions"][0][subject] if tag in question["tags"]]
    return question_generated, questions_list, warning


@client.command()
async def question(ctx, subject=None, duration=None, tag=None):
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
                if duration <= 0:
                    raise ValueError
                num_questions = duration
                original_author = ctx.author
            except: # this will trigger if duration cannot be turned into an int (i.e. it is invalid)
                await ctx.send("Please input a valid duration!")
                return

        question_ongoing = True 
        # check if tag is valid
        if tag is not None: 
            questions_list = [question for question in questions["questions"][0][subject] if tag in question["tags"]]
            if len(questions_list) == 0:
                await ctx.send(f"Tag {tag} is invalid! Either you misspelled the tag or that tag has not been added yet. Sorry!")
                return
        else:
            questions_list = questions["questions"][0][subject]
        correct_answers = 0
        question_counter = 1

        while question_ongoing:

            answer_submitted = False
            question_generated, questions_list, warning = generate_question(questions_list, subject)
            if warning:
                await ctx.send(f"Ran out of questions. Bank has been refreshed. You may see some repeated questions.")

            await ctx.send(f"Question **{question_counter}:**\n{question_generated['image']}")

            while not answer_submitted:
                msg = await client.wait_for('message', check=lambda message: message.author != client.user)
                answer = msg.content.upper().strip(" ")

                if answer == ".EXIT":
                    question_ongoing = False
                    await ctx.send("Session ended. Thanks for using the bot!")
                    break
                
                try:
                    if not answer[0] == ".":
                        continue # only accept commands with "." in the name. this is separate to avoid spamming the channel with "Invalid answers!"
                except:
                    continue # the bot breaks whenever something that isn't a string (images, etc) are inputted, this fixes that.

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
                    question_correct = 0
                
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


# assigns an emoji to each percentage, this is displayed in stats.
def emoji(percentage):
    if 75 <= percentage and percentage <= 100:
        return "<:a1:765211756704301086>"
    elif 70 <= percentage and percentage < 75:
        return "<:a2:765214881007009792>"
    elif 65 <= percentage and percentage < 70 :
        return "<:b3:765214880319406102>"
    elif 60 <= percentage and percentage < 65 :
        return "<:b4:765214880869253160>"
    elif 55 <= percentage and percentage < 60 :
        return "<:c5:765219041752121364>"
    elif 50 <= percentage and percentage < 55 :
        return "<:c6:765219041483948105>"
    elif 45 <= percentage and percentage < 50:
        return "<:d7:765219041160724533>"
    elif 40 <= percentage and percentage < 45:
        return "<:e8:765219041353662485>"
    elif percentage < 40:
        return "<:f9:765219041580417034>"
    return ""

@client.command()
async def stats(ctx, subject=None):
    player_id = ctx.author.id
    player_stats = users.get_stats(player_id)
    total_stats = users.get_player(player_id)
    if player_stats is None:
        await ctx.send("You have not answered any questions yet!")
        return
    
    # get the string
    # save it as a list then join with an "\n"
    string_list = [f"Stats for **{ctx.message.author.display_name}**"]

    # get overall stats:
    try:
        if subject not in subjects:
            raise ValueError
        string_list.append(f"**{subject}**:")
        subject_right = 0
        subject_wrong = 0
        for topic in player_stats[subject]:
            right, wrong = topic['right'], topic['wrong']
            percentage = right / (right + wrong) * 100 # percentage of questions in the topic that you got right
            subject_right += right
            subject_wrong += wrong
            emojis = emoji(percentage)
            string_list.append(f"{topic['tag']}: {emojis} **{percentage:.2f}**%")
        subject_qns = subject_right + subject_wrong
        subject_percentage = subject_right / subject_qns * 100
        subject_emoji = emoji(subject_percentage)
        string_list.insert(2, f"---")
        string_list.insert(2, f"Questions answered wrongly: **{subject_wrong}**")
        string_list.insert(2, f"Questions answered correctly: **{subject_right}**")
        string_list.insert(2, f"Total {subject} questions answered: **{subject_qns}**")
        string_list.insert(2, f"Percentage: **{subject_percentage:.2f}%** {subject_emoji}")


    except:
        total_qns, right_qns, wrong_qns = total_stats["number_right"] + total_stats["number_wrong"], total_stats["number_right"], total_stats["number_wrong"]
        string_list.append(f"Total questions answered: **{total_qns}**")
        string_list.append(f"Questions answered correctly: **{right_qns}**")
        string_list.append(f"Questions answered wrongly: **{wrong_qns}**")
        total_percentage = right_qns / total_qns * 100
        total_emoji = emoji(total_percentage)
        string_list.append(f"Percentage: **{total_percentage:.2f}%** {total_emoji}")
    await ctx.send("\n".join(string_list))

client.run(token)

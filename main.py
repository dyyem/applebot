import discord
from discord.ext import commands
import json
import random
import os
from boto.s3.connection import S3Connection

token = os.environ['TOKEN']

client = commands.Bot(command_prefix=".")
correct = ":white_check_mark:"
wrong = ":negative_squared_cross_mark:"
valid_subjects = ["chem", "phys"]
questions = json.load(open("questions.json"))

no_duplicates = False
continuing = True
question_sent = False


@client.event
async def on_ready():
    print("cum")


@client.command()
async def question(ctx, subject=None):
    global question_sent
    global no_duplicates
    global continuing
    question_sent, continuing = False, True
    if not no_duplicates:
        no_duplicates = True
        if subject not in valid_subjects:
            await ctx.send("Please input a valid subject!")

        else:
            questions_list = questions["questions"][0][subject]
            while continuing:

                if question_sent is False:
                    question_sent = True
                    qn = random.choice(questions_list)
                    if len(questions_list) == 0:
                        questions_list = questions["questions"][0][subject]
                    questions_list.remove(qn)
                    await ctx.send(qn["image"])
                    answer = None

                    # this is for mcq questions
                    while answer not in [".A", ".B", ".C", ".D"]:
                        msg = await client.wait_for('message', check=lambda message: message.author != client.user)
                        answer = msg.content.upper().strip(" ")

                        if answer in [".A", ".B", ".C", ".D"]:
                            await ctx.send(f"You answered **{answer[1:]}**!")

                            if answer[1:] == qn["correct"]:
                                await ctx.send(f"{correct} **Correct!** {correct}")
                            else:
                                await ctx.send(f"{wrong} **Wrong!** {wrong}\nThe correct answer was **{qn['correct']}**\nTags: {qn['tags']}")
                            question_sent = False

                        elif answer == ".EXIT":
                            continuing = False
                            no_duplicates = False
                            await ctx.send("Session ended. Thanks for using the bot!")
                            break
                        
                        elif answer == ".INFO":
                            identity = qn["id"]
                            await ctx.send(f"id: {identity}")
                
                elif question_sent:
                    await ctx.send("There is already a question!")


client.run(token)

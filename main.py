import discord
from discord.ext import commands
import json
import random

# storage conventions:
# so basically each qn is stored inside that questions.json
# we have the name of the subject
# we have an ID - (school, year, question number in that order)
# we have an imgur link to the photo - this is what will be posted
# we have a "correct option"
# and we have tags, showing which topic the question belongs to. like separation techniques for chem.
# i realize now that this should be in github docs or whatever? but i don't know how to use github

client = commands.Bot(command_prefix=".")
correct = ":white_check_mark:"
wrong = ":negative_squared_cross_mark:"
question_sent = False
valid_subjects = ["chem", "phys"]
questions = json.load(open("questions.json"))
continuing = True

@client.event
async def on_ready():
    print("cum")

@client.command()
async def question(ctx, subject = None):
    global question_sent
    global continuing
    question_sent, continuing = False, True
    if subject not in valid_subjects:
        await ctx.send("Please input a valid subject!")

    else:
        while continuing:

            if question_sent is False:
                question_sent = True
                qn = random.choice(questions["questions"][0][subject])
                await ctx.send(qn["image"])
                answer = None

                while answer not in ["A", "B", "C", "D"]:
                    msg = await client.wait_for('message', check=lambda message: message.author != client.user)
                    answer = msg.content.upper().strip(" ")

                    if answer in ["A", "B", "C", "D"]:
                        await ctx.send("You answered **%s**!" % answer)

                        if answer == qn["correct"]:
                            await ctx.send("%s **Correct!** %s" % (correct, correct))
                        else:
                            await ctx.send("%s **Wrong!** %s\nThe correct answer was **%s.**" % (wrong, wrong, qn["correct"]))
                        question_sent = False

                    elif answer == "EXIT":
                        continuing = False
                        await ctx.send("Session ended. Thanks for using the bot!")
                        break

                    else:
                        await ctx.send("Please input a valid answer!")

            elif question_sent:
                await ctx.send("There is already a question!")

client.run('NzYwODM4MDQ4MzAwMjY5NTg4.X3R3pg.1e6W2LONLmawQJ7ilyx68XpKC_g')
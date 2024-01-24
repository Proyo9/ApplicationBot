import discord
from dotenv import load_dotenv
import os
import bot_config
import updater

config = bot_config.config
applications = bot_config.applications

version = "1.0.0"  # DO NOT CHANGE

bot = discord.Bot()

os.system('cls')
print("Starting bot...")
if config['auto_update']:
    print("Checking for updates...")
    onLatest = updater.check(version, "main")
    onLatestConfig = updater.check(bot_config.version, "bot_config")
    onLatestUpdater = updater.check(updater.updater_version, "updater")
else:
    onLatest = True

bot = discord.Bot()
load_dotenv('.env')

class ApplicationModal(discord.ui.Modal):
    def __init__(self, title, application_questions, **kwargs):
        super().__init__(title=title, **kwargs)
        self.title = title

        for question_key in application_questions.keys():
            question = application_questions[question_key]
            style = discord.InputTextStyle.short
            if question['length'] == "long":
                style = discord.InputTextStyle.long
            required = question['required']
            placeholder = question['placeholder']
            self.add_item(discord.ui.InputText(label=question_key, placeholder=placeholder, style=style, required=required))

    async def callback(self, interaction: discord.Interaction):
        application_name = self.title.replace(" Application", "")
        user = interaction.user
        guild = interaction.guild
        catagory = guild.get_channel(config['application_catagory'])
        channel = await guild.create_text_channel(f"{user.name}-{application_name}", category=catagory)
        await channel.edit(topic=f"{user.id}")
        await channel.set_permissions(user, read_messages=True, send_messages=True)
        await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
        await channel.set_permissions(guild.get_role(config['application_team']), read_messages=True, send_messages=True)

        answers = {}
        for item in self.children:
            answers[item.label] = item.value

        embed = discord.Embed(title=f"{application_name} Application", description=f"Application by {user.mention}", color=discord.Color.green())
        for answer_key in answers.keys():
            embed.add_field(name=answer_key, value=answers[answer_key], inline=False)
        await channel.send(embed=embed, view=ApplicationButtons())
        await channel.send(config['messages']['application_new'])
        await interaction.response.send_message(config['messages']['application_sent'], ephemeral=True)

class ApplyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply", style=discord.ButtonStyle.success, custom_id="apply_button")
    async def button_callback(self, button, interaction):
        message = await interaction.channel.fetch_message(interaction.message.id)
        if message.embeds:
            embed_title = message.embeds[0].title
            application = embed_title.replace(" Application", "")
            if not canApply(message.guild, interaction.user, application):
                await interaction.response.send_message(f"You have reached the maximum amount of {application} Applications.", ephemeral=True)
                return
            if applications[application]['enabled']:
                await interaction.response.send_modal(ApplicationModal(title=embed_title, application_questions=applications[application]['questions']))
            else:
                await interaction.response.send_message("This application is not accepting responses.", ephemeral=True)
        else:
            await interaction.response.send_message("Could not find application.", ephemeral=True)

class ApplicationButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, custom_id="accept_button")
    async def accept(self, button, interaction):
        app_team = config['application_team']
        if app_team in [role.id for role in interaction.user.roles]:
            applicant = int(interaction.channel.topic)
            acceptMessage = config['messages']['application_accepted'].replace("{user}", f"<@{applicant}>")
            await interaction.response.send_message(acceptMessage, view=DeleteButton())
        else:
            await interaction.response.send_message("You do not have permission to change the status of this application.", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, custom_id="deny_button")
    async def decline(self, button, interaction):
        app_team = config['application_team']
        if app_team in [role.id for role in interaction.user.roles]:
            applicant = int(interaction.channel.topic)
            acceptMessage = config['messages']['application_denied'].replace("{user}", f"<@{applicant}>")
            await interaction.response.send_message(acceptMessage, view=DeleteButton())
        else:
            await interaction.response.send_message("You do not have permission to change the status of this application.", ephemeral=True)

class DeleteButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Delete Application", style=discord.ButtonStyle.danger, custom_id="delete_button")
    async def button_callback(self, button, interaction):
        await interaction.channel.delete()

def canApply(guild: discord.Guild, user: discord.User, application_name: str):
    max = applications[application_name]['max_applications']
    application_name = application_name.lower()
    if max == 0:
        return True
    catagory = guild.get_channel(config['application_catagory'])
    channels = catagory.channels
    user_applications = 0
    for channel in channels:
        if channel.name.startswith(f"{user.name}-{application_name}"):
            user_applications += 1
    return not user_applications >= max

@bot.event
async def on_ready():
    os.system('cls')
    bot.add_view(ApplyButton())
    bot.add_view(ApplicationButtons())
    bot.add_view(DeleteButton())
    botname = bot.user.name
    print(f'{botname} is now ONLINE.')

application_choices = []
for application in applications:
    if applications[application]['enabled']:
        application_choices.append(application)

@bot.slash_command(name="send", description="Send the application message in the channel.")
@discord.option(name="application", description="Which application do you want to start?", required=True, choices=application_choices)
async def send(ctx: discord.ApplicationContext, application: str):
    if ctx.author.guild_permissions.manage_guild:
        channel = ctx.channel
        embed = discord.Embed()
        embed.title = f"{application} Application"
        embed.description = applications[application]['description']
        embed.color = discord.Color.green()
        await channel.send(view=ApplyButton(), embed=embed)
        await ctx.respond("Application message sent.", ephemeral=True)
    else:
        await ctx.respond("You do not have permission to use this command.", ephemeral=True)

if config['apply_command']:
    @bot.slash_command(name="apply", description="Start the application.")
    @discord.option(name="application", description="Which application do you want to start?", required=True, choices=application_choices)
    async def apply(ctx: discord.ApplicationContext, application: str):
        print(canApply(ctx.guild, ctx.author, application))
        if not canApply(ctx.guild, ctx.author, application):
            await ctx.respond(f"You have reached the maximum amount of {application} Applications.", ephemeral=True)
            return
        application_questions = applications.get(application, {}).get("questions", {})
        modal = ApplicationModal(title=f"{application} Application", application_questions=application_questions)

        await ctx.send_modal(modal)

if onLatest and onLatestConfig and onLatestUpdater:
    bot.run(os.getenv('TOKEN'))
else:
    doupdate = None
    while doupdate != 'y' or 'n':
        doupdate = input("Would you like to automatically update? (y/n): ")
        if doupdate == 'y':
            if not onLatestConfig:
                updater.update('bot_config')
            if not onLatestUpdater:
                updater.update('updater')
            if not onLatest:
                updater.update('main')
            break
        elif doupdate == 'n':
            print("Continuing start... (This may cause errors)")
            bot.run(os.getenv('TOKEN'))
        else:
            continue

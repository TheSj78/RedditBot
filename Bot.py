from asyncio import sleep
import asyncio
import discord
import praw
import os

c_id = os.getenv('CLIENT_ID')
c_secret = os.getenv('CLIENT_SECRET')
b_token = os.getenv('BOT_TOKEN')


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
reddit = praw.Reddit(client_id = c_id, client_secret = c_secret, user_agent = 'Discord Bot', check_for_async = False)
setOfUsersTexted = set()
activeUsers = set()
PREFIX = '!'

@client.event
async def on_ready():
    print('\n\nLogged in as {0.user}'.format(client) + '\n\n')

@client.event
async def on_message(message):
    await client.change_presence(activity=discord.Game(name="with your mom"))

    if message.author.id == 711351178146873344: 
        return

    if not isinstance(message.channel, discord.DMChannel):
        if message.author == client.user:
            return

        if message.content.startswith(PREFIX):
            await doStuff(message)
    else:
        if message.author == client.user:
            return
        
        await client.get_channel(958147241166667816).send('<@' + str(message.author.id) + '> sent you this: \n > ' + message.content)
        # await client.get_channel(958539212712476683).send('<@' + str(message.author.id) + '> sent you this: \n > ' + message.content)

async def doStuff(message):
    message.content = message.content[len(PREFIX):].lower() #removing prefix
    
    if message.content.startswith('meme'):
        await sendMeme(message)
    elif message.content.startswith('help'):
        await sendHelp(message)
    elif message.content.startswith('clear'):
        await clearMessages(message)
    # elif message.content.startswith('dm'):
    #     await (message)
    elif message.content.startswith('reddit'):
        await redditStuff(message)
    elif message.content.startswith('list'):
        await listUsers(message)
    elif message.content.startswith('deletedm'):
        await deleteDM(message)
    if message.content.startswith('spamdm'):
        await spamDM(message)
    if message.content.startswith('spam') and message.author.id == 759194758890913802:
        await spam(message)

async def spamDM(message):
    if not message.author.id == 759194758890913802:
        await message.reply('ask a mod to do that')
        return

    try:
        if (message.content.split(' ').__len__() > 1):
            try:
                user = await client.fetch_user(message.content.split(' ')[1])
            except:
                user = message.mentions[0]

            string = message.content.split(' ')[2:]
            
            for i in range(0, 150):
                await user.send('<@' + str(user.id) + '> ' + ' '.join(string))
                await sleep(0.5)
            
            await message.add_reaction('👍')
            await sleep(2)
        else:
            await message.reply('Please enter a valid message and user to send!')
    except Exception as e:
        await message.reply('An Error Occured! ' + str(e))

    await message.clear_reactions()

async def sendMeme(message):
    await message.add_reaction('<:loading:957070740262371348>')
    if message.content.split(' ').__len__() > 1:
        amount = int(message.content.split(' ')[1])+1
        if amount > 10:
            amount = 10
        elif amount < 2:
            amount = 2
    else:
        amount = 3

    MESSAGE = await message.channel.send('Getting posts...')

    for meme in reddit.subreddit('memes').hot(limit=amount):
        if (meme.stickied == False and meme.over_18 == False):
            embed = discord.Embed (title = meme.title, url = meme.url, color = discord.Color.blue())
            embed.set_image(url=meme.url)
            embed.set_author(name=meme.author, url='https://reddit.com/u/' + str(meme.author), icon_url=meme.author.icon_img)
            embed.set_footer(text= '👍' + meme.ups.__str__() + ' | ' + '💬' + meme.num_comments.__str__())
            
            await message.clear_reactions()
            MESSAGE = await MESSAGE.edit(embed=embed, content='')

            await MESSAGE.add_reaction('➡️')
            await sleep(1)
            
            reac = await MESSAGE.channel.fetch_message(MESSAGE.id)
            
            while reac.reactions[0].count == 1:
                await sleep(2)
                reac = await MESSAGE.channel.fetch_message(MESSAGE.id)

            await MESSAGE.clear_reactions()
            await message.add_reaction('<:loading:957070740262371348>')

    await MESSAGE.delete()
    await message.reply('Memes sent!')
    await message.clear_reactions()

async def clearMessages(message):
    if message.author.guild_permissions.manage_messages:
        try:
            await message.channel.purge(limit=int(message.content[6:]))
            msg = await message.channel.send('Messages deleted!')
            await sleep(2)
            await msg.delete()
        except Exception as e:
            await message.reply('An error occured :( ' + str(e))
    else:
        await message.reply('You do not have the required permissions to do that!')     

async def sendHelp(message):
    await message.add_reaction('<:loading:957070740262371348>')

    embed = discord.Embed(title='Help', description='\n'.join([
        '```',
        '!meme [amount]',
        '!help',
        '!clear [amount]',
        '!dm [user] [message]',
        '!reddit [subreddit] [amount] [sort]',
        '!list',
        '```'
    ]), color=discord.Color.blue())
    await message.clear_reactions()

    await message.reply(embed=embed)

async def redditStuff(message):
    if activeUsers.__contains__(message.author.id):
        await message.reply('You already have a message open!')
        return
    else:
        activeUsers.add(message.author.id)
        
        await message.add_reaction('<:loading:992213026147156090>')

        if message.content.split(' ').__len__() > 1:
            subreddit = message.content.split(' ')[1]
            await message.add_reaction('<:loading:992213026147156090>')
        else:
            await message.reply('Please enter a subreddit!')
            activeUsers.remove(message.author.id)
            return

        if reddit.subreddit(subreddit) is None:
            await message.reply('That subreddit does not exist!')
            activeUsers.remove(message.author.id)
            return

        try:
            if message.content.split(' ').__len__() > 2:
                amount = int(message.content.split(' ')[2])+1
                if amount > 10: 
                    amount = 10
                elif amount < 2: 
                    amount = 2
            else:
                amount = 3
        except:
            await message.reply('Please enter a valid amount!')
            activeUsers.remove(message.author.id)
            return

        if message.content.split(' ').__len__() > 3:
            sort = message.content.split(' ')[3]
            if sort not in ['hot', 'new', 'rising', 'controversial', 'top']:
                message.reply('Invalid sort type, defaulting to hot!')
                sort = 'hot'
        else:
            sort = 'hot'

        if reddit.subreddit(subreddit).over18:
            await message.reply('inappropriate subreddit smh')
            activeUsers.remove(message.author.id)
            return

        MESSAGE = await message.channel.send('Getting posts...')        

        try:
            for post in getattr(reddit.subreddit(subreddit), sort)(limit=amount):
                if (post.stickied == False):
                    embed = discord.Embed (title = post.title, url = post.url, description = post.selftext, color = discord.Color.blue())
                    ourUrl = post.url
                    string = ''
                    if post.is_video:
                        ourUrl = 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Trollface_non-free.png/220px-Trollface_non-free.png'
                        string = ' | Can\'t display because post is a video L'
                    embed.set_image(url=ourUrl)
                    embed.set_author(name=post.author, url='https://reddit.com/u/' + str(post.author), icon_url=post.author.icon_img)
                    embed.set_footer(text= '👍' + post.ups.__str__() + ' | ' + '💬' + post.num_comments.__str__() + string)

                    await message.clear_reactions()
                    MESSAGE = await MESSAGE.edit(embed=embed, content='')

                    await MESSAGE.add_reaction('➡️')
                    await sleep(1)

                    try:
                        await client.wait_for('reaction_add', timeout=30.0, check=lambda reaction, user: user == message.author and reaction.emoji == '➡️')
                    except asyncio.TimeoutError:
                        await message.reply('Timed out!')
                        MESSAGE.clear_reactions()
                        activeUsers.remove(message.author.id)
                        return

                    await MESSAGE.clear_reactions()
                    await message.add_reaction('<:loading:992213026147156090>')

            await MESSAGE.delete()
            await message.reply('Posts sent!')
            await message.clear_reactions()
        except Exception as e:
            await message.reply('An Error Occured! ' + str(e))
            activeUsers.remove(message.author.id)
            await message.clear_reactions()

        activeUsers.remove(message.author.id)


    await message.clear_reactions()

async def listUsers(message):
    await message.add_reaction('<:loading:957070740262371348>')
    embed = discord.Embed(title='Users Texted', description='\n'.join(setOfUsersTexted), color=discord.Color.from_rgb(255, 255, 255))
    await message.channel.send(embed=embed)
    await message.clear_reactions()

async def deleteDM(message):
    await message.add_reaction('<:loading:957070740262371348>')
    if message.content.split(' ').__len__() > 1:
        try:
            user = await client.fetch_user(message.content.split(' ')[1])
        except:
            user = message.mentions[0]
        
        channel = await user.create_dm()
        async for msg in channel.history():
            if msg.author == client.user:
                await msg.delete()
        await message.reply('Messages deleted!')
        await message.clear_reactions()
        await message.add_reaction('👍')
        await sleep(2)
    else:
        await message.reply('Please enter a valid user to delete their DM!')
    await message.clear_reactions()

async def spam(message):
    channel = client.get_channel(957350769961611354)
    
    for i in range(0, 150):
        await channel.send('<@' + str(711351178146873344) + '>, your bot sucks. <:troll:958540996780654592> <:troll:958540996780654592>')
        await sleep(0.5)

    await message.add_reaction('👍')
    
client.run(b_token)
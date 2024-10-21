import os
import asyncio
import traceback

from dotenv import load_dotenv
from datetime import datetime

from discord import File, Game, Embed, Intents
from discord.ext import commands

from services.crawlService import CrawlService
from plugins.saveThumbnail import SaveThumbnailPlugin

load_dotenv()

bot = commands.Bot(command_prefix="wr!", intents=Intents.all(), application_id=os.getenv("DISCORD_CLIENT_ID"))
bot.remove_command("help")

crawlService = CrawlService()
saveThumbnailPlugin = SaveThumbnailPlugin()


async def load_extensions():
    print("------------------------------------")

    directory_prefix = "." if os.path.exists("cogs") else "src"

    for file in os.listdir(os.path.join(directory_prefix, "cogs")):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"cogs.{file[:-3]} ({file}) ✅")
            except:
                print(f"cogs.{file[:-3]} ({file}) ❌ -> {traceback.format_exc()}")

    print("------------------------------------")


@bot.event
async def on_ready():
    print(f"🔌 {bot.user} ({bot.user.id}) is now syncing command with Discord...")
    # await bot.tree.sync()

    print(f"🚀 {bot.user} ({bot.user.id}) is ready!")

    await bot.change_presence(activity=Game(name="Waktaverse Reactions 팀 운영 지원"))

    print("------------------------------------")

    try:
        channel = bot.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))

        while True:
            crawled = await crawlService.checkForNewPosts()

            for post in crawled:
                thumbnail = saveThumbnailPlugin.save_thumbnail(post.thumbnail)
                attachment = File(thumbnail, filename=thumbnail.split("/")[-1])

                embed = Embed(
                    title=post.subject,
                    type="article",
                    url=post.url,
                    description=f"[같이보기 링크]({post.url})",
                    timestamp=post.posted_at,
                )
                embed.set_image(url=f"attachment://{thumbnail.split("/")[-1]}")

                await channel.send(file=attachment, embed=embed)
                saveThumbnailPlugin.remove_thumbnail(thumbnail)

            await asyncio.sleep(60 * 5)
    except:
        print("Failed to crawl posts from Naver Cafe.")
        traceback.print_exc()

        try:
            channel = bot.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
            embed = Embed(
                title=":warning: 크롤링에 문제가 발생했습니다.",
                type="article",
                description=f"```{traceback.format_exc()}```",
                colour=16711680,
                timestamp=datetime.now(),
            )

            await channel.send(embed=embed)
        except:
            print("Failed to send error message to Discord channel.")
            traceback.print_exc()


async def main():
    async with bot:
        await bot.load_extension("jishaku")
        await load_extensions()

        await bot.start(os.getenv("DISCORD_TOKEN"))


asyncio.run(main())

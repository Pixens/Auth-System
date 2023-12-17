import requests
import discord
import yaml
import sys
import os

from logger import Logger


config = yaml.safe_load(open("./config.yml", "r"))
whitelisted = open("whitelist.txt", "r").read().splitlines()
activity = discord.Activity(type=discord.ActivityType.listening, name=config['bot_status'])
bot = discord.Bot(command_prefix="*", activity=activity, status=discord.Status.online)
headers = {
    "Authorization": "ewogICAgInVzZXJuYW1lIjogIlBpeGVucyIsCiAgICAicm9sZSI6ICJPd25lciIsCiAgICAiYXV0aG9yaXphdGlvbl90b2tlbiI6ICIyNDdhNGEyMDU5N2JkOWFiNzEzMTgxMTExYjE0MDYxNDcyYzQwMmI2MTVhMTc1M2ZlZjdkMTAyOWEyYzQxYTIxIgogIH0="
}
apps_request = requests.get("https://auth.boostup.cc/fetch-apps", headers=headers)
if apps_request.json()["success"]:
    apps = apps_request.json()["data"]
else:
    Logger.error('<!>', 'Failed to fetch applications.', {'error': apps_request.json()["message"]})
    sys.exit()

app_names = [app["app_name"] for app in apps]
duration_map = {
    "Lifetime": 36525,
    "1 Year": 365,
    "1 Month": 30,
    "1 Week": 7,
    "1 Day": 1,
    "1 Hour": 0.42
}

normal_color = "0x5780fc"
error_color = "0xf06156"


# ---General Commands---


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="reset-hwid",
    description="Resets hardware ID linked to a license key in order to use on another device."
)
async def reset_hwid(
    ctx,
    license: discord.Option(str, "License key you want to reset the hardware ID (HWID) for.", required=True)
):

    response = requests.patch("https://auth.boostup.cc/reset-hwid", json={"license_key": license}, headers=headers)
    embed = discord.Embed(
        title="HWID reset successful" if response.json()["success"] else "HWID reset failed",
        description=f"``👤`` License: ``{license}``\n``🤖`` Message: ``{response.json()['message']}``",
        color=int(normal_color, 16) if response.json()["success"] else int(error_color, 16)
    )

    await ctx.respond(embed=embed, ephemeral=True)

    if config['hwid_reset_logs_channel']:
        channel = bot.get_channel(int(config['hwid_reset_logs_channel']))
        embed.set_footer(text=f'Command ran by {ctx.author.name}')
        await channel.send(embed=embed)


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="restart-bot",
    description="Restarts the discord bot."
)
async def restart(
        ctx
):
    await ctx.respond("Restarting...", ephemeral=True)
    os.execv(sys.executable, ['python3'] + sys.argv)


# ---License Admin Commands---


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="generate-license",
    description="Generates a new license key for a tool."
)
async def generate_license(
        ctx,
        application: discord.Option(str, "Application for which the key is to be generated.", choices=app_names, required=True),
        duration: discord.Option(str, "Duration of the license.", choices=['Lifetime', '1 Year', '1 Month', '1 Week', '1 Day', '1 Hour'], required=True),
        note: discord.Option(str, "Note you want to put for the license key.", required=False)
):
    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to generate license key",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)

    else:
        payload = {
            "app_name": application,
            "duration": duration_map[duration],
            "key_mask": "Boostup-XXXXX-XXXXX",
            "note": note if note else ""
        }
        response = requests.post("https://auth.boostup.cc/create-license", json=payload, headers=headers)
        embed = discord.Embed(
            title="Successfully generated license key" if response.json()["success"] else "Failed to generate license key",
            description=f"``🔐`` License: ``{response.json()['data']['license_key'] if response.json()['success'] else None}``\n``🕒`` Expiry: ``{duration_map[duration]} day(s)``\n``🤖`` Application: ``{application}``",
            color=int(normal_color, 16) if response.json()["success"] else int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")
        await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="license-info",
    description="Generates a new license key for a tool."
)
async def fetch_license_info(
        ctx,
        license: discord.Option(str, "License key you want to get information for.", required=True)
):

    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to fetch license info",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)

    else:
        response = requests.get("https://auth.boostup.cc/license-info", json={"license_key": license}, headers=headers)
        if response.json()["success"]:
            embed = discord.Embed(
                title="Successfully fetched license info",
                description=f"``🔐`` License: ``{license}``\n``💻`` App ID: ``{response.json()['data']['app_id']}``\n``⌛️`` Duration: ``{response.json()['data']['duration']} day(s)``\n``🕒`` Expiry: ``{response.json()['data']['expires_on']}``\n``🗒️`` Note: ``{response.json()['data']['note']}``",
                color=int(normal_color, 16)
            )
        else:
            embed = discord.Embed(
                title="Failed to fetch license info",
                description=f"``🔐`` License: ``{license}``\n``⛔`` Message: ``{response.json()['message']}``",
                color=int(normal_color, 16)
            )

        await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="extend-license",
    description="Extends the time on an existing license."
)
async def extend_license(
        ctx,
        license: discord.Option(str, "License key you want to extend.", required=True),
        duration: discord.Option(str, "Duration you want to extend by.", required=True)
):
    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to extend license",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        response = requests.patch("https://auth.boostup.cc/extend-license", headers=headers, json={"license_key": license, "extension_days": duration})
        if response.json()["success"]:
            embed = discord.Embed(
                title="Successfully extended license",
                description=f"``🔐`` License: ``{license}``\n``⌛``: Extension Duration: ``{duration}``",
                color=int(normal_color, 16)
            )
        else:
            embed = discord.Embed(
                title="Failed to extend license",
                description=f"``⛔`` Message: ``{response.json()['message']}``",
                color=int(error_color, 16)
            )

        await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="delete-license",
    description="Deletes a license key."
)
async def delete_license(
        ctx,
        license: discord.Option(str, "License key you want to delete.", required=True)
):
    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to delete license",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)

    else:
        response = requests.delete("https://auth.boostup.cc/delete-license", json={"license_key": license}, headers=headers)
        if response.json()["success"]:
            embed = discord.Embed(
                title="Successfully deleted license key",
                description=f"```🔐``License: ``{license}``",
                color=int(normal_color, 16)
            )
        else:
            embed = discord.Embed(
                title="Failed to delete license key",
                description=f"```⛔``Message: ``{response.json()['message']}``",
                color=int(error_color, 16)
            )

        await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="reset-all-hwids",
    description="Resets hardware ID (HWID) for all keys in the database."
)
async def reset_all_hwids(
        ctx
):
    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to reset all HWIDs",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)

    else:
        response = requests.patch("https://auth.boostup.cc/reset-all-hwids", headers=headers)
        embed = discord.Embed(
            title="Successfully reset all HWIDs" if response.json()["success"] else "Failed to reset all HWIDs",
            description=f"``💠``Message: ``{response.json()['message']}``",
            color=int(normal_color, 16) if response.json()["success"] else int(error_color, 16)
        )

        await ctx.respond(embed=embed, ephemeral=True)


# ---Application Admin Commands---


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="create-app",
    description="Creates a new application."
)
async def create_app(
        ctx,
        name: discord.Option(str, "Name of the application you want to create.", required=True),
        version: discord.Option(str, "Version of the application you want to create.") = "1.0"
):
    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to create app",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)

    else:
        payload = {
            "app_name": name,
            "app_version": version
        }
        response = requests.post("https://auth.boostup.cc/create-app", headers=headers, json=payload)
        if response.json()["success"]:
            embed = discord.Embed(
                title="Successfully created app",
                description=f"``🪪`` App ID: ``{response.json()['data']['app_id']}``\n``📛`` App Name: ``{response.json()['data']['app_name']}``\n``🪖`` Public Secret: ``{response.json()['data']['public_secret']}``\n``💻`` App Version: ``{response.json()['data']['app_version']}``",
                color=int(normal_color, 16)
            )
        else:
            embed = discord.Embed(
                title="Failed to create app",
                description=f"``⛔`` Message: ``{response.json()['message']}``",
                color=int(error_color, 16)
            )

        await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="fetch-app",
    description="Gets information for an application."
)
async def fetch_app(
        ctx,
        application: discord.Option(str, "Application you want to get information for.", choices=app_names, required=True),
):
    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to create app",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)

    else:
        payload = {
            "app_name": application
        }
        response = requests.get("https://auth.boostup.cc//app-info", headers=headers, json=payload)
        if response.json()["success"]:
            embed = discord.Embed(
                title="Successfully fetched app",
                description=f"``🪪`` App ID: ``{response.json()['data']['app_id']}``\n``📛`` App Name: ``{response.json()['data']['app_name']}``\n``🪖`` Public Secret: ``{response.json()['data']['public_secret']}``\n``💻`` App Version: ``{response.json()['data']['app_version']}``\n``🧬`` Download: ``{response.json()['data']['download_link']}``\n``📁``: File Hash: ``{response.json()['data']['file_hash']}``",
                color=int(normal_color, 16)
            )
        else:
            embed = discord.Embed(
                title="Failed to fetch app",
                description=f"``⛔`` Message: ``{response.json()['message']}``",
                color=int(error_color, 16)
            )

        await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="update-app",
    description="Updates data of the selected app."
)
async def update_app(
        ctx,
        application: discord.Option(str, "Application you want to update data for.", choices=app_names, required=True),
        new_name: discord.Option(str, "New name for the application selected.") = str(),
        new_version: discord.Option(str, "New version for the application selected.") = str(),
        new_download_link: discord.Option(str, "New download link for the application selected.") = str(),
        new_file_hash: discord.Option(str, "New file hash for the application selected.") = str()
):
    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to create app",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)

    else:
        app_id = str()
        for app in apps:
            if app["app_name"] == application:
                app_id = app["app_id"]

        if not app_id:
            embed = discord.Embed(
                title="Failed to update app",
                description=f"``⛔`` Couldn't find corresponding app ID.",
                color=int(error_color, 16)
            )
            embed.set_footer(text="Boostup Auth Manager")

            await ctx.response(embed=embed, ephemeral=True)

        else:
            if not new_name and not new_version and not new_download_link and not new_file_hash:
                embed = discord.Embed(
                    title="Failed to update app",
                    description=f"``⛔`` No new data received.",
                    color=int(error_color, 16)
                )
                embed.set_footer(text="Boostup Auth Manager")

                await ctx.response(embed=embed, ephemeral=True)
            else:
                payload = {}
                if new_name:
                    payload["app_name"] = new_name
                if new_version:
                    payload["app_version"] = new_version
                if new_download_link:
                    payload["download_link"] = new_download_link
                if new_file_hash:
                    payload["file_hash"] = new_file_hash

                response = requests.patch(f"https://auth.boostup.cc/update-app/{app_id}", headers=headers, json=payload)
                embed = discord.Embed(
                    title="Successfully updated app" if response.json()["success"] else "Failed to update app",
                    description=f"``🫔`` Message: {response.json()['message']}",
                    color=int(normal_color, 16) if response.json()["success"] else int(error_color, 16)
                )

                await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
    guild_ids=config["guild_ids"],
    name="delete-app",
    description="Deletes selected app."
)
async def delete_app(
        ctx,
        application: discord.Option(str, "Application you want to delete.", choices=app_names, required=True)
):
    if str(ctx.author.id) not in whitelisted:
        embed = discord.Embed(
            title="Failed to delete app",
            description=f"``⛔`` You are not permitted to execute this command.",
            color=int(error_color, 16)
        )
        embed.set_footer(text="Boostup Auth Manager")

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        payload = {
            "app_name": application
        }
        response = requests.delete("https://auth.boostup.cc/delete-app", headers=headers, json=payload)
        embed = discord.Embed(
            title="Successfully deleted app" if response.json()["success"] else "Failed to delete app",
            description=f"``🫔`` Message: {response.json()['message']}",
            color=int(normal_color, 16) if response.json()["success"] else int(error_color, 16)
        )

        ctx.respond(embed=embed, ephemeral=True)


Logger.info("<+>", "Successfully started bot.")
bot.run(config['bot_token'])

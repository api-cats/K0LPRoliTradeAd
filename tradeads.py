#Hello someone /e wave
#https://github.com/K0LP7/K0LPRoliTradeAd
#Started working on this discord bot on 17/09/2025 (dd/mm) :P - k0lp
#Its a personal project but im sharing this if someone wants to use it or be inspired by it :D
#Made this bc bot from Arachnid didnt have an option to add robux :C (and few other features)
import discord
from discord.ext import commands
import json
import requests
from datetime import datetime, timedelta
import random
import asyncio

CONFIG_FILE = "config.json"

def load_config_file():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config_file(config_file):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_file, f, indent=4)

config_file = load_config_file()

urlTA = 'https://api.rolimons.com/tradeads/v1/createad'
urlIL = 'https://api.rolimons.com/items/v2/itemdetails'
urlPI = f'https://inventory.roblox.com/v1/users/{config_file["PlayerID"]}/assets/collectibles?limit=100&sortOrder=Asc'

responseIL = requests.get(urlIL)
resIL = responseIL.json()

Tag_Icons = {"upgrade": "📈 Upgrade","downgrade": "📉 Downgrade","adds": "➕ Adds","any": "📊 Any","wishlist": "🗄️ Wishlist","demand": "📊 Demand","rares": "💎 Rares","rap": "📊 Rap","robux": "💲 Robux","projecteds": "⚠️ Projecteds"}
AllTags = ["adds", "upgrade", "downgrade", "any", "wishlist", "demand", "rares", "rap", "robux", "projecteds"]

#Bot settings 
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)


#NFT command
@bot.group(name="nft", invoke_without_command=True)
async def nft(ctx):
    await ctx.send("⚠️ Use `add`, `remove`, `list` or `clear`! Use `!help nft` for more details!")

@nft.command(name="list") #NFT Embed List
async def nft_list(ctx):

    config_file = load_config_file()
    NFT_Items=[]
    NonRolimonsApiItems=0

    for NFT_List in config_file["NotForTrade"]:
        item_data = resIL["items"].get(str(NFT_List))
        if item_data:
            if item_data[1] != "": #Checks if theres an acronym and if there is it picks it
                Item_Name = item_data[1]
            else:
                Item_Name=item_data[0]# If there isnt sets item name
            Item_Value=item_data[4]
            NFT_Items.append((Item_Name, NFT_List, Item_Value))
        else:
            NonRolimonsApiItems = NonRolimonsApiItems +1
    if NonRolimonsApiItems >0:
        await ctx.send(f"❌ Rolimons API doesnt recognize {NonRolimonsApiItems} IDs in the config!")
        
    NFT_Items = sorted(NFT_Items, key=lambda x: x[2], reverse=True) #Sorts Items by value   
    NFT_Item_List = ""
    for Item_Name, NFT_List, _ in NFT_Items:
        NFT_Item_List += f"● {Item_Name} ({NFT_List})\n"
            
    nftembed = discord.Embed(
        title="🚫 Not For Trade List",
        color=0x33cc66
    )
    nftembed.add_field(name="", value=NFT_Item_List, inline=False)

    await ctx.send(embed=nftembed) #Sends embed

@nft.command(name="add") #NFT add
async def NFTAdd(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send("❌ Please provide an item ID or name to add!")
        return
    
    config_file = load_config_file()
    
    if arg.isnumeric():
        if int(arg) in config_file["NotForTrade"]:
            await ctx.send(f"❌ Item is already in NFT List.")
            return
        else:
            item_data = resIL["items"].get(str(int(arg)))
            if item_data:
                config_file["NotForTrade"].append(int(arg))
                save_config_file(config_file)  
                await ctx.send(f'✅ {arg} has been added to NFT List!')
            else:
                await ctx.send('❌ Couldnt find this ID in Rolimons API')
    else:
        for key, value in resIL["items"].items():
            if value[1].casefold() == arg.casefold() or value[0].casefold() == arg.casefold():
                if int(key) not in config_file["NotForTrade"]:
                    config_file["NotForTrade"].append(int(key))
                    save_config_file(config_file)  
                    await ctx.send(f'✅ {value[1]} has been added to NFT List!')
                    return
                else:
                    await ctx.send(f"❌ Item is already in NFT List.")
        else:
            await ctx.send('❌ Couldnt find this name in Rolimons API')
       
@nft.command(name="remove") #NFT remove
async def NFTRemove(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send('❌ Please provide an item ID or name to remove!')
        return
    
    config_file = load_config_file()
    
    if arg.isnumeric():
        if int(arg) in config_file["NotForTrade"]:
            config_file["NotForTrade"].remove(int(arg))
            save_config_file(config_file)  
            await ctx.send(f'✅ {arg} has been removed from NFT List!')
        else:
            await ctx.send('❌ Couldnt find this ID in your NFT List')
    else:
        for key, value in resIL["items"].items():
            if value[1].casefold() == arg.casefold() or value[0].casefold() == arg.casefold():
                if int(key) in config_file["NotForTrade"]:
                    config_file["NotForTrade"].remove(int(key))
                    save_config_file(config_file)  
                    await ctx.send(f'✅ {value[1]} has been removed from NFT List!')
                else:
                    await ctx.send('❌ Couldnt find this name in your NFT List')
                return
        else:
            await ctx.send('❌ Couldnt find this name in Rolimons API')

        if int(arg) not in config_file["NotForTrade"]:
            await ctx.send(f"❌ ID isnt in the NFT List.")
            return

@nft.command(name="clear") #NFT clear
async def NFTClear(ctx, *, arg: str = None):
    config_file = load_config_file()
    
    config_file["NotForTrade"].clear()
    save_config_file(config_file)
    await ctx.send("✅ Nft list has been cleared!")


#Tags command
@bot.group(name="tags", aliases=["tag"], invoke_without_command=True)
async def tags(ctx):
    await ctx.send('❌ Use `add`, `remove`, `list`, `clear` or `set`! Use `!help tags` for more details!')

@tags.command(name="list") #Tags Embed List
async def TagsList(ctx):

    tagsembed = discord.Embed(
        title="🏷️ Tags ",
        color=0x33cc66,
        description="- upgrade\n- downgrade\n- demand\n- rares\n- rap\n- robux\n- adds\n- projecteds\n- any\n- wishlist\n",
    )

    await ctx.send(embed=tagsembed) #Sends embed

@tags.command(name="add") #Tags add
async def TagsAdd(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send("❌ Forgot the tag! Use `tags list` to see list of tags.")
        return
    
    All_Of_Tags =["adds", "upgrade", "downgrade", "any", "wishlist", "demand", "rares", "rap", "robux", "projecteds"]
    if arg not in All_Of_Tags:
        await ctx.send(f"❌ Tag doesnt exist! Use `tags list` to see list of tags.")
        return

    config_file = load_config_file()

    if arg in config_file["Tags"]:
        await ctx.send(f"❌ Tag already in Tags.")
        return
    
    #Adds ID to the config
    if len(config_file["Tags"]) < 4:
        config_file["Tags"].append(arg)
        save_config_file(config_file)
        await ctx.send(f"✅ {arg} has been added to Tags")
    else:
        await ctx.send("❌ Theres 4 tags already!")

@tags.command(name="remove") #Tags remove
async def TagsRemove(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send("❌ Forgot the tag! Use `tags list` to see list of tags.")
        return
    
    config_file = load_config_file()
    
    if arg not in config_file["Tags"]:
        await ctx.send(f"❌ Tag not found in Tags.")
        return
    
    config_file["Tags"].remove(arg)
    save_config_file(config_file)
    await ctx.send(f"✅ {arg} has been removed from Tags!")

@tags.command(name="clear") #Tags clear
async def TagsClear(ctx, *, arg: str = None):
    config_file = load_config_file()
    
    config_file["Tags"].clear()
    save_config_file(config_file)
    await ctx.send("✅ Tags have been cleared!")


#Preset command        
@bot.group(name="preset", aliases=["presets"], invoke_without_command=True)
async def preset(ctx, arg1: str = None, arg2: str = None, arg3: str = None):
    if arg1 != None:
        config_file = load_config_file()
        if arg1.casefold() in config_file["Presets"]:
            if arg2.casefold() =="add":
                if len(config_file["Presets"][f"{arg1.casefold()}"]) < 4:
                    if arg3 in AllTags:
                        if arg3 not in config_file["Presets"][f"{arg1.casefold()}"]:
                            config_file["Presets"][f"{arg1.casefold()}"].append(f"{arg3.casefold()}")
                            save_config_file(config_file)
                            await ctx.send(f'✅ {arg3.casefold()} has been added to {arg1} preset!')
                        else:
                            await ctx.send(f'❌ This tag is already in {arg1} preset!')           
                    else:
                        await ctx.send('❌ Couldnt find this tag! Use `!tags list` for list of tags.')           
                else:
                    await ctx.send('❌ Theres more than 4 tags in this preset! Remove at least one to add more.')

            elif arg2.casefold() =="remove":
                if arg3 in config_file["Presets"][f"{arg1.casefold()}"]:
                    if arg3 in AllTags:
                        config_file["Presets"][f"{arg1.casefold()}"].remove(f"{arg3.casefold()}")
                        save_config_file(config_file)
                        await ctx.send(f'✅ {arg3.casefold()} has been removed from {arg1} preset!')
                    else:
                        await ctx.send('❌ Couldnt find this tag! Use `!tags list` for list of tags.')
                else:
                    await ctx.send(f'❌ This tag isnt in {arg1} preset!')

            elif arg2 == None:
                await ctx.send('❌ Use `!preset <preset> <add/remove> <tag>`! Use `!help preset` for more details.')
                
            return
        else:
            await ctx.send('❌ Use `add`, `remove`, `list` or preset you want to change! Use `!help tags presets` for more details.')

    else: 
        await ctx.send('❌ Use `add`, `remove`, `<preset>` or `list`! Use `!help preset` for more details.')

@preset.command(name="list")
async def presetlist(ctx):
    config_file=load_config_file()
    Presets=[]
    PresetList=""
    for item in config_file["Presets"]:
        Presets.append(item)
    for item in Presets:
        PresetList += f"**{item}**:\n"
        for item in config_file['Presets'][f'{item}']:
            PresetList += f"- {item}\n"

    presetembed = discord.Embed(
        title="🏷️ Tag Presets",
        color=0x33cc66,
    )
    presetembed.add_field(name="", value=PresetList, inline=True)

    await ctx.send(embed=presetembed) #Sends embed

@preset.command(name="set")
async def presetset(ctx, *, arg: str = None):
    config_file=load_config_file()
    if arg in config_file["Presets"]:
        config_file["Tags"] = config_file["Presets"][f"{arg.lower()}"]
        save_config_file(config_file)
        await ctx.send(f"✅ Tags changed to {arg.lower()} preset!")
        return
    
    elif arg not in config_file["Presets"]:
        await ctx.send(f"❌ Preset doesnt exist!")
        return
    
    await ctx.send("❌ Check `!tags set list` for list of presets!")

@preset.command(name="add") #preset add
async def presetadd(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send("❌ Forgot the parameter! Use `!help tags presets`.")
        return
    else:
        if arg not in config_file["Presets"]:
            config_file["Presets"][arg] = []
            save_config_file(config_file)
            await ctx.send(f"✅ {arg} preset has been added! Use `!preset <preset> <add/remove> <tag>` to add/remove tags.")
        else:
            await ctx.send("❌ Preset already exists! Use `!preset <preset> <add/remove> <tag>` to add/remove tags.")
    
@preset.command(name="remove") #preset remove
async def presetremove(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send("❌ Forgot the parameter! Use `!help tags presets`.")
        return
    else:
        if arg in config_file["Presets"]:
            del config_file["Presets"][arg]
            save_config_file(config_file)
            await ctx.send(f"✅ {arg} preset has been removed!")
        else:
            await ctx.send("❌ Couldnt find this preset! Use `!preset list to see all presets.")



#Config command        
@bot.command(name="config") 
async def config_command(ctx):
    config_file = load_config_file()

    responseIL = requests.get(urlIL)
    resIL = responseIL.json()

    responsePI = requests.get(urlPI)
    resPI = responsePI.json()

    configembed = discord.Embed(
        title="📋 Your Config",
        color=0x33cc66
    )

    if config_file["AutoPick"] == "false" and config_file["Top4"] == "false":
        Manual_Pick = "true"
    else:
        Manual_Pick = "false"

    #Fields
    configembed.add_field(name="Top 4", value=f"`{config_file['Top4'] }`", inline=True)  
    configembed.add_field(name="Auto Pick", value=f"`{config_file['AutoPick'] }`", inline=True)
    configembed.add_field(name="Manual Pick", value=f"`{Manual_Pick}`", inline=True)
    configembed.add_field(name="Min Value (autopick)", value=f"`{config_file['MinValue'] }`", inline=True)
    configembed.add_field(name="Demand Only", value=f"`{config_file['DemandOnly'] }`", inline=False)
    configembed.add_field(name="Time", value=f"`{int(config_file['Time']/60)} minutes`", inline=False)
    configembed.add_field(name="Robux", value=f"`{config_file['Robux'] }`", inline=False) #In life we have robux

    if config_file["AutoPick"] == "true": #Items offered Autopick
        configembed.add_field(name="✉️ Offered Items:", value="AutoPick chosen! Bot will randomly pick items", inline=False)

    Top4Items=[]
    #Items offered Top4
    if config_file['Top4'] == "true":
        for ItemsHold in resPI.get("data"):
            ItemID = ItemsHold.get("assetId")
            if ItemsHold.get("isOnHold") is True:
                continue
            if ItemID in config_file['NotForTrade']:
                continue
            item_data = resIL["items"].get(str(ItemID))
            if item_data:
                if item_data[1] != "": #Checks if theres an acronym and if there is it picks it
                    ItemName = item_data[1]
                else:
                    ItemName=item_data[0]# If there isnt sets item name
                value=item_data[4]
                rap=item_data[2]
                if config_file['DemandOnly'] == "true" and item_data[5] <= 0:#item_data[5] is demand in roli api
                    continue
                Top4Items.append((ItemID, value, ItemName))
        Top4List = [(ItemName, value) for _, value, ItemName in sorted(Top4Items, key=lambda x: x[1], reverse=True)[:4]]
        Top4FinalList = ""
        for Item_Name, value in Top4List:
            Top4FinalList += f"● {Item_Name} {value}\n"
        configembed.add_field(name="✉️ Offered Items", value=Top4FinalList, inline=False)


    if Manual_Pick == "true": #Manual pick
        Manual_Offered =[]
        if config_file["OfferedItems"]:
            for item in config_file["OfferedItems"]:
                item_data = resIL["items"].get(str(item))
                if item_data:
                    if item_data[1] != "": #Checks if theres an acronym and if there is it picks it
                        ItemName = item_data[1]
                    else:
                        ItemName=item_data[0]# If there isnt sets item name
                    value=item_data[4]
                    Manual_Offered.append((item, value, ItemName))

                ManualList = [(ItemName, value) for _, value, ItemName in sorted(Manual_Offered, key=lambda x: x[1], reverse=True)[:4]]
                ManualListFinal = ""
                for ItemName, value in ManualList:
                    ManualListFinal += f"● {ItemName} {value}\n"
        else:
            ManualListFinal="`None`"

        configembed.add_field(name="✉️ Offered Items:", value=ManualListFinal, inline=False)

    #Tags
    Tags = ""
    for item in config_file["Tags"]:
        if item in Tag_Icons:
            Tags += f"- {Tag_Icons[item]}\n"
        else:
            Tags += f"- {item}\n"

    configembed.add_field(name="🏷️ Tags", value=Tags, inline=False) #Tags
    
    #Requested Items
    Fancy_Requested = ""  
    if config_file["RequestedItems"]:
        for item in config_file["RequestedItems"]: #changed item_id to item
            item_data = resIL["items"].get(str(item))
            if item_data:
                if item_data[1] != "": #Checks if theres an acronym and if there is it picks it
                    Item_Name = item_data[1]
                else:
                    Item_Name=item_data[0]# If there isnt sets item name
                value=item_data[4]
                Fancy_Requested += f"● {Item_Name} {value}\n"
    else:
        Fancy_Requested = "`None`"

    configembed.add_field(name="🔍 Requested Items", value=Fancy_Requested, inline=False)

    await ctx.send(embed=configembed) #sends embed


@bot.command(name="inv") 
async def inv_command(ctx):

    CheckHold=[]
    Items=[]

    responsePI = requests.get(urlPI)
    res_PI = responsePI.json() 
    for ItemsHold in res_PI.get("data"):
        CheckHold.append(((ItemsHold.get("assetId"), ItemsHold.get("userAssetId"), ItemsHold.get("isOnHold"))))
    for item in CheckHold:
        item_data = resIL["items"].get(str(item[0]))
        if item_data:
            if item_data[1] != "": #Checks if theres an acronym and if there is it picks it
                Item_Name = item_data[1]
            else:
                Item_Name=item_data[0]# If there isnt sets item name
            value=item_data[4]
            Items.append((((Item_Name, value, item[1], item[0], item[2]))))
    Invsort = [(item[0], item[1], item[2], item[3], item[4]) for item in sorted(Items, key=lambda x: x[1], reverse=True)]       
    InvList=""
    for item in Invsort:
        if len(InvList) > 1800:
            await ctx.send(InvList)
            InvList=""
            InvList+=f"{item[0]} | Value: {item[1]} | ID: `{item[3]}` | Hold:{item[4]} | UIAD: [{item[2]}](https://www.rolimons.com/uaid/{item[2]})\n"
        else:
            InvList+=f"{item[0]} | Value: {item[1]} | ID: `{item[3]}` | Hold:{item[4]} | UIAD: [{item[2]}](https://www.rolimons.com/uaid/{item[2]})\n"
    await ctx.send(InvList)


#Set command
@bot.group(name="set", invoke_without_command=True)
async def set(ctx):
    await ctx.send('❌ Wrong option! Use `!help set` for more details!')

@set.command(name="autopick") #Set Autopick
async def SetAutopick(ctx):
    config_file = load_config_file()
    config_file["AutoPick"] = "true"
    config_file["Top4"] = "false"
    save_config_file(config_file)
    await ctx.send('✅ AutoPick has been picked!')

@set.command(name="demandonly") #Set DemandOnly
async def SetDemandOnly(ctx, *, arg: str = None):
    if arg == "true":
        config_file = load_config_file()
        config_file["DemandOnly"] = "true"
        await ctx.send('✅ DemandOnly has been set to: True')

        save_config_file(config_file)
        return

    if arg == "false":
        config_file = load_config_file()
        config_file["DemandOnly"] = "false"
        save_config_file(config_file)
        await ctx.send('✅ DemandOnly has been set to: False')
        return

    await ctx.send('❌ DemandOnly can be only set as: `false/true`')

@set.command(name="manualpick", aliases=["manual"]) #Set Manualpick
async def SetManualPick(ctx):
    config_file = load_config_file()
    config_file["AutoPick"] = "false"
    config_file["Top4"] = "false"
    save_config_file(config_file)
    await ctx.send('✅ ManualPick has been picked!')

@set.command(name="minvalue") #Set MinValue
async def SetMinValue(ctx, *, arg: str = None):
    config_file = load_config_file()
    if arg.isnumeric():
        config_file["MinValue"] = int(arg)
        save_config_file(config_file)
        await ctx.send(f'✅ Minvalue has been set to: `{arg}`')
    else:
        await ctx.send('❌ This isnt a number')

@set.command(name="playerid") #Set PlayerID
async def SetPlayerID(ctx, *, arg: str = None):
    config_file = load_config_file()
    if arg.isnumeric():
        config_file["PlayerID"] = int(arg)
        save_config_file(config_file)
        await ctx.send(f'✅ PlayerID has been set to: `{arg}`')
    else:
        await ctx.send('❌ This isnt a number')

@set.command(name="robux") #Set Robux
async def SetRobux(ctx, *, arg: str = None):
    config_file = load_config_file()
    if arg.isnumeric():
        config_file["Robux"] = int(arg)
        save_config_file(config_file)
        await ctx.send(f'✅ Robux has been set to: `{arg}`')
    else:
        await ctx.send('❌ This isnt a number')

@set.command(name="time") #Set Time
async def SetTime(ctx, *, arg: str = None):
    config_file = load_config_file()
    if arg.isnumeric():
        config_file["Time"] = int(arg)
        save_config_file(config_file)
        await ctx.send(f'✅ Time has been set to: `{arg}` seconds')
    else:
        await ctx.send('❌ This isnt a number')

@set.command(name="top4") #Set Top4
async def SetAutopick(ctx):
    config_file = load_config_file()
    config_file["Top4"] = "true"
    config_file["AutoPick"] = "false"
    save_config_file(config_file)
    await ctx.send('✅ Top4 has been picked!')

@set.command(name="rolitoken") #Set Rolimons Token
async def SetRoliToken(ctx, *, arg: str = None):

    config_file = load_config_file()
    config_file["RolimonsToken"] = arg
    save_config_file(config_file)
    await ctx.send('✅ Rolimons Token has been set')

@set.command(name="channel") #Set Discord Channel
async def SetChannel(ctx, *, arg: str = None):
        config_file = load_config_file()
        config_file["DiscordChannel"] = int(arg)
        save_config_file(config_file)
        await ctx.send('✅ Discord Channel has been set')



#Items Command
@bot.group(name="items", aliases=["item"], invoke_without_command=True)
async def items(ctx):
    await ctx.send('❌ Use `offered <option>` or `requested <option>`. Check `!help items` for more!')


#Items Offered
@items.group(name="offered", aliases=["o"], invoke_without_command=True) #Items offered
async def itemsoffered(ctx):
    await ctx.send('❌ Use `add`, `clear` or `remove`. Check `!help items` for more!')

@itemsoffered.command(name="add") #Items offered add
async def itemsofferedadd(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send('❌ Please provide an item ID or name to add')
        return
    
    config_file = load_config_file()
    if len(config_file["OfferedItems"]) < 4:
        if arg.isnumeric():
                item_data = resIL["items"].get(str(int(arg)))
                if item_data:
                    config_file["OfferedItems"].append(int(arg))
                    save_config_file(config_file)  
                    await ctx.send(f'✅ {arg} has been added to Offered Items!')
                else:
                    await ctx.send('❌ Couldnt find this ID in Rolimons API')
        else:
            for key, value in resIL["items"].items():
                print(key, value)
                if value[1].casefold() == arg.casefold() or value[0].casefold() == arg.casefold():
                    config_file["OfferedItems"].append(int(key))
                    save_config_file(config_file)  
                    await ctx.send(f'✅ {value[1]} has been added to Offered Items!')
                    return
            else:
                await ctx.send('❌ Couldnt find this name in Rolimons API')
    else:
        await ctx.send('❌ Theres 4 IDs in Offered Items!')            

@itemsoffered.command(name="remove") #Items offered remove
async def itemsofferedremove(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send('❌ Please provide an item ID or name to remove')
        return
    config_file = load_config_file()

    if arg.isnumeric():
        if int(arg) in config_file["OfferedItems"]:
            config_file["OfferedItems"].remove(int(arg))
            save_config_file(config_file)  
            await ctx.send(f'✅ {arg} has been removed from Offered Items!')
        else:
            await ctx.send('❌ Couldnt find this ID in your config')
    else:
        for key, value in resIL["items"].items():
            if value[1].casefold() == arg.casefold() or value[0].casefold() == arg.casefold():
                if int(key) in config_file["OfferedItems"]:
                    config_file["OfferedItems"].remove(int(key))
                    save_config_file(config_file)  
                    await ctx.send(f'✅ {value[1]} has been removed from Offered Items!')
                else:
                    await ctx.send('❌ Couldnt find this acronym in your config')
                return
        else:
            await ctx.send('❌ Couldnt find this name in Rolimons API')
            
@itemsoffered.command(name="clear") #Items offered clear
async def itemsofferedclear(ctx, *, arg: str = None):
    config_file = load_config_file()
    
    config_file["OfferedItems"].clear()
    save_config_file(config_file)
    await ctx.send("✅ OfferedItems items have been cleared!")


#Items Requested
@items.group(name="requested", aliases=["r"], invoke_without_command=True) #Items offered
async def itemsrequested(ctx):
    await ctx.send('❌ Use `add`, `clear` or `remove`. Check `!help items` for more!')

@itemsrequested.command(name="add") #Items offered add
async def itemsrequestedadd(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send('❌ Please provide an item ID to remove')
        return
    
    config_file = load_config_file()
    if len(config_file["RequestedItems"]) < 4:
        if arg.isnumeric():
                item_data = resIL["items"].get(str(int(arg)))
                if item_data:
                    config_file["RequestedItems"].append(int(arg))
                    save_config_file(config_file)  
                    await ctx.send(f'✅ {arg} has been added to Requested Items!')
                else:
                    await ctx.send('❌ Couldnt find this ID in Rolimons API')
        else:
            for key, value in resIL["items"].items():
                if value[1].casefold() == arg.casefold() or value[0].casefold() == arg.casefold():
                    config_file["RequestedItems"].append(int(key))
                    save_config_file(config_file)  
                    await ctx.send(f'✅ {value[1]} has been added to Requested Items!')
                    return
            else:
                await ctx.send('❌ Couldnt find this name in Rolimons API')
    else:
        await ctx.send('❌ Theres 4 IDs in Requested Items!') 

@itemsrequested.command(name="remove") #Items offered remove
async def itemsrequestedremove(ctx, *, arg: str = None):
    if arg is None:
        await ctx.send('❌ Please provide an item ID or name to remove')
        return
    config_file = load_config_file()

    if arg.isnumeric():
        if int(arg) in config_file["RequestedItems"]:
            config_file["RequestedItems"].remove(int(arg))
            save_config_file(config_file)  
            await ctx.send(f'✅ {arg} has been removed from Requested Items!')
        else:
            await ctx.send('❌ Couldnt find this ID in your config')
    else:
        for key, value in resIL["items"].items():
            if value[1].casefold() == arg.casefold() or value[0].casefold() == arg.casefold():
                if int(key) in config_file["RequestedItems"]:
                    config_file["RequestedItems"].remove(int(key))
                    save_config_file(config_file)  
                    await ctx.send(f'✅ {value[1]} has been removed from Requested Items!')
                else:
                    await ctx.send('❌ Couldnt find this acronym in your config')
                return
        else:
            await ctx.send('❌ Couldnt find this name in Rolimons API')

@itemsrequested.command(name="clear") #NFT clear
async def itemsrequestedclear(ctx, *, arg: str = None):
    config_file = load_config_file()
    
    config_file["RequestedItems"].clear()
    save_config_file(config_file)
    await ctx.send("✅ Requested Items have been cleared!")

#Help command
bot.remove_command('help')
@bot.group(name="help", invoke_without_command=True)
async def help(ctx, *, arg: str = None):
    if arg == None:
        nftembed = discord.Embed(
            title="📝 Help",
            description='List of all commands with options avaible in this discord bot.\nUse `!help <command>` for more details and examples.',
            color=0x33cc66
        )
        nftembed.add_field(name="inv", value="", inline=False)
        nftembed.add_field(name="config", value="", inline=False)
        nftembed.add_field(name="items/item:", value="offered/o or requested/r \n- `add <id/name>`\n- `remove <id/name>`\n- `clear`\n", inline=False)
        nftembed.add_field(name="tags/tag", value="`add <tag>`\n`remove <tag>`\n`clear`\n`list`\n", inline=False)
        nftembed.add_field(name="preset/presets", value="`<presetname> <add/remove> <tag>`\n`set <preset>`\n`add <preset>`\n`remove <preset>`\n`list`\n", inline=False)
        nftembed.add_field(name="set", value="`autopick`\n`channel`\n`demandonly <true/false>`\n`manualpick/manual`\n`minvalue <number>`\n`playerid <id>`\n`robux <number>`\n`time <number> (in seconds)`\n`rolitoken <token>`\n`top4`", inline=False)
        nftembed.add_field(name="nft", value='`add <id/name>`\n`remove <id/name>`\n`clear`\n`list`', inline=False)

        #nftembed.add_field(name="help", value="`None`\n`items`\n`set`\n`nft`\n`tags`\n`config`", inline=False)

        await ctx.send(embed=nftembed)
    if arg != None:
        await ctx.send("W.I.P but reaaaaaallly long progress bc i dont wanna :P") 


#Hello again someone
#Last change of discord bot was on 20/11/2025 :P (dd/mm)

#Start of Trade Ad maker
#Started working on this on 21/09/2025 :D (dd/mm)
async def trade_ad_loop():
    while True:
        config_file = load_config_file()
        Logs =""

        #Bot sending Errors/Trade ads to discord channel
        channel_id = config_file.get("DiscordChannel")
        channel = None
        if channel_id != 0:
            channel = bot.get_channel(channel_id)
        else:
            print("⚠️  Discord Channel not found! Check if you typed correct id or use !set channel <id> to set it!")
        #I should just replace almost all but im too lazy for that 🤤
        RolimonsToken = config_file["RolimonsToken"]
        Top4 = config_file["Top4"]
        AutoPick = config_file["AutoPick"]
        Minvalue = config_file["MinValue"]
        NotForTrade = config_file["NotForTrade"]
        OfferedItems = config_file["OfferedItems"]
        Robux = config_file["Robux"]
        RequestedItems = config_file["RequestedItems"]
        PlayerId = config_file["PlayerID"]
        Tags=config_file["Tags"]
        Time=config_file["Time"]
        DemandOnly=config_file["DemandOnly"]

        data = {
            "offer_item_ids": OfferedItems,
            "offer_robux": Robux,
            "player_id": PlayerId,
            "request_item_ids": RequestedItems,
            "request_tags": Tags
        }

        headers = {
            "content-type": "application/json",
            "cookie": "_RoliVerification=" + RolimonsToken
        }

        responsePI = requests.get(urlPI)
        res_PI = responsePI.json()
        responseIL = requests.get(urlIL)
        res_IL = responseIL.json()

        #NotOnthold=[]
        ItemValues=[]
        
        if Top4 == "true" or AutoPick == "true":
            dataIH = res_PI.get("data")
            for ItemsHold in dataIH:
                ItemID = ItemsHold.get("assetId")
                if ItemsHold.get("isOnHold") is True:
                    continue
                if ItemID in NotForTrade:
                    continue
                item_data = res_IL["items"].get(str(ItemID))
                if item_data:
                    value=item_data[4]
                    rap=item_data[2]
                    if DemandOnly == "true" and item_data[5] <= 0:#item_data[5] is demand in roli api
                        continue
                    if AutoPick == "true" and value < Minvalue:
                        continue
                    ItemValues.append((ItemID, value, rap))
            if Top4 == "true":
                Top4List = [ItemID for ItemID, _, _ in sorted(ItemValues, key=lambda x: x[1], reverse=True)[:4]]
                data["offer_item_ids"] = Top4List
            
            elif AutoPick == "true":
                if len(ItemValues) >= 4:
                    AutoPickList = [ItemID for ItemID, _, _ in sorted(random.sample(ItemValues, 4), key=lambda x: x[1], reverse=True)]
                else:
                    AutoPickList = [ItemID for ItemID, _, _ in sorted(ItemValues, key=lambda x: x[1], reverse=True)]
                data["offer_item_ids"] = AutoPickList
        
        if Robux <= 0: #u cant make a trade ad when robux are set to 0
            del data["offer_robux"]

        #Foolproofing Requesteds👀
        if config_file["Tags"] == [] and config_file["RequestedItems"] ==[]:
            config_file["Tags"] = config_file["default"]
            data["request_tags"] = config_file["default"]
            save_config_file(config_file)
            await channel.send('❌ YOU FORGOT TO ADD TAGS AND REQUESTED ITEMS 🤬 Set tags to default tho 🤤 @everyone')

        if len(config_file["Tags"]) + len(config_file["RequestedItems"]) >4:
            if len(config_file["RequestedItems"]) >1:
                config_file["Tags"] = []
                data["request_tags"] = []
                save_config_file(config_file)
                await channel.send('❌ Tags have been removed, Dont make trade ads when tags + items requested > 4 @everyone')
            else:
                config_file["RequestedItems"] = []
                config_file["Tags"] = config_file["default"]
                data["request_tags"] = config_file["default"]
                save_config_file(config_file)
                await channel.send('❌ Items requested have been removed and tags set to default. Dont make trade ads when tags + items requested > 4 @everyone')

        #Sends trade ad 
        responseTA = requests.post(urlTA, json=data, headers=headers)
            
        res_TA = responseTA.json()
        if res_TA.get("success") == True:
            TradeMode=""
            TotalValue = 0
            TotalRap = 0
            OffItems = []
            OffItemslist =[]

            if Top4 == "true":
                TradeMode = "Top4"
            elif AutoPick ==   "true":
                TradeMode = "Autopick"
            else:
                TradeMode = "Manualpick"
            if DemandOnly =="true" and TradeMode != "Manualpick":
                TradeMode += " with DemandOnly"

            Logs += (f"✅ Trade ad Posted! ({TradeMode})\n\n")

            if Top4 == "true" :
                OffItems = Top4List
            elif AutoPick == "true":
                OffItems = AutoPickList
            else: 
                OffItems = OfferedItems
            for item in OffItems:
                item_data = res_IL["items"].get(str(item))
                if item_data:
                    TotalValue += item_data[4]
                    TotalRap += item_data[2]
                    if item_data[1] == "":
                        OffItemslist.append(f"- {item_data[0]} | Value: {item_data[4]}")
                    else:
                        OffItemslist.append(f"- {item_data[1]} | Value: {item_data[4]}")

            Logs += (f"📊 Total Value: {TotalValue}\n")
            Logs += (f"📊 Total RAP: {TotalRap}\n\n")
            Logs += ("📜 Offered Items:\n")
            OffItemsPrint=""
            for line in OffItemslist:
                OffItemsPrint += f"{line}\n"
            Logs += (f"{OffItemsPrint}\n")

            if RequestedItems:
                ReqItems = []
                for line in RequestedItems:
                    item_data = res_IL["items"].get(str(line))
                    if item_data[1] == "":
                        ReqItems.append(f"- {item_data[0]} | Value: {item_data[4]}")
                    else:
                        ReqItems.append(f"- {item_data[1]} | Value: {item_data[4]}")

                ReqItemslist =""
                for line in ReqItems:
                    ReqItemslist += f"{line}\n"
                
                Logs += (f"🔍 Requested Items:\n{ReqItemslist}\n\n")

            #Tags
            TagsText = ""
            for item_str in config_file["Tags"]:
                TagsText += f"- {Tag_Icons.get(item_str)}\n"
            if TagsText:
                Logs += (f"🔍 Tags:\n{TagsText}\n")

            if Robux > 0:
                Logs += (f"💲 Robux: {Robux}\n\n")

            future_time = datetime.now() + timedelta(seconds=Time)   
            Logs +=(f"🕒 Next Trade Ad will be posted in: {Time / 60} minutes, Aka: {future_time.strftime('%H:%M')}\n")

            #Sends Trade ad into discord channel and terminal
            print(Logs)
            if channel:
                await channel.send(Logs)

        ErrorLogs =""     
        if res_TA.get("success") == False:
            future_time = datetime.now() + timedelta(seconds=Time)
            if res_TA.get("code") == 7105:
                ErrorLogs +=(f"⏳ Ad creation cooldown has not elapsed ⏳\n🕒 Next try will be at: {future_time.strftime('%H:%M')} 🕒")
    
            elif res_TA.get("code") == 7110:
                ErrorLogs+=(f"❌ Change your Robux! Robux number can't exceed 50% RAP. ❌\n🕒 Next try will be at: {future_time.strftime('%H:%M')} @everyone 🕒")            
            
            elif res_TA.get("code") == 5:
                ErrorLogs +=(f"❌ Invalid Rolimons Token! ❌\n🕒 Next try will be at: {future_time.strftime('%H:%M')} @everyone 🕒")
    
            elif res_TA.get("code") == 14:
                ErrorLogs +=(f"❌ 24-hour ad creation limit has been hit! ❌\n🕒 Next try will be at: {future_time.strftime('%H:%M')} @everyone 🕒")
    
            elif res_TA.get("code") == 7104:
                ErrorLogs+=(f"❌ Player does not own all offered items! ❌\n🕒 Next try will be at: {future_time.strftime('%H:%M')} @everyone 🕒")
    
            elif res_TA.get("code") == 7111:
                ErrorLogs+=(f"❌ Requested value exceeds limit based on offered value (More than 5x) ❌\n🕒 Next try will be at: {future_time.strftime('%H:%M')} @everyone 🕒")
                        
            elif res_TA.get("code") != None:
                ErrorLogs += (f"❌ Something is not working!\n❌ Error message: {res_TA.get('message')}\n❌ Error code: {res_TA.get('code')}\n🕒 Next try will be at: {future_time.strftime('%H:%M')} @everyone 🕒")
            
            print(ErrorLogs)
            if channel:
                await channel.send(ErrorLogs)

        await asyncio.sleep(int(Time))

#Hello hello again
#Last change of Trade Ad Thingy was on 22/10/2025 :P (dd/mm)

#Errors
@bot.event
async def on_command_error(ctx, error):
    print("Command error:", error)

#Starts Trade Ad Thingy when discord bot loads
@bot.event
async def on_ready():
    bot.loop.create_task(trade_ad_loop()) 

#Token
config_file = load_config_file()

TOKEN = config_file["TOKEN"]

if __name__ == "__main__":
    if not TOKEN:
        print("No discord token plz fix")
    else:
        bot.run(TOKEN)


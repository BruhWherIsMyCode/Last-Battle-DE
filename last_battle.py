from io import BytesIO
import os
import random
from dotenv import load_dotenv
load_dotenv()
import discord
from discord import (ApplicationContext, Bot, ButtonStyle,
    Color, File, Interaction, SeparatorSpacingSize, User)
from discord.ui import (ActionRow, Button, Container, DesignerView,
    MediaGallery, Section, Select, Separator, TextDisplay, Thumbnail, button)

fusers = {}
modes=("Building mode","Atack mode","Radiation mode",)
rad_emj=("<:0rd:1532872671484838139>",  "<:1rd:1530616688117022800>","<:2rd:1530616711437357146>",
         "<:3rd:1530616727229173780>","<:4rd:1530616745709146184>","<:5rd:1530616774108647476>",
         "<:6rd:1530616796111966318>","<:7rd:1530616814227427388>","<:8rd:1530616829452750880>",)
obj_emj=("<:grey:1525893303898214400>", "<:gfac:1525896582036324372>", "<:ghom:1525985697612304537>", "<:glan:1529613092257005744>",)
num_emj=("<:zero:1527297606986764360>","<:one:1527003069726855270>", "<:two:1527001046713499840>",
         "<:thre:1527003085443043418>", "<:four:1527003120905883648>", "<:five:1527003139335651469>",
         "<:six:1527003153260876039>", "<:sevn:1527003167030509669>", "<:eigt:1527003185309552760>",)
sym_emj=("<:wrk:1529150229193035917>","<:prd:1529150214764499084>", "<:atc:1529610411278733402>",)
wep_emj=("huh","<:nuke:1530907025855483994>",)
blac = "<:black:1527003711849631855>"
prd_cst = (20, 10, 10,)
wrk_cst = (10, 20, 10,)
rck_cst = (10,)
res_mov = (10, 10, 1,)
rad_rck = (4,)
rad_obj = (2, 1, 0,)
rad_shw = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2,)

class MyGame:
    def __init__(self):
        self.users = [None, None]
        self.views = [None, None]
        self.grounds = [[[0] * 8 for i in range(8)], [[0] * 8 for i in range(8)]]
        self.rads = [[[0] * 8 for i in range(8)], [[0] * 8 for i in range(8)]]
        self.counts = [[2, 2, 1], [2, 2, 1]]
        self.reses = [[20, 20, 1], [20, 20, 1]]
        self.moveof = False
    def __del__(self): print("game session deleted")
    async def create(self, player1, player2):
        self.users= [player1, player2]
        self.views = [self.users[0].view, self.users[1].view]
        self.views[0].game = self
        self.views[1].game = self
        self.users[0].game = self
        self.users[1].game = self
        fusers.pop(self.users[0].id, None)
        fusers.pop(self.users[1].id, None)
        self.users[0].number = False
        self.users[1].number = True
        for i in range(2):
            for j in range(len(self.counts[i])):
                k=0
                while k != self.counts[i][j]:
                    r1 = random.randint(0, 7)
                    r2 = random.randint(0, 7)
                    if not self.grounds[i][r1][r2]:
                        self.grounds[i][r1][r2] = j+1
                        k+=1
        self.views[0].status.content="Your move"
        print(self.views[0].status)
        self.views[1].status.content="Opponent's move"
        await self.views[0].show_game()
        await self.views[1].show_game()
    async def user_lost(self, user):
        loser_v = user
        winner_v = self.views[(loser_v.user.number+1)%2]
        await winner_v.victory()
        await loser_v.defeat()
        self.views[0].game = None
        self.views[1].game = None
        self.users[0].game = None
        self.users[1].game = None
    async def proceed(self):
        bder=self.views[self.moveof]
        ask = bder.g_set
        num=bder.user.number
        if bder.g_set[3]!=2:
            self.grounds[num][ask[1]-1][ask[2]-1]=ask[0]
            self.reses[num][1]-=prd_cst[ask[0]-1]
            self.reses[num][0]-=wrk_cst[ask[0]-1]
            self.counts[num][ask[0]-1]+=1
        else:
            if self.grounds[(num+1)%2][ask[1]-1][ask[2]-1]!=0:
                self.counts[(num+1)%2][self.grounds[(num+1)%2][ask[1]-1][ask[2]-1]-1]-=1
                if self.counts[(num+1)%2][0]==0: await self.user_lost(self.users[(num+1)%2])
                else:
                    t="Your object was destroyed! Coordinates: h=" + str(ask[1]) + ", w=" + str(ask[2])
                    await self.users[(num+1)%2].temp_msg(t)
                    self.grounds[(num+1)%2][ask[1]-1][ask[2]-1]=0
            self.reses[num][1]-=rck_cst[ask[0]-1]
            self.reses[num][2]-=1
            if self.rads[(num+1)%2][ask[1]-1][ask[2]-1]<rad_rck[ask[0]-1]: self.rads[(num+1)%2][ask[1]-1][ask[2]-1]=rad_rck[ask[0]-1]
            await self.views[(num+1)%2].sh_map(self.views[(num+1)%2].g_set[3]-1)
            await self.users[(num+1)%2].message.edit(view=self.views[(num+1)%2])
    async def next_user(self):
        self.views[self.moveof].status.content = "Opponent's move"
        for i in range(3): self.reses[self.moveof][i]=self.counts[self.moveof][i]*res_mov[i]
        for i in range(8):
            for j in range(8):
                if self.grounds[self.moveof][i][j]!=0:
                    if self.rads[self.moveof][i][j]<=rad_obj[self.grounds[self.moveof][i][j]-1]: self.rads[self.moveof][i][j]=rad_obj[self.grounds[self.moveof][i][j]-1]
                    else: self.rads[self.moveof][i][j]-=1
                elif self.rads[self.moveof][i][j]>2: self.rads[self.moveof][i][j]-=1
                else:
                    self.rads[self.moveof][i][j]=rad_shw[random.randint(0,17)]
        self.moveof=(self.moveof+1)%2
        self.views[self.moveof].status.content = "Your move"
        await self.views[0].show_game()
        await self.views[1].show_game()

class MyView(DesignerView):
    def __init__(self, user):
        self.user = user
        self.game = None
        self.menu = None
        self.table = None
        self.screen = TextDisplay("PLACEHOLDER")
        self.status = TextDisplay("Welcome! Start a game to play")
        self.selects = []
        self.rovv = None
        self.g_set = [0, 0, 0, 1]
        super().__init__(timeout=None)
    def __del__(self): print("game view deleted")
    async def create_menu(self):
        text1 = TextDisplay("# LAST BATTLE")
        thumbnail = Thumbnail(bot.user.display_avatar.url)
        section = Section(text1, self.status, accessory=thumbnail)
        section.add_text("-# Good luck")
        self.menu = Container(section, color=Color.from_rgb(180, 180, 180))
        async def delete_callback(interaction: Interaction):
            fusers.pop(self.user.id, None)
            await interaction.response.defer()
            await self.user.thread.delete()
            self.stop()
            self.user.view = None
            self.user = None
        async def play_callback(interaction: Interaction):
            if self.user.id in fusers: await interaction.response.send_message("You already are waiting for opponent",ephemeral=True)
            elif len(fusers) == 0:
                fusers[self.user.id] = self.user
                await interaction.response.send_message("Waiting for the opponent",ephemeral=True)
            else:
                opponent = next(iter(fusers.values()))
                game = MyGame()
                await game.create(self.user, opponent)
                await interaction.response.send_message("The game started! Good luck!",ephemeral=True)
        delete_button = Button(label="Delete Thread", style=ButtonStyle.red)
        delete_button.callback = delete_callback
        play_button = Button(label="Start the game", style=ButtonStyle.green)
        play_button.callback = play_callback
        row = ActionRow()
        row.add_item(delete_button)
        row.add_item(play_button)
        self.menu.add_item(row)
    async def show_menu(self):
        self.clear_items()
        self.add_item(self.menu)
        await self.message.edit(view=self)
    async def create_table(self):
        self.table = Container(color=Color.from_rgb(180, 180, 180))
        thumbnail1 = Thumbnail(bot.user.display_avatar.url)
        text3 = TextDisplay("# LAST BATTLE")
        section1 = Section(text3, self.status, accessory=thumbnail1)
        self.table.add_item(section1)
        self.add_item(self.table)
        self.screen = TextDisplay(f"Wait a bit...")
        self.table.add_item(self.screen)
        m_input = Select(placeholder = modes[0], min_values = 1, max_values = 1,
            options = [
                discord.SelectOption(label = "Building mode", value="0"),
                discord.SelectOption(label = "Atacking mode", value="1"),
                discord.SelectOption(label = "Radiation mode", value="2")])
        self.selects.append(
            Select(placeholder = "Object", min_values = 1, max_values = 1,
                options = [
                    discord.SelectOption(
                        label="Overground factory, 20 prod, 10 work",
                        value="1",
                        emoji=discord.PartialEmoji(name="gfac",id=1525896582036324372)),
                    discord.SelectOption(
                        label="Overground city, 10 prod, 20 work",
                        value="2",
                        emoji=discord.PartialEmoji(name="ghom",id=1525985697612304537)),
                    discord.SelectOption(
                        label="Launching_platform, 10 prod, 10 work",
                        value="3",
                        emoji=discord.PartialEmoji(name="glan",id=1529613092257005744))]))
        self.selects.append(
            Select(placeholder = "Rocket", min_values = 1, max_values = 1,
                options = [
                    discord.SelectOption(
                        label="Ordinal nuke, 10 prod",
                        value="1",
                        emoji=discord.PartialEmoji(name="nuke",id=1530907025855483994))]))
        y_input = Select(placeholder = "Vertical", min_values = 1, max_values = 1,
            options = [discord.SelectOption(label=str(i), value=str(i))for i in range(1, 9)])
        x_input = Select(placeholder = "Horizontal", min_values = 1, max_values = 1,
            options = [discord.SelectOption(label=str(i), value=str(i))for i in range(1, 9)])
        prc_but = Button(label="PROCEED", style=ButtonStyle.green)
        pas_but = Button(label="End the move", style=ButtonStyle.grey)
        hel_but = Button(label="Help", style=ButtonStyle.grey)
        sur_but = Button(label="Surrender", style=ButtonStyle.red)
        async def m_set(interaction: Interaction):
            mod = int(m_input.values[0])
            m_input.placeholder = modes[mod]
            await self.sh_map(mod)
            self.g_set[0] = 0
            self.g_set[3]=mod+1
            try:
                self.rovv.remove_item(self.selects[(mod+1)%2])
                self.rovv.add_item(self.selects[mod%2])
            except: pass
            print(self.g_set[3])
            await interaction.response.edit_message(view=self)
        async def b_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[0]=int(self.selects[0].values[0])
        async def r_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[0]=int(self.selects[1].values[0])
        async def y_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[1]=int(y_input.values[0])
        async def x_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[2]=int(x_input.values[0])
        async def act_ask(interaction: Interaction):
            if self.game.moveof != self.user.number: await interaction.response.send_message("It's not your move!",ephemeral=True)
            elif 0 in self.g_set: await interaction.response.send_message("You did not chosed the object or the coordinates",ephemeral=True)
            elif self.g_set[3]==2:
                if not self.game.reses[self.user.number][2]: await interaction.response.send_message("You don't have any free launch platforms",ephemeral=True)
                elif rck_cst[self.g_set[0]-1]>self.game.reses[self.user.number][1]: await interaction.response.send_message("You don't have enough production right now",ephemeral=True)
                else:
                    await self.game.proceed()
                    await self.sh_map(1)
                    self.selects[0].value=[]
                    self.selects[1].value=[]
                    x_input.value=[]
                    y_input.value=[]
                    self.g_set=[0, 0, 0, self.g_set[3]]
                    await interaction.response.edit_message(view=self)
            elif self.game.grounds[self.user.number][self.g_set[1]-1][self.g_set[2]-1]!=0: await interaction.response.send_message("It is already an object in this spot",ephemeral=True)
            elif wrk_cst[self.g_set[0]-1]>self.game.reses[self.user.number][0]: await interaction.response.send_message("You don't have enough workforce right now",ephemeral=True)
            elif prd_cst[self.g_set[0]-1]>self.game.reses[self.user.number][1]: await interaction.response.send_message("You don't have enough production right now",ephemeral=True)
            else:
                await self.game.proceed()
                await self.sh_map(int(self.g_set[3]-1))
                self.selects[0].value=[]
                self.selects[1].value=[]
                x_input.value=[]
                y_input.value=[]
                self.g_set=[0, 0, 0, self.g_set[3]]
                await interaction.response.edit_message(view=self)
        async def pass_move(interaction: Interaction):
            if self.game.moveof != self.user.number: await interaction.response.send_message("It's not your move!",ephemeral=True)
            else:
                await interaction.response.defer()
                await self.game.next_user()
        async def hint(interaction: Interaction):
            await interaction.response.send_message("This function is not ready yet",ephemeral=True)
        async def surrender(interaction: Interaction):
            await interaction.response.defer()
            await self.game.user_lost(self)
        m_input.callback = m_set
        self.selects[0].callback = b_set
        self.selects[1].callback = r_set
        x_input.callback = x_set
        y_input.callback = y_set
        prc_but.callback = act_ask
        hel_but.callback = hint
        pas_but.callback = pass_move
        sur_but.callback = surrender
        row0=ActionRow(m_input)
        self.rovv=ActionRow(self.selects[0])
        row2=ActionRow(x_input)
        row3=ActionRow(y_input)
        row4=ActionRow(prc_but, hel_but, pas_but, sur_but)
        self.table.add_item(row0)
        self.table.add_item(self.rovv)
        self.table.add_item(row2)
        self.table.add_item(row3)
        self.table.add_item(row4)
    async def sh_map(self, mode):
        num = self.user.number
        match mode:
            case 0:
                    ground = self.game.grounds[num]
                    emj_set = obj_emj
            case 1:
                    ground = self.game.rads[(num+1)%2]
                    emj_set = rad_emj
            case 2:
                    ground = self.game.rads[num]
                    emj_set = rad_emj
        res = self.game.reses[num]
        self.screen.content=f""+blac
        for i in range(1,9): self.screen.content += num_emj[i]
        self.screen.content+=blac
        for i in range(3):
            self.screen.content+="\n"+num_emj[i+1]
            for j in range(8): self.screen.content+=emj_set[ground[i][j]]
            self.screen.content+=sym_emj[i]
            for j in str(res[i]): self.screen.content+=num_emj[int(j)]
        for i in range(3,8):
            self.screen.content+="\n"+num_emj[i+1]
            for j in range(8): self.screen.content+=emj_set[ground[i][j]]
    async def show_game(self):
        self.clear_items()
        self.add_item(self.table)
        await self.sh_map(0)
        await self.message.edit(view=self) 
    async def defeat(self):
        await self.show_menu()
        self.status.content = "You lost. But you can play again!"
        await self.user.message.edit(view=self)
    async def victory(self):
        await self.show_menu()
        self.status.content = "You won, congrats with survival! One more round?"
        await self.user.message.edit(view=self)

class T_mes(DesignerView):
    def __init__(self, t):
        self.txt = t
        super().__init__(timeout=None)
        text1 = TextDisplay("# MESSAGE")
        text2 = TextDisplay(self.txt)
        okay = Button(label="OK", style=ButtonStyle.grey)
        async def ok(interaction: Interaction):
            await interaction.message.delete()
            self.stop()
        okay.callback = ok
        row = ActionRow(okay)
        window = Container(text1, text2, row, color=Color.from_rgb(255, 0, 0))
        self.add_item(window)
    def __del__(self): print("temporal message deleted")
    
class MyUser:
    def __init__(self):
        self.id = None
        self.thread = None
        self.name = None
        self.view = None
        self.game = None
        self.message = None
        self.number = None
    def __del__(self): print("game view deleted")
    @classmethod
    async def create(cls, ctx: discord.ApplicationContext):
        self = cls()
        self.name = ctx.author.name
        self.id = ctx.author.id
        self.thread = await ctx.channel.create_thread(name=f"{ctx.author.name}'s game",)
            #type=discord.ChannelType.private_thread, invitable=False)
        await self.thread.add_user(ctx.author)
        await self.thread.send(f"The new game thread for {self.name} was created")
        self.view = MyView(self)
        await self.view.create_table()
        await self.view.create_menu()
        self.message = await self.thread.send(view=self.view)
        await self.view.show_menu()
        await ctx.send(f"{self.thread.mention} thread for {self.name} created")
        return self
    async def temp_msg(self, txt):
        temp = T_mes(txt)
        await self.thread.send(view=temp)
        
bot = Bot()

@bot.event
async def on_ready():
    global events
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="start", description="start the game (not ready yet)")
async def new_game(ctx: discord.ApplicationContext):
    await ctx.respond("creating the thread...",ephemeral=True)
    global fusers
    user=await MyUser.create(ctx)
    
bot.run(os.getenv('TOKEN'))
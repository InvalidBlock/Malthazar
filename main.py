# 
# Para executar o bot novamente use o comando:
# source venv/bin/activate
# python main.py > bot.log 2>&1 &
#

# Import o necessário para variáveis de ambiente
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("Token não encontrado no .env")

# Importar biblioteca para Discord
import discord
# Importar do discord os app_commands
from discord import app_commands

# Importação do módulo responsável por expressões regulares voltadas ao Regex
import re

# Importação do gerador de aleatóriedade do python
import random

class malthazar(discord.Client):
    # Inicialização
    def __init__(self):
        # Pega todas intents do Discord para facilitar
        intents = discord.Intents.all()
        
        # Invocar na classe filha a classe pai (malthazar)
        super().__init__(
            # Definir as intents
            intents=intents
        )

        # Definir o que é a tree
        self.tree = app_commands.CommandTree(self)
    
    # Função de setup
    async def setup_hook(self):      
        # Sincroniza Novamente
        synced = await self.tree.sync(guild=guild)
        print(f"Sincronizados: {len(synced)} comandos")

# Definir a instância do bot
bot = malthazar()

# Definir a Guild
GUILD_ID = 1379932351987191910
guild = discord.Object(id=GUILD_ID)

# Comandos de dados
@bot.tree.command(guild=guild, name="r", description="Rola dados no formado N#XdY")
@app_commands.describe(
    expressao="Exemplos: 2#3d6 ou 2d6",
    gm="Para o GM não mostrar o valor do dado"
)
async def r(interaction:discord.Interaction, expressao: str, gm: bool):
    
    # ---------------------------
    #   DEFINIÇÃO DA GRAMÁTICA
    # ---------------------------
    # ^           -> início da string
    # (\d+)?      -> grupo 1 (opcional): número de repetições
    # #?          -> caractere "#" opcional
    # (\d*)       -> grupo 2: quantidade de dados (pode estar vazio *)
    # d           -> letra literal "d"
    # (\d+)       -> grupo 3: número de lados (obrigatório)
    # ([+-]\d+)?  -> Pode colocar +/- como modificador e é opcional
    # $           -> fim da string
    padrao = r"^(\d+)?#?(\d*)d(\d+)([+-]\d+)?$"
    
    # Faz a comparação da string do usuário com a regex.
    match = re.match(padrao, expressao.lower())

    # Se a comparação não der certa com o padrão definido, é um formato inválido.
    if not match:
        await interaction.response.send_message(
            "Formato inválido. Use N#XdY±M (ex: 2#3d6+4).",
            ephemeral=True  # Resposta visível apenas para o usuário
        )
        return  # Interrompe execução
    
    # ----------------------------
    #     EXTRAÇÃO DOS GRUPOS
    # ----------------------------

    # O group(1) é o número de repetições
    # Se não existir, assume por padrão que vai ser executado uma vez
    repeticoes = int(match.group(1)) if match.group(1) else 1

    # O group(2) é a quantidade de dados
    # Se vazio (ex: 2#d6), assume por padrão que é um dado
    quantidade = int(match.group(2)) if match.group(2) else 1

    # O group(3) é o número de lados que é obrigatório, portanto deve haver independente da expressão
    lados = int(match.group(3))
    
    # O group(4) é o modificador, não é obrigatório e por padrão caso não haja é definido como 0
    modificador = int(match.group(4)) if match.group(4) else 0
    
    # -------------------------
    #    VALIDAÇÃO SEMÂNTICA
    # -------------------------
    # Evitar valores negativos ou 0 (neutro)
    if repeticoes <= 0 or lados <= 0 or quantidade <= 0:
        await interaction.response.send_message(
            "Por favor insira valores positivos.",
            ephemeral=True
        )
        return
    
    # ---------------------------
    #    EXECUÇÃO DAS ROLAGENS
    # ---------------------------

    resposta = []  # O Array que armazena cada lance
    totalTodosLances = 0 # Valor obtido de todos os lances

    # Loop para múltiplas execuções (No caso de 2#...)
    for i in range(repeticoes):

        # Geração dos resultados individuais
        # Ele em resultados retorna a aleatoriedade vinda da quantidade de lados e repete pela quantidade de dados
        resultados = [
            random.randint(1, lados)
            for _ in range(quantidade)
        ]

        # Soma total dos dados jogados
        total = sum(resultados) + modificador

        # Armazena texto formatado da execução
        resposta.append(                
            f"[Exec: **{i+1}**]: **{total}** {resultados}" + f"{' +' if modificador >= 0 else ' '}{modificador} "
        )
        
        # Soma o total obtido nessa execução com o total de todos os lances
        totalTodosLances += total
    
        
    # -----------------------
    #    ENVIO DA RESPOSTA
    # -----------------------
    
    respostaFinal = f"{interaction.user.mention}, {expressao}:\n" + f"------------------\n" + "\n".join(resposta) + f"\n------------------\nTotal: **{totalTodosLances}**"

    # Junta todas as execuções em múltiplas linhas
    await interaction.response.send_message(
        respostaFinal,ephemeral=gm
    )

# Rodar o bot
bot.run(TOKEN)
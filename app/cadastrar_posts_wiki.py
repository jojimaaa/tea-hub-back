import os
import requests

# URLs da API
BASE_URL_POST = "http://localhost:8000/wiki/upload-wiki-post"
BASE_URL_TOPIC = "http://localhost:8000/wiki/topics/create_topic"

# Caminho da imagem que será usada em todos os posts
IMAGE_PATH = r"C:\Users\Nacpa\Desktop\Projeto LS 17-11\imagem_wiki.jpg"

# ---------------------- DADOS DOS POSTS ----------------------
posts = [
    {
        "id": "rotina-e-previsibilidade-no-tea",
        "title": "Rotina e previsibilidade no TEA",
        "body": "Uma das características comuns no TEA é a preferência por **rotinas previsíveis**. Mudanças bruscas podem gerar ansiedade, crises e sensação de perda de controle.\n\nTer uma rotina não significa engessar a vida, mas ajudar a criança (ou adulto) a **entender o que vem depois**.\n\nAlgumas estratégias práticas:\n\n- Usar **quadros de rotina** com figuras ou palavras.\n- Avisar com antecedência sobre mudanças (ex.: marcar no calendário).\n- Criar rituais simples para momentos importantes, como dormir ou ir à escola.\n\n> Rotina bem estruturada não é \"frescura\" — é uma forma de tornar o mundo mais compreensível e seguro para a pessoa autista.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "rotina",
        "img_url": ""
    },
    {
        "id": "brincadeiras-para-estimular-interacao",
        "title": "Brincadeiras para estimular interação no autismo",
        "body": "Brincar é uma das formas mais naturais de **aprender e se conectar**. Para muitas crianças autistas, porém, o brincar pode ser diferente do esperado.\n\nAlgumas ideias de brincadeiras que estimulam interação:\n\n- **Esconde-esconde de objetos**: você esconde e a criança procura, sempre comemorando junto.\n- **Brincadeiras de turno** (minha vez, sua vez): jogos simples de encaixe ou bola.\n- **Música e movimento**: cantar e fazer gestos, incentivando que a criança imite.\n\nDicas importantes:\n\n- Respeite o tempo da criança.\n- Observe quais brinquedos e temas ela gosta e **entre no mundo dela**.\n- Priorize a conexão, não a perfeição da atividade.\n\n> Quando o adulto se envolve de forma divertida e acolhedora, a brincadeira vira um poderoso recurso terapêutico.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "intervencao",
        "img_url": ""
    },
    {
        "id": "autismo-na-escola-como-orientar-professores",
        "title": "Autismo na escola: como orientar professores",
        "body": "A escola é um espaço fundamental de convivência e aprendizado. Quando uma criança autista chega à sala de aula, **a informação é a melhor aliada**.\n\nSugestões de pontos para conversar com a escola:\n\n- Quais são os **interesses da criança** (desenhos, jogos, temas favoritos).\n- Quais situações costumam gerar mais estresse (barulho, fila, recreio).\n- Estratégias que funcionam em casa para acalmar ou redirecionar.\n\nAdaptações simples fazem diferença:\n\n- Oferecer um **cantinho tranquilo** para momentos de sobrecarga.\n- Usar recursos visuais para combinados e regras.\n- Permitir fones abafadores de som, se necessário.\n\n> Escola, família e profissionais caminhando juntos aumentam muito as chances de inclusão real.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "educacao",
        "img_url": ""
    },
    {
        "id": "direitos-da-pessoa-autista-no-brasil",
        "title": "Direitos da pessoa autista no Brasil",
        "body": "No Brasil, a pessoa com TEA é reconhecida como **pessoa com deficiência** para todos os efeitos legais, o que garante uma série de direitos.\n\nEntre eles, podemos destacar:\n\n- Acesso prioritário em filas e atendimentos.\n- Direito a **atendimento educacional especializado**.\n- Possibilidade de benefícios sociais, como o BPC/LOAS, quando atendidos os critérios.\n- Acesso a tratamentos pelo SUS e pela rede pública.\n\nÉ importante manter documentos organizados:\n\n- Relatórios médicos.\n- Laudos atualizados.\n- Registros de terapias e acompanhamentos.\n\n> Conhecer os direitos é o primeiro passo para **exigir respeito e inclusão** em todas as áreas da vida.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "direitos",
        "img_url": ""
    },
    {
        "id": "sobrecarga-sensorial-no-autismo",
        "title": "Sobrecarga sensorial no autismo: o que é e como ajudar",
        "body": "Muitas pessoas autistas têm um jeito diferente de perceber estímulos como luz, som, cheiro e toque. Quando há estímulos demais, pode ocorrer a **sobrecarga sensorial**.\n\nSinais comuns:\n\n- Tampar os ouvidos em ambientes barulhentos.\n- Irritação com certos tecidos ou etiquetas de roupas.\n- Desconforto com cheiros fortes ou luz muito intensa.\n\nComo apoiar nesses momentos:\n\n- Diminuir o número de estímulos (baixar o som, apagar luz forte).\n- Oferecer um local mais calmo.\n- Validar o que a pessoa sente, sem minimizar.\n\n> A sobrecarga sensorial não é \"manha\" — é o corpo dizendo que já chegou ao limite.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "sensorial",
        "img_url": ""
    },
    {
        "id": "autocuidado-dos-pais-e-cuidadores",
        "title": "Autocuidado de pais e cuidadores de pessoas autistas",
        "body": "Cuidar de uma pessoa autista exige tempo, energia emocional e muitas decisões importantes. Nesse processo, é comum que pais e cuidadores **esqueçam de cuidar de si mesmos**.\n\nAlguns pontos para refletir:\n\n- Descansar não é egoísmo, é **necessidade**.\n- Pedir ajuda a familiares, amigos ou grupos de apoio alivia a carga.\n- Terapia para os cuidadores pode ser um espaço seguro para falar sobre medos e culpas.\n\nIdeias de autocuidado possível no dia a dia:\n\n- Pequenas pausas para respirar, ler ou ouvir música.\n- Dividir tarefas com outras pessoas da família.\n- Participar de comunidades de pais de autistas, seja presencial ou online.\n\n> Quando o cuidador cuida de si, ele fica mais forte para cuidar de quem ama.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "familia",
        "img_url": ""
    },
    {
        "id": "intervencoes-precoces-no-tea",
        "title": "Intervenções precoces no TEA: por que fazem diferença?",
        "body": "Quanto mais cedo o TEA é identificado, mais rápido é possível iniciar **intervenções adequadas**. Isso não significa \"curar\" o autismo, mas oferecer suporte para o desenvolvimento.\n\nBenefícios da intervenção precoce:\n\n- Estímulo à comunicação e à linguagem.\n- Desenvolvimento de habilidades sociais e acadêmicas.\n- Prevenção ou redução de comportamentos que atrapalham o dia a dia.\n\nAlguns tipos de intervenção:\n\n- Terapias focadas em linguagem e comunicação.\n- Terapia ocupacional, inclusive com integração sensorial.\n- Orientação familiar para aplicar estratégias em casa.\n\n> O objetivo da intervenção é ampliar possibilidades, respeitando sempre o jeito único de ser de cada pessoa autista.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "intervencao",
        "img_url": ""
    },
    {
        "id": "autismo-e-adolescencia",
        "title": "Autismo e adolescência: novos desafios, novas descobertas",
        "body": "A adolescência é uma fase de grandes mudanças para qualquer pessoa — e, no TEA, ela vem acompanhada de **novos desafios sociais e emocionais**.\n\nQuestões que costumam aparecer:\n\n- Maior consciência das diferenças em relação aos colegas.\n- Interesse por amizades e relacionamentos, mas dificuldade em entender regras sociais.\n- Aumento da ansiedade e, às vezes, sintomas depressivos.\n\nComo apoiar o adolescente autista:\n\n- Manter canais de diálogo abertos, respeitando seu tempo.\n- Buscar profissionais que tenham experiência com TEA na adolescência.\n- Incentivar grupos e atividades em que ele possa se sentir pertencente.\n\n> Com apoio adequado, a adolescência também pode ser um período de **autoconhecimento e fortalecimento da identidade**.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "ciclo-vida",
        "img_url": ""
    },
    {
        "id": "irmaos-de-criancas-autistas",
        "title": "Irmãos de crianças autistas: como acolher e incluir",
        "body": "Irmãos de crianças autistas também vivem o impacto do diagnóstico e das demandas do dia a dia. É importante que eles **não se sintam esquecidos**.\n\nPossíveis sentimentos dos irmãos:\n\n- Ciúmes pela atenção extra que o irmão autista recebe.\n- Confusão sobre o que é o autismo.\n- Medo de sofrer bullying ou preconceito junto com o irmão.\n\nComo a família pode ajudar:\n\n- Explicar o autismo em uma linguagem adequada à idade.\n- Reservar momentos exclusivos com cada filho.\n- Envolver o irmão nas conquistas, comemorações e decisões simples.\n\n> Quando todos são ouvidos, a família se fortalece como um time.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "familia",
        "img_url": ""
    },
    {
        "id": "como-falar-de-autismo-com-a-crianca",
        "title": "Como falar de autismo com a criança",
        "body": "Contar para a criança que ela é autista pode parecer assustador para muitos pais, mas pode ser um momento de **alívio e entendimento**.\n\nDicas para essa conversa:\n\n- Escolha um momento calmo, sem pressa.\n- Use exemplos concretos: diferenças na forma de perceber sons, luzes ou na forma de se comunicar.\n- Mostre modelos positivos de pessoas autistas (personagens, influenciadores, histórias reais).\n\nFrases que podem ajudar:\n\n- \"Cada pessoa é diferente. O seu cérebro funciona de um jeito chamado autista, e isso explica algumas coisas sobre você.\"\n- \"Você não está sozinho, existem muitas pessoas autistas no mundo.\"\n\n> Falar sobre o autismo com sinceridade e carinho ajuda a criança a construir **autoestima e orgulho da própria identidade**.",
        "author_name": "Equipe Wiki TEA",
        "created_date": "2025-11-11",
        "topic_id": "consciencia",
        "img_url": ""
    },
]

# ---------------------- FUNÇÕES AUXILIARES ----------------------

def criar_topics():
    """Cria os tópicos usados nos posts, se ainda não existirem."""
    topic_ids = sorted({post["topic_id"] for post in posts})
    print("Criando tópicos (se ainda não existirem)...")

    for tid in topic_ids:
        payload = {"name": tid}  # o normalize() vai gerar o mesmo id
        resp = requests.post(BASE_URL_TOPIC, json=payload)
        # 400 = "Tópico já existe" -> ok, podemos ignorar
        if resp.status_code == 400:
            print(f" - Tópico '{tid}' já existe.")
        else:
            print(f" - Tópico '{tid}' -> Status {resp.status_code}")
    print("-" * 60)


def enviar_posts():
    if not os.path.exists(IMAGE_PATH):
        print(f"Imagem não encontrada em: {IMAGE_PATH}")
        return

    for post in posts:
        data = {
            "title": post["title"],
            "body": post["body"],
            "author_name": post["author_name"],
            "topic_id": post["topic_id"],
        }

        with open(IMAGE_PATH, "rb") as img_file:
            files = {
                "image": (os.path.basename(IMAGE_PATH), img_file, "image/jpeg")
            }

            print(f"Enviando post: {post['id']} ...")
            resp = requests.post(BASE_URL_POST, data=data, files=files)
            print("Status:", resp.status_code)
            try:
                print("Resposta:", resp.json())
            except Exception:
                print("Resposta (texto):", resp.text)

        print("-" * 60)

# ---------------------- MAIN ----------------------

def main():
    criar_topics()
    enviar_posts()

if __name__ == "__main__":
    main()

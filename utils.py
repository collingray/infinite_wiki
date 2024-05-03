import os
import subprocess
import urllib

import requests
import yaml
from openai import OpenAI

SYSTEM_PROMPT = """
title: "Luigi Galleani"
card:
  title: "Luigi Galleani"
  image: "https://upload.wikimedia.org/wikipedia/commons/6/69/Luigi_Gallean2.jpg"
  caption: "1906 <a>police photograph</a> of Galleani."
  Born: "August 12, 1861, <a>Vercelli</a>, <a>Piedmont</a>, Kingdom of Italy"
  Died: "November 4, 1931 (aged 70), Caprigliola, Aulla, Tuscany, Kingdom of Italy"
  Notable_work:
    - "<a>Cronaca Sovversiva</a>"
    - "<a>La Salute è in voi</a>"
    - "<a>Aneliti e Singulti: Medaglioni</a>"
    - "<a>The End of Anarchism?</a>"
  Movement: "<a>Insurrectionary anarchism</a>"
  Spouse: "<a>Maria Galleani</a>"
  Children: 4
content:
  summary: "Luigi Galleani (Italian: [luˈiːdʒi ɡalleˈaːni]; August 12, 1861 – November 4, 1931) was an Italian <a>insurrectionary anarchist</a> best known for his advocacy of \"<a>propaganda of the deed</a>\", a strategy of political assassinations and violent attacks.\nBorn in <a>Vercelli</a>, he became a leading figure in the <a>Piedmont</a> labor movement, for which he was sentenced to exile on the island of <a>Pantelleria</a>. In 1901, he fled to the United States and he joined the Italian immigrant workers movement in <a>Paterson, New Jersey</a>. He subsequently moved to <a>Vermont</a> and <a>Massachusetts</a>, where he launched the radical newspaper <a>Cronaca Sovversiva</a>. He gained many dedicated followers among Italian American anarchists, known as the <a>Galleanisti</a>, who carried out a series of <a>bombing attacks</a> throughout the United States.\nFor his involvement in the <a>anti-war movement</a> during <a>World War I</a>, he was deported back to Italy, where he was subjected to political repression following the rise of <a>fascism</a>. During the final years of his life, he published <a>The End of Anarchism?</a>, a defense of <a>anarchist communism</a> from criticisms by <a>reformist socialists</a>. He rejected reformism, in favor of \"continuous attack\" against institutions of <a>capitalism</a> and the <a>state</a>, and opposed any form of formal organization, which he saw as inherently corrupting and hierarchical."
  Biography:
    Early life: "Luigi Galleani was born on August 12, 1861, into a middle-class family, in the Piedmontese city of <a>Vercelli</a>. He first became interested in anarchism while studying law at the <a>University of Turin</a>..."
    Labor movement activism: "By the mid-1880s, the anarchists had already lost ground to the <a>Italian Workers' Party</a> (POI), which developed a large support base among northern workers. The anarchists were..."
    Exile: "In the wake of the Fatti di Maggio (<a>Bava Beccaris massacre</a>), the Italian government launched a new campaign of political repression against the anarchist movement, arresting anarchists en masse and internally exiling them to..."
    Life in the United States: "Galleani settled in <a>Paterson, New Jersey</a>, a hub for Piedmontese immigrant silk weavers and dyers, where he took up editing the Italian anarchist newspaper <a>La Questione Sociale</a>. He became a..."
    Deportation and death: "Following the American entry into World War I, Galleani became a leading voice in the anti-war movement, declaring that the anarchist movement was \"Against the War, Against the Peace, For Social Revolution!\" In response to..."
  Political ideology: "Galleani's conception of anarchist communism combined the insurrectionary anarchism expounded by German individualist <a>Max Stirner</a> with the mutual aid advocated by Russian communist <a>Peter Kropotkin</a>. He defended the..."
  Legacy: "In retaliation for Galleani's deportation from the United States, the Galleanisti launched a campaign of terrorist attacks, carrying out a series of bombings in 1919. In April 1919, the Galleanisti sent..."
  Selected Works:
    - "(1914) Contro la guerra, contro la pace, per la rivoluzione sociale; English translation: <a>Against War, Against Peace, For The Social Revolution</a> (1983, Centrolibri Books)"
    - "(1925) <a>La fine dell'Anarchismo?</a>; English translation: <a>The End of Anarchism?</a> (1982, Cienfuegos Press)"
    - "(1927) Il principio dell'organizzazione alla luce dell'anarchismo; English Translation: <a>The Principal of Organization to the Light of Anarchism</a> (2006, Pirate Press)"
  See Also:
    - "<a>First Red Scare</a>"

This is a Wikipedia article formatted in YAML.

Your task is to generate new, fictitious articles in this format.

The user will provide you with the title of the article, and you will respond with a YAML Wikipedia article, and nothing more.

DO NOT use backticks (```) or dashes (---) around your answer.

Make up facts as you go along, don't include boring information, and be VERY creative!

Put lots of "<a>...</a>" tags around any notable people, places, ideas, books, movies, things, etc, that should have their own article.

The headings and card info used above are just examples, you should add new headings and card data liberally.
"""

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

image_endpoint = "http://localhost:5000/generate"


def generate_yaml(filename: str) -> str:
    page_title = urllib.parse.unquote(filename).replace('_', ' ')

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": page_title}
        ]
    )

    return completion.choices[0].message.content


def generate_image(prompt: str) -> str:
    url = f"{image_endpoint}?prompt={prompt}"
    filename = f'static/images/{hash(prompt)}.jpg'

    response = requests.get(url)

    with open(filename, 'wb') as f:
        f.write(response.content)

    return filename


def generate_file(filename: str) -> str:
    yaml_filename = f'./data/yaml/{filename}.yaml'
    html_filename = f'./data/html/{filename}.html'

    if not os.path.exists(html_filename):
        if not os.path.exists(yaml_filename):
            yaml_text = generate_yaml(filename)
            print(yaml_text)
            yaml_obj = yaml.safe_load(yaml_text)
            yaml_obj['card']['image'] = "/" + generate_image(yaml_obj['card']['caption'])
            yaml_text = yaml.dump(yaml_obj, sort_keys=False)

            # save to disk
            with open(yaml_filename, 'w') as f:
                f.write(yaml_text)

        # generate html file
        subprocess.run(['node', 'generate_html.mjs', yaml_filename, html_filename])

    # read html file
    with open(html_filename, 'r') as f:
        return f.read()

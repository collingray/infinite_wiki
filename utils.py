import os
import subprocess
import urllib

import requests
import yaml

import anthropic

SYSTEM_PROMPT = """
Your task is to generate new, fictitious Wikipedia articles in a YAML format.

The user will give you the title of the article.

Respond with ONLY the YAML content of the article, without enclosing it in any other text.

Each section can either contain a single string, with paragraphs separated by newlines, or a list of strings, to represent bullet points.

If quotation marks are used, make sure to escape them with a backslash.

Take care with formatting, as the client will be very strict about this.

It is of utmost importance that all strings are properly quoted, and that all keys are followed by a colon.

Make up facts as you go along, don't include boring information, and be VERY creative!

Don't constrain yourself to reality, make things up.

If the user gives you a title that is illegible, then interpret it as an acronym and make up what it stands for.

Remember to include an image in the card, and make sure the image is relevant to the article.

Put in many <a> tags around any notable people, places, ideas, books, movies, things, or anything else that should have its own article.

Be specific, always name the exact place, person, or thing, and don't be vague.

You will also be paid an addition $1 per <a> tag that you use in the article, both in the card and the content.
"""

EXAMPLE_DIALOG = [
    {"role": "user", "content": "Luigi Galleani"},
    {"role": "assistant", "content": """title: "Luigi Galleani"
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
        Early life: "Luigi Galleani was born on August 12, 1861, into a middle-class family, in the Piedmontese city of <a>Vercelli</a>. He first became interested in anarchism while studying law at the University of Turin, eventually renouncing his career in law in order to carry out anarchist propaganda against capitalism and the state. His skill in oratory and writing quickly made him a leading voice in the new generation of the Italian anarchist movement. Alongside Sicilian anarchist <a>Pietro Gori</a>, he led a resurgence of militant anarchist activism, which gained a large following among the workers of Northern Italy."
        Labor movement activism: "By the mid-1880s, the anarchists had already lost ground to the <a>Italian Workers' Party</a> (POI), which developed a large support base among northern workers. The anarchists were initially skeptical of the POI, due to the latter's tendencies towards <a>workerism</a> and <a>reformism</a>, but relations between the two parties became more cordial over time. In 1887, Galleani led the Piedmontese anarchist movement's reorientation towards the labor movement and its rapprochement with the POI. That year, he established the Turin-based newspaper <a>Gazzetta Operaia</a>, formed a number of workers' organizations in <a>Vercelli</a>, and distributed revolutionary propaganda among the factory workers of <a>Biella</a>. In 1888, he went on a lecture tour in towns throughout <a>Piedmont</a> and led a series of strike actions by Piedmontese workers in both <a>Turin</a> and <a>Vercelli</a>, increasing support for the anarchist movement and the POI.\nRelations between the anarchists and the POI worsened, due to the latter's continued participation in local elections. Nevertheless, Galleani continued to pursue the anarchist infiltration of the POI, in order to attempt to bring it towards revolutionary socialism. He continued to advocate for a conciliatory approach between the reformists and revolutionaries, resulting in the POI both continuing its electoral participation while also endorsing class conflict. Although he prevented a formal split from occurring, the two factions were ultimately irreconciable and Galleani's attempts to transform the POI proved unsuccessful.\nWhen his radical activism threatened him with arrest, in 1889 he fled to <a>France</a> and then to <a>Switzerland</a>. There he collaborated with the French anarchist geographer <a>Élisée Reclus</a> in the preparation of his <a>Nouvelle Geographie Universalle</a> and organised a students' demonstration at the <a>University of Geneva</a>, in honor of the <a>Haymarket martyrs</a>. Galleani was also scheduled to attend the Italian anarchist movement's <a>Capolago congress</a>, but en route to the congress from <a>Geneva</a>, he was arrested by the Swiss authorities and expelled back to Italy. Back in Italy, he immediately continued his radical activities, embarking on a speaking tour of <a>Tuscany</a>, with the aim of fomenting an uprising on <a>International Workers' Day of 1891</a>.\nIn 1892, together with <a>Pietro Gori</a> and Calabrese anarchist <a>Giovanni Domanico</a>, Galleani was delegated to represent the anarchists at the <a>Genoa Workers' Congress</a>, with the intention of obstructing the motions of the dominant reformist faction. In opposition to the social democrats, led by Lombard lawyer <a>Filippo Turati</a>, an alliance was formed by the anarchists and the workerists, who both opposed political participation. On August 14, a fierce argument broke out between the anarchist and socialist delegates, leading to two separate meetings being convened the following day. Having finally forced the anarchists to split from the movement, Turati's social democratic majority established the new <a>Italian Socialist Party (PSI)</a>, despite the objections of Galleani and his fellow delegates, whose own attempts at forming an anarchist party were unsuccessful. The congress proved that Galleani's agitational campaign had ultimately failed to gain a mass following among the workers, leading to many Italian anarchists becoming disillusioned with the labor movement, which came under the direction of the PSI."
        Exile: "In the wake of the Fatti di Maggio (<a>Bava Beccaris massacre</a>), the Italian government launched a new campaign of political repression against the anarchist movement, arresting anarchists en masse and internally exiling them to small islands for up to five years, all without a trial. Galleani himself was swiftly arrested, convicted for conspiracy, and exiled to the Sicilian island of <a>Pantelleria</a>. There he met and married <a>Maria Rallo</a>, who already had a young son. Luigi and Maria Galleani had four children of their own.\nWith <a>Elisee Reclus</a>'s aid, Galleani managed escape from Italy to Egypt, where he stayed with other Italian immigrants for a year. When he was threatened with extradition back to Italy, he fled to the United States, arriving in October 1901, shortly after the assassination of United States President <a>William McKinley</a>."
    Political ideology: "Galleani's conception of anarchist communism combined the insurrectionary anarchism expounded by German individualist <a>Max Stirner</a> with the mutual aid advocated by Russian communist <a>Peter Kropotkin</a>. He defended the principles of revolutionary spontaneity, autonomy, diversity, self-determination and direct action, and advocated for the violent overthrow of the state and capitalism through propaganda of the deed.\nHe rejected all forms of formal organization, including anarchist federations and <a>labor unions</a>, and opposed participating in the labor movement, as he believed it was inherently reformist and susceptible to corruption. From his rejection of reformism, he concluded that social change could only be brought about through violent attacks against institutions, which he believed could build towards a popular insurrection. As such, he publicly endorsed terrorism, or what he called \"propaganda of the deed\", which came in the form of the assassination of authority figures and the expropriation of private property. Galleani defended both the assassination of <a>William McKinley</a> by <a>Leon Czolgosz</a> and the assassination of <a>Umberto I of Italy</a> by <a>Gaetano Bresci</a>.\nIn his own words, his ultimate aim was to establish \"a society without masters, without government, without law, without any coercive control—a society functioning on the basis of mutual agreement and allowing each member the freedom to enjoy absolute autonomy.\" But he also rejected prefigurative politics, such as that advocated by <a>anarcho-syndicalists</a>, as he believed that people themselves would instinctively understand how to live as a free and equal society once the state and capitalism were overthrown."
    Legacy: "In retaliation for Galleani's deportation from the United States, the Galleanisti launched a campaign of terrorist attacks, carrying out a series of bombings in 1919. In April 1919, the Galleanisti sent around thirty bombs out to government officials. Most of the bombs were intercepted and disarmed before reaching their destination, with only one detonating - injuring the intended target's maid. In June 1919, they carried out a coordinated attack of nine bombings throughout the North-eastern United States, but none of their targets were killed or gravely wounded. One of the bombs detonated prematurely outside Attorney General A. Mitchell Palmer's house, killing the attacker. Another bomb that was placed in a church detonated following its discovery by police, killing ten police officers and a bystander. In the political repression that followed, many of the Galleanisti were arrested, including Italian American anarchists <a>Nicola Sacco</a> and <a>Bartolomeo Vanzetti</a>, who were executed despite the lack of evidence against them. In reprisal, the Galleanist <a>Mario Buda</a> was alleged to have carried out the <a>Wall Street bombing</a> of 1920, which killed 33 people.\nDuring the 1930s, the Romanian American anarchist <a>Marcus Graham</a> attempted to revive the Galleanist movement with the <a>San Francisco-based newspaper Man!</a>, but its efforts were unsuccessful and the paper was shut down in 1939. By the time of the defeat of Italian Fascism in World War II, the Italian American anarchist movement had largely dissipated. The Galleanist <a>L'Adunata dei Refrattari</a> continued publication until 1971, when it was succeeded by the anti-authoritarian periodical <a>Fifth Estate</a>.\nBy the late-20th century, Galleani's figure fell into obscurity, receiving relatively little research from scholars. It was only in 1982, when <a>The End of Anarchism?</a> received a translation into English, that interest in him again began to grow. In 2006, more English translations of his work were published in a compilation by <a>AK Press</a>."
    Selected Works:
        - "(1914) Contro la guerra, contro la pace, per la rivoluzione sociale; English translation: <a>Against War, Against Peace, For The Social Revolution</a> (1983, Centrolibri Books)"
        - "(1925) <a>La fine dell'Anarchismo?</a>; English translation: <a>The End of Anarchism?</a> (1982, Cienfuegos Press)"
        - "(1927) Il principio dell'organizzazione alla luce dell'anarchismo; English Translation: <a>The Principal of Organization to the Light of Anarchism</a> (2006, Pirate Press)"
    See Also:
        - "<a>First Red Scare</a>"
"""},
    {"role": "user", "content": "The City of New New York"},
    {"role": "assistant", "content": """title: "The City of New New York"                                                                                                                                                                             
card:                                                                                                                                                                                                         
    title: "The City of New New York"
    image: "https://upload.wikimedia.org/wikipedia/commons/1/1f/Futuristic_city.jpg"
    caption: "Photo of the futuristic city of New New York, taken in the year 2934"
    Population: "140 million residents"
    Area: "3511 square miles"
    Established: "January 1, 2571"
    Mayor: "<a>Luna Rodriguez</a>"
    Nickname: "The City That Never Sleeps... Literally"
content:
    summary: "The City of New New York is a bustling metropolis located on the eastern coast of the <a>United Earth Federation</a>. Established in the year 2543, it is known for its futuristic architecture, advanced technology, and vibrant cultural scene. With a population of over 140 million residents, the city spans an area of 3511 square miles, making it one of the largest and most populous cities in the federation. It's slogan is \"The City That Never Sleeps... Literally\", a nod to the city's 24-hour lifestyle and bustling nightlife."
    History:
        Founding: "The City of New New York was founded on January 1, 2571, by a group of architects and urban planners, wishing to rebuild the fabled city of Old New York, destroyed in the <a>Second Rebellion of the Skies</a>. They set out to create a utopian city that would serve as a beacon of progress and innovation for the entire federation. The city quickly grew into a thriving hub of commerce, art, and entertainment."                                                                                     
        Technological Advancements: "New New York is at the forefront of technological innovation, with flying cars, teleportation devices, and automated robots being a common sight in the city. The skyline is dotted with towering skyscrapers made of glass and steel, showcasing the architectural prowess of the city's designers."                                                                                      
    Culture:
        Arts and Entertainment: "The city is a cultural melting pot, with art galleries, theaters, and music venues showcasing a diverse array of talent from across the federation. The annual <a>New New York Arts Festival</a> draws millions of visitors from far and wide to celebrate creativity and expression."                                                                                                         
        Cuisine: "New New York is renowned for its eclectic culinary scene, featuring a mix of traditional Earth cuisine and intergalactic flavors. Visitors can enjoy everything from classic pizza and burgers to alien \"delicacies\" from distant planets."                                                                                                                                                                     
    Governance:
        Mayor Rodriguez: "<a>Luna Rodriguez</a> was elected as the mayor of New New York in 3020, making history as the youngest mayor ever to hold office in the city. Mayor Rodriguez implemented numerous initiatives to maximize the productivity of the workforce, which the press referred to as \"The Lunar Revolution\". Her policies have been credited with boosting the city's economy and improving the quality of life for its residents."
        City Council: "The city council of New New York is composed of representatives from various districts within the city. They work together to pass legislation, allocate resources, and address the needs of the diverse population."
    Economy:
        Industries: "New New York is a hub for technology, finance, entertainment, and <a>intergalactic trade</a>. The city's economy is booming, with companies from around the federation setting up headquarters in the futuristic skyline of the metropolis."
        Tourism: "Tourism plays a significant role in the economy of New New York, with visitors flocking to the city to experience its vibrant culture, cutting-edge technology, and unique attractions. From virtual reality theme parks to underwater museums, there is something for everyone in the city."
    Notable Landmarks:
        - "<a>Galactic Tower</a>"
        - "<a>Infinity Park</a>"
        - "<a>RoboDome Arena</a>"
        - "<a>Stellar Opera House</a>"
    See Also:
        - "<a>United Earth Federation</a>"
        - "<a>New New York Times</a>"
        - "<a>Interstellar Travel</a>"
"""},
    {"role": "user", "content": "Richard Nixon's 2814 Presidential Campaign"},
    {"role": "assistant", "content": """title: "Richard Nixon's 2814 Presidential Campaign"
card:
    title: "Richard Nixon's 2814 Presidential Campaign"
    image: "https://upload.wikimedia.org/wikipedia/commons/4/4f/Richard_Nixon_presidential_portrait.jpg"
    caption: "Official portrait of President Richard Nixon, 2814"
    Candidate: "<a>Richard Nixon</a>"
    Running Mate: "<a>John F. Kennedy Jr. Jr. Jr. Jr.</a>"
    Party: "<a>Neo Republican Party</a>"
    Campaign Slogan: "Nixon's back, baby!"
    Campaign Headquarters: "New Washington, D.C."
content:
    summary: "Richard Nixon's 2814 Presidential Campaign was a historic event in the history of the United States, marking the return of the former president to the political arena. Running as the candidate of the Neo Republican Party, Nixon sought to reclaim the presidency after a 700-year absence. His running mate, John F. Kennedy Jr. Jr. Jr. Jr., was a popular figure in his own right, known for his work in the field of <a>quantum diplomacy.</a>"
    Background:
        Return to Politics: "After being cryogenically frozen for over seven centuries, Richard Nixon was revived in the year 2814 by a team of scientists working for the Neo Republican Party. Eager to make his mark on history once again, Nixon announced his intention to run for president, citing the need for strong leadership in a time of intergalactic turmoil."
        Selection of Running Mate: "John F. Kennedy Jr. Jr. Jr. Jr. was chosen as Nixon's running mate due to his popularity among voters and his expertise in quantum diplomacy, a field that had become increasingly important in the age of <a>interstellar relations</a>. Together, Nixon and Kennedy formed a formidable team, promising to bring stability and prosperity to the galaxy."
    Campaign Platform:
        Economic Reform: "Nixon's platform focused on revitalizing the economy of the United States and its interstellar territories, promising to create new jobs and stimulate growth through economic reforms and <a>galactic terraforming</a> projects. He also pledged to repeal child labor laws and increase the retirement age to 200."
        Foreign Policy: "Kennedy's expertise in quantum diplomacy played a key role in shaping the campaign's foreign policy platform, which emphasized peaceful relations with alien civilizations and cooperation on issues of mutual interest."
        Technology: "Nixon's campaign pledged to invest in cutting-edge technologies, such as <a>hyperspace travel</a> and <a>terraforming</a>, to ensure the continued prosperity of the United States and its allies."
    Controversies:
        Time Travel Scandal: "During the campaign, rumors surfaced that Nixon had used a time machine to alter the course of history and secure his victory. Nixon staunchly denied the claims, famously claiming \"I am not a time traveler!\". Although these allegations were never proven, they cast a shadow over the campaign and raised questions about the integrity of the electoral process."
        Alien Endorsements: "Nixon's campaign was dogged by allegations of receiving endorsements from extraterrestrial beings, leading to accusations of foreign interference in the election. Despite these claims, Nixon denied any wrongdoing and continued to campaign vigorously until election day. He would later describe that the allegations were \"entirely accurate\", and that the aliens had been \"very helpful to his cause\"."
    Legacy:
        Victory: "In a stunning upset, Nixon and Kennedy won the 2814 presidential election by a narrow margin, defeating the incumbent president, <a>Barack Obama XIV</a>. Their victory marked a new era in American politics, ushering in a period of unprecedented prosperity and cooperation with alien civilizations."
        Nixon's Presidency: "As president, Nixon worked to implement his campaign promises, overseeing the construction of the <a>Interstellar Trade Center</a> and the signing of the <a>Galactic Peace Accords</a>. His administration was marked by a spirit of optimism and innovation, setting the stage for a new era of interstellar cooperation and progress."
    See Also:
        - "<a>Neo Republican Party</a>"
        - "<a>John F. Kennedy Jr. Jr. Jr. Jr.</a>"
        - "<a>Interstellar Relations</a>"
"""},
]

client = anthropic.Anthropic()

image_endpoint = "http://localhost:5000/generate"


def generate_yaml(filename: str) -> str:
    page_title = urllib.parse.unquote(filename).replace('_', ' ')

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        messages=EXAMPLE_DIALOG + [{"role": "user", "content": page_title}],
        max_tokens=2048,
        system=SYSTEM_PROMPT,
    )

    return message.content[0].text


def generate_image(prompt: str) -> str:
    url = f"{image_endpoint}?prompt={prompt}"

    return requests.get(url).json()['path']


def generate_file(filename: str) -> str:
    yaml_filename = f'./data/yaml/{filename}.yaml'
    html_filename = f'./data/html/{filename}.html'

    if not os.path.exists(html_filename):
        if not os.path.exists(yaml_filename):
            try:
                yaml_text = generate_yaml(filename)
                yaml_obj = yaml.safe_load(yaml_text)
                yaml_obj['card']['image'] = "/" + generate_image(yaml_obj['card']['caption'])
                yaml_text = yaml.dump(yaml_obj, sort_keys=False)
            except Exception as e:
                with open(f'./data/errors/{filename}.yaml', 'w') as f:
                    f.write(yaml_text)

                with open(f'./data/errors/{filename}.err', 'w') as f:
                    f.write(str(e))

                raise e

            # save to disk
            with open(yaml_filename, 'w') as f:
                f.write(yaml_text)

        # generate html file
        subprocess.run(['node', 'generate_html.mjs', yaml_filename, html_filename])

    # read html file
    with open(html_filename, 'r') as f:
        return f.read()

import ollama
import subprocess
import platform
from core.utilities.file_processing import FileProcessing

input_file = "D:/DavidLammy_reposters.csv"
output_file = "D:/DavidLammy_reposters_ollama.csv"

def ollama_serve():
    command = "ollama serve"
    if platform.system() == "Windows":
        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
    else:
        # macOS or Linux - use the default terminal (e.g., bash)
        subprocess.Popen(['open', '-a', 'Terminal', command] if platform.system() == "Darwin" else ['x-terminal-emulator', '-e', command], shell=True)

def generate_model_response(user_location):
    response = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'user',
            'content': f"""
            Here is the list of countries:

                Afghanistan
                Albania
                Algeria
                Andorra
                Angola
                Antigua and Barbuda
                Argentina
                Armenia
                Australia
                Austria
                Azerbaijan
                Bahamas
                Bahrain
                Bangladesh
                Barbados
                Belarus
                Belgium
                Belize
                Benin
                Bhutan
                Bolivia, Plurinational State of
                Bosnia and Herzegovina
                Botswana
                Brazil
                Brunei Darussalam
                Bulgaria
                Burkina Faso
                Burundi
                Cabo Verde
                Cambodia
                Cameroon
                Canada
                Central African Republic
                Chad
                Chile
                China
                Colombia
                Comoros
                Congo
                Congo, Democratic Republic of the
                Costa Rica
                CÃ´te d'Ivoire
                Croatia
                Cuba
                Cyprus
                Czechia
                Denmark
                Djibouti
                Dominica
                Dominican Republic
                Ecuador
                Egypt
                El Salvador
                Equatorial Guinea
                Eritrea
                Estonia
                Eswatini
                Ethiopia
                Fiji
                Finland
                France
                Gabon
                Gambia
                Georgia
                Germany
                Ghana
                Greece
                Grenada
                Guatemala
                Guinea
                Guinea-Bissau
                Guyana
                Haiti
                Honduras
                Hungary
                Iceland
                India
                Indonesia
                Iran, Islamic Republic of
                Iraq
                Republic of Ireland
                Israel
                Italy
                Jamaica
                Japan
                Jordan
                Kazakhstan
                Kenya
                Kiribati
                Korea, Democratic People's Republic of
                Korea, Republic of
                Kuwait
                Kyrgyzstan
                Lao People's Democratic Republic
                Latvia
                Lebanon
                Lesotho
                Liberia
                Libya
                Liechtenstein
                Lithuania
                Luxembourg
                Madagascar
                Malawi
                Malaysia
                Maldives
                Mali
                Malta
                Marshall Islands
                Mauritania
                Mauritius
                Mexico
                Micronesia, Federated States of
                Moldova, Republic of
                Monaco
                Mongolia
                Montenegro
                Morocco
                Mozambique
                Myanmar
                Namibia
                Nauru
                Nepal
                Netherlands
                New Zealand
                Nicaragua
                Niger
                Nigeria
                North Macedonia
                Norway
                Oman
                Pakistan
                Palau
                Panama
                Papua New Guinea
                Paraguay
                Peru
                Philippines
                Poland
                Portugal
                Qatar
                Romania
                Russian Federation
                Rwanda
                Saint Kitts and Nevis
                Saint Lucia
                Saint Vincent and the Grenadines
                Samoa
                San Marino
                Sao Tome and Principe
                Saudi Arabia
                Senegal
                Serbia
                Seychelles
                Sierra Leone
                Singapore
                Slovakia
                Slovenia
                Solomon Islands
                Somalia
                South Africa
                South Sudan
                Spain
                Sri Lanka
                Sudan
                Suriname
                Sweden
                Switzerland
                Syrian Arab Republic
                Tajikistan
                Tanzania, United Republic of
                Thailand
                Timor-Leste
                Togo
                Tonga
                Trinidad and Tobago
                Tunisia
                TÃ¼rkiye
                Turkmenistan
                Tuvalu
                Uganda
                Ukraine
                United Arab Emirates
                United Kingdom of Great Britain and Northern Ireland
                United States of America
                Uruguay
                Uzbekistan
                Vanuatu
                Venezuela, Bolivarian Republic of
                Vietnam
                Yemen
                Zambia
                Zimbabwe

            You are an expert in geography. 

            You assess a social media user's location to see if it can be interpreted to be geographically within one of the countries on my list.

            To be interpretable the location must be a valid geographic location.

            If the location is interpreted in another language it must be converted to english.

            You can interpret a language code as a country.

            Some examples of locations that are uninterpretable are: 
            - "United Kingdom and Thailand" this is invalid as it is two separate locations in different countries.
            - "🇬🇧 and 🇪🇸" this is invalid because it's two country codes, and only one country code can be interpreted.
            - "your mum's house" this is invalid becuase it's a phrase / joke and not a location.
            - "Still Plague Island" this is invalid becuase it's a phrase / joke and not a location.
            - "where you expect it least" this is invalid becuase it's a phrase / joke and not a location.
            - "Europe" this is invalid because it's not within a country but rather extranational.
            - "The World" this is invalid because it's not within a country but rather extranational.

            Your only response should be either [a country as it is written in the list] or [uninterpretable]. 

            Return your response within [].

            You must not include any other text such as your reasoning or processing in your response. 

            Social media user's location: {user_location}
            """,
        }
    ],
                           options={
                               "num_predict": 512,
                               "top_k": 40,
                               "top_p": 0.9,
                               "tfs_z": 1.0,
                               "repeat_last_n": 64,
                               "temperature": 0.1
                           })

    return response['message']['content']


def aggregate_location():
    input_data = FileProcessing.import_from_csv(input_file)
    output = []

    processed_count = 0

    for input_row in input_data:
        processed_count += 1

        user_location = input_row["Location"]
        ollama_location = ""
        if user_location != "":
            ollama_location = generate_model_response(user_location)

        output_row = {
            "User Location": user_location,
            "Ollama Location": ollama_location,
        }

        print(f"\n========== PROCESSING LOCATION #{processed_count}==========\n")
        print(f"\n{output_row}\n")

        output.append(output_row)

        FileProcessing.export_to_csv(output_file, output)

    print(f"\nFINISHED")
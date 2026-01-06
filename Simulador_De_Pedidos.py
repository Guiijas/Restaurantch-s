from datetime import datetime
import requests
from requests.structures import CaseInsensitiveDict
from requests.exceptions import HTTPError
import sqlite3

connection = sqlite3.connect("reservas.db") 
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS reservas(id_restaurante, usuario, data, horario, mesa)")


city_name = input(("Insira o nome da cidade que deseja ver os pontos de interesse!\n"))
distance_meter = int(input("Insira a distância do raio de procura em KM's para encontrar os restaurantes!\n"))
distance_formatted = distance_meter * 1000

adress_id = f"https://api.geoapify.com/v1/geocode/search?text={city_name},Brasil&lang=en&type=city&apiKey=142450b56fd049deb82c8d8ee8710a15"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
resp = requests.get(adress_id, headers=headers)
data_id = resp.json()

#print(resp.status_code)

for feature in data_id["features"]:
    properties = feature["properties"]
    lon = properties.get("lon")
    lat = properties.get("lat")
    if properties.get("city").lower() == city_name.lower():
        lon_lat = {
            "longitude":lon,
            "latitude":lat,
        }

city_lon = lon_lat["longitude"]
city_lat = lon_lat["latitude"]
#print(city_lon, city_lat)


url = f"https://api.geoapify.com/v2/places?categories=catering.restaurant&filter=circle:{city_lon},{city_lat},{distance_formatted}&limit=50&apiKey=142450b56fd049deb82c8d8ee8710a15"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"

try:
    response =  requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    print("Everything went ok and the communication has been established!")
except HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"Other error occurred: {err}")
    
restaurantes = []

for feature in data["features"]:
    props = feature["properties"]
    nome = props.get("name")
    restaurantes.append(nome)
#print(restaurantes)


restaurantes_menu = {item[0] : item[1] for item in zip(range(0, len(restaurantes)), restaurantes)}

print("------------------------")
print("Restaurantes da Região!")
print("------------------------")

for key, value in restaurantes_menu.items():
    print(f"{key} - {value}")


while True:
    try:
        id_restaurante = int(input("\nDigite o id do restaurante que deseja fazer a reserva.\n"))
        if id_restaurante not in restaurantes_menu:
            raise ValueError("Não existe nenhum restaurante com esse id!")
    except ValueError as e:
        print(e)
        continue
    else:
        break

for key in restaurantes:
    if id_restaurante == key:
        print(f"Bem-Vindo ao {restaurantes[id_restaurante]} ")
        break

def reservar_mesa():

    while True:    
        try:
            usuario = input((f"Insira seu nome para registrar a reserva em {restaurantes[id_restaurante]}!\n"))
            valida_usuario = any(char.isdigit() for char in usuario)
            if valida_usuario == True:
                raise ValueError("Error: digite um nome válido!")
        except ValueError as e:
            print(e)
            continue
        else:
            break
    while True:

        try:
            data = input(("Que dia deseja fazer a reserva? (Y-M-D)\n"))
            formato = "%Y-%m-%d"
            data_ = datetime.strptime(data, formato)
        except ValueError:
            print("Formato de data inválido! tente ANO-MES-DIA")
            continue
        else:
            break

    while True:
        try:
            horario = input(("Qual horario deseja fazer a reserva?\n"))
            hora_formatada = "%H:%M"
            hora = datetime.strptime(horario, hora_formatada)   
        except ValueError:
            print("O formato inserido da hora está incorreto, formato certo (Hora:Minuto)")
            continue
        else:
            break
    while True:
        try:
            qtd_pessoas = input("Mesa para quantas pessoas?\n")
            valida_quantidade = any(char.isalpha() for char in qtd_pessoas)
            if valida_quantidade == True:
                raise ValueError("A quantidade de pessoas deve conter somente números!")
        except ValueError as e:
            print(e)
            continue
        else:
            break
    return usuario, data, horario, qtd_pessoas
    

reserva = reservar_mesa()
print(f"Nome: {reserva[0]}\nData: {reserva[1]}\nHorario: {reserva[2]}\nMesa Para: {reserva[3]} pessoas\nRestaurante: {restaurantes[id_restaurante]}")


def valida_informacoes():
    while True:
        confirmacao = input(("\nAs informações acima estão corretas?\n"))

        if confirmacao.lower() == "sim":
            print(f"Sua reserva no restaurante {restaurantes[id_restaurante]} foi feita com sucesso!")
            break
        else:
            print("Por favor preencha os campos novamente trocando as informações!")
            reservar_mesa()
            continue

valida = valida_informacoes()

def Armazena_reserva():
    informacoes_reserva = [id_restaurante, reserva[0], reserva[1], reserva[2], reserva[3]]
    return informacoes_reserva

dados_reserva = Armazena_reserva()


Dados = [
    (dados_reserva),
]

cursor.executemany("INSERT INTO reservas VALUES(?, ?, ?, ?, ?)", Dados)
connection.commit()


for row in cursor.execute("SELECT * FROM reservas"):
    print(row)





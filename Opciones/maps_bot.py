from turtle import distance
import requests
import urllib
import locale
locale.setlocale(locale.LC_ALL, 'es-ES')

api_url="http://www.mapquestapi.com/directions/v2/route?"
key = "AAS76Zb0bjeEQVKeGU04ZfVa3GOxVApG"

#print(json_data)
# print(url)

while True:
    origin = input("ingresa el origen: ")
    if origin == 'q':
        break
    destination= input("ingrese destino: ")
    if destination == 'q':
        break
    
    url = api_url + urllib.parse.urlencode({"key":key, "from":origin, "to":destination})
    json_data = requests.get(url).json()
    status_code = json_data["info"]["statuscode"]
    
    if status_code == 0:
        trip_duration = json_data["route"]["formattedTime"]
        distance = json_data["route"]["distance"] * 1.61
        fuel_used = json_data["route"]["fuelUsed"] * 3.79
        print("=======================================")
        print(f"Información del viaje desde {origin.capitalize()} hasta {destination.capitalize()}")
        print(f"Duración del viaje: {trip_duration}")
        print("Distancia: " + str("{:.2f}".format(distance)+" km."))
        print("Combustible utilizado: " + str("{:.2f}".format(fuel_used)+" litros."))
        print("========================================")
        print("Indicaciones del Viaje")
        
        for each in json_data["route"]["legs"][0]["maneuvers"]:
            distance_remaining = distance - each["distance"] * 1.61
            print(each["narrative"] + "(" + str("{:.2f}".format(distance_remaining)+" km faltantes)."))
            distance = distance_remaining
            
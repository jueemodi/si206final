import sqlite3
import requests
import json
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
#make a list of countries, loop through, create new request call, save the data 
base_url = "https://corona.lmao.ninja/v3/covid-19/countries/"
country_list = ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola",
"Argentina","Armenia", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh",
"Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Botswana",
"Brazil", "Brunei", "Bulgaria", "Burundi", "Cambodia", "Cameroon", "Canada", "Chad",
"Chile", "China", "Colombia", "Comoros", "Croatia", "Cuba", "Cyprus", "Denmark",
"Djibouti", "Dominica", "Ecuador", "Egypt", "Eritrea", "Estonia", "Eswatini",
"Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana",
"Greece", "Grenada", "Guatemala", "Guinea", "Guyana", "Haiti", "Honduras", "Hungary",
"Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", 
"Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait",
"Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
"Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali",
"Malta", "Mauritania", "Mauritius", "Mexico", "Moldova", "Monaco", "Mongolia",
"Montenegro", "Morocco", "Mozambique", "Namibia", "Nauru", "Nepal", "Netherlands",
"Nicaragua", "Niger", "Nigeria", "Norway", "Oman", "Pakistan", "Palau", "Panama", 
"Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia",
"Rwanda", "Samoa", "Senegal", "Serbia", "Seychelles", "Singapore", "Slovakia", "Slovenia",
"Somalia", "Spain", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan",
"Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Tunisia", "Turkey", "Uganda", "Ukraine", "UAE", "UK", "USA", "Uruguay", "Uzbekistan", "Vanuatu",
"Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"]
country_data = [] #why list

#for each country, Dominicacreates a dict including active&critical cases + cases&deaths&tests per 1 million
# for country in country_list:
#     url = base_url + country
#     resp = requests.get(url)
#     data = resp.text
#     json_data = json.loads(data)
#     country_data.append(json_data)

# def setUpCountryList(filename):
#     full_path = os.path.join(os.path.dirname(__file__), filename)
#     f = open(full_path)
#     file_data = f.read()
#     f.close()
#     print(file_data)
#     return file_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def getCount(): 
    #gets the rowcount so we know how many countries to add and where to start
    #returns list of 25 countries from original country list
    
    cur, conn = setUpDatabase('countries.db')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS country_totals 
                    (cont INTEGER, country TEXT, casesPerMill NUMBER, deathsPerMill NUMBER,  
                    testsPerMill NUMBER, recoveredPerMill NUMBER)
                    ''')
    cur.execute("SELECT COUNT(*) FROM country_totals") 
    conn.commit()
    rows = cur.fetchone()[0]
    
    if rows < 25:
        countries = country_list[:25]
    elif rows >= 25 and rows < 50:
        countries = country_list[25:50]
    elif rows >= 50 and rows < 75:
        countries = country_list[50:75]
    elif rows >= 75 and rows < 100:
        countries = country_list[75:100]
    elif rows >= 100 and rows < 125:
        countries = country_list[100:125]
    elif rows >= 125 and rows < 150:
        countries = country_list[125:150]
    elif rows >= 150 and rows < 175:
        countries = country_list[150:175]
    elif rows >= 175 and rows < 200:
        countries = country_list[175:200]
    elif rows >= 200 and rows < 225:
        countries = country_list[200:225]

    return countries 

def createContinentTable(cur, conn):
    continents = ["Europe", "N. America", "S.America", "Asia", "Africa", "Australia", "Antarctica"]
    cur.execute("CREATE TABLE IF NOT EXISTS Continents (id INTEGER PRIMARY KEY, continent TEXT UNIQUE)")
    for i in range(len(continents)):
       cur.execute("INSERT OR IGNORE INTO Continents (id,continent) VALUES (?,?)",(i,continents[i]))
    conn.commit()

def createCountryTable(countries, cur, conn): #creates a table of countries and their respective covid data per 1 mill

    for country in countries: #use slices
        url = base_url + country
        resp = requests.get(url)
        data = resp.text
        json_data = json.loads(data)
        country_data.append(json_data)

        #creates a table
    
        country = json_data["country"]
        casesPerMill = float(json_data["casesPerOneMillion"])
        deathsPerMill = float(json_data["deathsPerOneMillion"])
        testsPerMill = float(json_data["testsPerOneMillion"])
        recoveredPerMill = float(json_data["recoveredPerOneMillion"])
        continent = str(json_data["continent"])

        #getting continent ID 
        if continent == "Europe":
            cont_id = 0
        elif continent == "North America":
            cont_id = 1
        elif continent == "South America":
            cont_id = 2
        elif continent == "Asia":
            cont_id = 3
        elif continent == "Africa":
            cont_id = 4
        elif continent == "Australia":
            cont_id = 5
        elif continent == "Antarctica":
            cont_id = 6
        else:
            cont_id=10
        
        

        cur.execute('''INSERT OR IGNORE INTO country_totals  
                    (cont, country, casesPerMill, deathsPerMill, testsPerMill, recoveredPerMill) VALUES (?, ?, ?, ?, ?, ?)''', 
                    (cont_id, country, casesPerMill, deathsPerMill, testsPerMill, recoveredPerMill))

        
        #break countries into lists of 25, if rows in table was <25, get data from first list
        #if b/w 25-50 do the second list 
        #function to count length of table
        #select count function from table 
    conn.commit()
    

def main():
    cur, conn = setUpDatabase("countries.db")
    countries = getCount()
    createCountryTable(countries, cur, conn)
    createContinentTable(cur, conn) #have counts here and pass in parameter to this function, what iteration is it, run a diff slice

main()


    


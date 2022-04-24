from audioop import avg
import sqlite3
from turtle import color
import requests
import json
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

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

def setUpDatabase(db_name):
    '''
    Create the database and return the cursor and connection objects.
    Used in function to update databses
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def calculate(file):
    
    #calc avg number of deaths across countries in list
    cur, conn = setUpDatabase("countries.db")
    avg_death = cur.execute("SELECT AVG(deathsPerMill) FROM country_totals").fetchone()[0]
    avg_cases = cur.execute("SELECT AVG(casesPerMill) FROM country_totals").fetchone()[0]
    

    europe_avgdeaths = cur.execute("""
                SELECT AVG(country_totals.deathsPerMill)
                FROM country_totals JOIN continents
                ON country_totals.cont = continents.id
                WHERE country_totals.cont = 0
                """).fetchone()[0]

    #writes avgs to file
    full_path = os.path.join(os.path.dirname(__file__), file)
    with open(full_path, 'w') as fname:
        fname.write("Avg Deaths Per Mill:\n")
        fname.write(str(avg_death))
        fname.write("\nAvg Cases Per Mill:\n")
        fname.write(str(avg_cases))
        fname.write("\nAvg Deaths Per Mill in Europe:\n")
        fname.write(str(europe_avgdeaths))

def visual(file):
    #creating bar chart to show a the avg cases vs avg deaths
    #also bar chart showing US deaths compared to avg deaths
    cur, conn = setUpDatabase("countries.db")
    avg_tests = float(cur.execute("SELECT AVG(testsPerMill) FROM country_totals").fetchone()[0])
    avg_cases = float(cur.execute("SELECT AVG(casesPerMill) FROM country_totals").fetchone()[0])
    objects = ("avg_tests","avg_cases")
    #neither are showing up?
    y_pos = np.arange(len(objects))
    performance = [avg_tests, avg_cases]

    plt.bar(y_pos, performance, align='center', alpha=0.5, color = "red")
    plt.xticks(y_pos, objects)
    plt.ylabel('Averages')
    plt.title('Average Cases & Tests Per Million for All Countries')

    plt.show()


def main():
    calculate("file.txt")
    visual("file.txt")

main()
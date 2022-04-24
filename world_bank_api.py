import requests
import json
import sys
import os
import matplotlib
import sqlite3
import unittest
import csv
import matplotlib.pyplot as plt
import pprint
import time


# get 25 or less country's GDP and popualtion data in 2020 from the world bank api, 
# return a dictionary with country name as key and the GDP and population data in a list as value
def get_data():
    page = input('What page of data from the World Bank API do you want?')
    
    format = 'JSON'
    indicator_gdp = 'NY.GDP.MKTP.CD'
    per_page = 25
    url_1 = f'http://api.worldbank.org/v2/country/all/indicator/{indicator_gdp}?date=2020&format={format}&page={page}&per_page={per_page}'
    gdp_info = requests.get(url_1)
    gdp_info = json.loads(gdp_info.text)

    # Popu data
    indicator_popu = 'SP.POP.TOTL'
    url_2 = f'http://api.worldbank.org/v2/country/all/indicator/{indicator_popu}?date=2020&format={format}&page={page}&per_page={per_page}'
    popu_info = requests.get(url_2)
    popu_info = json.loads(popu_info.text)

    # put in a dictionary together
    data_dict = {}
    count = 0
    for country_dict in gdp_info[1]:
        # If world bank doesn't have GDP data for this country, skip it
        if country_dict['value'] == None:
            count += 1
            continue
        else:
            name = country_dict['country']['value']
            gdp = float(country_dict['value'])
            popu = popu_info[1][count]['value']
            count += 1
            data_dict[name] = [gdp, popu]
    
    return data_dict

# sets up database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def create_country(data, cur, conn):
    # create the GDP table
    print('creating GDP table')
    cur.execute('CREATE TABLE IF NOT EXISTS GDP (id INTEGER PRIMARY KEY, name TEXT UNIQUE, gdp NUMBER, popu INTEGER)')
    conn.commit()
    
    for country_name in data.keys():
        gdp = data[country_name][0]
        popu = data[country_name][1]
        cur.execute("INSERT OR IGNORE INTO GDP (name, gdp, popu) VALUES(?,?,?)", (country_name, gdp, popu))
        conn.commit()

def calculate_gdp_per_capita(filename, cur, conn):
    cur.execute('SELECT name, gdp/popu FROM GDP')
    person_gdp = cur.fetchall()

    with open(filename, 'w') as f:
        f.write("Writing the calculation for a country's GDP per capita in the database")
        f.write('\n')
        for index in range(len(person_gdp)):
            f.write(person_gdp[index][0])
            f.write(',')
            f.write(str(person_gdp[index][1]))
            f.write('\n')

def make_graph_highest_gdp(cur):  
    cur.execute('SELECT name, gdp/popu FROM GDP')
    person_gdp = cur.fetchall()

    # sort the list of tuples
    person_gdp.sort(key = lambda x:x[1], reverse = True)

    country, gdp = zip(*person_gdp)
    country = country[:5]
    gdp = gdp[:5]

    plt.xlabel('countries with the highest GDP per capita')
    plt.ylabel('USD $')

    plt.scatter(country, gdp)
    plt.show()

def make_graph_lowest_gdp(cur):
    cur.execute('SELECT name, gdp/popu FROM GDP')
    person_gdp = cur.fetchall()

    # sort the list of tuples
    person_gdp.sort(key = lambda x:x[1])

    country, gdp = zip(*person_gdp)
    country = country[:5]
    gdp = gdp[:5]

    plt.xlabel('countries with the highest GDP per capita')
    plt.ylabel('USD $')

    plt.scatter(country, gdp)
    plt.show()

    
def main():
    data = get_data()
    # change this to 'country'
    cur, conn = setUpDatabase('test.db')
    create_country(data, cur, conn)
    calculate_gdp_per_capita('calculations.csv', cur, conn)

    # uncomment one of these to make a scatter plot, at the end, when all wanted data is in the database
    make_graph_highest_gdp(cur)
    # make_graph_lowest_gdp(cur)

if __name__ == "__main__":
    main()
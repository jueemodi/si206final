from inspect import formatargvalues
import sqlite3
import requests
import os
import json
import matplotlib.pyplot as plt


#add like 5 more countries as buffer !!

def get_data(db_name): 
    base_url = "https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/averages"
    params_dict = {'date_from':'2021-01-01T00:00:00+00:00', 'date_to':'2021-12-31T00:00:00+00:00', 'country_id':"", 'limit': 25, 'offset':0, 'sort': 'desc', 'spatial':'country', 'temporal':'year', 'group':'false'}
    country_list = ['AE', 'KR', 'SA', 'PR', 'PG', 'NZ', 'AF', 'AO', 'AR', 'AM', 'AU', 'AZ', 'BE', 'BZ', 'BO', 'BR', 'BG',  'CM', 'CA', 'TD', 'CL', 'CN',  'HR', 'CY', 'DK', 'EC', 'EE','ET', 'FI', 'FR',  'DE', 'GH', 'GR', 'GT', 'GY', 'HN', 'HU', 'IS', 'IN', 'ID', 'IE', 'IL', 'IT', 'JP', 'JO', 'KZ', 'KE',  'XK', 'KW', 'KG','LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LT', 'LU', 'MG','MY', 'MT', 'MR', 'MX',  'MN',  'MA', 'MZ',  'NP','NE', 'NG', 'NO', 'PK', 'PE', 'PH', 'PL', 'PT','QA', 'RO', 'RU', 'RW', 'SN', 'RS', 'SK', 'SI', 'ES', 'SD', 'SE', 'CH',  'TW', 'TZ', 'TH', 'TG', 'TR', 'UG', 'UA', 'GB', 'US', 'UZ',  'VE', 'VN', 'YE', 'ZM', 'ZW']
   
    result_list = []
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS Aqi2020 (name TEXT, pm25_ave FLOAT, pm10_ave FLOAT, no2_ave FLOAT, so2_ave FLOAT, co_ave FLOAT)')
    cur.execute('SELECT COUNT (*) FROM Aqi2020')
    conn.commit()
    rows = cur.fetchone()[0]
    if rows < 25: 
        country_list = country_list[:25]
    elif rows >= 25 and rows < 50: 
        country_list = country_list[25:50]
    elif rows >= 50 and rows < 75: 
        country_list = country_list[50:75]
    elif rows >= 75 and rows < 100:
        country_list = country_list[75:100]
    else: 
        country_list = country_list[100:]

    for country in country_list:
    # update params _dict
        params_dict['country_id'] = country
        req_c = requests.get(base_url, params = params_dict)
        countries = json.loads(req_c.text)
        result_list.append(countries)
    #request call 
    
    # loop over the data to find the dictionary you want data['results'] and save to dict 
    
    country_dict = {}
    for country_data in result_list: 
        results = country_data['results']
        for data in results: # Could loop through the country list, find the first instance of that name in the response, then start a while name == *name of outerloop variable* from there. Keep the four flags and the continue check I made
            country_name = data['subtitle']
            if country_name not in country_dict: 
                country_dict[country_name] = {}
            pollutants_dict = country_dict[country_name] 
            if data['parameter'] == 'pm10': 
                pollutants_dict['pm10'] = data['average']
            elif data['parameter'] == 'pm25': 
                pollutants_dict['pm25'] = data['average']
            elif data['parameter'] == 'no2': 
                pollutants_dict['no2'] = data['average']
            elif data['parameter'] == 'so2': 
                pollutants_dict['so2'] = data['average']
            elif data['parameter'] == 'co': 
                pollutants_dict['co'] = data['average']
            country_dict[country_name] = pollutants_dict
    return country_dict 

def setUpDatabase(db_name, country_dict): 
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
   # cur.execute('CREATE TABLE IF NOT EXISTS Aqi2020 (name TEXT, pm25_ave FLOAT, pm10_ave FLOAT, no2_ave FLOAT, so2_ave FLOAT, co_ave FLOAT)')
    
    for name in country_dict: 
        inner = country_dict[name]
        curpm25 = inner.get('pm25', 'NULL') 
        curpm10 = inner.get('pm10', 'NULL') 
        curso2 = inner.get('so2', 'NULL') 
        curno2 = inner.get('no2', 'NULL') 
        curco = inner.get('co', 'NULL')
        cur.execute('INSERT OR IGNORE INTO Aqi2020 (name, pm25_ave, pm10_ave, no2_ave, so2_ave, co_ave) VALUES (?,?,?,?,?,?)', (name, curpm25,curpm10, curno2, curso2, curco,))
    conn.commit()


def calculate_averages(db_name): 
    total_pm25 = 0
    total_pm10 = 0
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    cur.execute('SELECT COUNT (*) FROM Aqi2020')
    rows = cur.fetchone()[0]
    cur.execute('SELECT * FROM Aqi2020')
    for row in cur: 
        total_pm25 += float(row[1])
        total_pm10 += float(row[2])
    global_pm25 = total_pm25/rows
    global_pm10 = total_pm10/rows

    full_path = os.path.join(os.path.dirname(__file__), 'calc.txt')
    with open(full_path, 'w') as fname:
        fname.write("Avg Global PM2.5:\n")
        fname.write(str(global_pm25))
        fname.write("\n Avg Global PM10:\n")
        fname.write(str(global_pm10))
        
    #open and read the file after the appending:

    return global_pm25,global_pm10 

def graphs(db_name):
    global_pm25, global_pm10 = calculate_averages(db_name)
    values = [global_pm25, global_pm10]
    category = ['pm25', 'pm10']
    plt.barh(category,values)
    x_axis = [0,5,10,15,20,25,30]
    ax1 = plt.subplot()
    ax1.set_xticks(x_axis)
    ax1.set(xlabel='Average in µg/m³', ylabel='Pollutant Type', title ='Average Global Air Quality')
    plt.autoscale()
    plt.show()

def graph2(db_name): 
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    cur.execute('SELECT pm25_ave FROM Aqi2020 WHERE name = "United States of America"')
    us_data = cur.fetchone()[0]
    
    global_pm25 = calculate_averages(db_name)[0] 
    values = [global_pm25, us_data]
    category = ['global pm2.5', 'U.S. pm2.5']
    fig = plt.figure()
    plt.bar(category, values)
    plt.xlabel("Global vs Country") 
    plt.ylabel("Average in µg/m³")
    plt.title("Average PM2.5 in USA vs Global")
    plt.show()

def main(): 
    country_dict = get_data('countries.db')
    setUpDatabase('countries.db', country_dict)
    calculate_averages('countries.db')
    graphs('countries.db')
    graph2('countries.db')


if __name__ == "__main__":
	main()
# {US: {}}
#US, belgium, brazil, greece

# do we need to create correlation between say CO2 and covid cases or can i just make a graph of CO2 for diff countries 

#calculate global air quality by pollutant in 2020

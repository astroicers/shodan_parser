import socket
import struct
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import sys
from urllib.parse import urlencode, quote_plus
import mysql.connector as mariadb
#import sqlite3

def cut_net_mask_range(input_ip):
    t_list = []
    ip = input_ip.split(
        '.')[0] + '.' + input_ip.split('.')[1] + '.'+input_ip.split('.')[2] + '.'
    head_num = int(input_ip.split('.')[3].split('-')[0])
    feet_num = int(input_ip.split('.')[3].split('-')[1])
    for x in range(head_num, feet_num + 1):
        t_list.append(ip + str(x))
    return t_list


def cut_net_mask(input_ip):
    target = input_ip.split('/')[0]
    mask = input_ip.split('/')[1]
    answer = []
    target = target.split('.')
    temp = str()
    for x in target:
        x = int(x)
        x = bin(x)
        x = str(x).lstrip('0b')
        while len(x) < 8:
            x = '0' + x
        temp = temp + x
    top = 0b0
    all = str()
    while top < int('1'*(32 - int(mask)), 2):
        y = bin(top)
        y = str(y).lstrip('0b')
        while len(y) < (32 - int(mask)):
            y = '0' + y
        all = temp[0:int(mask)] + y
        top += 0b1
        ip1 = all[0:8]
        ip2 = all[8:16]
        ip3 = all[16:24]
        ip4 = all[24:32]
        answer.append(str(int(ip1, 2)) + '.' + str(int(ip2, 2)) +
                      '.' + str(int(ip3, 2)) + '.' + str(int(ip4, 2)))
    return answer

def ip2long(ip):
    o =list(map(int, ip.split('.')))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res


def db_service_data_drop(target_dec, flag):
    if flag == 2:
        print("DELETE FROM service_table WHERE _IP=%s" % target_dec)
        c.execute("DELETE FROM service_table WHERE _IP=%s" % target_dec)
        mariadb_connection.commit()


def db_device_data(target_dec, device_json, flag):
    print(
        "SELECT _LAST_UPDATE FROM device_table WHERE _IP=%s" % target_dec)
    c.execute(
        "SELECT _LAST_UPDATE FROM device_table WHERE _IP=%s" % target_dec)
    ip_n_time = c.fetchall()
    time_tag = ''
    try:
        for row in ip_n_time:
            time_tag = row[0]
    except:
        time_tag = ''
    print('**'+time_tag+'**')
    if time_tag != '':  # data exist
        if time_tag == device_json['Last Update']:  # Unupdated data
            flag = 1
            return flag
        else:  # Updated data
            print("UPDATE device_table SET _CITY='%s',_COUNTRY='%s',_ORGANIZATION='%s',_ISP='%s',_LAST_UPDATE='%s',_ASN='%s' WHERE _IP=%s" % (
                device_json['City'], device_json['Country'], device_json['Organization'], device_json['ISP'], device_json['Last Update'], device_json['ASN'], target_dec))
            c.execute("UPDATE device_table SET _CITY='%s',_COUNTRY='%s',_ORGANIZATION='%s',_ISP='%s',_LAST_UPDATE='%s',_ASN='%s' WHERE _IP=%s" % (
                device_json['City'], device_json['Country'], device_json['Organization'], device_json['ISP'], device_json['Last Update'], device_json['ASN'], target_dec))
            mariadb_connection.commit()
            flag = 2
            return flag

    else:  # data not exist
        print("INSERT INTO device_table (_IP,_CITY,_COUNTRY,_ORGANIZATION,_ISP,_LAST_UPDATE,_ASN) VALUES (%s,'%s','%s','%s','%s','%s','%s')" % (
            device_json['ip'], device_json['City'], device_json['Country'], device_json['Organization'], device_json['ISP'], device_json['Last Update'], device_json['ASN']))
        c.execute("INSERT INTO device_table (_IP,_CITY,_COUNTRY,_ORGANIZATION,_ISP,_LAST_UPDATE,_ASN) VALUES (%s,'%s','%s','%s','%s','%s','%s')" % (
            device_json['ip'], device_json['City'], device_json['Country'], device_json['Organization'], device_json['ISP'], device_json['Last Update'], device_json['ASN']))
        mariadb_connection.commit()
        flag = 0
        return flag


def db_service_data(target_dec, service_json, flag):
    if flag == 2:
        c.execute("UPDATE service_table SET _PROTOCOL='%s',_STATE='%s',_DATA='%s',_SUB_TITLE='%s',_SUB_DATA='%s' WHERE _IP=%s AND _PORT=%s" % (
            service_json['protocol'], service_json['state'], service_json['data'], service_json['sub_title'], service_json['sub_data'], target_dec, service_json['port']))
        mariadb_connection.commit()
        print("UPDATE service_table SET _PROTOCOL='%s',_STATE='%s',_DATA='%s',_SUB_TITLE='%s',_SUB_DATA='%s' WHERE _IP=%s AND _PORT=%s" % (
            service_json['protocol'], service_json['state'], service_json['data'], service_json['sub_title'], service_json['sub_data'], target_dec, service_json['port']))
    elif flag == 0:
        c.execute("INSERT INTO service_table (_IP,_PORT,_PROTOCOL,_STATE,_DATA,_SUB_TITLE,_SUB_DATA) VALUES (%s,%s,'%s','%s','%s','%s','%s')" % (
            target_dec, service_json['port'], service_json['protocol'], service_json['state'], service_json['data'], service_json['sub_title'], service_json['sub_data']))
        print("INSERT INTO service_table (_IP,_PORT,_PROTOCOL,_STATE,_DATA,_SUB_TITLE,_SUB_DATA) VALUES (%s,%s,'%s','%s','%s','%s','%s')" % (
            target_dec, service_json['port'], service_json['protocol'], service_json['state'], service_json['data'], service_json['sub_title'], service_json['sub_data']))
        mariadb_connection.commit()
    else:
        print('error flag:'+str(flag))


#conn = sqlite3.connect('shodan.db')
#c = conn.cursor()
mariadb_connection = mariadb.connect(
    user='root', password='3edc$RFV5tgb', database='shodan_db', host='192.168.1.131')
c = mariadb_connection.cursor(buffered=True)

file_path = 'ip.txt'
target_list = []
try:
    f = open(file_path, 'r')
    lines = f.readlines()
    for line in lines:
        print(line)
        line = line.rstrip('\r\n').rstrip('\n')
        if '/' in line:
            for x in cut_net_mask(line):
                target_list.append(x)
        elif '-' in line:
            for x in cut_net_mask_range(line):
                target_list.append(x)
        else:
            target_list.append(line)
    f.close()
except:
    print('Error:Check your file path.')
    sys.exit()

driver = webdriver.Chrome('/home/astroicers/chromedriver')
flag = 0
for num, target in enumerate(target_list):
    target_dec = ip2long(target)
    driver.get("https://www.shodan.io/host/%s" % target)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(soup.title.string)
    flag = 0
    if soup.title.string != '404 Not Found':
        # device data
        device_json = {'ip': target_dec}

        device_key = []
        for x in soup.find_all('td'):
            device_key.append(str(x)[4:-5])

        device_value = []
        for x in soup.find_all('th'):
            device_value.append(str(x)[4:-5])
        while 1:
            if len(device_key) > 7:
                device_key.pop()
            elif len(device_value) > 7:
                device_value.pop()
            else:
                break
        for id, key in enumerate(device_key):
            device_json[key] = quote_plus(device_value[id].encode('utf-8'))
        if 'City' not in device_key:
            device_json['City']=''
        if 'Country' not in device_key:
            device_json['Country']=''
        if 'Organization' not in device_key:
            device_json['Organization']=''
        if 'ISP' not in device_key:
            device_json['ISP']=''
        if 'Last Update' not in device_key:
            device_json['Last Update']=''
        if 'ASN' not in device_key:
            device_json['ASN']=''
        print(device_json)

        # device data post sqlite db  
        flag = db_device_data(target_dec, device_json, flag)
        print('device flag:'+str(flag))
        # service data
        if flag != 1:
            print('service flag:'+str(flag))
            db_service_data_drop(target_dec, flag)
            services = soup.find_all(class_="service service-long")
            for service in services:
                service_json = {}
                port = service.find(class_='port').text
                protocol = service.find(class_='protocol').text
                state = service.find(class_='state').text
                data = service.find('pre').text
                sub_title = ''
                sub_data = ''
                try:
                    sub_title = service.find('h4').text
                    try:
                        sub_data = service.find_all('pre')[1].text
                    except:
                        sub_data = ''
                except:
                    sub_title = ''
                service_json = {'ip': target_dec, 'port': int(port),
                                'protocol': quote_plus(protocol.encode('utf-8')), 'state': quote_plus(state.encode('utf-8')),
                                'data': quote_plus(data.encode('utf-8')), 'sub_title': quote_plus(sub_title.encode('utf-8')),
                                'sub_data': quote_plus(sub_data.encode('utf-8'))}

                print(service_json)
                print('---'*40)

                # service data post sqlite db
                db_service_data(target_dec, service_json, flag)

    # per 50 restart browser
    if num % 50 == 0 and num != 0:
        driver.close()
        print('Restart Browser')
        driver = webdriver.Chrome(
            '/home/astroicers/chromedriver')

driver.close()
mariadb_connection.close()
print('exit')

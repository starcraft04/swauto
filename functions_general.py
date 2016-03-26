import time
import logging
import csv
import sys
from random import randint
   
def randomWait(wait_time, random_wait):
    wait_time = wait_time + randint(0,random_wait)
    time.sleep(wait_time)
    
def fromStringToTuple(string):
    string = string.replace(' ', '')
    string = string.replace('(', '')
    string = string.replace(')', '')
    string = string.split(',')
    coords = (int(string[0]),int(string[1]))
    return coords

def updateCsv(csv_file_name, stage_type, stage_name, numOf):
    csv_dict = csv.DictReader(open(csv_file_name, 'rb'), delimiter=',')
    csv_dict_titles = csv_dict.fieldnames
    csv_dict_rows = list(csv_dict)
    numOfLines = len(csv_dict_rows)
    rows = []
    line_found = False

    if numOfLines > 0:
        for line in csv_dict_rows:
            if line['type'] == stage_type and line['name'] == stage_name:
                #print('Updating line')
                rows.append({'type':stage_type,\
                            'name':stage_name,\
                            'victory':int(line['victory'])+numOf['victory'],\
                            'defeat':int(line['defeat'])+numOf['defeat'],\
                            'runes':int(line['runes'])+numOf['runes'],\
                            'mystical_scrolls':int(line['mystical_scrolls'])+numOf['mscroll'],\
                            'unknown_scrolls':int(line['unknown_scrolls'])+numOf['uscroll'],\
                            'rainbowmon':int(line['rainbowmon'])+numOf['rainbowmon'],\
                            'summoning_stones':int(line['summoning_stones'])+numOf['sstones'],\
                            'monster':int(line['monster'])+numOf['monster'],\
                            'unknown':int(line['unknown'])+numOf['unknown']})
                line_found = True
            else:
                #print('Copying line')
                rows.append({'type':line['type'],\
                            'name':line['name'],\
                            'victory':line['victory'],\
                            'defeat':line['defeat'],\
                            'runes':line['runes'],\
                            'mystical_scrolls':line['mystical_scrolls'],\
                            'unknown_scrolls':line['unknown_scrolls'],\
                            'rainbowmon':line['rainbowmon'],\
                            'summoning_stones':line['summoning_stones'],\
                            'monster':line['monster'],\
                            'unknown':line['unknown']})
    if not line_found:
        #print('Creating new line')
        rows.append({'type':stage_type,\
                    'name':stage_name,\
                    'victory':numOf['victory'],\
                    'defeat':numOf['defeat'],\
                    'runes':numOf['runes'],\
                    'mystical_scrolls':numOf['mscroll'],\
                    'unknown_scrolls':numOf['uscroll'],\
                    'rainbowmon':numOf['rainbowmon'],\
                    'summoning_stones':numOf['sstones'],\
                    'monster':numOf['monster'],\
                    'unknown':numOf['unknown']})

    csv_write_file = open(csv_file_name, 'wb')

    csvwriter = csv.DictWriter(csv_write_file, delimiter=',', fieldnames=csv_dict_titles)

    csvwriter.writerow(dict((fn,fn) for fn in csv_dict_titles))
    for row in rows:
         csvwriter.writerow(row)
    csv_write_file.close()

def main():
    print('function general')
    
if __name__ == "__main__":
    main()

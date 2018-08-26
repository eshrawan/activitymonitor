import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
import time
from datetime import datetime
import evdev
from evdev import InputDevice, categorize  # import * is evil :)
import os
import urllib2
from urllib2 import Request,urlopen,URLError,HTTPError
import requests
import serial
import re

global lost_data
lost_data = ""
button = 2
state = 4
rst = 3

GPIO.setup(button,GPIO.IN)
GPIO.setup(state,GPIO.IN)
GPIO.setup(rst,GPIO.OUT)
GPIO.output(rst, False)

lcd_rs        = 8  # Note this might need to     be changed to 21 for older revision Pi's.
lcd_en        = 7
lcd_d4        = 12
lcd_d5        = 16
lcd_d6        = 20
lcd_d7        = 21
lcd_backlight = 25

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 20
lcd_rows    = 4

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

lcd.set_backlight(0)

activity_list = ["Listen Music", "Watch Edu Video", "Read/Listen Book", "Solve Puzzle", "Eating Food", "Video Games"]

##dev = InputDevice('/dev/input/event0')
##print dev
scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BACK', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'ENTER', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 57: u' ',100: u'RALT', 106: u'RIGHT', 108: u'DOWN', 105: u'LEFT', 103: u'UP',
    82: u'0',79: u'1',80: u'2',81: u'3',75: u'4',76: u'5',77: u'6',71: u'7',72: u'8',73: u'9',96: u'R_ENTER',
    83: u'.',78: u'+',74: u'-',55: u'*',97: u'RCTRL',98: u'/',69: u'NUM_LOCK',
}## 57:u'ENTER'

site = 'http://activity.iotgecko.com/Hit.aspx'

def check_connectivity():
    try:
        urlopen(site,timeout = 2)
        return True
    except:
        return False

def keycheck():
    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            data = evdev.categorize(event)  # Save the event temporarily to introspect it
            if data.keystate == 1:  # Down events only
                key_lookup = scancodes.get(data.scancode) or u'UNKNOWN:{}'.format(data.scancode)  # Lookup or return UNKNOWN:XX
                data = format(key_lookup)
                return str(data)

def enter_name(first_attemp):
        print first_attemp
        name = ""
        number = 1
        if first_attemp == True:
            lcd.clear()
            lcd.message(str(number) + ". Student Name:\n")
            lcd.set_cursor(0,3)
            lcd.message("ENTER :sel ESC :EXIT")
        elif first_attemp == False :
            number = len(student_name) + 1
            if number < 5:
                lcd.clear()
                lcd.message(str(number) + ". Student Name:\n")
                lcd.set_cursor(0,3)
                lcd.message("ENTER :sel ESC :EXIT")
            else:
                lcd.clear()
                lcd.message("You Reg Max Student")
                lcd.set_cursor(0,1)
                lcd.message("Press ESC to exit")
            
        key = ""
        col = 0
        while(key != "ESC"):
            key = keycheck()
            
            if(key == "ENTER"):
                first_attemp = False
                col = 0
                number = number + 1
                student_name.append(name)
                lcd.clear()
                lcd.message("Student Name is:\n" + str(name))
                name = ''
                time.sleep(2)
                if number <= 4:
                    lcd.clear()
                    lcd.message(str(number) + ". Student Name:\n")
                    lcd.set_cursor(0,3)
                    lcd.message("ENTER :sel ESC: EXIT")
                else:
                    lcd.clear()
                    lcd.message("You Reg Max Student")
                    lcd.set_cursor(0,1)
                    lcd.message("Press ESC to exit")
                

            else:
                if(number <= 4):
                    if(key != "ESC"):
                        if(key == "BACK"):
                            name = name[:(len(name)-1)]
                            col = col-1
                            lcd.set_cursor(col,1)
                            lcd.message(' ')
                                
                        else:
                            if (key != "UP" and key != "DOWN" and key != "LEFT" and key != "RIGHT" and
                               key != "LSHFT" and key != "RSHFT"):
                                name += key
                                lcd.set_cursor(col,1)
                                lcd.message(key)
                                col = col+1
                        
##                        print name[2]
        return student_name

def menu1():
    lcd.clear()
    lcd.message("-> Register Mode")
    lcd.set_cursor(0,1)
    lcd.message("   Activity Mode")
    key = ""
    menu = 1
    while (key != "ENTER"):
        key = keycheck()
        if(key == "DOWN"):
            lcd.clear()
            lcd.message("   Register Mode")
            lcd.set_cursor(0,1)
            lcd.message("-> Activity Mode")
            menu = 2
            time.sleep(1)
        elif(key == "UP"):
            lcd.clear()
            lcd.message("-> Register Mode")
            lcd.set_cursor(0,1)
            lcd.message("   Activity Mode")
            menu = 1
            time.sleep(1)
    return menu

def student_select(list_name):
    lcd.clear()
    x = 0
    y = 0
    key = ""
    keydown = 0
    arrow = "-> "
    length = len(list_name)
    print "len: " + str(length)
    for x in range(length):
        lcd.set_cursor(1, x)
        lcd.message(str(x + 1) + "." + str(list_name[x]))
    lcd.set_cursor(0, 0)
    lcd.message("->" + str(0 + 1)+"." + str(list_name[0]))
    while key != "ENTER":
        key = keycheck()
        if(key == "DOWN"):
            keydown = keydown + 1
        if(key == "UP"):
            keydown = keydown - 1
        if(keydown < 0 ):
            keydown = 0
        if keydown > 3 :
            keydown = 3
        if keydown > (length - 1):
            keydown = length - 1
        if(keydown < 5):
                lcd.clear()
                lcd.set_cursor(0, keydown)
                lcd.message("->" + str(keydown + 1)+"." + str(list_name[keydown]))
                for x in range(length):
                    lcd.set_cursor(1, x)
                    lcd.message(str(x + 1) + "." + str(list_name[x]))
                lcd.set_cursor(0, keydown)
                lcd.message("->" + str(keydown + 1)+"." + str(list_name[keydown]))
                print "keydown: " + str(keydown)
                time.sleep(1)
    return list_name[keydown]
        
def activity_select():
    lcd.clear()
    lcd.set_cursor(1,0)
    lcd.message("1." + str(activity_list[0]))
    lcd.set_cursor(1,1)
    lcd.message("2." + str(activity_list[1]))
    lcd.set_cursor(1,2)
    lcd.message("3." + str(activity_list[2]))
    lcd.set_cursor(1,3)
    lcd.message("4." + str(activity_list[3]))
    lcd.set_cursor(0, 0)
    lcd.message("->" + "1"+"." + str(activity_list[0]))
    x = 0
    y = 0
    key = ""
    keydown = 0
    while key != "ENTER":
        key = keycheck()
        if(key == "ESC"):
            break
        if(key == "DOWN"):
            keydown = keydown + 1
        if(key == "UP"):
            keydown = keydown - 1
        if(keydown < 0 ):
            keydown = 0
        if(keydown > 5):
            keydown = 5
        if keydown < 4:
            lcd.clear()
            lcd.set_cursor(1,0)
            lcd.message("1." + str(activity_list[0]))
            lcd.set_cursor(1,1)
            lcd.message("2." + str(activity_list[1]))
            lcd.set_cursor(1,2)
            lcd.message("3." + str(activity_list[2]))
            lcd.set_cursor(1,3)
            lcd.message("4." + str(activity_list[3]))
            lcd.set_cursor(0, keydown)
            lcd.message("->" + str(keydown + 1)+"." + str(activity_list[keydown]))
        elif keydown >= 4:
            lcd.clear()
            lcd.set_cursor(1,0)
            lcd.message("5." + str(activity_list[4]))
            lcd.set_cursor(1,1)
            lcd.message("6." + str(activity_list[5]))
            lcd.set_cursor(0, (keydown - 4))
            lcd.message("->" + str(keydown + 1)+"." + str(activity_list[keydown]))
    if(key == "ESC"):
            return "None"
    else:
        return activity_list[keydown]

def date_time(DateTime):
    try:
        res = urlopen('http://just-the-time.appspot.com/')
        time_str = res.read().strip()
        print time_str
        local_date = time_str[0:10]
        local_time = time_str[11:16]
        
    except:
        now = datetime.utcnow()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        local_date = str(month) + ":" + str(day) + ":" + str(year)
        local_time = str(hour) + ":" + str(minute)
    print local_date
    print local_time
##    hour = int(time[0:2])
##    hour = hour + 5
##    minute = int(time[3:5])
##    minute = minute + 30
##    local_time = str(hour) + ":" + str(minute)
    if (DateTime == "Date"):
        return local_date
    if (DateTime == "Time"):
        return local_time

def send_data(avg, data_type, name, act):
    global lost_data 
    scale = ""
    url = 'http://activity.iotgecko.com/Hit.aspx'
    if avg < 30:
        scale = "LOW"
    if avg > 30 and avg < 60:
        scale = "MEDIUM"
    if avg > 60:
        scale = "HIGH"
    date = date_time("Date")
    local_time = date_time("Time")
    std_name = name
    activity = act
    
    if data_type == "not_final":
        send_data = "{\"Type\":\"0\",\"Name\":\""+ str(std_name) + "\",\"Act\":\""  + str(activity) + "\",\"Value\":\""+ str(scale) + "\",\"Date\":\"" + str(date) + "\",\"Time\":\""+ str(local_time) + "\"}"
        try:
            print "len lost data:" + str(len(lost_data))
            if len(lost_data) > 0:
                lost_data = str(lost_data) + "," + str(send_data)
                lost_send_data = "[" + str(lost_data) + "]"
                print "lost_send_data: " + str(lost_send_data)
                req = urllib2.Request(url)
                headers = {'Content-Type':'application/json'}
                response = requests.post(url, lost_send_data, headers=headers)
                print "lost data response: " + str(response.text)
                lost_data = ""
                print "length lost data:" + str(len(lost_data))
            
                
            elif len(lost_data) == 0:
                final_data = "[" + str(send_data) +"]"
                print "final data: " + str(final_data)
                req = urllib2.Request(url)
                headers = {'Content-Type':'application/json'}
                response = requests.post(url, final_data, headers=headers)
                print "single data: " + str(response.text)
        except:
            if lost_data == "":
                lost_data = str(send_data)       
            
    elif data_type == "final":
        send_final_data = "[{\"Type\":\"1\", \"Name\":\""+ str(std_name) + "\",\"Act\":\""  + str(activity) + "\",\"Value\":\""+ str(scale) + "\",\"Date\":\"" + str(date) + "\",\"Time\":\""+ str(local_time) + "\"}]"
        print "send_final_data:" + str(send_final_data)
        while True:
                try:
                    req = urllib2.Request(url)
                    headers = {'Content-Type':'application/json'}
                    response = requests.post(url, send_final_data, headers=headers)
                    print response.text
                    break
                except:
                    lcd.clear()
                    lcd.message('Final data not send')
                    lcd.set_cursor(0,1)
                    lcd.message('Please check conn')
                    lcd.set_cursor(0,2)
                    lcd.message('Rst to Discard data')
    

def collect_data(student, activity):
    headset_connection = True
    for_final_avg = list()
    data = list()
    scale = ""
    key = ""
    result = ""
    addition_val = 0
    final_add = 0
    minutes_avg = 0
    port = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=0.43)
    lcd.clear()
    lcd.message("Name: " + str(student) + "\n" + str(activity))
    lcd.set_cursor(0,2)
    lcd.message("Monitoring")
    time.sleep(1)
    t1 = datetime.now()
    while GPIO.input(button) == True:
        t2 = datetime.now()
        delta = t2 - t1 
        time_elapse = delta.total_seconds()
        if time_elapse > 60 :
            if len(data) > 0:
                for i in range(len(data)):
                    addition_val = data[i] + addition_val
                minutes_avg = addition_val/ len(data)
                for_final_avg.append(minutes_avg)
                if minutes_avg < 30:
                    scale = "LOW"
                if minutes_avg > 30 and minutes_avg < 60:
                    scale = "MEDIUM"
                if minutes_avg > 60:
                    scale = "HIGH"
                lcd.clear()
                lcd.message("Name: " + str(student) + "\n" + str(activity))
                lcd.set_cursor(0,3)
                lcd.message("Avg Data:" + str(scale))
                send_data(minutes_avg, "not_final",student, activity)
                time.sleep(1)
                print "minutes_avg" + str(minutes_avg)
                minutes_avg = 0
                addition_val = 0
                del data[:]
                t1 = datetime.now()
                port = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=0.43)
            else:
                lcd.clear()
                lcd.message('No data found')
                lcd.set_cursor(0,1)
                lcd.message('Reset Headset again')
                time.sleep(2)
        
        else:
            if GPIO.input(state) == True:
                rcv = port.readall().strip()
                try:
                    rcv = int('0' + rcv)
##                print "rcv: " + str(rcv)
                    if rcv > 0:
                        data.append(rcv)
    ##                    print data
                        if rcv < 30:
                            scale = "LOW"
                        if rcv > 30 and minutes_avg < 60:
                            scale = "MEDIUM"
                        if rcv > 60:
                            scale = "HIGH"
                        lcd.clear()
                        lcd.message("Name: " + str(student) + "\n" + str(activity))
                        lcd.set_cursor(0,2)
                        lcd.message("Live Data:" + str(scale))
                    else:
                        lcd.clear()
                        lcd.message("Name: " + str(student) + "\n" + str(activity))
                        lcd.set_cursor(0,2)
                        lcd.message("Live Data:No Data")
                except:
                    None
            while GPIO.input(state) == False and GPIO.input(button) == True:
                lcd.clear()
                lcd.message('Headset not Connect')
                lcd.set_cursor(0,1)
                lcd.message('Press Reset')
                time.sleep(1)
                if GPIO.input(state) == False:
                    headset_connection = False
                else:
                    headset_connection = True

    if time_elapse < 60:
        print "len_dat: " + str(len(data))
        if len(data) > 0:
            for i in range(len(data)):
                addition_val = data[i] + addition_val
            print "addintion_val: " + str(addition_val)
            minutes_avg = addition_val/ len(data)
            for_final_avg.append(minutes_avg)
            if minutes_avg < 30:
                scale = "LOW"
            if minutes_avg > 30 and minutes_avg < 60:
                scale = "MEDIUM"
            if minutes_avg > 60:
                scale = "HIGH"
            lcd.clear()
            lcd.message("Name: " + str(student) + "\n" + str(activity))
            lcd.set_cursor(0,3)
            lcd.message("Avg Data:" + str(scale))
            send_data(minutes_avg, "not_final",student, activity)
            time.sleep(1)
            print "minutes_avg" + str(minutes_avg)
            minutes_avg = 0
            addition_val = 0
            del data[:]
            
    if headset_connection == True:
        if len(for_final_avg) > 0:
            for i in range(len(for_final_avg)):
                final_add = for_final_avg[i] + final_add
            print "final addition:" + str(final_add)
            final_avg = final_add / len(for_final_avg)
            print "final: " + str(final_avg)
            send_data(final_avg, "final",student, activity)

reset = True
        
t1 = datetime.now()
while GPIO.input(button) == False:
    t2 = datetime.now()
    delta = t2 - t1
    time_elapse = delta.total_seconds()
    if time_elapse > 5:
        reset = False
        main = False
        break


while reset == True:
    try:
        main = True
        path = None
        lcd.clear()
        lcd.message('   Neurosky Based \n    Kid Activity \n     Monitoring \n       System')
        time.sleep(3)
        lcd.clear()
        lcd.message('Searching for the\nKeyboard')
        time.sleep(2)
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for device in devices:
             d_name = device.name
             d_phys = device.phys
             if (d_name.find('Keykoard')>0 or d_name.find('Keyboard')>0) and d_phys.find('input0')>0:
                 path = device.fn
                 print 'got keyboard at ', path
                 break

        if not path:
            print 'keyboard not found'
            lcd.clear()
            lcd.message('keyboard not found')
            time.sleep(2)
            lcd.clear()
            lcd.message('  Connect Keyboard  ')

            while GPIO.input(button):
                main = False
                lcd.set_cursor(0,2)
                lcd.message('    Press reset     ')
                time.sleep(0.5)
                lcd.set_cursor(0,2)
                lcd.message('                    ')
                time.sleep(0.5)
                
        else:
            lcd.clear()
            lcd.message('Found Keyboard')
            time.sleep(2)
            dev = InputDevice(path)
            print 'dev=' ,dev
            lcd.clear()
            lcd.message('connecting to \nInternet')
            time.sleep(1)
            x = 0
            t1 = datetime.now()
            while not check_connectivity():
                t2 = datetime.now()
                delta = t2 - t1 
                time_elapse = delta.total_seconds()
                if time_elapse > 15:
                    lcd.clear()
                    lcd.message('Error: Check\nInternet Conn ')
                    print "error check you internet connection"
                    time.sleep(1)
                    main = False
                    while GPIO.input(button) == True:
                        lcd.clear()
                        lcd.message('Press reset to\nrestart')
                        time.sleep(0.5)
                    break
                else:
                    main = True
                    
            student_name = list()
            lcd.clear()
            lcd.message('Connected')
            time.sleep(1)
            first_time = True
        while main == True :
            key = ""
            menu = menu1()
            GPIO.output(rst, True)
            if menu == 1:
                student = enter_name(first_time)
                first_time = False
                print "student:" + str( student)
            if menu == 2:
                if len(student_name) > 0:               
                   select_student = student_select(student)
                   select_activity = activity_select()
                   
                   if select_activity == "None":
                       select_student = student_select(student)
                       select_activity = activity_select()
                   found_headset = True
                   t1 = datetime.now()
                   
                   while GPIO.input(state) == False:
                       lcd.clear()
                       lcd.message('Connecting to \nHeadset')
                       time.sleep(0.5)
                       t2 = datetime.now()
                       delta = t2 - t1 
                       time_elapse = delta.total_seconds()
                       if time_elapse > 15:
                           lcd.clear()
                           lcd.message('Hedset not connected')
                           lcd.set_cursor(0,1)
                           lcd.message('Press reset')
                           while GPIO.input(button) == True:
                               found_headset = False
                               main = False
                           break
                   
                   if found_headset == True:
                       lcd.clear()
                       lcd.message('Headset Connected \nENTER = start \nESC = EXIT')
                       while key != "ENTER" and key != "ESC":
                            key = keycheck()
                       if(key == "ENTER"):
                           collect_data(select_student,select_activity)
                else:
                    lcd.clear()
                    lcd.message("Enter min 1 Student")
                    time.sleep(1)
                    GPIO.output(rst, False)
        GPIO.output(rst, False)
    except:
        lcd.clear()
        lcd.message('Got Error \nPress Reset')
        while GPIO.input(button) == True:
            None
lcd.clear()
lcd.message('Program Terminate')

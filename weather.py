from Tkinter import *
from keys import OPEN_WEATHER_API_KEY
from urllib2 import urlopen
from io import BytesIO
from PIL import Image, ImageTk
import datetime
import tkFont
import contextlib
import json
from sys import platform as sp


class Weather:

    def __init__(self, master):
        self.city_name = "Bangalore"
        self.custom_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
        self.custom_heading_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.current_city_id = self.get_city_id(self.city_name)  # open weather map city id
        if self.current_city_id != -1:  # if city id found
            # initialization of all member variables to None
            self.t_dt = self.t_temp_day = self.t_temp_min = self.t_temp_max = self.t_pressure = \
                self.t_humidity = self.t_weather_icon = self.t_weather_main = self.t_weather_desc = \
                self.t_wind_speed = self.t_wind_dir = self.t_cloudiness = self.t_rain = None
            # retrieve and display weather data
            self.get_weather_today(self.current_city_id)
            self.display_data(master)

            # console log
            print("UNIX Date: %d, Date: %s" % (self.t_dt, (datetime.datetime.fromtimestamp(self.t_dt))
                                               .strftime('%d-%m-%Y %H:%M:%S')))
            print("Temp day: %0.2f%sC" % (self.t_temp_day, degree_sign.encode('utf-8')))
            print("Pressure: %0.2f hPa" % self.t_pressure)
            print("Humidity: %0.2f %%" % self.t_humidity)
            print("Weather: %s, Description: %s" % (self.t_weather_main, self.t_weather_desc))
            print("Wind Speed: %0.2f m/s" % self.t_wind_speed)
            print("Wind Direction, degrees: %0.2f" % self.t_wind_dir)
            print("Cloudiness: %0.2f %%" % self.t_cloudiness)
            print("Rain: %0.2f mm" % self.t_rain)

        else:
            # city id not found
            label_invalid = Label(master, text="Sorry, city not found. Please try a different name.")
            label_invalid.pack()

    # get the weather information of the passed city id
    def get_weather_today(self, current_city_id):
        current_weather_url = "http://api.openweathermap.org/data/2.5/forecast/daily?id=%d&units=metric&appid=%s" \
                              % (current_city_id, OPEN_WEATHER_API_KEY)
        with contextlib.closing(urlopen(current_weather_url)) as response:
            json_data = json.load(response)
        weather_list = json_data['list']
        json_data_list = weather_list[0]
        self.load_data_from_json(json_data_list)

    # retrieve data from passed json object
    def load_data_from_json(self, cur_json_list):
        self.t_dt = cur_json_list['dt']
        t_temp = cur_json_list['temp']
        self.t_temp_day = t_temp['day']
        self.t_temp_min = t_temp['min']
        self.t_temp_max = t_temp['max']
        self.t_pressure = cur_json_list['pressure']
        self.t_humidity = cur_json_list['humidity']
        t_weather = cur_json_list['weather'][0]
        self.t_weather_main = t_weather['main']
        self.t_weather_desc = t_weather['description']
        self.t_weather_icon = t_weather['icon']
        self.t_wind_speed = cur_json_list['speed']
        self.t_wind_dir = cur_json_list['deg']
        self.t_cloudiness = cur_json_list['clouds']
        self.t_rain = cur_json_list['rain']

    # find open weather map city id for the given city name
    @staticmethod
    def get_city_id(city_name):
        with open('city.list.json', 'r') as city_list:
            data_string = city_list.read()

        json_data = json.loads(data_string)
        for city in json_data['city']:
            if city['name'] == city_name:
                return city['_id']
        else:
            return -1   # city id not found

    # display retrieved data on GUI
    def display_data(self, master):
        label_city = Label(master, text=self.city_name, font=self.custom_heading_font)
        label_city.grid(row=0, columnspan=2, padx=4, pady=4)

        Label(master, text="Today", font=self.custom_font).grid(row=1, column=0, padx=2, pady=2)
        label_time = Label(master, text=(datetime.datetime.fromtimestamp(self.t_dt)).strftime('%d-%m-%Y'))
        label_time.grid(row=1, column=1, padx=2, pady=2)

        weather_icon_url = "http://openweathermap.org/img/w/%s.png" % self.t_weather_icon
        with contextlib.closing(urlopen(weather_icon_url)) as raw_data:
            image = Image.open(BytesIO(raw_data.read()))
        weather_icon = ImageTk.PhotoImage(image)
        label_icon = Label(master, image=weather_icon)
        label_icon.image = weather_icon     # keep a reference
        # When a PhotoImage object is garbage-collected by Python
        # (e.g. when you return from a function which stored an image in a local variable),
        # the image is cleared even if it is being displayed by a Tkinter widget.
        # To avoid this, the program must keep an extra reference to the image object.
        label_icon.grid(row=2, rowspan=2, column=0)
        Label(master, text=self.t_weather_main, font=self.custom_font).grid(row=2, column=1, padx=2, pady=2)
        Label(master, text=self.t_weather_desc.capitalize()).grid(row=3, column=1, padx=2, pady=2)

        label_temp_day = Label(master, text="Temperature:\n %0.2f%sC" % (self.t_temp_day, degree_sign.encode('utf-8')),
                               font=self.custom_font)
        label_temp_day.grid(row=4, column=0, rowspan=2, padx=2, pady=2)
        Label(master, text="Minimum: %0.2f%sC" % (self.t_temp_min, degree_sign.encode('utf-8')))\
            .grid(row=4, column=1, padx=2, pady=2)
        Label(master, text="Maximum: %0.2f%sC" % (self.t_temp_max, degree_sign.encode('utf-8')))\
            .grid(row=5, column=1, padx=2, pady=2)

        Label(master, text="Pressure").grid(row=6, column=0, padx=2, pady=2)
        Label(master, text="%0.2f hPa" % self.t_pressure).grid(row=6, column=1, padx=2, pady=2)

        Label(master, text="Humidity").grid(row=7, column=0, padx=2, pady=2)
        Label(master, text="%0.2f %%" % self.t_humidity).grid(row=7, column=1, padx=2, pady=2)

        Label(master, text="Wind Speed").grid(row=8, column=0, padx=2, pady=2)
        Label(master, text="%0.2f m/s" % self.t_wind_speed).grid(row=8, column=1, padx=2, pady=2)

        Label(master, text="Wind Direction").grid(row=9, column=0, padx=2, pady=2)
        Label(master, text="%0.2f degrees" % self.t_wind_dir).grid(row=9, column=1, padx=2, pady=2)

        Label(master, text="Cloudiness").grid(row=10, column=0, padx=2, pady=2)
        Label(master, text="%0.2f %%" % self.t_cloudiness).grid(row=10, column=1, padx=2, pady=2)

        Label(master, text="Rain").grid(row=11, column=0, padx=2, pady=2)
        Label(master, text="%0.2f mm" % self.t_rain).grid(row=11, column=1, padx=2, pady=2)


root = Tk()
root.wm_title("Sunshine")
if sp=='linux' or sp=='linux2' or sp=='darwin':
    img = PhotoImage(file='sun.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
else:
    root.iconbitmap(default='sun.ico')
degree_sign = u'\N{DEGREE SIGN}'
weather = Weather(root)
root.mainloop()

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
import socket
import string


# check for internet connectivity
def is_connected():
    try:
        # see if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False


class Weather:
    def __init__(self, master, city):
        button_city.config(state=DISABLED)
        if city != "":
            if is_connected():  # internet available, fetch weather data
                weather_frame = Frame(master)
                weather_frame.grid(row=0)

                self.city_name = string.capwords(city)
                self.day = 0
                self.custom_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
                self.custom_heading_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
                self.current_city_id = self.get_city_id(self.city_name)  # open weather map city id
                if self.current_city_id != -1:  # if city id found
                    # initialization of all member variables to None
                    self.t_dt = StringVar()
                    self.t_temp_day = StringVar()
                    self.t_temp_min = StringVar()
                    self.t_temp_max = StringVar()
                    self.t_pressure = StringVar()
                    self.t_humidity = StringVar()
                    self.t_weather_icon_url = None
                    self.t_weather_main = StringVar()
                    self.t_weather_desc = StringVar()
                    self.t_wind_speed = StringVar()
                    self.t_wind_dir = StringVar()
                    self.t_cloudiness = StringVar()
                    self.t_rain = StringVar()
                    self.label_weather_icon = Label(weather_frame)
                    # retrieve and display weather data
                    self.get_weather(self.current_city_id, self.day)
                    self.display_data(weather_frame)

                    # bottom navigation frame
                    bottom_frame = Frame(master, height=2, borderwidth=1, relief=FLAT)
                    bottom_frame.grid(row=1, columnspan=2, padx=4, pady=4)

                    prev_img = ImageTk.PhotoImage(file="prev.png")
                    self.prev_button = Button(bottom_frame, text="<<", image=prev_img, command=self.go_to_prev)
                    self.prev_button.image = prev_img
                    self.prev_button.grid(row=0, column=0, padx=4, pady=4)
                    self.prev_button.config(state=DISABLED)

                    next_img = ImageTk.PhotoImage(file="next.png")
                    self.next_button = Button(bottom_frame, text=">>", image=next_img, command=self.go_to_next)
                    self.next_button.image = next_img
                    self.next_button.grid(row=0, column=1, padx=4, pady=4)

                else:
                    # city id not found
                    label_invalid = Label(master, text="Sorry, city not found.\nPlease try a different name.",
                                          font=("Helvetica", 10, "bold"))
                    label_invalid.place(relx=0.5, rely=0.5, anchor="center")
                    label_invalid.pack(fill=BOTH, expand=1, padx=4, pady=4)

            else:
                # internet not available, display error message
                label_no_internet = Label(master, text="Sorry, can not connect to internet. \n"
                                                       "Please check your connection and try again.",
                                          font=("Helvetica", 10, "bold"))
                label_no_internet.place(relx=0.5, rely=0.5, anchor="center")
                label_no_internet.pack(fill=BOTH, expand=1, padx=4, pady=4)
        else:
            # string empty, display error message
            label_empty_str = Label(master, text="Please enter a city to proceed.",
                                    font=("Helvetica", 10, "bold"))
            label_empty_str.place(relx=0.5, rely=0.5, anchor="center")
            label_empty_str.pack(fill=BOTH, expand=1, padx=4, pady=4)

        button_city.config(state=NORMAL)

    # get the weather information of the passed city id
    def get_weather(self, current_city_id, day):
        current_weather_url = "http://api.openweathermap.org/data/2.5/forecast/daily?id=%d&units=metric&appid=%s" \
                              % (current_city_id, OPEN_WEATHER_API_KEY)
        with contextlib.closing(urlopen(current_weather_url)) as response:
            json_data = json.load(response)
        weather_list = json_data['list']
        json_data_list = weather_list[day]
        print(json_data_list)
        self.load_data_from_json(json_data_list)

    # retrieve data from passed json object
    def load_data_from_json(self, cur_json_list):
        self.t_dt.set((datetime.datetime.fromtimestamp(cur_json_list['dt'])).strftime('%d-%m-%Y'))
        t_temp = cur_json_list['temp']
        self.t_temp_day.set("Temperature:\n %0.2f%sC" % (t_temp['day'], degree_sign.encode('utf-8')))
        self.t_temp_min.set("Minimum: %0.2f%sC" % (t_temp['min'], degree_sign.encode('utf-8')))
        self.t_temp_max.set("Maximum: %0.2f%sC" % (t_temp['max'], degree_sign.encode('utf-8')))
        self.t_pressure.set("%0.2f hPa" % cur_json_list['pressure'])
        self.t_humidity.set("%0.2f %%" % cur_json_list['humidity'])
        t_weather = cur_json_list['weather'][0]
        self.t_weather_main.set(t_weather['main'])
        self.t_weather_desc.set(t_weather['description'].capitalize())
        t_weather_icon = t_weather['icon']
        self.t_weather_icon_url = "http://openweathermap.org/img/w/%s.png" % t_weather_icon
        self.t_wind_speed.set("%0.2f m/s" % cur_json_list['speed'])
        self.t_wind_dir.set("%0.2f degrees" % cur_json_list['deg'])
        self.t_cloudiness.set("%0.2f %%" % cur_json_list['clouds'])
        if 'rain' in cur_json_list:
            self.t_rain.set("%0.2f mm" % cur_json_list['rain'])
        else:
            self.t_rain.set("No rain today.")

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
            return -1  # city id not found

    # display retrieved data on GUI
    def display_data(self, master):
        label_city = Label(master, text=self.city_name, font=self.custom_heading_font)
        label_city.grid(row=0, columnspan=2, padx=4, pady=4)

        label_time = Label(master, textvariable=self.t_dt, font=self.custom_font)
        label_time.grid(row=1, columnspan=2, padx=2, pady=2)

        self.set_weather_icon()

        Label(master, textvariable=self.t_weather_main, font=self.custom_font).grid(row=2, column=1, padx=2, pady=2)
        Label(master, textvariable=self.t_weather_desc).grid(row=3, column=1, padx=2, pady=2)

        label_temp_day = Label(master, textvariable=self.t_temp_day, font=self.custom_font)
        label_temp_day.grid(row=4, column=0, rowspan=2, padx=2, pady=2)
        Label(master, textvariable=self.t_temp_min).grid(row=4, column=1, padx=2, pady=2)
        Label(master, textvariable=self.t_temp_max).grid(row=5, column=1, padx=2, pady=2)

        Label(master, text="Pressure").grid(row=6, column=0, padx=2, pady=2)
        Label(master, textvariable=self.t_pressure).grid(row=6, column=1, padx=2, pady=2)

        Label(master, text="Humidity").grid(row=7, column=0, padx=2, pady=2)
        Label(master, textvariable=self.t_humidity).grid(row=7, column=1, padx=2, pady=2)

        Label(master, text="Wind Speed").grid(row=8, column=0, padx=2, pady=2)
        Label(master, textvariable=self.t_wind_speed).grid(row=8, column=1, padx=2, pady=2)

        Label(master, text="Wind Direction").grid(row=9, column=0, padx=2, pady=2)
        Label(master, textvariable=self.t_wind_dir).grid(row=9, column=1, padx=2, pady=2)

        Label(master, text="Cloudiness").grid(row=10, column=0, padx=2, pady=2)
        Label(master, textvariable=self.t_cloudiness).grid(row=10, column=1, padx=2, pady=2)

        Label(master, text="Rain").grid(row=11, column=0, padx=2, pady=2)
        Label(master, textvariable=self.t_rain).grid(row=11, column=1, padx=2, pady=2)

        self.scale_widgets(master)

    # scale the widgets with the master window
    @staticmethod
    def scale_widgets(master):
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=1)
        master.rowconfigure(3, weight=1)
        master.rowconfigure(4, weight=1)
        master.rowconfigure(5, weight=1)
        master.rowconfigure(6, weight=1)
        master.rowconfigure(7, weight=1)
        master.rowconfigure(8, weight=1)
        master.rowconfigure(9, weight=1)
        master.rowconfigure(10, weight=1)
        master.rowconfigure(11, weight=1)
        master.rowconfigure(12, weight=1)

    # set the weather icon
    def set_weather_icon(self):
        with contextlib.closing(urlopen(self.t_weather_icon_url)) as raw_data:
            image = Image.open(BytesIO(raw_data.read()))
        weather_icon = ImageTk.PhotoImage(image)
        self.label_weather_icon.configure(image=weather_icon)
        self.label_weather_icon.image = weather_icon  # keep a reference
        # When a PhotoImage object is garbage-collected by Python
        # (e.g. when you return from a function which stored an image in a local variable),
        # the image is cleared even if it is being displayed by a Tkinter widget.
        # To avoid this, the program must keep an extra reference to the image object.
        self.label_weather_icon.grid(row=2, rowspan=2, column=0)

    # get the previous day's weather
    def go_to_prev(self):
        print("Go to previous day")
        self.day -= 1
        if self.day > 6:
            self.day = 6
        elif self.day < 0:
            self.day = 0
        else:
            self.get_weather(self.current_city_id, self.day)
            self.set_weather_icon()
        self.button_state_check()

    # get the next day's weather
    def go_to_next(self):
        print("Go to next day")
        self.day += 1
        if self.day > 6:
            self.day = 6
        elif self.day < 0:
            self.day = 0
        else:
            self.get_weather(self.current_city_id, self.day)
            self.set_weather_icon()
        self.button_state_check()

    # update the state of the navigation buttons
    def button_state_check(self):
        if self.day == 0:
            self.prev_button.config(state=DISABLED)
            self.next_button.config(state=NORMAL)
        elif self.day == 6:
            self.prev_button.config(state=NORMAL)
            self.next_button.config(state=DISABLED)
        else:
            self.prev_button.config(state=NORMAL)
            self.next_button.config(state=NORMAL)


# called on show weather button click
def show():
    city = entry_city.get()
    print city
    for child in content_frame.winfo_children():
        child.destroy()
    Weather(content_frame, city)

root = Tk()
root.wm_title("Sunshine")
if sp == 'linux' or sp == 'linux2' or sp == 'darwin':
    img = PhotoImage(file='sun.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
else:
    root.iconbitmap(default='sun.ico')
degree_sign = u'\N{DEGREE SIGN}'
REMOTE_SERVER = "www.google.com"

# top city frame
font = tkFont.Font(family="Helvetica", size=10)

top_frame = Frame(root)
top_frame.grid(row=0, columnspan=2, padx=4, pady=4)

Label(top_frame, text="City", font=font).grid(row=0, column=0, sticky="W", padx=4, pady=4)

entry_city = Entry(top_frame, font=font)
entry_city.grid(row=0, column=1, padx=4, pady=4)
entry_city.focus_set()

content_frame = Frame(root)
content_frame.grid(row=1, columnspan=2)

button_city = Button(top_frame, text="Show Weather", command=show, font=font, relief=GROOVE)
button_city.grid(row=1, columnspan=2, padx=4, pady=4)

root.update()
root.minsize(200, root.winfo_height())
root.bind("<Return>", lambda x: show())     # invoke function on pressing enter

# scaling
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

root.mainloop()

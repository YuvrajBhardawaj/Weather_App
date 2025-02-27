import tkinter as tk
from tkinter import PhotoImage, Canvas
from PIL import Image, ImageTk
import threading
from modules.api import get_location, get_weather, get_weekly_forecast
from modules.loader import Loader
import time
from io import BytesIO
import requests
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("900x500+300+200")
        self.root.resizable(False, False)
        self.root.config(bg="lightblue")

        # Loader
        self.loader = Loader(root)

        # Search Box with Rounded Background
        self.canvas = Canvas(root, width=450, height=70, bg="lightblue", highlightthickness=0)
        self.canvas.place(x=20, y=20)
        self.rounded_rectangle(10, 10, 440, 60, 25, fill="#444")  # Rounded rectangle background

        # Search Input Field (Inside the Rounded Box)
        self.textfield = tk.Entry(root, justify="left", width=20, font=("poppins", 21, "bold"), bg="#444", fg="white", border=0, insertbackground="white")
        self.textfield.place(x=55, y=38)

        # Search Icon Button
        # Load and resize the search icon dynamically
        search_icon_img = Image.open("assets/search_icon.png")
        search_icon_img = search_icon_img.resize((40, 40), Image.Resampling.LANCZOS)  # Adjust size accordingly
        self.search_icon = ImageTk.PhotoImage(search_icon_img)

        self.search_button = tk.Button(root, image=self.search_icon, borderwidth=0, cursor="hand2", bg="#444", command=self.fetch_weather)
        self.search_button.place(x=400, y=34)

        # Logo
        logo_image = Image.open("assets/logo.png").resize((150, 130))
        self.logo_tk = ImageTk.PhotoImage(logo_image)
        self.logo_label = tk.Label(root, image=self.logo_tk, bg="lightblue")
        self.logo_label.place(x=700, y=10)

        # Time display
        self.weather_label = tk.Label(root, font=("arial", 15), bg="lightblue")
        self.weather_label.place(x=30, y=100)
        self.clock_label = tk.Label(root, font=("Helvetica", 12), bg="lightblue")
        self.clock_label.place(x=30, y=130)

        # Temperature
        self.temp_label = tk.Label(root, font=("arial", 50, 'bold'), fg='#ee666d', bg='lightblue')
        self.feelsLike_label = tk.Label(root, font=('arial', 20), bg='lightblue')
        self.loc_label = tk.Label(root, font=("arial", 10, 'bold'), fg='#1a0a6b', bg='lightblue')

        self.temp_label.pack(pady=(80, 10))
        self.feelsLike_label.pack()
        self.loc_label.pack()

        #forecast
        self.create_forecast_labels()
        # Info labels
        self.create_info_labels()

        #Project Icon
        self.icon = Image.open("assets/logo.png")
        self.icon = ImageTk.PhotoImage(self.icon)
        self.root.wm_iconphoto(True, self.icon)

    def rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle on a canvas."""
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1,
            x2, y1 + radius, x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2, x1, y2,
            x1, y2 - radius, x1, y1 + radius, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def create_info_labels(self):
        self.frame_img = PhotoImage(file="assets/box.png")
        self.frame_label = tk.Label(self.root, image=self.frame_img, bg="lightblue")
        self.frame_label.pack(padx=20, pady=10, side=tk.BOTTOM, fill='x')

        self.labels = {
            "Wind": (120, 420),
            "Humidity": (250, 420),
            "Description": (430, 420),
            "Pressure": (650, 420)
        }
        self.data_labels = {}

        for key, (x, y) in self.labels.items():
            tk.Label(self.root, text=key, font=("Helvetica", 15, 'bold'), fg='white', bg="#1ab5ef").place(x=x, y=y)
            self.data_labels[key] = tk.Label(self.root, text="...", font=('arial', 15, 'bold'), bg="#1ab5ef", fg='white')
            self.data_labels[key].place(x=x, y=y+30)

    def create_forecast_labels(self):
        forecast_frame = tk.Frame(self.root, bg="lightblue", padx=15, pady=10)
        forecast_frame.pack()

        # Row 0
        self.days = []
        for i in range(5):
            lbl = tk.Label(forecast_frame,font=("Helvetica", 15, 'bold'),bg="lightblue", fg="grey", padx=10, pady=5)
            lbl.grid(row=0, column=i, padx=5)
            self.days.append(lbl)
            
        # Row 1
        self.icons = []
        for i in range(5):
            lbl = tk.Label(forecast_frame, bg="lightblue", fg="white", padx=10, pady=5)
            lbl.grid(row=1, column=i, padx=5)
            self.icons.append(lbl)

        # Row 2
        self.temperatures = []
        for i in range(5):
            lbl = tk.Label(forecast_frame,font=("Helvetica", 12, 'bold'), bg="lightblue", fg="grey", padx=10, pady=5)
            lbl.grid(row=2, column=i, padx=5)
            self.temperatures.append(lbl)

        # Row3
        self.condition = []
        for i in range(5):
            lbl = tk.Label(forecast_frame,font=("Helvetica", 12, 'bold'), bg="lightblue", fg="grey", padx=10, pady=5)
            lbl.grid(row=3, column=i, padx=5, pady=1)
            self.condition.append(lbl)

    def fetch_weather(self):
        """Fetch weather data in a background thread to prevent UI freezing."""
        city = self.textfield.get().strip()

        if not city:
            self.weather_label.config(text="Please Enter City Name")
            return

        self.loader.show()

        def task():
            try:
                start_time = time.time()
                location = get_location(city)
                weather = get_weather(city) if location else None
                weekly_forcast = get_weekly_forecast(city)
                #print(weekly_forcast)
                print(f"Location Fetch Time: {time.time() - start_time:.2f}s")  # Log time

                if not location or not weather:
                    raise ValueError("Invalid response from API")
                self.weather_label.config(text="Last Updated At")
                self.clock_label.config(text=location['time'])
                self.root.after(0, lambda: self.update_ui(location, weather, weekly_forcast))
            except Exception as e:
                print("API Error:", e)  # Debugging
                self.root.after(0, self.display_error)
            finally:
                self.root.after(100, self.loader.hide)

        threading.Thread(target=task, daemon=True).start()

    def display_error(self):
        """Display error message when API request fails."""
        for lbl in self.data_labels.values():
            lbl.config(text="Not available")
        self.weather_label.config(text="Error fetching data")


    def update_ui(self, location, weather, forecast):
        if weather:
            self.temp_label.config(text=f"{weather['temperature']}⁰C")
            self.feelsLike_label.config(text=f"Feels Like {weather['feelslike']}⁰C")
            self.data_labels["Wind"].config(text=f"{weather['wind_speed']} km/h")
            self.data_labels["Humidity"].config(text=f"{weather['humidity']}%")
            self.data_labels["Description"].config(text=weather['description'])
            self.data_labels["Pressure"].config(text=f"{weather['pressure']} hPa")
            self.loc_label.config(text=f"TimeZone : {location['timezone']}")

            # Update Main Weather Icon
            icon_code = weather["icon"]
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

            try:
                response = requests.get(icon_url)
                img = Image.open(BytesIO(response.content)).resize((100, 100), Image.Resampling.LANCZOS)
                self.logo_tk = ImageTk.PhotoImage(img)
                self.logo_label.config(image=self.logo_tk)
                self.logo_label.image = self.logo_tk  # Prevent garbage collection
            except Exception as e:
                print("Error loading main weather icon:", e)

            # 🟢 **Update Forecast for the Next 5 Days**
            if forecast:
                for i in range(5):                    
                    # Update Day Label
                    if(i==0):
                        self.days[i].config(text="Today")
                    else:
                        self.days[i].config(text=f"{forecast[i]['day']}")

                    # Update Temperature Label
                    self.temperatures[i].config(text=f"{forecast[i]['temp']}°C")

                    # Fetch and Update Weather Icon
                    icon_code = forecast[i]["icon"]
                    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
                    try:
                        response = requests.get(icon_url)
                        img = Image.open(BytesIO(response.content)).resize((55, 55), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        self.icons[i].config(image=img_tk)
                        self.icons[i].image = img_tk  # Prevent garbage collection
                        self.root.after(0)
                    except Exception as e:
                        print("Error loading forecast icon")

                    for i in range(5):
                        self.condition[i].config(text=f"{forecast[i]['condition']}")



# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import PhotoImage, Canvas
from PIL import Image, ImageTk
import threading
from modules.api import get_location, get_weather, get_weekly_forecast, get_icon
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

        self.temp_label.pack(pady=(90, 10))
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
        self.frame = tk.Frame(self.root, bg="#1ab5ef", padx=15, pady=10)
        self.frame.pack()

        labels = ["Wind", "Humidity", "Description", "Pressure"]
        self.data_labels = {}  # Dictionary to store labels for later updates

        for i, label in enumerate(labels):
            tk.Label(self.frame, text=label, font=("Arial", 15, 'bold'), bg='#1ab5ef', fg='white').grid(row=0, column=i, padx=10)
            self.data_labels[label] = tk.Label(self.frame, text="...", font=("Arial", 15), bg='#1ab5ef', fg='white')
            self.data_labels[label].grid(row=1, column=i, padx=10)

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
        self.clock_label.config(text="")
        self.loc_label.config(text="")
        self.weather_label.config(text="Error fetching data")
        self.temp_label.config(text="")
        self.feelsLike_label.config(text="Error in fetching")
        self.data_labels["Wind"].config(text="...")
        self.data_labels["Humidity"].config(text="...")
        self.data_labels["Description"].config(text="...")
        self.data_labels["Pressure"].config(text="...")
        logo_image = Image.open("assets/logo.png").resize((150, 130))
        self.logo_tk = ImageTk.PhotoImage(logo_image)
        self.logo_label.config(image=self.logo_tk)

        for i in range(5):
            # Update Day Label
            self.days[i].config(text="")

            self.temperatures[i].config(text="")

            self.icons[i].config(image="")

            self.condition[i].config(text="")


    def update_ui(self, location, weather, forecast):
        if weather:
            self.temp_label.config(text=f"{weather['temperature']}⁰C")
            self.feelsLike_label.config(text=f"Feels Like {weather['feelslike']}⁰C")
            self.data_labels["Wind"].config(text=f"{weather['wind_speed']} km/h")
            self.data_labels["Humidity"].config(text=f"{weather['humidity']}%")
            self.data_labels["Description"].config(text=weather['description'])
            self.data_labels["Pressure"].config(text=f"{weather['pressure']} hPa")
            self.loc_label.config(text=f"TimeZone : {location['timezone']}")
            self.logo_label.config(image="")
            # Update Main Weather Icon
            icon_code = weather["icon"]

            def load_main_icon():
                response=get_icon(icon_code)
                img = Image.open(BytesIO(response.content)).resize((100, 100), Image.Resampling.LANCZOS)
                self.root.after(0, lambda: update_main_icon(img))
            
            def update_main_icon(img):
                self.logo_tk = ImageTk.PhotoImage(img)
                self.logo_label.config(image=self.logo_tk)
                self.logo_label.image = self.logo_tk 
            threading.Thread(target=load_main_icon, daemon=True).start()

            # 🟢 **Update Forecast for the Next 5 Days**
        if forecast:
            for i in range(5):
                self.icons[i].config(image="")
                
            def load_forecast_icon(i,icon_code):
                try:
                    response = get_icon(icon_code)
                    img = Image.open(BytesIO(response.content)).resize((55, 55), Image.Resampling.LANCZOS)
                    self.root.after(0, lambda: update_forecast_icon(i, img))
                except Exception as e:
                    print(f"Error loading forecast icon for day {i}:", e)
                    self.root.after(0, lambda: update_forecast_icon(i, None))

            def update_forecast_icon(i,img):
                if(not img):
                   self.icons[i].config(text="Error")
                   return
                img_tk = ImageTk.PhotoImage(img)
                self.icons[i].config(image=img_tk)
                self.icons[i].image = img_tk  # Prevent garbage collection

            for i in range(5):
                # Update Day Label
                self.days[i].config(text="Today" if i == 0 else forecast[i]['day'])

                # Update Temperature Label
                self.temperatures[i].config(text=f"{forecast[i]['temp']}°C")

                # Fetch and Update Weather Icon in a separate thread
                icon_code = forecast[i]["icon"]
                threading.Thread(target=lambda: load_forecast_icon(i, icon_code), daemon=True).start()

                # Update Condition Label
                self.condition[i].config(text=f"{forecast[i]['condition']}")

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()  
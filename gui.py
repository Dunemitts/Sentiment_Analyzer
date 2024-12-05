import tkinter as tk
from tkinter import ttk
from main import ReviewAnalyzer #import function from main.py
import os

class HotelGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Hotel Review Analyzer")
        self.analyzer = ReviewAnalyzer()
        self.selected_hotel = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):

        # Allow the column and row to expand
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(3, weight=1)

        # Basic Search Options
        self.basic_search_frame = ttk.Frame(self.master)
        self.basic_search_frame.grid(column=0, row=0, columnspan=4, padx=5, pady=5)

        self.city_label = ttk.Label(self.basic_search_frame, text="Select City:")
        self.city_label.grid(column=0, row=0, padx=5, pady=5)

        self.city_var = tk.StringVar()
        self.city_dropdown = ttk.Combobox(self.basic_search_frame, textvariable=self.city_var, state='readonly')
        self.city_dropdown['values'] = ['Beijing', 'Chicago', 'Las-Vegas', 'London', 'Montreal', 'New-Delhi', 'New-York-City', 'San-Francisco', 'Shanghai']
        self.city_dropdown.grid(column=1, row=0, padx=5, pady=5)

        self.select_button = ttk.Button(self.basic_search_frame, text="Show Hotels", command=self.show_hotels)
        self.select_button.grid(column=2, row=0, padx=5, pady=5)

        self.select_hotel_button = ttk.Button(self.basic_search_frame, text="Select Hotel", command=self.select_hotel)
        self.select_hotel_button.grid(column=3, row=0, padx=5, pady=5)

        self.hotel_listbox = tk.Listbox(self.master, width=50)
        self.hotel_listbox.grid(column=0, row=3, columnspan=5, padx=5, pady=5, sticky="nsew")

        self.result_label = ttk.Label(self.master, text="", wraplength=400)
        self.result_label.grid(column=0, row=4, columnspan=5, padx=5, pady=5)

        self.result_frame = ttk.Frame(self.master)
        self.result_frame.grid(column=0, row=4, columnspan=3, padx=5, pady=5)

        self.positive_label = ttk.Label(self.result_frame, text="Positive Reviews: 0")
        self.positive_label.grid(column=0, row=0, sticky="W")

        self.negative_label = ttk.Label(self.result_frame, text="Negative Reviews: 0")
        self.negative_label.grid(column=1, row=0, sticky="W")

        self.total_reviews_label = ttk.Label(self.result_frame, text="Total Reviews: 0")
        self.total_reviews_label.grid(column=2, row=0, sticky="W")

        self.average_ratings_frame = ttk.Frame(self.result_frame)
        self.average_ratings_frame.grid(column=0, row=3, columnspan=3, sticky="W")

        # Advanced Search Options
        self.advanced_search_frame = ttk.Frame(self.master)
        self.advanced_search_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=5)

        self.breakfast_var = tk.IntVar()
        self.cleanliness_var = tk.IntVar()
        self.price_var = tk.IntVar()
        self.service_var = tk.IntVar()
        self.location_var = tk.IntVar()

        self.breakfast_label = ttk.Label(self.advanced_search_frame, text="Breakfast:")
        self.breakfast_label.grid(column=0, row=0, padx=5, pady=5)
        self.breakfast_dropdown = ttk.Combobox(self.advanced_search_frame, textvariable=self.breakfast_var, values=list(range(6)))
        self.breakfast_dropdown.set(0)
        self.breakfast_dropdown.grid(column=1, row=0, padx=5, pady=5)

        self.cleanliness_label = ttk.Label(self.advanced_search_frame, text="Cleanliness:")
        self.cleanliness_label.grid(column=2, row=0, padx=5, pady=5)
        self.cleanliness_dropdown = ttk.Combobox(self.advanced_search_frame, textvariable=self.cleanliness_var, values=list(range(6)))
        self.cleanliness_dropdown.set(0)
        self.cleanliness_dropdown.grid(column=3, row=0, padx=5, pady=5)

        self.price_label = ttk.Label(self.advanced_search_frame, text="Price:")
        self.price_label.grid(column=0, row=1, padx=5, pady=5)
        self.price_dropdown = ttk.Combobox(self.advanced_search_frame, textvariable=self.price_var, values=list(range(6)))
        self.price_dropdown.set(0)
        self.price_dropdown.grid(column=1, row=1, padx=5, pady=5)

        self.service_label = ttk.Label(self.advanced_search_frame, text="Service:")
        self.service_label.grid(column=2, row=1, padx=5, pady=5)
        self.service_dropdown = ttk.Combobox(self.advanced_search_frame, textvariable=self.service_var, values=list(range(6)))
        self.service_dropdown.set(0)
        self.service_dropdown.grid(column=3, row=1, padx=5, pady=5)

        self.location_label = ttk.Label(self.advanced_search_frame, text="Location:")
        self.location_label.grid(column=0, row=2, padx=5, pady=5)
        self.location_dropdown = ttk.Combobox(self.advanced_search_frame, textvariable=self.location_var, values=list(range(6)))
        self.location_dropdown.set(0)
        self.location_dropdown.grid(column=1, row=2, padx=5, pady=5)

        self.apply_filters_button = ttk.Button(self.advanced_search_frame, text="Apply Filters", command=self.apply_filters)
        self.apply_filters_button.grid(column=2, row=2, columnspan=2, padx=5, pady=5)

    def show_hotels(self):
        city = self.city_var.get()
        hotel_files = self.get_hotel_files(city)
        self.hotel_listbox.delete(0, tk.END) 
        for file in hotel_files:
            hotel_name = file[:-14].replace("_", " ").title()
            self.hotel_listbox.insert(tk.END, hotel_name)

    def get_hotel_files(self, city):
            processed_data_path = os.path.join("processed_data", city)
            return [file for file in os.listdir(processed_data_path) if file.endswith("_processed.csv")]

    def select_hotel(self):
        try:
            selected_index = self.hotel_listbox.curselection()[0]
            print(selected_index)
            selected_hotel = self.hotel_listbox.get(selected_index)
            print(f"Selected hotel: {selected_hotel}")
            self.selected_hotel.set(selected_hotel)
            self.search_hotel()
        except IndexError:
            self.result_label.config(text="Please select a hotel from the list.")

    def search_hotel(self):
        if self.selected_hotel.get():
            hotel_name = self.selected_hotel.get()
            hotel_file  = f"{hotel_name.lower().replace(' ', '_')}_processed.csv"
            print(f"Searching for processed file: {hotel_file}")
            self.search_processed_hotel(hotel_file)
            print(f"Analyzing {hotel_file}")
            result = self.analyze_document_sentiment(hotel_file.replace("_processed.csv", ""))
            if result:
                self.display_results(result)
        else:
            self.result_label.config(text="Please select a hotel from the list.")

    def search_processed_hotel(self, hotel_name):
        self.result_frame.pack_forget()
        self.result_label.config(text="Searching for existing file...")
        self.master.update_idletasks()
        self.analyzer.search_processed_hotel(hotel_name)
        if self.analyzer.file_processed:
            self.result_label.config(text=f"File found for {hotel_name}")

    def apply_filters(self):
        city = self.city_var.get()
        if not city:
            self.result_label.config(text="Please select a city first.")
            return
        
        filters = {
            'breakfast': self.breakfast_var.get() if self.breakfast_var.get() != 0 else None,
            'cleanliness': self.cleanliness_var.get() if self.cleanliness_var.get() != 0 else None,
            'price': self.price_var.get() if self.price_var.get() != 0 else None,
            'service': self.service_var.get() if self.service_var.get() != 0 else None,
            'location': self.location_var.get() if self.location_var.get() != 0 else None
        }
        
        filtered_hotels = self.analyzer.filter_hotels(city, filters)
        self.hotel_listbox.delete(0, tk.END)
        for hotel in filtered_hotels:
            self.hotel_listbox.insert(tk.END, hotel)


    def analyze_document_sentiment(self, hotel_name):
        self.result_frame.pack_forget()
        self.result_label.config(text="Analyzing...")
        self.master.update_idletasks()

        result = self.analyzer.analyze_document_sentiment(hotel_name)
        self.result_label.config(text="Analysis complete")
        return result
    
    def display_results(self, result):
        if not self.selected_hotel.get():
            return
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(0, weight=1)

        self.positive_label.config(text=f"Positive Reviews: {result['positive_reviews']}")
        self.negative_label.config(text=f"Negative Reviews: {result['negative_reviews']}")
        self.total_reviews_label.config(text=f"Total Reviews: {result['total_reviews']}")

        self.average_ratings_frame = ttk.Frame(self.result_frame)
        self.average_ratings_frame.grid(column=0, row=1, columnspan=3, sticky="W")

        for widget in self.average_ratings_frame.winfo_children():
            widget.grid(sticky="W", padx=5)

        for category, rating in result["average_ratings"].items():
            label = ttk.Label(self.average_ratings_frame, text=f"{category}: {rating}")
            label.grid(sticky="W", padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = HotelGUI(root)
    root.mainloop()

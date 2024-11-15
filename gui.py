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
        self.hotel_label = ttk.Label(self.master, text="Enter hotel name:")
        self.hotel_label.grid(column=0, row=0, padx=5, pady=5)

        self.hotel_entry = ttk.Entry(self.master)
        self.hotel_entry.grid(column=1, row=0, padx=5, pady=5)

        self.search_button = ttk.Button(self.master, text="Search", command=self.search_hotel)
        self.search_button.grid(column=2, row=0, padx=5, pady=5)

        self.city_label = ttk.Label(self.master, text="Select City:")
        self.city_label.grid(column=0, row=1, padx=5, pady=5)

        self.city_var = tk.StringVar()
        self.city_dropdown = ttk.Combobox(self.master, textvariable=self.city_var, state='readonly')
        self.city_dropdown['values'] = ['Beijing', 'Chicago', 'Las-Vegas', 'London', 'Montreal', 'New-Delhi', 'New-York-City', 'San-Francisco', 'Shanghai']
        self.city_dropdown.grid(column=1, row=1, padx=5, pady=5)

        self.hotel_listbox = tk.Listbox(self.master)
        self.hotel_listbox.grid(column=1, row=2, columnspan=2, padx=5, pady=5)

        self.select_button = ttk.Button(self.master, text="Show Hotels", command=self.show_hotels)
        self.select_button.grid(column=2, row=1, padx=5, pady=5)

        self.select_hotel_button = ttk.Button(self.master, text="Select Hotel", command=self.select_hotel)
        self.select_hotel_button.grid(column=3, row=1, padx=5, pady=5)

        self.result_label = ttk.Label(self.master, text="", wraplength=400)
        self.result_label.grid(column=0, row=3, columnspan=3, padx=5, pady=5)

        self.result_frame = ttk.Frame(self.master)
        self.result_frame.grid(column=0, row=3, columnspan=3, padx=5, pady=5)

        self.positive_label = ttk.Label(self.result_frame, text="Positive Reviews: 0")
        self.positive_label.grid(column=0, row=0, sticky="W")

        self.negative_label = ttk.Label(self.result_frame, text="Negative Reviews: 0")
        self.negative_label.grid(column=1, row=0, sticky="W")

        self.total_reviews_label = ttk.Label(self.result_frame, text="Total Reviews: 0")
        self.total_reviews_label.grid(column=2, row=0, sticky="W")

        self.average_ratings_frame = ttk.Frame(self.result_frame)
        self.average_ratings_frame.grid(column=0, row=1, columnspan=3, sticky="W")

    def show_hotels(self):
        city = self.city_var.get()
        hotel_files = self.get_hotel_files(city)
        self.hotel_listbox.delete(0, tk.END)  # Clear existing items
        for file in hotel_files:
            self.hotel_listbox.insert(tk.END, file)

    def get_hotel_files(self, city):
            processed_data_path = os.path.join("processed_data", city)
            return [file for file in os.listdir(processed_data_path) if file.endswith("_processed.csv")]

    def select_hotel(self):
        try:
            selected_index = self.hotel_listbox.curselection()[0]
            print(selected_index)
            selected_hotel = self.hotel_listbox.get(selected_index)
            print(selected_hotel)
            self.selected_hotel.set(selected_hotel)
            self.search_hotel()
        except IndexError:
            self.result_label.config(text="Please select a hotel from the list.")

    def search_hotel(self):
        if self.selected_hotel.get():
            hotel_name = self.selected_hotel.get()
        else:
            hotel_name = self.hotel_entry.get()
        print(f"searching {hotel_name}")
        self.search_processed_hotel(hotel_name)
        print(f"analyzing {hotel_name}")
        result = self.analyze_document_sentiment(hotel_name)
        if result:
            self.display_results(result)

    def search_processed_hotel(self, hotel_name):
        self.result_frame.pack_forget()
        self.result_label.config(text="Searching for existing file...")
        self.master.update_idletasks()
        self.analyzer.search_processed_hotel(hotel_name)
        if self.analyzer.file_processed:
            self.result_label.config(text=f"File found for {hotel_name}")
        else:
            self.result_label.config(text="Processing new file...")
            self.master.update_idletasks()
            self.analyzer.process_file(hotel_name)
            self.result_label.config(text=f"Processed {hotel_name}")

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

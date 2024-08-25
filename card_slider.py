import customtkinter as ctk
from PIL import Image, ImageTk

import pymysql

import requests
from io import BytesIO    

import os
from dotenv import load_dotenv


load_dotenv()

class ProductCard(ctk.CTkFrame):
    def __init__(self, master, image, name, price, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.image = image.resize((100, 100), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.image)
        
        self.image_label = ctk.CTkLabel(self, image=self.photo)
        self.image_label.pack()
        
        self.name_label = ctk.CTkLabel(self, text=name)
        self.name_label.pack()
        
        self.price_label = ctk.CTkLabel(self, text=f"${price}")
        self.price_label.pack()

class ScrollableFrame(ctk.CTkFrame):
    def __init__(self, master, load_more_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.canvas = ctk.CTkCanvas(self)
        self.scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.load_more_callback = load_more_callback
        self.canvas.bind("<Configure>", self.on_scroll)

    def on_scroll(self, event):
        if self.canvas.yview()[1] > 0.9:
            self.load_more_callback()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Product Catalog")
        self.geometry("600x400")
        
        self.scrollable_frame = ScrollableFrame(self, self.load_more_products)
        self.scrollable_frame.pack(fill="both", expand=True)
        
        self.offset = 0
        self.limit = 20
        self.load_more_products()
    
    def fetch_products(self, offset, limit):
        connection = pymysql.connect(
            host=os.getenv('HOST'),
            port=int(os.getenv('PORT')),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            db=os.getenv('DATABASE'),
        )
        cursor = connection.cursor()
        cursor.execute("SELECT image, title, price FROM postings LIMIT %s OFFSET %s", (limit, offset))
        products = cursor.fetchall()
        connection.close()
        return products
    
    def load_image(self, image_path):
        response = requests.get(image_path)
        img_data = BytesIO(response.content)  # Use BytesIO to handle the image data
        img = Image.open(img_data)
        return img

    def load_more_products(self):
        products = self.fetch_products(self.offset, self.limit)
        for image_path, name, price in products:
            img = self.load_image(image_path)
            card = ProductCard(self.scrollable_frame.scrollable_frame, img, name, price)
            card.pack(pady=10)
        self.offset += self.limit

if __name__ == "__main__":
    app = App()
    app.mainloop()

import tkinter as tk
import customtkinter as ctk
import os
import json

# Represents an item
class Item():
    def __init__(self,
                 name: str = "Item",
                 price : float = 0.0):
        self.name = name
        self.price = price

    def get_name(self):
        return self.name
    
    def get_price(self):
        return self.price

# Custom default packing method
def default_pack(object, **kwargs):
        kwargs.setdefault('padx', 10)
        kwargs.setdefault('pady', 5)
        kwargs.setdefault('fill', 'x')
        object.pack(**kwargs)

# Button for Selecting a file with file path display
class CTkItemListing(ctk.CTkFrame):
    def __init__(self,
                 master,
                 controller,
                 item : Item = None,
                 **kwargs):
        super().__init__(master = master, 
                         fg_color="#252525",
                         **kwargs)

        self.controller = controller
        self.item = item

        self.display = ctk.CTkFrame(master = self, fg_color = "transparent")
        self.display.pack(pady = 5)

        # Name display
        self.name_display = ctk.CTkLabel(
            master = self.display,
            text = self.item.get_name(),
            anchor = 'w',
            width = 160
        )
        self.name_display.pack(side = tk.LEFT, padx = (10, 5))

        # Price display
        self.price_display = ctk.CTkLabel(
            master = self.display,
            text = f"{self.item.get_price():.2f}€",
            text_color = "#65CF33",
            anchor = 'e',
            width = 30
        )
        self.price_display.pack(side = tk.LEFT, padx = (5, 10))

        # Remove from shopping list button
        self.button = ctk.CTkButton(
            master = self.display,
            width = 28,
            height = 28,
            fg_color = "#585858",
            hover_color = "#353535",
            text = "-",
            command = self.delist)
        self.button.pack(side = tk.LEFT, pady = 2, padx = (0, 10))

    def delist(self):
        self.controller.remove_item_listing(self)
        self.destroy()

# Interface for adding a new item to the shopping list
class CTkItemListingPrompt(ctk.CTkFrame):
    def __init__(self,
                 master,
                 controller,
                 item : Item = Item("New Item", 0.00),
                 **kwargs):
        super().__init__(master = master,
                         fg_color="#383838",
                          **kwargs)

        self.name = tk.StringVar(value = item.get_name())
        self.price = tk.StringVar(value = str(item.get_price()))
        self.controller = controller

        self.display = ctk.CTkFrame(master = self, fg_color = "transparent")
        self.display.pack(pady = 5)

        # Slot to insert item name
        self.name_entry = ctk.CTkEntry(
            master = self.display,
            width = 120,
            textvariable = self.name)
        self.name_entry.pack(side = tk.LEFT, padx = (10, 10))

        # Slot to insert item price
        self.price_entry = ctk.CTkEntry(
            master = self.display,
            width = 60,
            textvariable = self.price)
        self.price_entry.pack(side = tk.LEFT, padx = (10, 10))

        # Add to shopping list button
        self.button = ctk.CTkButton(
            master = self.display,
            width = 28,
            height = 28,
            fg_color = "#65CF33",
            hover_color = "#32661B",
            text = "+",
            command = self.list)
        self.button.pack(side = tk.LEFT, padx = (0, 2), pady = 2)

        # Cancel button
        self.cancel_button = ctk.CTkButton(
            master = self.display,
            width = 28,
            height = 28,
            fg_color = "#f16262",
            hover_color = "#863c3c",
            text = "X",
            command = self.cancel)
        self.cancel_button.pack(side = tk.LEFT, pady = 2, padx = (2, 10))
    
    def valid_price(self):
        try:
            return float(self.price.get()) >= 0.00
        except ValueError:
            return False

    def list(self):
        name = self.name.get().strip()
        if name and self.valid_price():
            self.controller.add_item_listing(Item(name, round(float(self.price.get()), 2)))
            self.controller.remove_item_prompt(self)
            self.destroy()

    def cancel(self):
        self.controller.remove_item_prompt(self)
        self.destroy()

class ListFrame(ctk.CTkFrame):
    def __init__(self,
                 master,
                 controller,
                 items_listings : list[Item],
                 items_prompts : list[Item],
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.controller : ShoppingListApp = controller

        # Item list
        self.listing_list : list[CTkItemListing] = []
        self.prompt_list : list[CTkItemListingPrompt] = []

        # Purchase total
        self.total : float = 0.0

        # Listings display
        self.listing_display = ctk.CTkScrollableFrame(self, fg_color = "transparent")
        default_pack(self.listing_display, expand = True, fill = 'both')

        self.new_item_button = ctk.CTkButton(
            master = self.listing_display,
            width = 140,
            height = 48,
            text = "Add an Item",
            command = self.add_item_prompt)
        default_pack(self.new_item_button, side = 'bottom')

        # Total display
        self.total_frame = ctk.CTkFrame(self, fg_color = "#252525")
        default_pack(self.total_frame, pady = (0, 10))

        self.total_label = ctk.CTkLabel(
            master=self.total_frame,
            text="Total:",
            anchor="w"
        )
        self.total_label.pack(side = tk.LEFT, padx = (10, 0))

        self.total_value = ctk.CTkLabel(
            master=self.total_frame,
            text="0.00€",
            text_color = "#4CAF50",
            anchor="e"
        )
        self.total_value.pack(side = tk.RIGHT, padx = (0, 10))

        for item in items_listings:
            self.add_item_listing(item)
        for item in items_prompts:
            self.add_item_prompt(item)

    def add_item_listing(self, item : Item):
        listing = CTkItemListing(
            master = self.listing_display,
            controller = self,
            item = item
        )
        self.listing_list.append(listing)
        self.update_total(item.get_price())
        self.refresh_listing_display()

    def remove_item_listing(self, listing : CTkItemListing):
        self.listing_list.remove(listing)
        self.add_item_prompt(listing.item)
        self.update_total(-listing.item.get_price())

    def update_total(self, price : float):
        self.total += price
        self.total_value.configure(text = f"{self.total:.2f}€")

    def refresh_listing_display(self):
        self.listing_list.sort(reverse = True, key = lambda listing : listing.item.get_price())
        for listing in self.listing_list:
            listing.pack_forget()
            default_pack(listing, side = 'top', padx = 9)

    def add_item_prompt(self, item : Item = Item("New Item", 0.00)):
        prompt = CTkItemListingPrompt(
            master = self.listing_display,
            controller = self,
            item = item,
        )
        self.prompt_list.append(prompt)
        default_pack(prompt, side = 'bottom', padx = 9)

    def remove_item_prompt(self, prompt : CTkItemListingPrompt):
        self.prompt_list.remove(prompt)

class AppData:
    def __init__(self, filename = "steam_basket.json"):
        self.filename = filename

    def save(self, listings : list[CTkItemListing], prompts : list[CTkItemListingPrompt]):
        data = {
            'listings' : [{"name": listing.item.get_name(), "price": listing.item.get_price()} for listing in listings],
            'prompts' : [{"name": prompt.name.get(), "price": float(prompt.price.get()) if prompt.valid_price() else 0.00} for prompt in prompts]
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load(self):
        if not os.path.exists(self.filename):
            return [], []
        else:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            items_listings = [Item(i["name"], i["price"]) for i in data.get('listings', [])]
            items_prompts = [Item(i["name"], i["price"]) for i in data.get('prompts', [])]
            return items_listings, items_prompts

# Main app controller
class ShoppingListApp:
    def __init__(self, root):
        self.root : ctk.CTk = root
        self.root.title("SteamBasket")
        self.root.geometry(f"400x600")
        self.root.minsize(400, 600)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.data = AppData()
        items_listings, items_prompts = self.data.load()

        # Create main frame
        self.main_frame = ListFrame(
            master = self.root, 
            controller = self,
            items_listings = items_listings,
            items_prompts = items_prompts)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_close(self):
        self.data.save(self.main_frame.listing_list, self.main_frame.prompt_list)
        self.root.destroy()

# Main program loop
def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()

    app  = ShoppingListApp(root)
    root.mainloop()

# Use of special variable to start the program on main
if __name__=="__main__":
    main()
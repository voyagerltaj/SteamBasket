import tkinter as tk
import customtkinter as ctk

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
    def __init__(self, *args,
                 controller = None,
                 item : Item = None,
                 **kwargs):
        super().__init__(*args, 
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
        self.controller.remove_item(self.item)
        self.destroy()

# Interface for adding a new item to the shopping list
class CTkItemListingPrompt(ctk.CTkFrame):
    def __init__(self, *args,
                 controller = None,
                 item = None,
                 **kwargs):
        super().__init__(*args,
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
            command = self.destroy)
        self.cancel_button.pack(side = tk.LEFT, pady = 2, padx = (2, 10))

    def list(self):
        try:
            price = float(self.price.get())
            name = self.name.get().strip()
            if name:
                self.controller.add_item(Item(name, round(price, 2)))
                self.destroy()
        except ValueError:
            pass

class ListFrame(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller : ShoppingListApp = controller

        # Item list
        self.item_list : list[Item] = []
        self.listing_list : list[CTkItemListing] = []

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

    def add_item(self, item):
        self.item_list.append(item)
        self.item_list.sort(reverse = True, key = lambda Item : Item.get_price())
        self.update_total()
        self.refresh_listing_display()

    def remove_item(self, item):
        self.item_list.remove(item)
        self.add_item_prompt(item)
        self.update_total()

    def update_total(self):
        self.total = 0.0
        for item in self.item_list:
            self.total += item.get_price()
        self.total_value.configure(text = f"{self.total:.2f}€")

    def refresh_listing_display(self):
        for frame in self.listing_list:
            frame.destroy()
        self.listing_list.clear()

        for item in self.item_list:
            frame = CTkItemListing(
                master = self.listing_display,
                item = item,
                controller = self
            )
            default_pack(frame, side = 'top', padx = 9)
            self.listing_list.append(frame)

    def add_item_prompt(self, item = Item("New Item", 0.00)):
        frame = CTkItemListingPrompt(
            master = self.listing_display,
            item = item,
            controller = self
        )
        default_pack(frame, side = 'bottom', padx = 9)

# Main app to manage frames
class ShoppingListApp:
    def __init__(self, root):
        self.root : ctk.CTk = root
        self.root.title("Shopping List")
        self.root.geometry(f"400x600")

        # Create main frame
        self.main_frame = ListFrame(self.root, self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
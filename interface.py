import customtkinter as CTK
import subprocess
from tkinter import filedialog
import os
import shutil

class SimpleDialog(CTK.CTk):
    def __init__(self, master=None, title="", message=""):
        super().__init__(master)
        self.title(title)
        self.geometry('300x150')
        
        label = CTK.CTkLabel(self, text=message, font=('Roboto', 14))
        label.pack(pady=20, padx=20)
        
        button = CTK.CTkButton(self, text="OK", command=self.destroy)
        button.pack(pady=10)
        
        self.iconbitmap('Files/statics/error.ico')

class CustomFrame(CTK.CTkFrame):
    def __init__(self, master=None, label_text="", combobox_values=[], **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = CTK.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.combobox = CTK.CTkComboBox(self, values=combobox_values, state='readonly')
        self.combobox.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.columnconfigure(1, weight=1)  # Ensure the combobox expands to fill space
        
class CustomEntryFrame(CTK.CTkFrame):
    def __init__(self, master=None, label_text="", **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = CTK.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.entry = CTK.CTkEntry(self)
        self.entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.columnconfigure(1, weight=1)  # Ensure the combobox expands to fill space
        
def center_window(window, width, height):
    # Obtém as dimensões da tela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcula a posição x e y para centralizar a janela
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Define a geometria da janela
    window.geometry(f'{width}x{height}+{x}+{y}')

country_list_BB = ['USA', 'CND']
country_list_Amazon = ['USA', 'MXC', 'India', 'BR']

def show_message():
    dialog = SimpleDialog(title="Error", message="Some Field is Missing")
    center_window(dialog, 300, 150)
    dialog.mainloop()

def on_confirm():
    keyword_value = keyword.get()
    need_change_location = check_var.get() == 'on'
    selected_retail = retail.get()
    selected_country = country.get()

    if not keyword_value or not selected_retail or not selected_country:
        show_message()
        return
    
    try:
        if selected_retail == "Best Buy" and selected_country == "USA":
            subprocess.run(['python', 'Files/scrapers/best_buy.py', keyword_value], check=True)
        elif selected_retail == "Best Buy" and selected_country == "CND":
            # subprocess.run(['python', 'scrapers/best_buy_cnd.py', keyword_value], check=True)
            dialog = SimpleDialog(title="In progress", message="Not there yet, future release")
            center_window(dialog, 300, 150)
            dialog.mainloop()
        elif selected_retail == "Amazon":
            subprocess.run(['python', 'Files/scrapers/amazon.py', keyword_value, selected_country, str(need_change_location)], check=True)
        
        # Habilitar o botão de download após a conclusão do subprocesso
        download_button.configure(state='normal')
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the script: {e}")
        show_message()
    

def update_country_list(*args):
    selected_retail = retail.get()
    if selected_retail == 'Best Buy':
        list_CB = country_list_BB
    elif selected_retail == 'Amazon':
        list_CB = country_list_Amazon
    else:
        list_CB = ['Error']
    country_combobox.configure(values=list_CB)
    if list_CB:
        country_combobox.set(list_CB[0])  # Set default value if available

def on_button_click():
    directory = filedialog.askdirectory(title="Choose a folder to Download the CSV")
    if directory:
        save_csv_file(directory)

def save_csv_file(directory):
    source_file = "Files/outputs/Best_Buy/product_data.csv"
    if os.path.exists(source_file):
        destination_file = os.path.join(directory, "product_data.csv")
        shutil.copy(source_file, destination_file)
        print(f"Arquivo salvo em: {destination_file}")
    else:
        print(f"O arquivo {source_file} não existe.")
    source_file = 'Files/outputs/Best_Buy/new_models.csv'
    if os.path.exists(source_file):
        destination_file = os.path.join(directory, "added_models.csv")
        shutil.copy(source_file, destination_file)
        print(f"Arquivo salvo em: {destination_file}")
    else:
        print(f"O arquivo {source_file} não existe.")
    source_file = 'Files/outputs/Best_Buy/old_models.csv'
    if os.path.exists(source_file):
        destination_file = os.path.join(directory, "removed_models.csv")
        shutil.copy(source_file, destination_file)
        print(f"Arquivo salvo em: {destination_file}")
    else:
        print(f"O arquivo {source_file} não existe.")

CTK.set_appearance_mode('dark')
CTK.set_default_color_theme('dark-blue')

# Setup the main window
root = CTK.CTk()
width, height = 800, 500
center_window(root, width, height)

root.title("Scraper For Retails")
# Define the icon for the application
root.iconbitmap('Files/statics/favicon.ico')

frame = CTK.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill='both', expand=True)

label = CTK.CTkLabel(master=frame, text='Scraper for Retails', font=('Roboto', 30))
label.pack(pady=24, padx=20)

# Create and pack the CTkEntry
keyword = CTK.StringVar(value="")
keyword_frame = CustomEntryFrame(frame, label_text="Keyword to Scrape")
keyword_frame.pack(pady=10, padx=20, fill='x')
keyword_frame.entry.configure(textvariable=keyword)

# Retail combobox frame
retail_frame = CustomFrame(frame, label_text="            Retail            ", combobox_values=['Amazon', 'Best Buy'])
retail_frame.pack(pady=10, padx=20, fill='x')

retail = CTK.StringVar(value="")
retail_frame.combobox.configure(variable=retail)
retail.trace_add('write', update_country_list)

# Country combobox frame
country_frame = CustomFrame(frame, label_text=" Country to Scrape ", combobox_values=[''])
country_frame.pack(pady=10, padx=20, fill='x')

country_combobox = country_frame.combobox
country = CTK.StringVar(value="")
country_combobox.configure(variable=country)

check_var = CTK.StringVar(value="on")
need_change_location_cb = CTK.CTkCheckBox(master=frame, text='Are you scraping inside the target country?', variable=check_var, onvalue='on', offvalue='off')
need_change_location_cb.pack(pady=24, padx=20)

confirm_button = CTK.CTkButton(master=frame, text='Confirm', command=on_confirm)
confirm_button.pack(pady=10, padx=20)

download_button = CTK.CTkButton(master=frame, text='Download Products Data', command=on_button_click, state='disabled')
download_button.pack(pady=10, padx=20)

root.mainloop()

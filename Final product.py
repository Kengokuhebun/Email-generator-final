import customtkinter
import sqlite3
import bcrypt
import tkinter
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


customtkinter.set_appearance_mode("dark")  # Set dark mode
customtkinter.set_default_color_theme("dark-blue")  # Set color scheme

app = customtkinter.CTk()
app.geometry('600x440')
app.title('Login and Sign Up System')

# Connect to database
conn = sqlite3.connect('data.sql')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        business_name TEXT NOT NULL,
        owner_name TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')

# Define signup function
def Signupbutton_function():
    username = usernameentry1.get()
    password = passwordentry1.get()
    if username != '' and password != '':
        cursor.execute('SELECT username FROM users WHERE username=?', (username,))
        if cursor.fetchone() is not None:
            messagebox.showerror('Error', 'Username already exists.')
        else:
            encoded_password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
            cursor.execute('INSERT INTO users VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            messagebox.showinfo('Success', 'Account created successfully.')
    else:
        messagebox.showerror('Error', 'Enter all data.')

# Define login function
def Loginbutton2_function():
    global username  # Declare username as global to store the logged-in user
    username = usernameentry2.get()
    password = passwordentry2.get()
    if username != '' and password != '':
        cursor.execute('SELECT password FROM users WHERE username=?', [username])
        result = cursor.fetchone()
        if result:
            if bcrypt.checkpw(password.encode('utf-8'), result[0]):
                messagebox.showinfo('Success', 'Logged in successfully')
                show_main_menu()  # Call the function to display the main menu
            else:
                messagebox.showerror('Error', 'Invalid password')
        else:
            messagebox.showerror('Error', 'User does not exist.')
    else:
        messagebox.showerror('Error', 'Enter all data.')


# Define the email composition function
import random

# Creating the main menu window after successful login
selected_contacts = []

def add_contact():
    business_name = business_name_entry.get()
    owner_name = owner_name_entry.get()
    email = email_entry.get()

    if business_name and owner_name and email:
        contact = {'Business': business_name, 'Owner': owner_name, 'Email': email}

        # Insert the contact into the SQLite database
        cursor.execute('INSERT INTO contacts (business_name, owner_name, email) VALUES (?, ?, ?)',
                       (business_name, owner_name, email))
        conn.commit()

        # Clear the input fields after adding
        business_name_entry.delete(0, END)
        owner_name_entry.delete(0, END)
        email_entry.delete(0, END)

        # Update the contact listbox
        update_contact_listbox()
        messagebox.showinfo('Success', 'Contact added successfully!')
    else:
        messagebox.showerror('Error', 'All fields are required!')

# Function to update the listbox with contacts from the database
def update_contact_listbox():
    contact_listbox.delete(0, END)  # Clear the listbox

    cursor.execute('SELECT rowid, business_name, owner_name FROM contacts')
    contacts = cursor.fetchall()  # Fetch all contacts from the database

    for idx, contact in enumerate(contacts):
        contact_listbox.insert(END, f"{idx+1}. {contact[1]} - {contact[2]}")

# Function to select contacts for email
def select_contact(event):
    global selected_contacts
    selected_contacts.clear()
    selected = contact_listbox.curselection()  # Get selected contact(s) index
    for index in selected:
        contact_id = contact_listbox.get(index).split(".")[0]  # Extract rowid
        cursor.execute('SELECT email FROM contacts WHERE rowid=?', (contact_id,))
        email = cursor.fetchone()[0]
        selected_contacts.append(email)  # Add the email of the selected contact
    messagebox.showinfo('Selected', f'Selected {len(selected_contacts)} contact(s) for email.')

# Function to send an email to the selected contacts



# Function to clear the current frame
def clear_frame():
    for widget in app.winfo_children():
        widget.destroy()

# Show the main menu after login
# Show the main menu after login
def show_main_menu():
    clear_frame()
    app.geometry('1000x600')  # Resize window for main menu

    # Create a frame for the sidebar
    sidebar_frame = customtkinter.CTkFrame(app, width=200)
    sidebar_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    # Sidebar content
    sidebar_label = customtkinter.CTkLabel(sidebar_frame, text="Menu", font=('Century Gothic', 18))
    sidebar_label.pack(pady=20)

    add_contact_button = customtkinter.CTkButton(sidebar_frame, text="Add Contact", command=show_add_contact_form)
    add_contact_button.pack(pady=10)

    generate_email_button = customtkinter.CTkButton(sidebar_frame, text="Generate Email", command=show_generate_email_window)
    generate_email_button.pack(pady=10)

    # Create a frame for the main content
    main_content_frame = customtkinter.CTkFrame(app)
    main_content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

    main_label = customtkinter.CTkLabel(main_content_frame, text="Welcome to the Main Menu", font=('Century Gothic', 24))
    main_label.pack(pady=20)

    # Additional content can be added here
    info_label = customtkinter.CTkLabel(main_content_frame, text="Select an option from the menu to get started.", font=('Century Gothic', 16))
    info_label.pack(pady=10)


# Function to show the form for adding contacts
def show_add_contact_form():
    clear_frame()

    label = customtkinter.CTkLabel(app, text="Add a New Contact", font=('Century Gothic', 20))
    label.pack(pady=20)

    global business_name_entry, owner_name_entry, email_entry

    # Business name entry
    business_name_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Business Name")
    business_name_entry.pack(pady=10)

    # Owner name entry
    owner_name_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Owner Name")
    owner_name_entry.pack(pady=10)

    # Email entry
    email_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Email Address")
    email_entry.pack(pady=10)

    # Add contact button
    add_contact_button = customtkinter.CTkButton(app, text="Add Contact", command=add_contact)
    add_contact_button.pack(pady=20)

    # Back button to return to main menu
    back_button = customtkinter.CTkButton(app, text="Back", command=show_main_menu)
    back_button.pack(pady=10)

    # Display the list of contacts
    global contact_listbox
    contact_listbox = customtkinter.CTkListbox(app, width=400, height=150)
    contact_listbox.pack(pady=20)
    contact_listbox.bind('<<ListboxSelect>>', select_contact)

    update_contact_listbox()  # Display any pre-existing contacts

# Function to show the email sending window
# Function to show the email generation window
def show_generate_email_window():
    clear_frame()

    label = customtkinter.CTkLabel(app, text="Generate Email", font=('Century Gothic', 20))
    label.pack(pady=20)

    # Create a text box for subject input
    subject_label = customtkinter.CTkLabel(app, text="Subject:", font=('Century Gothic', 14))
    subject_label.pack(pady=5)

    global subject_entry
    subject_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Enter Subject")
    subject_entry.pack(pady=10)

    # Tone selection
    tone_label = customtkinter.CTkLabel(app, text="Select Tone:", font=('Century Gothic', 14))
    tone_label.pack(pady=5)

    tone_var = StringVar(value="neutral")  # Default tone

    tones = ["Serious", "Persuasive", "Neutral"]
    for tone in tones:
        tone_radio = customtkinter.CTkRadioButton(app, text=tone, variable=tone_var, value=tone.lower())
        tone_radio.pack(anchor='w')

    # Button to generate email
    generate_email_button = customtkinter.CTkButton(app, text="Generate Email", command=lambda: generate_email(tone_var.get()))
    generate_email_button.pack(pady=20)

    # Text box for generated email
    global generated_email_textbox
    generated_email_textbox = customtkinter.CTkTextbox(app, height=150, width=400)
    generated_email_textbox.pack(pady=10)

    # Back button to return to main menu
    back_button = customtkinter.CTkButton(app, text="Back", command=show_main_menu)
    back_button.pack(pady=10)

    # Display the list of contacts in a sidebar
    sidebar_frame = customtkinter.CTkFrame(app, width=200)
    sidebar_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    global contact_listbox
    contact_listbox = Listbox(sidebar_frame, selectmode=MULTIPLE, width=30, height=20)
    contact_listbox.pack(pady=10)
    contact_listbox.bind('<<ListboxSelect>>', select_contact)

    update_contact_listbox()  # Display any pre-existing contacts

# Function to update the listbox with contacts from the database
def update_contact_listbox():
    contact_listbox.delete(0, END)  # Clear the listbox

    cursor.execute('SELECT rowid, business_name, owner_name FROM contacts')
    contacts = cursor.fetchall()  # Fetch all contacts from the database

    for contact in contacts:
        contact_listbox.insert(END, f"{contact[0]}. {contact[1]} - {contact[2]}")

# Function to generate email based on subject and tone
def generate_email(tone):
    subject = subject_entry.get().strip()
    if not subject:
        messagebox.showerror('Error', 'Please enter a subject.')
        return

    # Check if any contacts are selected
    if not selected_contacts:
        messagebox.showerror('Error', 'Please select at least one contact.')
        return

    email_variations = {
        "meeting": {
            "serious": [
                "Please be reminded of the upcoming meeting. Your attendance is crucial.",
                "This is a formal reminder about the meeting scheduled for next week. Please prepare accordingly.",
                "I would like to emphasize the importance of our meeting next week. Please ensure your presence."
            ],
            "persuasive": [
                "I highly encourage you to attend the meeting next week. Your input is invaluable!",
                "Don't miss out on the opportunity to contribute to our meeting next week. Your voice matters!",
                "Join us for the meeting next week and share your thoughts. We need your insights!"
            ],
            "neutral": [
                "We have a meeting scheduled for next week. Please mark your calendars.",
                "Just a reminder about the meeting next week. Looking forward to seeing everyone.",
                "The meeting is set for next week. Please be prepared to discuss the agenda."
            ]
        },
        "contract": {
            "serious": [
                "Please review the contract carefully. It is imperative that we adhere to the terms.",
                "This contract requires your immediate attention. Please ensure compliance.",
                "I must stress the importance of understanding the contract details thoroughly."
            ],
            "persuasive": [
                "I believe this contract will greatly benefit us. Let's discuss it further.",
                "This contract presents a fantastic opportunity. I urge you to consider it seriously.",
                "I am confident that this contract will lead to positive outcomes for us."
            ],
            "neutral": [
                "Attached is the contract for your review. Please let me know your thoughts.",
                "Here is the contract we discussed. Looking forward to your feedback.",
                "Please find the contract attached for your consideration."
            ]
        },
        "event invitation": {
            "serious": [
                "You are formally invited to the event. Your presence is essential.",
                "This is a formal invitation to the event. Please RSVP at your earliest convenience.",
                "We would like to formally invite you to the event. Your attendance is important."
            ],
            "persuasive": [
                "We would love for you to join us at the event! It promises to be an exciting occasion.",
                "Don't miss out on this event! Your participation will make it even more special.",
                "Join us for an unforgettable experience at the event. We can't wait to see you there!"
            ],
            "neutral": [
                "You are invited to the event. Please let us know if you can attend.",
                "We are hosting an event and would like you to join us. Details to follow.",
                "This is an invitation to our upcoming event. We hope to see you there."
            ]
        }
    }

    if subject.lower() in email_variations:
        generated_email_textbox.delete("1.0", END)  # Clear previous text
        for contact in selected_contacts:
            cursor.execute('SELECT owner_name FROM contacts WHERE email=?', (contact,))
            client_name = cursor.fetchone()
            client_name = client_name[0] if client_name else "Client"

            personalized_emails = email_variations[subject.lower()][tone]
            for email_body in personalized_emails:
                formatted_email = (
                    f"Subject: {subject}\n\n"
                    f"Dear {client_name},\n\n"
                    f"{email_body}\n\n"
                    "Best regards,\nYour Team"
                )
                generated_email_textbox.insert(END, formatted_email + "\n\n")  # Insert each variation
    else:
        messagebox.showerror('Error', 'Subject not recognized. Please use meeting, contract, or event invitation.')

# Update the button in the main menu to call the new function

def show_manage_clients_window():
    # Clear the current frame and prepare the manage clients window
    clear_frame()

    label = customtkinter.CTkLabel(app, text="Manage Clients", font=('Century Gothic', 20))
    label.pack(pady=20)

    global contact_frame
    contact_frame = customtkinter.CTkFrame(app)
    contact_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Back button to return to the main menu
    back_button = customtkinter.CTkButton(app, text="Back", command=show_main_menu)
    back_button.pack(pady=10)

    display_all_contacts()

def display_all_contacts():
    # Clear existing widgets in the frame
    for widget in contact_frame.winfo_children():
        widget.destroy()

    cursor.execute('SELECT rowid, business_name, owner_name, email FROM contacts')
    contacts = cursor.fetchall()

    if not contacts:
        no_contacts_label = customtkinter.CTkLabel(contact_frame, text="No contacts available.", font=('Century Gothic', 16))
        no_contacts_label.pack(pady=20)
        return

    for contact in contacts:
        rowid, business_name, owner_name, email = contact

        # Create a card for each contact
        card = customtkinter.CTkFrame(contact_frame, corner_radius=10)
        card.pack(fill=X, padx=10, pady=5)

        contact_info = f"{business_name}\nOwner: {owner_name}\nEmail: {email}"
        contact_label = customtkinter.CTkLabel(card, text=contact_info, font=('Century Gothic', 14))
        contact_label.pack(side=LEFT, padx=10)

        # Add Edit and Delete buttons
        edit_button = customtkinter.CTkButton(card, text="Edit", width=100, command=lambda c=contact: edit_contact(c))
        edit_button.pack(side=RIGHT, padx=10, pady=5)

        delete_button = customtkinter.CTkButton(card, text="Delete", width=100, command=lambda rid=rowid: delete_contact(rid))
        delete_button.pack(side=RIGHT, padx=10, pady=5)

def edit_contact(contact):
    rowid, business_name, owner_name, email = contact

    # Clear the current frame for editing
    clear_frame()

    label = customtkinter.CTkLabel(app, text="Edit Contact", font=('Century Gothic', 20))
    label.pack(pady=20)

    # Pre-filled entry fields for contact information
    global business_name_entry, owner_name_entry, email_entry
    business_name_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Business Name")
    business_name_entry.insert(0, business_name)
    business_name_entry.pack(pady=10)

    owner_name_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Owner Name")
    owner_name_entry.insert(0, owner_name)
    owner_name_entry.pack(pady=10)

    email_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Email Address")
    email_entry.insert(0, email)
    email_entry.pack(pady=10)

    # Save changes button
    save_button = customtkinter.CTkButton(app, text="Save Changes", command=lambda: save_contact_changes(rowid))
    save_button.pack(pady=20)

    # Back button
    back_button = customtkinter.CTkButton(app, text="Back", command=show_manage_clients_window)
    back_button.pack(pady=10)

def save_contact_changes(rowid):
    updated_business_name = business_name_entry.get()
    updated_owner_name = owner_name_entry.get()
    updated_email = email_entry.get()

    if not (updated_business_name and updated_owner_name and updated_email):
        messagebox.showerror('Error', 'All fields are required.')
        return

    cursor.execute('''
        UPDATE contacts 
        SET business_name = ?, owner_name = ?, email = ? 
        WHERE rowid = ?
    ''', (updated_business_name, updated_owner_name, updated_email, rowid))
    conn.commit()

    messagebox.showinfo('Success', 'Contact updated successfully!')
    show_manage_clients_window()

def delete_contact(rowid):
    cursor.execute('DELETE FROM contacts WHERE rowid = ?', (rowid,))
    conn.commit()

    messagebox.showinfo('Success', 'Contact deleted successfully!')
    display_all_contacts()

# Add the button to the main menu
def show_main_menu():
    clear_frame()
    app.geometry('1000x600')  # Resize window for main menu

    sidebar_frame = customtkinter.CTkFrame(app, width=200)
    sidebar_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    sidebar_label = customtkinter.CTkLabel(sidebar_frame, text="Menu", font=('Century Gothic', 18))
    sidebar_label.pack(pady=20)

    add_contact_button = customtkinter.CTkButton(sidebar_frame, text="Add Contact", command=show_add_contact_form)
    add_contact_button.pack(pady=10)

    generate_email_button = customtkinter.CTkButton(sidebar_frame, text="Generate Email", command=show_generate_email_window)
    generate_email_button.pack(pady=10)

    manage_clients_button = customtkinter.CTkButton(sidebar_frame, text="Manage Clients", command=show_manage_clients_window)
    manage_clients_button.pack(pady=10)

    main_content_frame = customtkinter.CTkFrame(app)
    main_content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

    main_label = customtkinter.CTkLabel(main_content_frame, text="Welcome to the Main Menu", font=('Century Gothic', 24))
    main_label.pack(pady=20)

    info_label = customtkinter.CTkLabel(main_content_frame, text="Select an option from the menu to get started.", font=('Century Gothic', 16))
    info_label.pack(pady=10)
    
def show_settings_window():
    global username  # Access the global username variable

    clear_frame()

    label = customtkinter.CTkLabel(app, text="Settings", font=('Century Gothic', 20))
    label.pack(pady=20)

    # Display current username
    username_label = customtkinter.CTkLabel(app, text=f"Current Username: {username}", font=('Century Gothic', 16))
    username_label.pack(pady=10)

    # Change password section
    change_password_label = customtkinter.CTkLabel(app, text="Change Password", font=('Century Gothic', 18))
    change_password_label.pack(pady=20)

    global current_password_entry, new_password_entry, confirm_password_entry

    current_password_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Current Password", show="*")
    current_password_entry.pack(pady=10)

    new_password_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="New Password", show="*")
    new_password_entry.pack(pady=10)

    confirm_password_entry = customtkinter.CTkEntry(app, width=300, placeholder_text="Confirm New Password", show="*")
    confirm_password_entry.pack(pady=10)

    save_password_button = customtkinter.CTkButton(app, text="Change Password", command=change_password)
    save_password_button.pack(pady=10)

    # Light/Dark mode toggle
    mode_toggle_label = customtkinter.CTkLabel(app, text="Appearance Mode", font=('Century Gothic', 18))
    mode_toggle_label.pack(pady=20)

    appearance_mode_var = StringVar(value="dark")

    def toggle_appearance_mode():
        mode = appearance_mode_var.get()
        customtkinter.set_appearance_mode(mode)

    dark_mode_radio = customtkinter.CTkRadioButton(
        app, text="Dark Mode", variable=appearance_mode_var, value="dark", command=toggle_appearance_mode
    )
    dark_mode_radio.pack(anchor="w", padx=20)

    light_mode_radio = customtkinter.CTkRadioButton(
        app, text="Light Mode", variable=appearance_mode_var, value="light", command=toggle_appearance_mode
    )
    light_mode_radio.pack(anchor="w", padx=20)

    # Back button to return to the main menu
    back_button = customtkinter.CTkButton(app, text="Back", command=show_main_menu)
    back_button.pack(pady=10)

def change_password():
    current_password = current_password_entry.get()
    new_password = new_password_entry.get()
    confirm_password = confirm_password_entry.get()

    if not (current_password and new_password and confirm_password):
        messagebox.showerror("Error", "All fields are required.")
        return

    # Validate current password
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(current_password.encode("utf-8"), result[0]):
        if new_password == confirm_password:
            # Update password
            hashed_new_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed_new_password, username))
            conn.commit()
            messagebox.showinfo("Success", "Password changed successfully!")
        else:
            messagebox.showerror("Error", "New passwords do not match.")
    else:
        messagebox.showerror("Error", "Current password is incorrect.")

# Add the Settings button to the main menu
def show_main_menu():
    clear_frame()
    app.geometry("1000x600")  # Resize window for main menu

    sidebar_frame = customtkinter.CTkFrame(app, width=200)
    sidebar_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    sidebar_label = customtkinter.CTkLabel(sidebar_frame, text="Menu", font=('Century Gothic', 18))
    sidebar_label.pack(pady=20)

    add_contact_button = customtkinter.CTkButton(sidebar_frame, text="Add Contact", command=show_add_contact_form)
    add_contact_button.pack(pady=10)

    generate_email_button = customtkinter.CTkButton(sidebar_frame, text="Generate Email", command=show_generate_email_window)
    generate_email_button.pack(pady=10)

    manage_clients_button = customtkinter.CTkButton(sidebar_frame, text="Manage Clients", command=show_manage_clients_window)
    manage_clients_button.pack(pady=10)

    settings_button = customtkinter.CTkButton(sidebar_frame, text="Settings", command=show_settings_window)
    settings_button.pack(pady=10)

    main_content_frame = customtkinter.CTkFrame(app)
    main_content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

    main_label = customtkinter.CTkLabel(main_content_frame, text="Welcome to the Main Menu", font=('Century Gothic', 24))
    main_label.pack(pady=20)

    info_label = customtkinter.CTkLabel(main_content_frame, text="Select an option from the menu to get started.", font=('Century Gothic', 16))
    info_label.pack(pady=10)

def show_main_menu():
    clear_frame()
    app.geometry("1000x600")  # Resize window for main menu

    sidebar_frame = customtkinter.CTkFrame(app, width=200)
    sidebar_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    sidebar_label = customtkinter.CTkLabel(sidebar_frame, text="Menu", font=('Century Gothic', 18))
    sidebar_label.pack(pady=20)

    add_contact_button = customtkinter.CTkButton(sidebar_frame, text="Add Contact", command=show_add_contact_form)
    add_contact_button.pack(pady=10)

    generate_email_button = customtkinter.CTkButton(sidebar_frame, text="Generate Email", command=show_generate_email_window)
    generate_email_button.pack(pady=10)

    manage_clients_button = customtkinter.CTkButton(sidebar_frame, text="Manage Clients", command=show_manage_clients_window)
    manage_clients_button.pack(pady=10)

    settings_button = customtkinter.CTkButton(sidebar_frame, text="Settings", command=show_settings_window)
    settings_button.pack(pady=10)

    logout_button = customtkinter.CTkButton(sidebar_frame, text="Logout", command=logout)
    logout_button.pack(pady=10)

    main_content_frame = customtkinter.CTkFrame(app)
    main_content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

    main_label = customtkinter.CTkLabel(main_content_frame, text="Welcome to the Main Menu", font=('Century Gothic', 24))
    main_label.pack(pady=20)

    info_label = customtkinter.CTkLabel(main_content_frame, text="Select an option from the menu to get started.", font=('Century Gothic', 16))
    info_label.pack(pady=10)

def logout():
    global username  # Clear the logged-in user's data
    username = None
    clear_frame()
    create_signup_frame()  # Redirect to the signup/login window



# Function for login button
def Loginbutton1_function():
    clear_frame()  # Clear current frame and open new one (login window)
    setup_frame2()

# Create signup frame (frame1)
def create_signup_frame():
    img1 = ImageTk.PhotoImage(Image.open("./assets/5.png"))
    image_label1 = customtkinter.CTkLabel(master=app, image=img1)
    image_label1.pack()

    frame1 = customtkinter.CTkFrame(master=image_label1, width=320, height=360, corner_radius=15)
    frame1.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    Createaccount_label = customtkinter.CTkLabel(master=frame1, text="Create your Account", font=('Century Gothic', 20))
    Createaccount_label.place(x=50, y=45)

    global usernameentry1
    global passwordentry1
    usernameentry1 = customtkinter.CTkEntry(master=frame1, width=220, placeholder_text='Username')
    usernameentry1.place(x=50, y=110)

    passwordentry1 = customtkinter.CTkEntry(master=frame1, width=220, placeholder_text='Password', show="*")
    passwordentry1.place(x=50, y=165)

    login_label1 = customtkinter.CTkLabel(master=frame1, text="Already have an account?", font=('Century Gothic', 12))
    login_label1.place(x=30, y=240)

    Signupbutton1 = customtkinter.CTkButton(master=frame1, width=220, text="Sign up", command=Signupbutton_function, corner_radius=6)
    Signupbutton1.place(x=50, y=200)

    loginbutton1 = customtkinter.CTkButton(master=frame1, text_color="blue", command=Loginbutton1_function, text="Login", hover_color="green", cursor="hand2", width=20, corner_radius=80)
    loginbutton1.place(x=200, y=240)

# Function to set up elements in frame2 (login window)
def setup_frame2():
    img2 = ImageTk.PhotoImage(Image.open("./assets/5.png"))
    image_label2 = customtkinter.CTkLabel(master=app, image=img2)
    image_label2.pack()

    frame2_custom = customtkinter.CTkFrame(master=image_label2, width=320, height=360, corner_radius=15)
    frame2_custom.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    login_label2 = customtkinter.CTkLabel(master=frame2_custom, text="Login to your Account", font=('Century Gothic', 20))
    login_label2.place(x=50, y=45)

    global usernameentry2
    global passwordentry2

    usernameentry2 = customtkinter.CTkEntry(master=frame2_custom, width=220, placeholder_text='Username')
    usernameentry2.place(x=50, y=110)

    passwordentry2 = customtkinter.CTkEntry(master=frame2_custom, width=220, placeholder_text='Password', show="*")
    passwordentry2.place(x=50, y=165)

    loginbutton2 = customtkinter.CTkButton(master=frame2_custom, width=220, text="Login", corner_radius=6, command=Loginbutton2_function)
    loginbutton2.place(x=50, y=240)

# Initialize the sign-up frame when the app starts
create_signup_frame()

# Start the app's main loop
app.mainloop()
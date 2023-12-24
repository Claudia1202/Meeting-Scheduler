import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, messagebox
import re


#clasele 

class Person:
    def __init__(self, FirstName, LastName, email):
        self.FirstName = FirstName
        self.LastName = LastName
        self.email = email

class Meeting:
    def __init__(self, StartTime, EndTime, Subject, Participants):
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.Subject = Subject 
        self.Participants = Participants

#conexiunea cu bd
def get_connection():
    host = "localhost"
    dbname = "meeting_db"
    user = "postgres"  
    password = "postgres"    

    try:
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("Connection with database was established.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    


conn = get_connection()

######## PRIMA COMANDA ########
def add_person(conn, person):
# FUNCTII VALIDARE INFO

    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO Person (FirstName, LastName, Email)
                          VALUES (%s, %s, %s) RETURNING PersonID;""", 
                          (person.FirstName, person.LastName, person.email))
        person_id = cursor.fetchone()[0]
        conn.commit()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def add_person_w():

# verifica structura emailului
    def validate_email(email):
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(pattern, email)):
            return True 
        else:
            return False
        
# verifica daca emailul apartine deja altei persoane inregistrate
    def is_dupe_email(email):
        cursorr = conn.cursor()
        try:
            cursorr.execute("SELECT EXISTS(SELECT 1 FROM Person WHERE Email = %s);", (email,))
            exists = cursorr.fetchone()[0]
            if exists:
                return True
            else:
                return False
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cursorr.close()

    def submit():
        new_person = Person(first_name_entry.get(), last_name_entry.get(), email_entry.get())
        if validate_email(email_entry.get()):
            if not is_dupe_email(email_entry.get()):
                add_person(conn, new_person)
                add_person_window.destroy()  
            else:
                messagebox.showerror("Error", "Email already exists in the database.")
        else:
            messagebox.showerror("Error", "Invalid email.")


# Fereastra Add New Person 
    add_person_window = Toplevel(root)
    add_person_window.title("Add New Person")
    add_person_window.configure(bg="#FFC0CB")
    add_person_window.geometry("400x250")

    first_name = Label(add_person_window, text="FIRST NAME:", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB")
    first_name.grid(row=0, column=0, padx=10, pady=10)
    first_name_entry = Entry(add_person_window)
    first_name_entry.grid(row=0, column=1, padx=10, pady=10)

    last_name = Label(add_person_window, text="LAST NAME:", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB")
    last_name.grid(row=1, column=0, padx=10, pady=10)
    last_name_entry = Entry(add_person_window)
    last_name_entry.grid(row=1, column=1, padx=10, pady=10)

    email = Label(add_person_window, text="EMAIL:", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB")
    email.grid(row=2, column=0, padx=10, pady=10)
    email_entry = Entry(add_person_window)
    email_entry.grid(row=2, column=1, padx=10, pady=10)

    # buton submit 
    submit_button = Button(add_person_window, text="Submit", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB", command=submit)
    submit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)





####### MENIU PRINCIPAL #######
root = tk.Tk()
root.geometry("800x500")
root.title("Meeting Scheduler")
root.configure(bg="#FFC0CB")

title = tk.Label(root, text="YOUR MEETING SCHEDULER", font=('Georgia', 18, 'bold'), fg="#FFFFFF", bg="#FFC0CB")
title.pack(pady=70)

button1 = tk.Button(root, text="Add New Person", font=('Georgia', 12), height=1, width=19, fg='#FFFFFF', bg='#CD8C95', command=add_person_w)
button1.pack(pady=10)

button2 = tk.Button(root, text="Add New Meeting", font=('Georgia', 12),  height=1, width=19, fg='#FFFFFF', bg='#CD8C95')
button2.pack(pady=10)

button3 = tk.Button(root, text="Display Meetings", font=('Georgia', 12),  height=1, width=19, fg='#FFFFFF', bg='#CD8C95')
button3.pack(pady=10)


root.mainloop()


if conn is not None:
    conn.close()

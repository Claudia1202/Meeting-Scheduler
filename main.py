import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import tkinter as tk

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

####### MENIU PRINCIPAL #######
root = tk.Tk()
root.geometry("800x500")
root.title("Meeting Scheduler")
root.configure(bg="#FFC0CB")

title = tk.Label(root, text="YOUR MEETING SCHEDULER", font=('Georgia', 18, 'bold'), fg="#FFFFFF", bg="#FFC0CB")
title.pack(pady=70)

button1 = tk.Button(root, text="Add New Person", font=('Georgia', 12), height=1, width=19, fg='#FFFFFF', bg='#CD8C95')
button1.pack(pady=10)

button2 = tk.Button(root, text="Add New Meeting", font=('Georgia', 12),  height=1, width=19, fg='#FFFFFF', bg='#CD8C95')
button2.pack(pady=10)

button3 = tk.Button(root, text="Display Meetings", font=('Georgia', 12),  height=1, width=19, fg='#FFFFFF', bg='#CD8C95')
button3.pack(pady=10)


root.mainloop()


if conn is not None:
    conn.close()

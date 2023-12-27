import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, messagebox
import re
from datetime import datetime


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


####### A DOUA COMANDA #######

def schedule_meeting(conn, meeting):
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO Meeting (StartDateTime, EndDateTime, Subject) 
                          VALUES (%s, %s, %s) RETURNING MeetingID;""", 
                          (meeting.StartTime, meeting.EndTime, meeting.Subject))
        meeting_id = cursor.fetchone()[0]

        for person_id in meeting.Participants:
            cursor.execute("""INSERT INTO MeetingParticipants (MeetingID, PersonID) 
                              VALUES (%s, %s);""", 
                              (meeting_id, person_id))

        conn.commit()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def schedule_meeting_w():

    # verifica sa fie valid formatul datelor
    def is_valid_date(data):
        try:
            datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False
    
# verifica daca datele introduse sunt in viitor fata de momentul programarii acesteia
    def is_future_date(data):
        if datetime.strptime(data, '%Y-%m-%d %H:%M:%S') > datetime.now():
            return True
        else:
            return False

    def is_end_after_start(start_date, end_date):
        start = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        if end > start:
            return True
        else:
            return False

    def get_participants(entry):
        ids = entry.get()
        id_list = ids.split(',')
        return id_list
    
    def can_add_to_meeting(conn, person_id, new_start_time, new_end_time):
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT EXISTS(
                SELECT 1
                FROM Meeting M
                JOIN MeetingParticipants MP ON M.MeetingID = MP.MeetingID
                WHERE MP.PersonID = %s AND 
                    M.EndDateTime > %s AND 
                    M.StartDateTime < %s);
            """, (person_id, new_start_time, new_end_time))

            return not cursor.fetchone()[0]

        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
            return False  
        finally:
            cursor.close()

    def see_list():
        participants_list_window = Toplevel()
        participants_list_window.title("All Participants")
        participants_list_window.configure(bg="#FFC0CB")
        participants_list_window.geometry("400x250")

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT PersonID, FirstName, LastName FROM Person;")
            rows = cursor.fetchall()
            
            for row in rows:
                person_id, first_name, last_name = row
                label = Label(participants_list_window, text=f"ID: {person_id}, Name: {first_name} {last_name}", bg="#FFC0CB", fg="white")
                label.pack()
                
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            cursor.close()

    def submit2():
        participants = get_participants(participants_id_entry)
        new_start_time = start_time_entry.get()
        new_end_time = end_time_entry.get()
        subject = subject_entry.get()

        # validare date introduse
        if not (is_valid_date(new_start_time) and is_valid_date(new_end_time)):
            messagebox.showerror("Error", "Invalid date format. Please use format: YYYY-MM-DD HH:MM:SS.")
            return
        
        if not (is_future_date(new_start_time) and is_future_date(new_end_time)):
            messagebox.showerror("Error", "Dates must be in the future.")
            return
        
        if not is_end_after_start(new_start_time, new_end_time):
            messagebox.showerror("Error", "End time must be after start time.")
            return

        all_can_join = True
        cannot_participate = []
        can_participate = []

        for person_id in participants:
            if not can_add_to_meeting(conn, person_id, new_start_time, new_end_time):
                cannot_participate.append(person_id)
                all_can_join = False
            else:
                can_participate.append(person_id)
# Nu exista suprapuneri de program
        if all_can_join:
            new_meeting = Meeting(new_start_time, new_end_time, subject, participants)
            schedule_meeting(conn, new_meeting)
            schedule_meeting_window.destroy()
# Uneia sau mai multor persoane li se suprapune sedinta nou creata cu altele deja existente
        else:
            new_meeting = Meeting(new_start_time, new_end_time, subject, can_participate)
            schedule_meeting(conn, new_meeting)
            schedule_meeting_window.destroy()
            messagebox.showerror("Error", f"""Participant(s) {', '.join(str(person_id) for person_id in cannot_participate)} 
                has(have) another meeting in this interval. Participant(s) {', '.join(str(person_id) for person_id in can_participate)} 
                    was(were) added to the meeting.""")

# Fereastra Add New Meeting 
    schedule_meeting_window = Toplevel(root)
    schedule_meeting_window.title("Add New Meeting")
    schedule_meeting_window.configure(bg="#FFC0CB")
    schedule_meeting_window.geometry("400x250")

    start_time = Label(schedule_meeting_window, text="START TIME:", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB")
    start_time.grid(row=0, column=0, padx=10, pady=10)
    start_time_entry = Entry(schedule_meeting_window)
    start_time_entry.grid(row=0, column=1, padx=10, pady=10)

    end_time = Label(schedule_meeting_window, text="END TIME:", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB")
    end_time.grid(row=1, column=0, padx=10, pady=10)
    end_time_entry = Entry(schedule_meeting_window)
    end_time_entry.grid(row=1, column=1, padx=10, pady=10)

    subject = Label(schedule_meeting_window, text="SUBJECT:", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB")
    subject.grid(row=2, column=0, padx=10, pady=10)
    subject_entry = Entry(schedule_meeting_window)
    subject_entry.grid(row=2, column=1, padx=10, pady=10)

    subject = Label(schedule_meeting_window, text="SUBJECT:", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB")
    subject.grid(row=2, column=0, padx=10, pady=10)
    subject_entry = Entry(schedule_meeting_window)
    subject_entry.grid(row=2, column=1, padx=10, pady=10)

    participants_id = Label(schedule_meeting_window, text="PARTICIPANTS:", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB")
    participants_id.grid(row=3, column=0, padx=10, pady=10)
    participants_id_entry = Entry(schedule_meeting_window)
    participants_id_entry.grid(row=3, column=1, padx=10, pady=10)

    participants_list = Button(schedule_meeting_window, text="See list", font=('Georgia', 10), fg='#FFFFFF', bg="#FFC0CB", command=see_list)
    participants_list.grid(row=3, column=2, padx=10, pady=10)

    # buton submit 
    submit_button = Button(schedule_meeting_window, text="Submit", font=('Georgia', 12), fg='#FFFFFF', bg="#FFC0CB", command=submit2)
    submit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)


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

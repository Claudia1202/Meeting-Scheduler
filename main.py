import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import tkinter as tk
from tkinter import Frame, Toplevel, Label, Entry, Button, messagebox
import re
from datetime import datetime
from icalendar import Calendar, Event
import pytz
import os

filepath = r"C:\Users\Claudia\Documents\Python-teme"

#clasele 

class Person:
    """Reprezinta persoanele care pot fi adaugate in meetinguri.

    Attribute:
        FirstName (str): Prenumele persoanei.
        LastName (str): Numele persoanei.
        email (str): Adresa de email.
    """
    def __init__(self, FirstName, LastName, email):
        self.FirstName = FirstName
        self.LastName = LastName
        self.email = email

class Meeting:
    """Reprezinta sedintele.

    Attribute:
        StartTime (datetime): timpul de incepere al sedintei.
        EndTime (datetime): timpul de incheiere al sedintei.
        Subject (str): subiectul sedintei.
        Participants (list): lista de participanti ai sedintei.
    """
    def __init__(self, StartTime, EndTime, Subject, Participants):
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.Subject = Subject 
        self.Participants = Participants

#conexiunea cu bd
def get_connection():
    """Creeaza o conexiune cu baza de date PostgreSQL.

    Returneaza:
        psycopg2.connection: Conexiunea cu baza de date sau None daca nu se formeaza o conexiune.
    """
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
    
background_color = "#ECE2F0" 
darker_color = "#957DAD"  
text_color = "#333333"  
font_style = "Raleway"
font_size = 12

conn = get_connection()

######## PRIMA COMANDA ########
def add_person(conn, person):
    """Adauga o noua persoana in tabela Person din baza de date.
    Args:
        conn: conexiunea cu baza de date.
        person (Person): obiectul Person de adaugat in baza de date.
    """
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
    """Creeaza o fereastra pentru a adauga o persoana in baza de date."""

 # verifica structura emailului
    def validate_email(email):
        """Functia verifica daca emailul introdus este valid.
        Parametri:
            email (str): emailul persoanei adaugate."""
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        if(re.fullmatch(pattern, email)):
            return True 
        else:
            return False
        
 # verifica daca emailul apartine deja altei persoane inregistrate
    def is_dupe_email(email):
        """Functia verifica daca emailul exista deja in baza de date.
        Parametri:
            email (str): emailul persoanei adaugate.
        """
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
        """Functia apelata de butonul "submit" valideaza datele si adauga in baza de date persoana a carei date sunt introduse.
        """
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
    add_person_window.configure(bg=background_color)
    add_person_window.geometry("400x250")

    main_frame = Frame(add_person_window, bg=background_color)
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    entry_frame = Frame(main_frame, bg=background_color)
    entry_frame.pack(side="top", fill="x")

    first_name = Label(entry_frame, text="FIRST NAME:", font=(font_style, font_size), fg=text_color, bg=background_color)
    first_name.grid(row=0, column=0, sticky="w", padx=10, pady=10)
    first_name_entry = Entry(entry_frame)
    first_name_entry.grid(row=0, column=1, padx=10, pady=10)

    last_name = Label(entry_frame, text="LAST NAME:", font=(font_style, font_size), fg=text_color, bg=background_color)
    last_name.grid(row=1, column=0, sticky="w", padx=10, pady=10)
    last_name_entry = Entry(entry_frame)
    last_name_entry.grid(row=1, column=1, padx=10, pady=10)

    email = Label(entry_frame, text="EMAIL:", font=(font_style, font_size), fg=text_color, bg=background_color)
    email.grid(row=2, column=0, sticky="w", padx=10, pady=10)
    email_entry = Entry(entry_frame)
    email_entry.grid(row=2, column=1, padx=10, pady=10)

    button_frame = Frame(main_frame, bg=background_color)
    button_frame.pack(side="bottom", pady=10, fill="x")

    # buton submit 
    submit_button = Button(button_frame, text="Submit", font=(font_style, font_size), fg=text_color, bg=darker_color, command=submit)
    submit_button.pack()


####### A DOUA COMANDA #######

def schedule_meeting(conn, meeting):
    """
    Adauga in baza de date o sedinta.

    Parametri:
    conn (psycopg2.extensions.connection): conexiunea cu baza de date.
    meeting (Meeting): obiectil de tip Meeting.
    """
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
    """
    Creeaza o fereastra pentru a adauga o noua sedinta.
    """
    # verifica sa fie valid formatul datelor
    def is_valid_date(data):
        """Verifica ca datele introduse sa aiba format valid.
            Parametri:
            data (str): Datele care trebuie verificate."""
        try:
            datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False
    
    def is_future_date(data):
        """Verifica daca datele introduse sunt in viitor.
        Parametri:
            data (str): Datele care trebuie verificate."""
        if datetime.strptime(data, "%Y-%m-%d %H:%M:%S") > datetime.now():
            return True
        else:
            return False

    def is_end_after_start(start_date, end_date):
        """
        Verifica ca data de sfarsit sa fie dupa data de inceput.

        Parametri:
        start_date (str): data de start.
        end_date (str): data de sfarsit.
        """
        start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        if end > start:
            return True
        else:
            return False

    def get_participants(entry):
        """Grupeaza participantii introdusi intr o lista.

        Parametri:
        entry (tkinter.Entry): entry-ul unde sunt scrise ID-urile participantilor.
        Returneaza:
        list: lista cu ID-ul participantilor.
        """
        ids = entry.get()
        id_list = ids.split(",")
        return id_list
    
    def can_add_to_meeting(conn, person_id, new_start_time, new_end_time):
        """
        Verifica daca un participant poate fi adaugat in meeting, sau are un alt meeting programat in acel interval.

        Parametri:
        conn (psycopg2.extensions.connection): conexiunea cu baza de date.
        person_id (int): ID-ul persoanei verificate.
        new_start_time (str): timpul de start.
        new_end_time (str): timpul de incheiere.
        """
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

#lista completa cu participanti
    def see_list():
        """
        Afiseaza o lista cu toate persoanele din baza de date si ID-urile lor.
        """
        participants_list_window = Toplevel()
        participants_list_window.title("All Participants")
        participants_list_window.configure(bg=background_color)
        participants_list_window.geometry("400x250")

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT PersonID, FirstName, LastName FROM Person;")
            rows = cursor.fetchall()
            count_rows = 0
            for row in rows:
                person_id, first_name, last_name = row
                label = Label(participants_list_window, text=f"ID: {person_id}, Name: {first_name} {last_name}", bg=background_color, fg=text_color)
                label.grid(row=count_rows, sticky="w", padx=10, pady=5)
                count_rows += 1
                
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            cursor.close()

    def submit2():
        """Functia colecteaza informatiile de la utilizator pentru a programa o noua sedinta,
        verifica validitatea datelor introduse si, daca datele sunt valide, incearca sa adauge sedinta în baza de date.
        In cazul in care unul sau mai multi participanti au deja o alta sedinta programata in acelasi interval,
        se afiseaza un mesaj de eroare, iar participantii disponibili sunt totusi adaugati la noua sedinta.
        """
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
            messagebox.showerror("Error", f"""Participant(s) {", ".join(str(person_id) for person_id in cannot_participate)} 
                has(have) another meeting in this interval. Participant(s) {", ".join(str(person_id) for person_id in can_participate)} 
                    was(were) added to the meeting.""")

# Fereastra Add New Meeting 
    schedule_meeting_window = Toplevel(root)
    schedule_meeting_window.title("Add New Meeting")
    schedule_meeting_window.configure(bg=background_color)
    schedule_meeting_window.geometry("400x250")

    main_frame = Frame(schedule_meeting_window, bg=background_color)
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    entry_frame = Frame(main_frame, bg=background_color)
    entry_frame.pack(side="top", fill="x")

    start_time = Label(entry_frame, text="START TIME:", font=(font_style, font_size), fg=text_color, bg=background_color)
    start_time.grid(row=0, column=0, sticky="w")
    start_time_entry = Entry(entry_frame)
    start_time_entry.grid(row=0, column=1, padx=10, pady=10)

    end_time = Label(entry_frame, text="END TIME:", font=(font_style, font_size), fg=text_color, bg=background_color)
    end_time.grid(row=1, column=0, sticky="w")
    end_time_entry = Entry(entry_frame)
    end_time_entry.grid(row=1, column=1, padx=10, pady=10)

    subject = Label(entry_frame, text="SUBJECT:", font=(font_style, font_size), fg=text_color, bg=background_color)
    subject.grid(row=2, column=0, sticky="w")
    subject_entry = Entry(entry_frame)
    subject_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)

    participants_id = Label(entry_frame, text="PARTICIPANTS:", font=(font_style, font_size), fg=text_color, bg=background_color)
    participants_id.grid(row=3, column=0, sticky="w")
    participants_id_entry = Entry(entry_frame)
    participants_id_entry.grid(row=3, column=1, padx=10, pady=10)

    participants_list = Button(entry_frame, text="See list", font=(font_style, 10), fg=text_color, bg=darker_color, command=see_list)
    participants_list.grid(row=3, column=2, padx=10, pady=10)

    button_frame = Frame(main_frame, bg=background_color)
    button_frame.pack(side="bottom", pady=10, fill="x")

    # buton submit 
    submit_button = Button(button_frame, text="Submit", font=(font_style, font_size), fg=text_color, bg=darker_color, command=submit2)
    submit_button.pack()

######### A TREIA COMANDA #########

def display_meetings(conn, start_time, end_time):
    """
    Interogheaza baza de date pentru a gasi si returna sedinte in intervalul specificat.

    Parametri:
        conn (psycopg2.extensions.connection): conexiunea cu baza de date.
        start_time (str): timpul de inceput pentru interogare.
        end_time (str): timpul de sfarsit pentru interogare.

    Returneaza:
        list: Lista cu sedintele gasite.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT * FROM Meeting
                          WHERE StartDateTime >= %s AND EndDateTime <= %s;""", 
                          (start_time, end_time))
        meetings = cursor.fetchall()
        return meetings
        #messagebox.showinfo("Display Meetings", meeting_info)
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def display_meetings_w():

    """
    Creeaza o fereastra pentru afisarea sedintelor dintr-un interval specificat.
    Permite exportul sedintelor in format .ics.
    """
    # EXPORT IN FISIER CU EXTENSIA ICS 
    def export_meetings_to_ics(meetings, file_path, file_name_entry):    
        """
        Exporta sedintele selectate din baza de date intr-un fisier .ics specificat.

        Parametri:
            meetings (list): lista de sedinte selectata.
            file_path (str): Calea catre fisierul .ics.
            file_name_entry (tkinter.Entry): Entry widget ce contine numele fisierului.
        """
        try:

            filename = file_name_entry.get()
            new_path = os.path.join(file_path, filename)
            cal = Calendar()

            for meeting in meetings:
                event = Event()
                event.add("summary", meeting[3])  # meeting subject
                event.add("dtstart", meeting[1])  # start time
                event.add("dtend", meeting[2])    # end time
                event.add("dtstamp", datetime.now(pytz.utc))  
                cal.add_component(event)

            with open(new_path, "wb") as f:
                f.write(cal.to_ical())
            messagebox.showinfo("Success", "Export completed successfully and saved to " + file_path)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


    def is_valid_date(data):
            """Verifica ca datele introduse sa aiba format valid.
            Parametri:
            data (str): Datele care trebuie verificate."""
            try:
                datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
                return True
            except ValueError:
                return False
            

    def show():
        """Afiseaza o fereastra cu sedintele din intervalul specificat.
        Permite utilizatorului să vizualizeze sedintele si sa le exporte intr-un fisier ICS.
        Utilizeaza datele introduse de utilizator pentru a interoga baza de date si afiseaza rezultatele.
        Afiseaza un mesaj de eroare daca datele introduse nu sunt valide sau daca nu exista sedinte in intervalul specificat.
        """
        
        start_interval = start_time_entry.get()
        end_interval = end_time_entry.get()
        meetings = display_meetings(conn, start_interval, end_interval)

        if not (is_valid_date(start_interval) and is_valid_date(end_interval)):
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD HH:MM:SS.")
            return

     # fereastra display_meetings
        show_meetings_window = Toplevel(root)
        show_meetings_window.title("Meetings from " + start_interval + " to " + end_interval)
        show_meetings_window.configure(bg=background_color)
        show_meetings_window.geometry("500x400")  

        main_frame = Frame(show_meetings_window, bg=background_color)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        entry_frame = Frame(main_frame, bg=background_color)
        entry_frame.pack(side="top", fill="x")

        if not meetings:
            no_meetings_label = Label(entry_frame, text="No meetings found in the given interval.", bg=background_color, fg=text_color)
            no_meetings_label.pack()

        count_rows = 0
        for meeting in meetings:
            meeting_id, start, end, subject = meeting
            meeting_info = f"ID: {meeting_id}, Start: {start}, End: {end}, Subject: {subject}"
            Label(entry_frame, text=meeting_info, bg=background_color, fg=text_color).grid(sticky="w")

        button_frame = Frame(main_frame, bg=background_color)
        button_frame.pack(side="bottom", pady=10, fill="x")  

        file_name = Label(button_frame, text="Filename", font=(font_style, 11), fg=text_color, bg=background_color)
        file_name.pack(side="top", anchor='w')  
        file_name_entry = Entry(button_frame)
        file_name_entry.pack(side="top", anchor='w', pady=10)  

        export_button = Button(button_frame, text="EXPORT", font=(font_style, font_size), fg=text_color, bg=darker_color, command=lambda: export_meetings_to_ics(meetings, filepath, file_name_entry))
        export_button.pack(side="top")



# fereastra display_meetings care se deschide din meniu
    display_meetings_window = Toplevel(root)
    display_meetings_window.title("Display Meetings")
    display_meetings_window.configure(bg=background_color)
    display_meetings_window.geometry("400x250")

    main_frame = Frame(display_meetings_window, bg=background_color)
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    entry_frame = Frame(main_frame, bg=background_color)
    entry_frame.pack(side="top", fill="x")

    start_time = Label(entry_frame, text="START TIME:", font=(font_style, font_size), fg=text_color, bg=background_color)
    start_time.grid(row=0, column=0, sticky="w", padx=10, pady=20)
    start_time_entry = Entry(entry_frame)
    start_time_entry.grid(row=0, column=1, padx=10, pady=20)

    end_time = Label(entry_frame, text="END TIME:", font=(font_style, font_size), fg=text_color, bg=background_color)
    end_time.grid(row=1, column=0, sticky="w", padx=10, pady=10)
    end_time_entry = Entry(entry_frame)
    end_time_entry.grid(row=1, column=1, padx=10, pady=10)

    button_frame = Frame(main_frame, bg=background_color)
    button_frame.pack(side="bottom", pady=10, fill="x")

    # buton show 
    show_button = Button(button_frame, text="SHOW", font=(font_style, font_size), fg=text_color, bg=darker_color, command=show)
    show_button.pack()


##### IMPORT DIN FISIER ICS IN BAZA DE DATE  #####

def import_meetings_w():
    """
        Creeaza o fereastra pentru importul sedintelor dintr-un fisier .ics in baza de date.
    """
     
    def import_meetings(file_path, filename_entry):
        """
        Importa sedintele dintr-un fisier .ics specificat in baza de date.

        Parametri:
            file_path (str): Calea catre fisierul .ics.
            filename_entry (tkinter.Entry): Entry widget ce contine numele fisierului.
        """
        filename = filename_entry.get()
        new_path = os.path.join(file_path, filename)
        
        try:
            with open(new_path, "rb") as f:
                ics_content = f.read()

            cal = Calendar.from_ical(ics_content)
            count = 0 #cate evenimente s au importat

            for component in cal.walk("VEVENT"):
                start_time = component.get("dtstart").dt
                end_time = component.get("dtend").dt
                subject = component.get("summary")
            # participanti
                participanti = component.get("attendee")
                participant_ids = []

                if participanti:
                    if not isinstance(participanti, list):
                        participanti = [participanti]
                    
                    for participant in participanti:
                        email = str(participant).split(":")[-1]
                # cautam participantul in baza de date
                        try:
                            cursor = conn.cursor()
                            cursor.execute("SELECT PersonID FROM Person WHERE Email = %s;", (email,))
                            person = cursor.fetchone()
                            if person:
                                participant_ids.append(person[0])
                            cursor.close()
                        except psycopg2.Error as e:
                            print(f"Error finding participant in database: {e}")

                Imported_Meeting = Meeting(start_time, end_time, subject, participant_ids)
                schedule_meeting(conn, Imported_Meeting)
                count += 1 

            messagebox.showinfo("Success", f"Successfully imported {count} meeting(s) from {filename}.")
        except Exception as e:
            messagebox.showerror("Import Failed", f"Failed to import meetings due to error: {e}")



    import_meetings_window = Toplevel()
    import_meetings_window.title("Import Meetings")
    import_meetings_window.configure(bg=background_color)
    import_meetings_window.geometry("400x250")

    main_frame = Frame(import_meetings_window, bg=background_color)
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    entry_frame = Frame(main_frame, bg=background_color)
    entry_frame.pack(side="top", fill="x")

    filename = Label(entry_frame, text="FILE NAME:", font=(font_style, font_size), fg=text_color, bg=background_color)
    filename.grid(row=0, column=0, padx=10, pady=10)
    filename_entry = Entry(entry_frame)
    filename_entry.grid(row=0, column=1, padx=10, pady=10)

    button_frame = Frame(main_frame, bg=background_color)
    button_frame.pack(side="bottom", pady=10, fill="x")

    import_button = Button(button_frame, text="IMPORT", font=(font_style, font_size), fg=text_color, bg=darker_color, command=lambda: import_meetings(filepath, filename_entry)
)
    import_button.pack()


####### MENIU PRINCIPAL #######
    
root = tk.Tk()
root.geometry("800x600")
root.title("Meeting Scheduler")
root.configure(bg=background_color)

title_frame = Frame(root, bg=background_color)
title_frame.pack(fill="x")


title = tk.Label(root, text="YOUR MEETING SCHEDULER", font=(font_style, 18, "bold"), fg=text_color, bg=background_color)
title.pack(pady=70)

button_frame = Frame(root, bg=background_color)
button_frame.pack(fill="x", pady=20)

button1 = tk.Button(root, text="Add New Person", font=(font_style, font_size), height=1, width=19, fg=text_color, bg=darker_color, command=add_person_w)
button1.pack(pady=10)

button2 = tk.Button(root, text="Add New Meeting", font=(font_style, font_size),  height=1, width=19, fg=text_color, bg=darker_color, command=schedule_meeting_w)
button2.pack(pady=10)

button3 = tk.Button(root, text="Display Meetings", font=(font_style, font_size),  height=1, width=19, fg=text_color, bg=darker_color, command=display_meetings_w)
button3.pack(pady=10)

button4 = tk.Button(root, text="Import Meetings", font=(font_style, font_size),  height=1, width=19, fg=text_color, bg=darker_color, command=import_meetings_w)
button4.pack(pady=10)

root.mainloop()


if conn is not None:
    conn.close()

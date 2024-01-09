import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

"""Functia care creeaza baza de date(daca nu exista deja) postgres cu tabelele Person (persoanele care participa la meetings), Meetings (sedintele cu data, ora si participanti) 
si MeetingParticipants (tine evidenta participantilor la fiecare sedinta)
"""
def create_database():
    host = "localhost"
    dbname = "postgres"
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
        cursor = conn.cursor()

        # verific daca exista deja baza de date
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'meeting_db'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("CREATE DATABASE meeting_db;")
            print("Database created successfully!")
        else:
             print("Database already exists!")

    except Exception as e:
        print("An error occurred:", e)

    finally:
        cursor.close()
        conn.close()

    try:
        conn = psycopg2.connect(
            host=host,
            dbname="meeting_db",
            user=user,
            password=password
        )
        cursor = conn.cursor()

        person_table = """
        CREATE TABLE IF NOT EXISTS Person (
            PersonID SERIAL PRIMARY KEY,
            FirstName VARCHAR(50),
            LastName VARCHAR(50),
            Email VARCHAR(50)
        );
        """
        meeting_table = """
        CREATE TABLE IF NOT EXISTS Meeting (
            MeetingID SERIAL PRIMARY KEY,
            StartDateTime TIMESTAMP,
            EndDateTime TIMESTAMP,
            Subject VARCHAR(100)
        );
        """
        participants_table = """
        CREATE TABLE IF NOT EXISTS MeetingParticipants (
            MeetingID INT REFERENCES Meeting(MeetingID),
            PersonID INT REFERENCES Person(PersonID),
            PRIMARY KEY (MeetingID, PersonID)
        );
        """

        cursor.execute(person_table)
        cursor.execute(meeting_table)
        cursor.execute(participants_table)
        conn.commit()

        print("Table created successfully!")

    except Exception as e:
        print("An error occurred:", e)

    finally:
        cursor.close()
        conn.close()

create_database()


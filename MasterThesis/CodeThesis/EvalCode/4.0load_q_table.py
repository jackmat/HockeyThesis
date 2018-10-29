import sys
import MySQLdb
import csv

path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
fileup = "q_table.csv"

def write_to_db(db, c, q):
    try:
        c.execute(q)
        db.commit()
    except:
        print("Error: could not write to db")
        db.close()
        sys.exit()

def main():
    vi_db = MySQLdb.connect(
        host = '127.0.0.1',
        port = 3306,
        user="root", 
        passwd="", 
        db="nhl")
    cursor = vi_db.cursor()
    query = "DROP TABLE IF EXISTS q_table;"
    write_to_db(vi_db, cursor, query)
    query = """ CREATE TABLE q_table (
                NodeId INT,
                Expected_Goals DOUBLE,
                Probability_Home_Goal DOUBLE,
                Probability_Away_Goal DOUBLE); """
    write_to_db(vi_db, cursor, query)
    query = "ALTER TABLE q_table ADD INDEX ( NodeId, Expected_Goals, Probability_Home_Goal, Probability_Away_Goal );"
    write_to_db(vi_db, cursor, query)
    with open(path+fileup, "r") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            query = """ INSERT IGNORE INTO q_table
                            VALUES({0}, {1}, {2}, {3})
                    """.format(row[1], row[2], row[3], row[4])
            write_to_db(vi_db, cursor, query)
    vi_db.close()

if __name__ == "__main__":
    main()
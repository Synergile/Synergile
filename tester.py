import discord
import sqlite3
import os
class beta():
    def db_getter(self):
        db = sqlite3.connect('testers.db')
        crsr = db.cursor()
        return db, crsr
    def beta_getter(self, auth):
        db, crsr = beta().db_getter()
        rffa = []
        tester_data = crsr.fetchall()
        for x in tester_data:
            if x == auth:
                return True
            else:
                return False
                print ('NOT A TESTER')

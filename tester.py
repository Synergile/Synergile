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
        for x in crsr.fetchall():
            rffa.append(x)
        if auth in rffa:
            return True
        else:
            print(f'NOT A BETA TESTER: {auth}')
            return False


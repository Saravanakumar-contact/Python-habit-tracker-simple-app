from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.list import OneLineListItem
import sqlite3
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd

KV = '''
MDScreen:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "HabitPro - Daily Tracker"

        MDTextField:
            id: habit
            hint_text: "Enter habit"

        MDRaisedButton:
            text: "Add Habit"
            on_release: app.add_habit()

        ScrollView:
            MDList:
                id: habit_list

        MDRaisedButton:
            text: "Show Analytics"
            on_release: app.show_graph()
'''

class HabitApp(MDApp):
    def build(self):
        self.conn = sqlite3.connect("habit.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY, name TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY, habit_id INTEGER, date TEXT)")
        self.conn.commit()
        return Builder.load_string(KV)

    def add_habit(self):
        name = self.root.ids.habit.text
        if name:
            self.cursor.execute("INSERT INTO habits(name) VALUES(?)", (name,))
            self.conn.commit()
            self.root.ids.habit.text = ""
            self.load_habits()

    def load_habits(self):
        self.root.ids.habit_list.clear_widgets()
        self.cursor.execute("SELECT * FROM habits")
        for h in self.cursor.fetchall():
            self.root.ids.habit_list.add_widget(
                OneLineListItem(text=h[1], on_release=lambda x, h=h: self.mark_done(h[0]))
            )

    def mark_done(self, hid):
        self.cursor.execute("INSERT INTO logs(habit_id, date) VALUES(?,?)", (hid, str(date.today())))
        self.conn.commit()

    def show_graph(self):
        self.cursor.execute("SELECT date, COUNT(*) FROM logs GROUP BY date")
        data = self.cursor.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["Date", "Count"])
            df.plot(x="Date", y="Count", kind="line", title="Daily Habit Completion")
            plt.show()

HabitApp().run()

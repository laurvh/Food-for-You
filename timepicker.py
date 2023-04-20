# FULL CREDIT TO: https://stackoverflow.com/questions/57034118/time-picker-for-tkinter

import tkinter as tk
import datetime

class App(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.hourstr=tk.StringVar(self,'')
        self.hour = tk.Spinbox(self,from_=0,to=23,wrap=True,textvariable=self.hourstr,width=2,state="readonly")
        self.minstr=tk.StringVar(self,'')
        self.minstr.trace("w",self.trace_var)
        self.last_value = ""
        self.min = tk.Spinbox(self,from_=0,to=59,wrap=True,textvariable=self.minstr,width=2,state="readonly")
        self.hour.grid()
        self.min.grid(row=0,column=1)

    def trace_var(self,*args):
        if self.last_value == "59" and self.minstr.get() == "0":
            self.hourstr.set(int(self.hourstr.get())+1 if self.hourstr.get() !="23" else 0)
        self.last_value = self.minstr.get()

    "author: KS"
    "returns time in (hour, time)"
    #http://www.learningaboutelectronics.com/Articles/How-to-create-a-time-object-in-Python.php
    def getTime(self):
        return datetime.time(int(self.hourstr.get()), int(self.minstr.get()), 0)

from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window 
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
# from kivymd.uix.textfield import MDTextFieldHelperText
from kivymd.uix.label import MDLabel
import re,os, time
from kivy.properties import StringProperty, NumericProperty, Property
from kivymd.uix.screen import MDScreen  
import csv,sqlite3
# from kivymd.uix.filemanager import MDFileManager
from mods.filemanager2 import MDFileManager
from functools import partial 
from kivymd.uix.snackbar.snackbar import MDSnackbar,MDSnackbarText
from kivy.properties import ColorProperty
import webbrowser

import json 

onandroid = 0
portraitwindow = 0

def tryquery(self,query1,query2):
    cur = self.cur
    try:
        v = cur.execute(query1).fetchall()
    except Exception as e:
        cur.execute(query2)

def execqueryifnotexist(self,query1,query2):
    cur = self.cur
    try:
        v = cur.execute(query1).fetchall()
        if len(v) == 0:
            cur.execute(query2)
            self.con.commit()
    except Exception as e:
        v = 1

def execquery(self,query1):
    cur = self.cur
    try:
        cur.execute(query1)
        
    except Exception as e:
        v = 1

def checkqueryifexist(self,query1):
    cur = self.cur
    try:
        v = cur.execute(query1).fetchall()
        if len(v) == 0:
            return [0]
        else:
            return [1,v[0]]
    except Exception as e:
        return [0]

gwd = os.path.dirname(os.path.realpath(__file__))

class fmApp(MDApp):
    def loadkv(self):
        Builder.load_file('loggedin.kv')
    
    def build(self):
        if portraitwindow:
            Window.size = [300, 500]
            Window.top = 50
            Window.left = 100
        self.theme_cls.primary_palette = "Violet"
        
        con = sqlite3.connect("techris-omr.db")
        cur = con.cursor()
        self.cur = cur
        self.con = con
        tryquery(self,"SELECT * from users","CREATE TABLE users(email text)")
        tryquery(self,"SELECT * from settings","CREATE TABLE settings(key text, value)")
        execqueryifnotexist(self,'SELECT * FROM SETTINGS WHERE key = "curemail"', 'INSERT INTO SETTINGS (key,value) VALUES ("curemail","")')
        execqueryifnotexist(self,'SELECT * FROM SETTINGS WHERE key = "curotp"', 'INSERT INTO SETTINGS (key,value) VALUES ("curotp","")')
        
        if onandroid:
            vb = Builder.load_file('assets/kv/v.kv')
        else:
            vb = Builder.load_file('assets/kv/v.kv')
        if onandroid: 
            self.storage_path = primary_external_storage_path()
        else:
            self.storage_path = gwd # os.path.expanduser("~")  # path to the directory that will be opened in the file manager
         
         
         
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,  # function called when the user reaches directory tree root
            select_path=self.select_path,  # function called when selecting a file/directory
            preview = True , # False, True
            selector='multi', 
            ext = ['.png','.jpg','.jpeg'], 
            getsettings = self.getsettings,
            setsettings = self.setsettings
            # background_color_selection_button="brown"
            # background_down = 'red'
        )
        
        
        return vb

    def getsettings(self,):
        print(gwd)
        if os.path.isfile(gwd + '/settings/settings.json'):
            with open(gwd + '/settings/settings.json', "r") as read_file:
                data = json.load(read_file)
        else:
            data = {
                    'folder' : '', 
                    'sortby' : 'name',
                    "sortname" : "asc",
                    "sortdate" : "des"
                    }

        return data 

    def setsettings(self,key,value):
        data = self.getsettings()
        data[key] = value
        with open(gwd + '/settings/settings.json', 'w') as gp:
            json.dump(data, gp, indent=4)    
        
    def openfile(self):
        self.file_manager.selection = []
        self.file_manager.ids.selectedcount.text = "0"
        data = self.getsettings()
        print('data folder is ' + data['folder'])
        app.theme_cls.primaryColor = [1.0, 1.0, 1.0, 1.0]
        print(app.theme_cls.primaryColor)
        
        if not data['folder'] == '':
            if os.path.isdir(data['folder']):
                # self.storage_path = data['folder']
                self.file_manager.show(data['folder'])
            else:
                self.file_manager.show(self.storage_path)
        else:
            self.file_manager.show(self.storage_path)
    

    def exit_manager(self, *args):
        print(self.root.ids)
        app.theme_cls.primaryColor = [0.4941,0.3019,0.4863,1]
        
        try:
            self.file_manager.checkloaded.cancel()
        except:
            v =1
        self.manager_open = False
        self.file_manager.ids.rv.data = []
        self.file_manager.close()

    def log(self,retainothers=0,log1="",log2 = "",log3 = "",log4 = ""):
        self.ids2 = self.root.get_screen("log").ids
        print('log4 is' + log1)
        if retainothers > 0:
            if retainothers == 1:
                self.ids2.log1.text = log1
            if retainothers == 2:
                self.ids2.log2.text = log1
            if retainothers == 3:
                self.ids2.log3.text = log1
            if retainothers == 4:
                self.ids2.log4.text = log1
        elif retainothers == -1:
            self.ids2.log1.text = ""
            self.ids2.log2.text = ""
            self.ids2.log3.text = ""
            self.ids2.log4.text = ""
        else:
            self.ids2.log1.text = log1
            self.ids2.log2.text = log2
            self.ids2.log3.text = log3
            self.ids2.log4.text = log4

    def backtomain(self):
        self.root.current = 'main'
    def select_path(self,path): 
        print(path)
        try:
            self.file_manager.checkloaded.cancel()
        except:
            v =1
        self.exit_manager()
        self.root.current = 'log'
        
        text = ''
        for file in self.file_manager.selection:
            text += os.path.split(file)[1] +'\n'

        self.log(0,'Following files are chosen',text)
        
        
    def on_start(self):
        super().on_start()
        result = checkqueryifexist(self,'SELECT * FROM SETTINGS WHERE key = "curemail"')
        self.ids = self.root.get_screen("main").ids
        if len(result) > 1:
            if not result[1][1] == '':
                self.root.current = 'loggedin'

            
    def resettext(self,dt):
        self.ids.v2.text = ''

    
    
   

        
    def visitmsm(self):
        webbrowser.open('https://techris.in/contact-us/')    
app = fmApp()
app.run()
#해야할 것
#이미지 복사 부분 pillow이용해서 간단하게
#코드 정리 - 변수이름/주석 등등
#예외처리 추가
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import face_recognition
import pickle
import numpy as np
from PIL import Image, ImageTk


def make_file(directory):
    if not os.path.isfile(directory):
        new_file = open(directory, "w")
        new_file.close()

def delete_file(directory):
    os.remove(directory)
    
def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def delete_dir(directory):
    if os.path.exists(directory):
        file_list = os.listdir(directory)
        for file in file_list:
            delete_file(directory+"\\"+file)
        os.rmdir(directory)

def get_file_list(directory):
    if os.path.exists(directory):
        file_list = os.listdir(directory)
        return file_list
    
class App(tk.Tk):
    
    def __init__(self):
        #make window/container frame
        #container has every pages
        #make kind of global variable
        
        #set directories
        self.MAIN_DIRECTORY = "C:\App"
        make_dir(self.MAIN_DIRECTORY)

        self.PHOTO_DIRECTORY = self.MAIN_DIRECTORY+"\photos"
        make_dir(self.PHOTO_DIRECTORY)

        self.CHARACTER_DIRECTORY = self.MAIN_DIRECTORY+"\characters"
        make_dir(self.CHARACTER_DIRECTORY)

        self.CHARACTER_TEXT_DIRECTORY = self.CHARACTER_DIRECTORY + "\characters.txt"
        make_file(self.CHARACTER_TEXT_DIRECTORY)

        self.UNKNOWN_CHARACTER_DIRECTORY = self.MAIN_DIRECTORY+"\characters"+"\\unknown"
        make_dir(self.UNKNOWN_CHARACTER_DIRECTORY)

        self.UNKNOWN_CHARACTER_TEXT_DIRECTORY = self.MAIN_DIRECTORY+"\characters"+"\\unknown"+"\character.txt"
        make_file(self.UNKNOWN_CHARACTER_TEXT_DIRECTORY)

        self.PHOTO_TEXT_DIRECTORY = self.PHOTO_DIRECTORY + "\photos.txt"
        make_file(self.PHOTO_TEXT_DIRECTORY)

        #set unknown character photo number
        unknown_character_text_file = open(self.UNKNOWN_CHARACTER_TEXT_DIRECTORY, "rb")
        try:
            unknown_character_number = pickle.load(unknown_character_text_file)
        except EOFError: #no value when first access
            unknown_character_text_file.close()
            unknown_character_text_file = open(self.UNKNOWN_CHARACTER_TEXT_DIRECTORY, "wb")
            unknown_character_photo_number = 0
            pickle.dump(unknown_character_photo_number,unknown_character_text_file)
            
        #set character number
        character_text_file = open(self.CHARACTER_TEXT_DIRECTORY, "rb")
        try:
            self.characters = pickle.load(character_text_file)
        except EOFError: #no value when first access
            self.characters = ['unknown']
        self.character_number = len(self.characters)
        character_text_file.close()

        #set photo number
        photo_text_file = open(self.PHOTO_TEXT_DIRECTORY, "rb")
        try:
            photo_number = pickle.load(photo_text_file)
        except EOFError: #no value when first access
            photo_text_file.close()
            photo_text_file = open(self.PHOTO_TEXT_DIRECTORY, "wb")
            photo_number = 0
            pickle.dump(photo_number,photo_text_file)
        self.photo_number = photo_number
        photo_text_file.close()

        #load character image encoding set
        self.characters_representative_image_encoding = []
        for character in self.characters:
            if character == 'unknown': #unknown has no encoding file
                continue
            encoding_text_file = open(self.CHARACTER_DIRECTORY + "\\" + character + "\encoding.txt", "rb")
            encoding = pickle.load(encoding_text_file)
            self.characters_representative_image_encoding.append(encoding)
            encoding_text_file.close()

        #set accuracy variables
        self.tolerate = 0.4
        self.num_jit = 5
        
        #make window and frames
        tk.Tk.__init__(self)
        self.geometry('600x600') #set size of window
        window = tk.Frame(self)
        window.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES) ##side->위젯을 어느 방향으로 모을지, fill->위젯이 어느방향으로 확대될지. expand->쓰이지 않는 공간까지 위젯을 확대할지
        
        self.frames = {}
        for page in (MainPage, ImageAddPage, SetCharacterPage, SearchByCharacterPage):
            frame = page(window, self)
            page_name = page.__name__
            self.frames[page_name] = frame
            frame.grid(row=0,column=0,sticky="nsew") ##sticky->공간이 위젯보다 클 때 위젯이 어디에 가서 붙을지 nsew는 사방으로 즉, 중간에 위치
            
        self.show_page("MainPage")

    def show_page(self, pagename):
        #make given frame's position is top

        frame = self.frames[pagename]
        frame.tkraise()
        

class MainPage(tk.Frame):
    def __init__(self, parent, handler):
        #make MainPage frame
        #make widgets
        #show widgets

        #make frame
        tk.Frame.__init__(self, parent, width=600, height=600, padx = 160, pady=30)
        
        #make title/buttons
        l_title = tk.Label(self, text="MainPage", height=5, width=40)
        
        b_page1 = tk.Button(self, height=5, width=40, text="사진추가", command=lambda: handler.show_page("ImageAddPage"))
        b_page2 = tk.Button(self, height=5, width=40, text="인물등록", command=lambda: handler.show_page("SetCharacterPage"))
        b_page3 = tk.Button(self, height=5, width=40, text="인물로 사진 검색", command=lambda: handler.show_page("SearchByCharacterPage"))
        #b_page4 = tk.Button(self, height=5, width=40, text="갤러리", command=lambda: handler.show_page("GalleryPage"))

        #show widgets
        l_title.grid(row=0, column=0)
        b_page1.grid(row=1, column=0)
        b_page2.grid(row=2, column=0)
        b_page3.grid(row=3, column=0)
        #b_page4.grid(row=4, column=0)
        
class ImageAddPage(tk.Frame):
    def __init__(self, parent, handler):
        #make ImageAddPage frame
        #make widgets
        #show widgets

        #make frame
        tk.Frame.__init__(self, parent, width=600, height=600, padx = 160, pady=30)

        #make title/text/imageLabel/buttons
        l_title = tk.Label(self, text="ImageAddPage", height=5, width=40)
        
        self.t_file_path = tk.Text(self, height=1, width=30)

        self.l_file_image = tk.Label(self)

        b_add_image = tk.Button(self, text="add image", command=lambda:self.add_image())
        b_confirm_image = tk.Button(self, text="confirm image", command=lambda:self.confirm_image(handler))
        b_back = tk.Button(self, text="Back", command=lambda: handler.show_page("MainPage"))

        #show widgets
        l_title.grid(row=0, column=0, columnspan=3)
        self.t_file_path.grid(row=1, column=0, columnspan=2)
        b_add_image.grid(row=1, column=2)
        b_confirm_image.grid(row=2, column=0, columnspan=3)
        self.l_file_image.grid(row=3, column=0, columnspan=3)
        b_back.grid(row=5, column=0, columnspan=3)
        
    def add_image(self):
        #get image path
        #draw image path to textbox

        #get file path
        self.file_path = tk.filedialog.askopenfilename()

        #exception
        if not self.file_path:
            messagebox.showerror(title="경로 오류", message="파일을 선택해주세요")
            return
        
        if "." not in self.file_path:
            messagebox.showerror(title="경로 오류", message="파일이 아닙니다")
            return
            
        file_name = self.file_path.split("\\")
        file_name = file_name[len(file_name)-1]
        file_type = file_name.split(".")
        file_type = file_type[1]
        PROPER_TYPE = ["png","PNG", "jpg", "JPG", "gif", "GIF", "jpeg", "JPEG"]
        if file_type not in PROPER_TYPE:
            messagebox.showerror(title="경로 오류", message="이미지 파일이 아닙니다")
            return

        #update file path text
        self.t_file_path.delete(1.0,tk.END)
        self.t_file_path.insert(1.0,self.file_path)

        #show file's thumbnail
        self.thumbnail = Image.open(self.file_path)
        self.thumbnail = self.thumbnail.resize((128,128))
        self.p_thumbnail = ImageTk.PhotoImage(self.thumbnail)
        self.l_thmubnail = tk.Label(self, image=self.p_thumbnail)
        self.l_thmubnail.grid(row=4, column=0, columnspan=3)

    def confirm_image(self, handler):
        #copy image to App directory
        #classfy image
        
        #exception
        file_path = self.t_file_path.get(1.0,tk.END)
        file_path = file_path.rstrip("\n")
        if not file_path:
            messagebox.showerror(title="경로 오류", message="경로가 비어있습니다")
            return

        if "." not in file_path:
            messagebox.showerror(title="경로 오류", message="파일이 아닙니다")
            return
            
        file_name = file_path.split("\\")
        file_name = file_name[len(file_name)-1]
        file_type = file_name.split(".")
        file_type = file_type[1]
        PROPER_TYPE = ["png","PNG", "jpg", "JPG", "gif", "GIF", "jpeg", "JPEG"]
        if file_type not in PROPER_TYPE:
            messagebox.showerror(title="경로 오류", message="이미지 파일이 아닙니다")
            return
            
        #copy image to App directory
        original_image = Image.open(file_path)
        new_image = original_image.copy()
        new_image.save(handler.PHOTO_DIRECTORY + "\image" + str(handler.photo_number) + ".png")

        #classfy image
        self.classfy_image(handler, handler.PHOTO_DIRECTORY + "\image" + str(handler.photo_number) + ".png")
        
        #update photo number
        handler.photo_number = handler.photo_number + 1
        photo_text_file = open(handler.PHOTO_TEXT_DIRECTORY, "wb")
        pickle.dump(handler.photo_number, photo_text_file)
        photo_text_file.close()

        handler.show_page("MainPage")

    def classfy_image(self, handler, file_path):
        #encode image file
        #classfy image file by character
        
        #load image
        unknown_image = face_recognition.load_image_file(file_path)

        #encode image
        unknown_image_encoding = face_recognition.face_encodings(unknown_image, num_jitters=handler.num_jit)[0]

        #get most appropriate character
        recognized_character_index = 0
        face_distance_value = 1
        for i in range(handler.character_number-1):
            result = face_recognition.face_distance([np.array(handler.characters_representative_image_encoding[i])], unknown_image_encoding)
            if face_distance_value > result:
                face_distance_value = result
                recognized_character_index = i

        ###classfy image###       
        ##if there is no character in image##
        if face_distance_value > handler.tolerate:
            #get unknown character photo number
            unknown_character_text_file = open(handler.UNKNOWN_CHARACTER_TEXT_DIRECTORY,"rb")
            unknown_character_photo_number = pickle.load(unknown_character_text_file)
            unknown_character_text_file.close()

            #copy image to unknown's directory
            original_image = Image.open(file_path)
            new_image = original_image.copy()
            new_image.save(handler.UNKNOWN_CHARACTER_DIRECTORY + "\\image" + str(unknown_character_photo_number) + ".png")

            #update unknown character photo number
            unknown_character_text_file = open(handler.UNKNOWN_CHARACTER_TEXT_DIRECTORY,"wb")
            unknown_character_photo_number = unknown_character_photo_number + 1
            pickle.dump(unknown_character_photo_number, unknown_character_text_file)
            unknown_character_text_file.close()

            return

        ##if there is character in image##
        #get recognized character directory
        recognized_character = handler.characters[recognized_character_index+1]
        RECOGNIZED_CHARACTER_DIRECTORY = handler.CHARACTER_DIRECTORY +  "\\" + recognized_character

        #get recognized character photo number
        character_text_file = open(RECOGNIZED_CHARACTER_DIRECTORY + "\\character.txt", "rb")
        recognized_character_photo_number = pickle.load(character_text_file)
        character_text_file.close()

        #copy image to recognized character's directory
        original_image = Image.open(file_path)
        new_image = original_image.copy()
        new_image.save(RECOGNIZED_CHARACTER_DIRECTORY + "\\image" + str(recognized_character_photo_number) + ".png")

        #update recognized character photo number
        character_text_file = open(RECOGNIZED_CHARACTER_DIRECTORY + "\\character.txt", "wb")
        recognized_character_photo_number = recognized_character_photo_number + 1
        pickle.dump(recognized_character_photo_number, character_text_file)
        character_text_file.close()
        
        
class SetCharacterPage(tk.Frame):
    def __init__(self, parent, handler):
        #make SetCharacterPage frame
        #make widgets
        #show widgets
        
        #make frame
        tk.Frame.__init__(self, parent, width=600, height=600, padx = 160, pady=30)

        #make title/listBox/text/buttons
        l_title = tk.Label(self, text="SetCharacterPage", height=5, width=40)
        
        self.l_character_list = tk.Listbox(self, width=41)
        i = 0
        for character in handler.characters:
            self.l_character_list.insert(i,character)
            i = i + 1
            
        self.t_character_name = tk.Text(self, height=1, width=41)
        self.t_character_photo_path = tk.Text(self, height=1, width=20)
        
        b_add_character_photo_path = tk.Button(self, width=20, text="AddCharactePhotoPath", command=lambda:self.add_character_photo_path())
        b_add_character = tk.Button(self, text="add_character", command=lambda:self.add_character(handler))
        b_delete_character = tk.Button(self, width=20, text="delete_character", command=lambda:self.delete_character(handler))
        b_back = tk.Button(self, text="Back", command=lambda: handler.show_page("MainPage"))

        #show widgets
        l_title.grid(row=0, column=0, columnspan=3)
        self.t_character_name.grid(row=1, column=0, columnspan=3)
        self.t_character_photo_path.grid(row=2, column=0, columnspan=2)
        b_add_character_photo_path.grid(row=2, column=2)
        b_add_character.grid(row=3, column=0, columnspan=3)
        self.l_character_list.grid(row=5, column=0, columnspan=3)
        b_delete_character.grid(row=6, column=2)
        b_back.grid(row=7, column=0, columnspan=3)
        
    def add_character_photo_path(self):
        #get photo path
        #draw photo path to textbox
        #show thumbnail
        
        #get representativePhotoPath
        self.character_photo_path = tk.filedialog.askopenfilename()

        #exception
        if not self.character_photo_path:
            messagebox.showerror(title="경로 오류", message="파일을 선택해주세요")
            return

        if "." not in self.character_photo_path:
            messagebox.showerror(title="경로 오류", message="파일이 아닙니다")
            return
            
        file_name = self.character_photo_path.split("\\")
        file_name = file_name[len(file_name)-1]
        file_type = file_name.split(".")
        file_type = file_type[1]
        PROPER_TYPE = ["png","PNG", "jpg", "JPG", "gif", "GIF", "jpeg", "JPEG"]
        if file_type not in PROPER_TYPE:
            messagebox.showerror(title="경로 오류", message="이미지 파일이 아닙니다")
            return
        
        #update text
        self.t_character_photo_path.delete(1.0,tk.END)
        self.t_character_photo_path.insert(1.0,self.character_photo_path)

        #show thumbnail
        self.thumbnail = Image.open(self.character_photo_path)
        self.thumbnail = self.thumbnail.resize((128,128))
        self.p_thumbnail = ImageTk.PhotoImage(self.thumbnail)
        self.l_thumbnail = tk.Label(self, image=self.p_thumbnail)
        self.l_thumbnail.image = self.p_thumbnail
        self.l_thumbnail.grid(row=4, column=0, columnspan=3)

    def add_character(self, handler):
        #add character to listbox
        #update listbox
        #re-classfy unknown's image
        
        ##exception##
        #exception for character name
        character_name = self.t_character_name.get(1.0,tk.END)
        character_name = character_name.rstrip("\n")

        if not character_name:
            messagebox.showerror(title="인물 이름 오류", message="인물 이름을 입력해주세요")
            return

        if character_name == "unknown":
            messagebox.showerror(title="인물 이름 오류", message="인물 이름은 unknown일 수 없습니다")
            return
        
        if character_name in handler.characters:
            messagebox.showerror(title="인물 이름 오류", message="이미 존재하는 인물과 같은 이름의 인물을 추가할 수 없습니다")
            return
        
        #exception for file path
        file_path = self.t_character_photo_path.get(1.0,tk.END)
        file_path = file_path.rstrip("\n")
        if not file_path:
            messagebox.showerror(title="경로", message="파일을 선택해주세요")
            return
        
        if "." not in file_path:
            messagebox.showerror(title="경로 오류", message="파일이 아닙니다")
            return

        file_name = file_path.split("\\")
        file_name = file_name[len(file_name)-1]
        file_type = file_name.split(".")
        file_type = file_type[1]
        PROPER_TYPE = ["png","PNG", "jpg", "JPG", "gif", "GIF", "jpeg", "JPEG"]
        if file_type not in PROPER_TYPE:
            messagebox.showerror(title="경로 오류", message="이미지 파일이 아닙니다")
            return    
        
        #make directory
        NEW_CHARACTER_DIRECTORY = handler.CHARACTER_DIRECTORY + "\\" + character_name
        make_dir(NEW_CHARACTER_DIRECTORY)
        make_file(NEW_CHARACTER_DIRECTORY + "\character.txt")
        make_file(NEW_CHARACTER_DIRECTORY + "\encoding.txt")
        new_character_text_file = open(NEW_CHARACTER_DIRECTORY + "\character.txt", "wb")
        photo_number = 0
        pickle.dump(photo_number, new_character_text_file)
        new_character_text_file.close()

        #update listBox
        self.l_character_list.insert(handler.character_number, character_name)

        #copy representative image
        original_image = Image.open(self.character_photo_path)
        new_image = original_image.copy()
        new_image.save(NEW_CHARACTER_DIRECTORY + "\\representativeImage.png")

        #make encoding
        new_character_encoding_file = open(NEW_CHARACTER_DIRECTORY + "\encoding.txt", "wb")
        new_character_encoding = face_recognition.face_encodings(face_recognition.load_image_file(NEW_CHARACTER_DIRECTORY + "\\representativeImage.png"), num_jitters=handler.num_jit)[0]
        pickle.dump(new_character_encoding,new_character_encoding_file)
        new_character_encoding_file.close()
        handler.characters_representative_image_encoding.append(new_character_encoding)

        #update characters.txt file
        handler.characters.append(character_name)
        character_text_file = open(handler.CHARACTER_TEXT_DIRECTORY, "wb")
        pickle.dump(handler.characters, character_text_file)
        character_text_file.close()

        #update character number
        handler.character_number = handler.character_number + 1
        
        #update listbox for searchbycharacterpage
        search_by_character_page = handler.frames["SearchByCharacterPage"]
        search_by_character_page.l_character_list.delete(0,search_by_character_page.l_character_list.size()-1)
        i = 0
        for character in handler.characters:
            search_by_character_page.l_character_list.insert(i,character)
            i = i + 1

        ##re-classfy unknown's photos##
        file_list = get_file_list(handler.UNKNOWN_CHARACTER_DIRECTORY)
        file_list.remove("character.txt")

        for file in file_list:
            #load image
            unknown_image = face_recognition.load_image_file(handler.UNKNOWN_CHARACTER_DIRECTORY + "\\" + file)

            #encode image
            unknown_image_encoding = face_recognition.face_encodings(unknown_image, num_jitters=handler.num_jit)[0]

            ###classfy image###
            #get recognized chracter
            recognized_character_index = 0
            face_distance_value = 1
            for i in range(handler.character_number-1): #unknown has no encoding
                result = face_recognition.face_distance([np.array(handler.characters_representative_image_encoding[i])], unknown_image_encoding)
                if face_distance_value > result:
                    face_distance_value = result
                    recognized_character_index = i
                ##if there is no character in image##
                if face_distance_value > handler.tolerate:
                    continue
                
                ##if there is character in image##
                #get directory
                recognized_character = handler.characters[recognized_character_index+1]
                RECOGNIZED_CHARACTER_DIRECTORY = handler.CHARACTER_DIRECTORY +  "\\" + recognized_character

                #get character photo number
                character_text_file = open(RECOGNIZED_CHARACTER_DIRECTORY + "\\character.txt", "rb")
                character_photo_number = pickle.load(character_text_file)
                character_text_file.close()

                #copy image
                original_image = Image.open(handler.UNKNOWN_CHARACTER_DIRECTORY + "\\" + file)
                new_image = original_image.copy()
                new_image.save(RECOGNIZED_CHARACTER_DIRECTORY + "\\image" + str(character_photo_number) + ".png")

                #delete original image in unknown directory
                delete_file(handler.UNKNOWN_CHARACTER_DIRECTORY + "\\" + file)
                
                #update character photo number 
                character_text_file = open(RECOGNIZED_CHARACTER_DIRECTORY + "\\character.txt", "wb")
                character_photo_number = character_photo_number + 1
                pickle.dump(character_photo_number, character_text_file)
                character_text_file.close()
            
        
    def delete_character(self, handler):
        #delete character in listbox
        #update listbox
        #take character's image to unknown directory

        #exception
        name_to_delete = self.l_character_list.get(tk.ACTIVE)
        name_to_delete = name_to_delete.rstrip("\n")
        
        if not name_to_delete:
            messagebox.showerror(title="인물 선택 오류", message="삭제할 인물을 선택해주세요")
            return

        if name_to_delete == "unknown":
            messagebox.showerror(title="인물 선택 오류", message="삭제할 인물 이름은 unknown일 수 없습니다")
            return
            
        ##take character's image to unknown directory##
        character_photo_list = get_file_list(handler.CHARACTER_DIRECTORY + "\\" + name_to_delete)
        character_photo_list.remove("character.txt")
        character_photo_list.remove("encoding.txt")

        for photo in character_photo_list:
            #get unknown photo number
            unknown_text_file = open(handler.UNKNOWN_CHARACTER_TEXT_DIRECTORY, "rb")
            unknown_photo_number = pickle.load(unknown_text_file)
            unknown_text_file.close()
            
            #copy image
            original_image = Image.open(handler.CHARACTER_DIRECTORY + "\\" + name_to_delete + "\\" + photo)
            new_image = original_image.copy()
            new_image.save(handler.UNKNOWN_CHARACTER_DIRECTORY + "\\image" + str(unknown_photo_number) + ".png")

            #update unknown photo number
            unknown_photo_number = unknown_photo_number + 1
            unknown_text_file = open(handler.UNKNOWN_CHARACTER_TEXT_DIRECTORY, "wb")
            pickle.dump(unknown_photo_number, unknown_text_file)
            unknown_text_file.close()
            
        #delete directory
        delete_dir(handler.CHARACTER_DIRECTORY + "\\" + name_to_delete)

        #update listBox
        self.l_character_list.delete(tk.ACTIVE)

        #update character number
        handler.character_number = handler.character_number - 1

        #update characters.txt file
        handler.characters.remove(name_to_delete)
        character_text_file = open(handler.CHARACTER_TEXT_DIRECTORY, "wb")
        pickle.dump(handler.characters, character_text_file)
        character_text_file.close()

        #update listbox for searchbycharacterpage
        search_by_character_page = handler.frames["SearchByCharacterPage"]
        search_by_character_page.l_character_list.delete(0,search_by_character_page.l_character_list.size()-1)
        i = 0
        for character in handler.characters:
            search_by_character_page.l_character_list.insert(i,character)
            i = i + 1

        
        
class SearchByCharacterPage(tk.Frame):
    def __init__(self, parent, handler):
        #make SearchByCharacterPage frame
        #make widgets
        #show widgets

        #make frame
        tk.Frame.__init__(self, parent, width=600, height=600, padx = 160, pady=30)

        #make title/listbox/button
        l_title = tk.Label(self, text="SearchByCharacterPage", height=5, width=40)
 
        self.l_character_list = tk.Listbox(self, width=41, height=5)
        i = 0
        for character in handler.characters:
            self.l_character_list.insert(i,character)
            i = i + 1
            
        self.l_searched_image_list = tk.Listbox(self, width=41)
        
        b_search_character_image = tk.Button(self, text="search", command=lambda:self.search_by_character(handler))
        b_show = tk.Button(self, text="show", command=lambda:self.show(handler))
        b_back = tk.Button(self, text="Back", command=lambda: handler.show_page("MainPage"))

        #show widgets
        l_title.grid(row=0, column=0)
        self.l_character_list.grid(row=1, column=0)
        b_search_character_image.grid(row=2, column=0)
        self.l_searched_image_list.grid(row=3, column=0)
        b_show.grid(row=4, column=0)
        b_back.grid(row=6, column=0)

    def search_by_character(self, handler):
        #show selected character's photo list
        
        self.name_to_search = self.l_character_list.get(tk.ACTIVE)
        self.name_to_search = self.name_to_search.rstrip("\n")
        SEARCH_DIRECTORY = handler.CHARACTER_DIRECTORY + "\\" + self.name_to_search
        
        ##if search unknown##
        if self.name_to_search == "unknown":
            file_list = get_file_list(SEARCH_DIRECTORY)
            file_list.remove("character.txt") #unknown has no encoding.txt file

            self.l_searched_image_list.delete(0,self.l_searched_image_list.size()-1)
            i=0
            for file in file_list:
                self.l_searched_image_list.insert(i, file)
                i = i + 1
            return
        
        ##if search character except unknown##
        file_list = get_file_list(SEARCH_DIRECTORY)
        file_list.remove("character.txt")
        file_list.remove("encoding.txt")

        self.l_searched_image_list.delete(0,self.l_searched_image_list.size()-1)
        i=0
        for file in file_list:
            self.l_searched_image_list.insert(i, file)
            i = i + 1
        
    def show(self, handler):
        #show selected photo
        
        file_name_to_show = self.l_searched_image_list.get(tk.ACTIVE)
        file_name_to_show = file_name_to_show.rstrip("\n")

        #exception
        if not file_name_to_show:
            messagebox.showerror(title="파일 탐색 오류", message="해당하는 인물의 사진이 없습니다")
            return

        #show thumbnail        
        IMAGE_DIRECTORY = handler.CHARACTER_DIRECTORY + "\\" + self.name_to_search + "\\" + file_name_to_show

        self.thumbnail = Image.open(IMAGE_DIRECTORY)
        self.thumbnail = self.thumbnail.resize((128,128))
        self.p_thumbnail = ImageTk.PhotoImage(self.thumbnail)
        self.l_thumbnail = tk.Label(self, image=self.p_thumbnail)
        self.l_thumbnail.image = self.p_thumbnail
        self.l_thumbnail.grid(row=5, column=0)
        
#class GalleryPage(tk.Frame):
#    def __init__(self, parent, handler):
#        #
#        #
#        #
#        
#        tk.Frame.__init__(self, parent, width=600, height=600, padx = 160, pady=30)
#
#        #make title/button
#        l_title = tk.Label(self, text="GalleryPage", height=5, width=40)
#        
#        b_back = tk.Button(self, text="Back", command=lambda: handler.show_page("MainPage"))
#
#        #show widgets
#        l_title.grid(row=0, column=0)
#        b_back.grid(row=1, column=0)



app = App()
app.mainloop()

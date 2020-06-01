import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import face_recognition
import pickle

def makeFile(directory):
    if not os.path.isfile(directory):
        file = open(directory, "w")
        file.close()

def deleteFile(directory):
    os.remove(directory)
    
def makeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def deleteDir(directory):
    if os.path.exists(directory):
        fileList = os.listdir(directory)
        for file in fileList:
            deleteFile(directory+"\\"+file)
        os.rmdir(directory)
    
class App(tk.Tk):
    
    def __init__(self):
        #set directory
        self.mainDirectory = "C:\App"
        makeDir(self.mainDirectory)

        self.photoDirectory = self.mainDirectory+"\photos"
        makeDir(self.photoDirectory)

        self.characterDirectory = self.mainDirectory+"\characters"
        makeDir(self.characterDirectory)

        self.characterTextDirectory = self.characterDirectory + "\characters.txt"
        makeFile(self.characterTextDirectory)

        self.photoTextDirectory = self.photoDirectory + "\photos.txt"
        makeFile(self.photoTextDirectory)

        #set photoNumber, characterNumber
        f = open(self.characterTextDirectory, "rb")
        try:
            self.characters = pickle.load(f)
        except EOFError:
            self.characters = []
        self.characterNumber = len(self.characters)
        f.close()
        
        f = open(self.photoTextDirectory, "rb")
        try:
            number = pickle.load(f)
        except EOFError:
            f.close()
            f = open(self.photoTextDirectory, "wb")
            number = 0
            pickle.dump(number,f)
        self.photoNumber = number
        f.close()

        #load characterImageEncodingSet
        self.charactersRepresentativeImageEncoding = []
        i=0
        for character in self.characters:
            f = open(self.characterDirectory + "\\" + character + "\encoding.txt", "rb")
            self.charactersRepresentativeImageEncoding.append(pickle.load(f))
        
        #make window and frames
        tk.Tk.__init__(self)

        window = tk.Frame(self)
        window.pack(side="top", fill="both", expand=True)
        
        self.frames = {}
        for page in (MainPage, ImageAddPage, SetCharacterPage, SearchByCharacterPage, GalleryPage):
            frame = page(window, self)
            self.frames[page.__name__] = frame
            frame.grid(row=0,column=0,sticky="nsew")
            
        self.showPage("MainPage")

    def showPage(self, pagename):
        frame = self.frames[pagename]
        frame.tkraise()
        

class MainPage(tk.Frame):
    def __init__(self, parent, handler):
        tk.Frame.__init__(self, parent)

        #make title/buttons
        lTitle = tk.Label(self, text="MainPage")
        
        bPage1 = tk.Button(self, text="사진추가", command=lambda: handler.showPage("ImageAddPage"))
        bPage2 = tk.Button(self, text="인물등록", command=lambda: handler.showPage("SetCharacterPage"))
        bPage3 = tk.Button(self, text="인물로 사진 검색", command=lambda: handler.showPage("SearchByCharacterPage"))
        bPage4 = tk.Button(self, text="갤러리", command=lambda: handler.showPage("GalleryPage"))

        #show widgets
        lTitle.pack()
        bPage1.pack()
        bPage2.pack()
        bPage3.pack()
        bPage4.pack()
        
class ImageAddPage(tk.Frame):
    def __init__(self, parent, handler):
        tk.Frame.__init__(self, parent)

        #make title/text/imageLabel/buttons
        lTitle = tk.Label(self, text="ImageAddPage")
        
        self.tFilePath = tk.Text(self, height=1)

        self.lFileImage = tk.Label(self)

        bAddImage = tk.Button(self, text="AddImage", command=lambda:self.addImage())
        bconfirmImage = tk.Button(self, text="confirmImage", command=lambda:self.confirmImage(handler))
        bBack = tk.Button(self, text="Back", command=lambda: handler.showPage("MainPage"))

        #show widgets
        lTitle.pack()
        bAddImage.pack()
        self.tFilePath.pack()
        bconfirmImage.pack()
        self.lFileImage.pack()
        bBack.pack()
        
    def addImage(self):
        #get filePathisc
        self.filePath = tk.filedialog.askopenfilename()

        #exception
        if not self.filePath:
            return
        fileName = self.filePath.split("\\")
        fileName = fileName[len(fileName)-1]
        fileType = fileName.split(".")
        fileType = fileType[1]
        properType = ["png","PNG", "jpg", "JPG", "gif", "GIF", "jpeg", "JPEG"]
        if fileType not in properType:
            messagebox.showerror(title="경로 오류", message="이미지 파일이 아닙니다")
            return
        
        #show file's thumbnail
        #self.pFileImage = tk.PhotoImage(file=self.filePath)
        #self.pFileImage = self.pFileImage.subsample(2,2)
        #self.lFileImage.destroy()
        #self.lFileImage = tk.Label(self, image=self.pFileImage)
        #self.lFileImage.pack()

        #update filePath text
        self.tFilePath.delete(1.0,tk.END)
        self.tFilePath.insert(1.0,self.filePath)

    def confirmImage(self, handler):
        #exception
        filePath = self.tFilePath.get(1.0,tk.END)
        filePath = filePath.rstrip("\n")
        if not filePath:
            messagebox.showerror(title="경로 오류", message="경로가 비어있습니다")
            return
            
        #copy image to App directory
        originalImage = open(self.filePath, "rb")
        image = open(handler.photoDirectory + "\image" + str(handler.photoNumber) + ".png", "wb")
        
        
        while True:
            line = originalImage.readline()
            if not line:
                break
            image.write(line)

        #update photoNumber
        handler.photoNumber = handler.photoNumber + 1
        f = open(handler.photoTextDirectory, "wb")
        pickle.dump(handler.photoNumber, f)
        f.close()

        self.classfyImage(handler, filePath)

        handler.showPage("MainPage")

    def classfyImage(self, handler, filePath):
        #load image/encode image/classfy image
        unknownImage = face_recognition.load_image_file(filePath)
        
        unknownImageEncoding = face_recognition.face_encodings(unknownImage)[0]
        
        results = face_recognition.face_distance(handler.charactersRepresentativeImageEncoding, unknownImageEncoding)
        print(results)
                
        
class SetCharacterPage(tk.Frame):
    def __init__(self, parent, handler):        
        tk.Frame.__init__(self, parent)

        #make title/listBox/text/buttons
        lTitle = tk.Label(self, text="SetCharacterPage")
        
        self.lCharacterList = tk.Listbox(self)
        i = 0
        for character in handler.characters:
            self.lCharacterList.insert(i,character)
            i = i + 1
            
        self.tCharacterName = tk.Text(self, height=1)
        self.tCharacterPhotoPath = tk.Text(self, height=1)
        
        bAddCharacterPhotoPath = tk.Button(self, text="AddCharactePhotoPath", command=lambda:self.addCharacterPhotoPath())
        bAddCharacter = tk.Button(self, text="AddCharacter", command=lambda:self.addCharacter(handler))
        bDeleteCharacter = tk.Button(self, text="DeleteCharacter", command=lambda:self.deleteCharacter(handler))
        bBack = tk.Button(self, text="Back", command=lambda: handler.showPage("MainPage"))


        #show widgets
        lTitle.pack()
        self.tCharacterName.pack()
        self.tCharacterPhotoPath.pack()
        bAddCharacterPhotoPath.pack()
        bAddCharacter.pack()
        bDeleteCharacter.pack()
        self.lCharacterList.pack()
        bBack.pack()
        
    def addCharacterPhotoPath(self):
        #get representativePhotoPath
        self.characterPhotoPath = tk.filedialog.askopenfilename()

        #exception
        fileName = self.characterPhotoPath.split("\\")
        fileName = fileName[len(fileName)-1]
        fileType = fileName.split(".")
        fileType = fileType[1]
        properType = ["png","PNG", "jpg", "JPG", "gif", "GIF", "jpeg", "JPEG"]
        if fileType not in properType:
            messagebox.showerror(title="경로 오류", message="이미지 파일이 아닙니다")
            return
        
        #update text
        self.tCharacterPhotoPath.delete(1.0,tk.END)
        self.tCharacterPhotoPath.insert(1.0,self.characterPhotoPath)


    def addCharacter(self, handler):
        #exception
        characterName = self.tCharacterName.get(1.0,tk.END)
        characterName = characterName.rstrip("\n")
        if not characterName:
            messagebox.showerror(title="인물 이름 오류", message="인물 이름을 입력해주세요")
            return
        
        filePath = self.tCharacterPhotoPath.get(1.0,tk.END)
        filePath = filePath.rstrip("\n")
        if not filePath:
            messagebox.showerror(title="인물 대표 사진 오류", message="인물의 대표 사진을 입력해주세요")
            return        
        
        #make directory/update listBox/copy representative image/make encoding/update characters.txt file
        characterDirectory = handler.characterDirectory + "\\" + characterName
        makeDir(characterDirectory)
        makeFile(characterDirectory + "\character.txt")
        makeFile(characterDirectory + "\encoding.txt")
        f = open(characterDirectory + "\character.txt", "wb")
        i = 0
        pickle.dump(i, f)
        f.close()
        
        self.lCharacterList.insert(handler.characterNumber, characterName)
        handler.characterNumber = handler.characterNumber + 1
        
        originalImage = open(self.characterPhotoPath, "rb")
        image = open(characterDirectory + "\\representativeImage.png", "wb")
        while True:
            line = originalImage.readline()
            if not line:
                break
            image.write(line)
        originalImage.close()

        f = open(characterDirectory + "\encoding.txt", "wb")
        encoding = face_recognition.face_encodings(face_recognition.load_image_file(characterDirectory + "\\representativeImage.png"))[0]
        pickle.dump(encoding,f)
        f.close()
        handler.charactersRepresentativeImageEncoding.append(encoding)
        
        handler.characters.append(characterName)
        f = open(handler.characterTextDirectory, "wb")
        pickle.dump(handler.characters, f)
        f.close()
        
    def deleteCharacter(self, handler):
        #exception
        NameToDelete = self.lCharacterList.get(tk.ACTIVE)
        NameToDelete = NameToDelete.rstrip("\n")
        if not NameToDelete:
            messagebox.showerror(title="인물 선택 오류", message="삭제할 인물을 선택해주세요")
            return
        #update listBox/delete directory/update characters.txt file
        deleteDir(handler.characterDirectory + "\\" + NameToDelete)
        
        self.lCharacterList.delete(tk.ACTIVE)
        handler.characterNumber = handler.characterNumber - 1

        handler.characters.remove(NameToDelete)
        f = open(handler.characterTextDirectory, "wb")
        pickle.dump(handler.characters, f)
        f.close()

        
class SearchByCharacterPage(tk.Frame):
    def __init__(self, parent, handler):
        tk.Frame.__init__(self, parent)

        #make title/button
        lTitle = tk.Label(self, text="SearchByCharacterPage")
        
        bBack = tk.Button(self, text="Back", command=lambda: handler.showPage("MainPage"))

        #show widgets
        lTitle.pack()
        bBack.pack()
        
class GalleryPage(tk.Frame):
    def __init__(self, parent, handler):
        tk.Frame.__init__(self, parent)

        #make title/button
        lTitle = tk.Label(self, text="GalleryPage")
        
        bBack = tk.Button(self, text="Back", command=lambda: handler.showPage("MainPage"))

        #show widgets
        lTitle.pack()
        bBack.pack()



app = App()
app.mainloop()

import tkinter as tk
from tkinter import filedialog
import os

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

        #set fileNumber, characterNumber
        f = open(self.characterTextDirectory, "r")
        string = f.read()
        string.split("\n")
        self.characterNumber = len(string)
        f.close()
        
        f = open(self.photoTextDirectory, "r")
        number = f.read()
        self.photoNumber = int(number) if number else 0
        f.close()

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

        #show file's thumbnail
        self.pFileImage = tk.PhotoImage(file=self.filePath)
        self.pFileImage = self.pFileImage.subsample(2,2)
        self.lFileImage.destroy()
        self.lFileImage = tk.Label(self, image=self.pFileImage)
        self.lFileImage.pack()

        #update filePath text
        self.tFilePath.delete(1.0,tk.END)
        self.tFilePath.insert(1.0,self.filePath)

    def confirmImage(self, handler):
        #copy image to App directory
        originalImage = open(self.filePath, "rb")
        image = open(handler.photoDirectory + "\image"  + str(handler.photoNumber) + ".png", "wb")
        handler.photoNumber = handler.photoNumber+1
        
        while True:
            line = originalImage.readline()
            if not line:
                break
            image.write(line)

        #update photoNumber    
        f = open(handler.photoTextDirectory, "w")
        f.write(str(handler.photoNumber))
        f.close()

        handler.showPage("MainPage")
        
class SetCharacterPage(tk.Frame):
    def __init__(self, parent, handler):        
        tk.Frame.__init__(self, parent)

        #make title/listBox/text/buttons
        lTitle = tk.Label(self, text="SetCharacterPage")
        
        self.lCharacterList = tk.Listbox(self)
        f = open(handler.characterTextDirectory, "r")
        string = f.read()
        f.close()
        string = string.split("\n")
        i = 0
        for ch in string:
            self.lCharacterList.insert(i,ch)
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

        #update text
        self.tCharacterPhotoPath.delete(1.0,tk.END)
        self.tCharacterPhotoPath.insert(1.0,self.characterPhotoPath)


    def addCharacter(self, handler):
        #make directory/update listBox/copy representative image/update characters.txt file
        characterName = self.tCharacterName.get(1.0,tk.END)
        characterName = characterName.rstrip("\n")
        characterDirectory = handler.characterDirectory + "\\" + characterName
        makeDir(characterDirectory)

        self.lCharacterList.insert(handler.characterNumber, characterName)
        handler.characterNumber = handler.characterNumber + 1
        
        originalImage = open(self.characterPhotoPath, "rb")
        image = open(characterDirectory + "\\representiveImage.png", "wb")

        while True:
            line = originalImage.readline()
            if not line:
                break
            image.write(line)

        f = open(handler.characterTextDirectory, "a")
        f.write(characterName)
        f.close()
        
    def deleteCharacter(self, handler):
        #update listBox/delete directory/update characters.txt file
        NameToDelete = self.lCharacterList.get(tk.ACTIVE)
        NameToDelete = NameToDelete.rstrip("\n")
        deleteDir(handler.characterDirectory + "\\" + NameToDelete)
        
        self.lCharacterList.delete(tk.ACTIVE)
        handler.characterNumber = handler.characterNumber - 1
        
        f = open(handler.characterTextDirectory, "r")
        string =  f.read()
        f.close()
        f = open(handler.characterTextDirectory, "w")
        string = string.split("\n")
        for line in string:
            if(line == NameToDelete):
                continue
            f.write(line)
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

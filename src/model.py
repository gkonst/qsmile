class Icon(object):
    def __init__(self, text , image = None):
        self.text = text
        self.image = image

    def addText(self, text):
        #print self.text
        #print type(text)
        self.text.append(text)
        #print type(self.text[0])
        #print self.text
    def __str__(self):
        return "Icon(image=" + str(self.image) + ", text=" + str(self.text) + ")"
    
class Pack(object):
    def __init__(self):
        self.icons = []
        self.author = ""
        self.name = "UNKNOWN"
        self.icon = ""
        self.version = ""
        self.desc = ""
        self.created = ""
        
    def addIcon(self,  icon):
        self.icons.append(icon)
        
    def deleteIcon(self, i):
        del self.icons[i]
        
    def find(self, image):
        for icon in self.icons:
            if icon.image == image:
                return icon

    def generateIconFilename(self):
        temp = list(self.icons[-1].image[0:-4])
        if(ord(temp[1]) == 122):
            temp[0] = chr(ord(temp[0]) + 1)
        else:
            temp[1] = chr(ord(temp[1]) + 1)
        return "".join(temp)
    
    def validateIcon(self, i):
        if not self.icons[i]:
            return False
        elif not self.icons[i].image:
            return False
        elif not self.icons[i].text:
            return False
        else:
            return True


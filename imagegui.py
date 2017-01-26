#Original version created by Grant Luberda
#Improved version created by Alex Duda
#Other contributors: Dr. Marc Berthoud, Becca Russell
#University of Chicago-Yerkes Observatory: ImageGUI Image Alignment Tool (Version 2.0)
#Developed in 2013

#-----------imports------------

from Tkinter import * #GUI creation library
import tkMessageBox #Creates and displays messages
import tkFileDialog #allows user to browse and open files
import ImageTk #library for interacting with images using Tkinter
import Image #library for interacting with images as arrays
import PIL #powerful library for image manipulation
import pyfits #library for working with FITS images
from numpy import *
import numpy #powerful python math library, useful for image arrays
import sys #library for system interaction
import os #library for operating system interaction
#import pylab
from optparse import OptionParser #library that allows command line arguments

#Global Variables (may be deleted later)






#------Class Definitions-------

class fitsImage:
    
    'provides a model for an object that contains details of the fits image currently selected'
    def __init__(self, color, path, data):
        self.index = 0
        self.color=color
        self.path=path
        self.data=data
        self.x=data.shape[1]
        self.y=data.shape[0]
        self.resized=[]
        self.coords=0
        self.tkx=IntVar()
        self.tky=IntVar()
        self.tkx.set(0)
        self.tky.set(0)
        
        
    def setCoordsHandler(self, event):
       self.tkx.set(event.x)
       self.tky.set(event.y)
       self.coords=(self.tkx.get()*manager.change, self.y-self.tky.get()*manager.change)
       print self.coords[0], self.coords[1]
       manager.waitvar.set(manager.waitvar.get()+1)
       
class Manager:
    'manages global variables within the program'
    def __init__(self):
        self.averagedarks=[]
        self.averageflats=[]
        self.formats=formats = [('FITS','*.FITS'),('FITS','*.fits'),('FITS','*.fit')] #accepted image format list
        self.darkvar=IntVar()
        self.darksbutton=Button()
        self.flatsbutton=Button()
        self.darksentry=Entry()
        self.flatsentry=Entry()
        self.ColorImage=0
        self.change=1
        self.resized=0
        self.waitvar=IntVar() #variable that tells the GUI when to update during align process
        self.waitvar.set(0)
        self.fitsAttributes=['','','']
        self.redpath=""
        self.greenpath=""
        self.bluepath=""
        self.text="""
Yerkes Observatory               (``',
Alex Duda Grand Luberda         / `''/
Becca Russell Marc Berthoud    /    /
ImageGUI Version 2.0        o\/    /
                            \,    /          _
                           /(    /         ,',`,
                          /x`''7/_________r_ ,=,
                         (x   //---) )------',=,
                        / `''7'   / /     ' ,=,
                       /    /    / /       '-'
                      (    /    / (
                       `'''    |(o)|
                              `|~~~|`
                               |===|                 
                               |   |
                               |===|
                               |   |
                               |___|
                              |`___`|
                      ,-----'`~~~~~~~`'-----,
                       `~~~~~~~~~~~~~~~~~~~`

"""      
#---------Functions-----------
        
def getPaths(endString, field, color): #gets user-selected paths for FITS image files
    
    findPath = tkFileDialog.askopenfilename(parent=root, title ="Select "+endString, filetypes=manager.formats)
    
    
    if len(findPath)>0:
        Write('Selected '+endString)
        field.delete(0, END)
        field.insert(0, findPath)
    else:
        Write('NO IMAGE SELECTED')
        
def makeObjects():
    
        manager.fitsAttributes[0]=fitsImage('red', redentry.get(), pyfits.getdata(redentry.get()))
        manager.fitsAttributes[1]=fitsImage('green', greenentry.get(), pyfits.getdata(greenentry.get()))
        manager.fitsAttributes[2]=fitsImage('blue', blueentry.get(), pyfits.getdata(blueentry.get()))
    




def Align():
    
    
    try:
        makeObjects()
        displayCanvas.delete(ALL)
        colorbutton.configure(state="disabled")
        displayCanvas.configure(cursor="crosshair")
        
        dataList=[]
        resizedList=[]
        #iterates through process 3 times for each image
        for i in range(3):
            dataList.append(manager.fitsAttributes[i].data) #adds each image's data to an element in the list
            #print dataList[i]
            dataList[i]=fliplr(rot90(dataList[i], 2)) 
            dataList[i]=dataList[i].copy()
            x=manager.fitsAttributes[i].x
            y=manager.fitsAttributes[i].y
            
            
            dimensions=x*y
            scaleArray=dataList[i].copy()
            
            scaleArray.shape=(dimensions,) 
            scaleArray.sort()
            smin=scaleArray[dimensions/100]
            smax=scaleArray[dimensions-dimensions/100]
            scaleimg=255.0*(dataList[i]-smin)/(smax-smin) #scales image color values to be better represented. (98% scaling) (I think...)
            scaleimg[scaleimg<0]=0.0
            scaleimg[scaleimg>255]=255
            dataList[i]=scaleimg.copy()
            
            dataList[i].shape=(x*y)
            
            newImage=Image.new('L', (x, y)) #creates Image object with dimensions of original .fits data
            
            newImage.putdata(dataList[i]) #puts .fits image data in Image object
            resizedList.append(newImage)
	    
           
            if x>500 and x>=y: #resizes image to fit in display area. Now works with rectangles
                manager.change=x/500.0
                
                newX=x/manager.change
                newY=y/manager.change
               
                
            elif y>500 and y>x:
                manager.change=y/500.0
                newX=x/manager.change
                newY=y/manager.change
                
            elif y>500 and x>500:
                if x>y:
                    manager.change=x/500.0
                
                    newX=x/manager.change
                    newY=y/manager.change
                  
                    
                elif y>x:
                    manager.change=y/500.0
                    newX=x/manager.change
                    newY=y/manager.change
	    elif x<500 and x>=y:
                manager.change=x/500.0
		newX=x/manager.change
		newY=y/manager.change
                  
                    
                
            resizedList[i]=resizedList[i].resize((int(newX), int(newY)), Image.ANTIALIAS)
            resizedList[i]=ImageTk.PhotoImage(resizedList[i])
            manager.fitsAttributes[i].resized=resizedList[i]
	    displayCanvas.config(width=newX, height=newY)
            displayCanvas.delete(ALL)
            displayCanvas.bind("<Button-1>", manager.fitsAttributes[i].setCoordsHandler)
            Write("Please select the brightest star in this image.")
            
        
        #creates PhotoImage object of each image
        #print resizedList
        
        
            displayCanvas.create_image((newX/2,newY/2), image=manager.fitsAttributes[i].resized)
            displayCanvas.wait_variable(manager.waitvar)
            if manager.waitvar.get()==256:
                sys.exit()
            else:
                pass
            
            
        displayCanvas.unbind("<Button-1>")
        displayCanvas.delete(ALL)
        colorbutton.configure(state="active")
        displayCanvas.configure(cursor="")
        
        
    except IOError:
        Write('Please make sure all images are selected and are valid .fits files')
        colorbutton.configure(state="active")
     
    except AttributeError:
        Write('Please make sure all images are selected')
        colorbutton.configure(state="active")
        
        
def RGB(): #aligns images based on coordinates gathered during Align() and creates RGB image for display.
    if manager.fitsAttributes==['','','']:
        makeObjects()
    else:
        pass
    try:
        alignpaths=[manager.fitsAttributes[0].path, manager.fitsAttributes[1].path, manager.fitsAttributes[2].path]
        coordsList=[manager.fitsAttributes[0].coords, manager.fitsAttributes[1].coords, manager.fitsAttributes[2].coords]
	
	#print coordsList
        
        pathlist = [manager.fitsAttributes[0].path, manager.fitsAttributes[1].path, manager.fitsAttributes[2].path]
        
        if coordsList!=[0,0,0]:
                
            xlist = []
            ylist = []
            xshift = []
            yshift = []
    
            # Gets the images and puts them into a list
            imglist = [manager.fitsAttributes[0].data, manager.fitsAttributes[1].data, manager.fitsAttributes[2].data]
    	    print imglist
            i=0
            for img in imglist:
                
                #defines area to search for brightest pixel
                boxRadius=10 #5 is okay, 10 is good, 20 is too large, trying 15.
    
                if coordsList[i][0]<boxRadius and coordsList[i][1]<boxRadius: #
                    coordsList[i]=(coordsList[i][0]+boxRadius, coordsList[i][1]+boxRadius)
                    
                elif coordsList[i][0]<boxRadius:
                    coordsList[i]=(coordsList[i][0]+boxRadius, coordsList[i][1])
                    
                elif coordsList[i][1]<boxRadius:
                    coordsList[i]=(coordsList[i][0], coordsList[i][1]+boxRadius)
                    
                
                
                pixelbox = img[coordsList[i][1]-boxRadius:coordsList[i][1]+boxRadius,coordsList[i][0]-boxRadius:coordsList[i][0]+boxRadius]
                #print pixelbox
                #print pixelbox
                # To get index of maximum value/finds brightest pixel
                pixel = pixelbox.argmax()
		print pixel
		print pixelbox
                xlist.append(pixel%(2*boxRadius)+coordsList[i][0])
                ylist.append(pixel/(2*boxRadius)+coordsList[i][1])
                
                
                Write('Image aligned')
                i=i+1
            
            print xlist, ylist
            # Locates the center of mass of star
            xcom = sum(xlist)/len(xlist)
            ycom = sum(ylist)/len(ylist)
            print [x-xcom for x in xlist] , [y-ycom for y in ylist]
            # Calculates the x and y shift for each image
            for x in xlist:
                xshift.append(int(round(x-xcom))*-1)
            for y in ylist:
                yshift.append(int(round(y-ycom))*-1)
    
            num = 0
    
            # Shifts each of the images according the the values in xshift and yshift
            for element in imglist:
                blank=array(zeros(imglist[num].shape))
                if xshift[num] > 0:
                    blank[:,+xshift[num]:] =  imglist[num][:,:-xshift[num]]
                if xshift[num] == 0:
                    blank[:,:] = imglist[num][:,:]
                if xshift[num]< 0:
                    blank[:,:+xshift[num]] = imglist[num][:,-xshift[num]:]
                if yshift[num] > 0:
                    imglist[num][+yshift[num]:,:] = blank[:-yshift[num],:]
                if yshift[num] == 0:
                    imglist[num][:,:] = blank[:,:]
                if yshift[num] < 0:
                    imglist[num][:yshift[num],:] = blank[-yshift[num]:,:]
                # Adds the images and paths to a global variable for use in RGB
               
                alignpaths[num] = manager.fitsAttributes[num].path
                num = num + 1
            Write('All images successfully aligned.')
            
    
    
    
    
    
        else:
                pass
        """
        This function takes the file paths, checks to see if they are valid FITS images, and compiles them into an RGB image.
        """
        # Allows for error checking
        errorflag = 0
        redpath = manager.fitsAttributes[0].path
        greenpath = manager.fitsAttributes[1].path
        bluepath = manager.fitsAttributes[2].path
        if errorflag == 0:
            number = slider.get()
            # Compares the file path in the entry field with file paths used 
            # in "Align." If they are identical, the program assumes the user 
            # wants to use the aligned images.  If not it uses the file in the entry
            # field.  The program then checks that the selected images are valid 
            # FITS files.
            if redpath == alignpaths[0]:
                img1 = manager.fitsAttributes[0].data
                Write('Using aligned red image.')
            else:
                try:
                    img1 = manager.fitsAttributes[0].data
                except:
                    errorflag = 1
                    Write('Read error for red image.')
                    return numpy.zeros((10,10))
            if greenpath == alignpaths[1]:
                img2 = manager.fitsAttributes[1].data
                Write('Using aligned green image.')
            else:
                try:
                    img2 = manager.fitsAttributes[1].data
                except:
                    errorflag = 1
                    Write('Read error for green image.')
                    return numpy.zeros((10,10))
            if bluepath == alignpaths[2]:
                img3 = manager.fitsAttributes[2].data
                Write('Using aligned blue image.')
            else:
                try:
                    img3 = manager.fitsAttributes[2].data
                except:
                    errorflag = 1
                    Write('Read error for blue image.')
                    return numpy.zeros((10,10))
            if img1.shape != img2.shape or img1.shape != img3.shape or img2.shape!=img3.shape:
                    Write('Please select images of the same dimensions.')
            else: 
                shape = img1.shape
                # See if we can clean the images
                try:
                    img1 = mysmoothing(img1)
                    img2 = mysmoothing(img2)
                    img3 = mysmoothing(img3)
                    Write('Images were cleaned')
                except:
                    pass
                oldimglist=[img1, img2, img3]
    
                imglist = []
                # Creates an image cube for use in a scaling file (If one is used)
                inputimage = zeros((shape[0],shape[1],3))
                inputimage[:,:,0] = oldimglist[0]
                inputimage[:,:,1] = oldimglist[1]
                inputimage[:,:,2] = oldimglist[2]
                # Checks to see if the user is using a specific scaling file.
                try:
                    myscaling(inputimage).shape
                    colorimage = myscaling(inputimage)
                except:
                    for image in oldimglist:
                        # Allows mathematical operations to be performed even if the 
                        # user chose not to use flats or darks
                        
                        darks = manager.averagedarks
                        if len(list(darks)) == 0:
                            darks = zeros((image.shape[0],image.shape[1]))
                       
                        flats = manager.averageflats
                        if len(list(flats)) == 0:
                            # Creates an array of 1's with correct dimensions
                            flats = zeros((image.shape[0],image.shape[1]))
                            flats[:,:] = 1
                        # Reduction and Scaling of the images
                        image = (image-darks)/flats
                        image = image-(image.mean()-std(image)*0.01)
                        # Scales image based on value in the slider
                        image = image/(std(image)*(20.0/number))
                        imglist.append(image)
                    colorimage = zeros((shape[0],shape[1],3))
                    colorimage[:,:,0] = imglist[0]
                    colorimage[:,:,1] = imglist[1] 
                    colorimage[:,:,2] = imglist[2]
                colorimage[where(colorimage>1)] = 1
                colorimage[where(colorimage<0)] = 0
                # Turns interactive pylab on. This is equivalent to typing "-pylab" when
                # starting python.
                colorimage=flipud(colorimage) #flips the image upside down to display and save image properly. Edited 9-19-11 Alex Duda @ home
                
                
                
                y=colorimage.shape[0]
                x=colorimage.shape[1]
                
                #print colorimage.shape
                #print colorimage.dtype
                colorimage=colorimage.copy()
                colorimage.shape=[x*y,3]
                colordata=list(tuple(numpy.array(255*pixel, dtype=numpy.int16)) for pixel in colorimage)
                
                manager.ColorImage=Image.new('RGB',(x,y)) 
    
                manager.ColorImage.putdata(colordata)
                
                resizedImage=manager.ColorImage
                #print colorImage
               
                if x>500 and x>=y:
                    manager.change=x/500.0
                    
                    newX=x/manager.change
                    newY=y/manager.change
                    
                elif y>500 and y>x:
                    manager.change=y/500.0
                    newX=x/manager.change
                    newY=y/manager.change
                   
                elif y>500 and x>500:
                    if x>y:
                        manager.change=x/500.0
                    
                        newX=x/manager.change
                        newY=y/manager.change
                        
                    elif y>x:
                        manager.change=y/500.0
                        newX=x/manager.change
                        newY=y/manager.change
                elif x<500 and x>=y:
                    manager.change=x/500.0
                    newX=x/manager.change
                    newY=y/manager.change
                elif y<500 and x<y:
                    manager.change=y/500.0
                    newX=x/manager.change
                    newY=y/manager.change
                elif x<500 and y<500:
                    manager.change=x/500.0
                    newX=x/manager.change
                    newY=y/manager.change
                  
                        
    
                resizedImage=resizedImage.resize((int(newX),int(newY)), Image.ANTIALIAS)
                resizedImage=ImageTk.PhotoImage(resizedImage)
                manager.resized=resizedImage
                displayCanvas.create_image((newX/2,newY/2),image=manager.resized)
    
    
    
                Write('The completed RGB image.')
                savebutton.configure(state="active")
                displayCanvas.update()
                coordsList=[]
    except AttributeError:
        Write('Please make sure all images are selected')


def Getdf(color, field):
    """
    This function allows the user to select multiple dark or flat frames and average them together.  It then reduces the color image using this data.
    """
    dflist = []
    field.delete(0, END)
    # Opens file dialog to select files
    input_images = tkFileDialog.askopenfilenames(parent=root, title ="Select files", filetypes=manager.formats)
    filelist = list(input_images)
    for element in filelist:
        dflist.append(pyfits.getdata(element))
        field.insert(END, element+', ')
    # Averages the frames adds them to a global variable for use in "RGB".
    total = 0
    for element in dflist:
        total = total + element
    if len(dflist)==0:
        Write('No frames selected!')
    else: 
        if color == 'dark':
            
            manager.averagedarks = total/len(dflist)
            Write('Dark frames have been averaged')
            fDebug()
        if color == 'flat':
           
            manager.averageflats = total/len(dflist)
            Write('Flat frames have been averaged')
            fDebug()


def Save(): #saves color image to .jpg file
    if manager.ColorImage==0:
        Write('There is no image to save!')
    else:
        
        savepath = tkFileDialog.asksaveasfilename(parent=root, title ="Save RGB Image", defaultextension = '.jpg') #changed from "asksaveasfile" to "asksaveasfilename" 8-13-11
        if '/' not in savepath: #added to let user cancel saving process 9-19-11
          Write('Save cancelled')
          fDebug()
        elif '.fits' in savepath:
          tkMessageBox.showwarning('Error!','This program can only save to .jpg files') #added to eliminate problems that may arise when people try to save as a FITS file
          Write('Save cancelled')
        else:
          
          try: #handles errors when users input "wrong" extensions
            
            manager.ColorImage.save(savepath, "JPEG")
            if os.path.exists(savepath):
              Write('Image saved.')
              fDebug()
          except KeyError:
            tkMessageBox.showwarning('Error!','Unknown file extension, please save using a valid file extension')
            
            fDebug()













    
def fDebug():
    pass

def Draw():
    """
    This funtion draws in the dark and flat field buttons and entry fields when the checkbox is selected, and destroys them when it is not.
    """
    # Recieves value from the checkbox
    if manager.darkvar.get() == 1:
        # Draws the button and entry field for the dark fields
        
        manager.darksbutton = Button(rgbframe, text='Select Dark Frames', command=lambda: Getdf('dark', manager.darksentry))
        manager.darksbutton.grid(column=1, row=4, pady=1, padx=5, sticky=(E+W))
        
        manager.darksentry = Entry(rgbframe, width=65)
        manager.darksentry.grid(column=2, row=4, padx=8, sticky=(W))
        # Draws the button and entry field for the flat fields
        
        manager.flatsbutton = Button(rgbframe, text='Select Flat Frames', command=lambda:Getdf('flat', manager.flatsentry))
        manager.flatsbutton.grid(column=1, row=5, padx=5, sticky=(E+W))
        
        manager.flatsentry = Entry(rgbframe, width=65)
        manager.flatsentry.grid(column=2, row=5, padx=8, sticky=(W))
    # Recieves the value from the checkbox
    if manager.darkvar.get() == 0:
        
        # Destroys the unwanted fields and clears the global variables used to store the fields
        manager.darksbutton.destroy()
        manager.flatsbutton.destroy()
        manager.darksentry.destroy()
        manager.flatsentry.destroy()
       




    
def Write(msg):
    """
    This function writes the given line of text into the message box and sdeletes any extra lines.
    """
    # Counts the number of lines in the text box by finding the index of the last line and returns it as an integer
    numlines = int(msgbox.index('end - 1 line').split('.')[0])
    # Deletes the first line of text in the text box if there are more than 5 lines in the box
    if numlines > 5:
        msgbox.delete(1.0, 2.0)
    #insert message and newline in box
    msgbox.insert('end', msg)
    msgbox.insert('end', '\n')
    
def Quit():
    manager.waitvar.set(256) #changes tkinter wait variable value to something that 
    sys.exit()



#----------GUI Creation----------

root=Tk() #creates a new Tkinter.Tk instance
mainframe = Frame(root) #creates a new frame within that root instance
mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) #places the frame in root at specified location
manager=Manager()
rgbframe = Frame(mainframe) #new frame for managaing RGB buttons in mainframe
rgbframe.grid(column=1, row=1, sticky=(N, W, E, S))
buttonframe = Frame(mainframe) #new frame in mainframe
buttonframe.grid(column=1, row=2, sticky=(E+W))
messageframe = Frame(mainframe) #frame for managing messages in mainframe
messageframe.grid(column=1, row=3, sticky=(W))
extrasframe = Frame(messageframe) #miscellaneous frame
extrasframe.grid(column=1, row=0, sticky=(W))

redbutton = Button(rgbframe, text='Select Red Image', fg='red', padx=5, command=lambda:getPaths('red image.', redentry, 'red'))
redbutton.grid(column=1, row=1, pady=1, padx=5, sticky=(E+W))    
greenbutton = Button(rgbframe, text='Select Green Image', fg='green',command=lambda:getPaths('green image.', greenentry, 'green')) #creates buttons for selecting images
greenbutton.grid(column=1, row=2, padx=5, pady=1, sticky=(E+W))
bluebutton = Button(rgbframe, text='Select Blue Image', fg='blue',command=lambda:getPaths('red image.', blueentry, 'blue'))
bluebutton.grid(column=1, row=3, padx=5, pady=1, sticky=(E+W))
alignbutton = Button(buttonframe, text='Align Images', padx=5,command=Align)
alignbutton.grid(column=0, row=1, padx=5, pady=10, sticky=(E))
colorbutton = Button(buttonframe, text='Get RGB', command=RGB)               #other buttons for saving, quitting, aligning...
colorbutton.grid(column=1, row=1, padx=5, sticky=(E))
savebutton = Button(buttonframe, text='Save JPEG', command=Save)
savebutton.configure(state='disabled')
savebutton.grid(column=2, row=1, padx=5, sticky=(E))
bquit = Button(buttonframe, text='QUIT', command=Quit)
bquit.grid(column=3, row=1, padx=5, sticky=(E))
usedarks = Checkbutton(extrasframe, text='Darks and Flats', command=Draw, variable=manager.darkvar) #shows darks and flats selection area if necessary
usedarks.grid(column=0, row=0, padx=0)

redentry = Entry(rgbframe, width=65)
redentry.grid(column=2, row=1, padx=8, sticky=(W))
greenentry = Entry(rgbframe, width=65)
greenentry.grid(column=2, row=2, padx=8, sticky=(W))
blueentry = Entry(rgbframe, width=65)
blueentry.grid(column=2, row=3, padx=8, sticky=(W))


msgbox = Text(messageframe, width=80, height=5, relief=SUNKEN) #message box creation
msgbox.grid(column=0, row=0, padx=5, pady=5)

slider = Scale(extrasframe, from_=1, to_=20, orient=HORIZONTAL, label='Brightness', length=200, ) #brightness slider
slider.grid(column=0, row =1)
slider.set(15)

displayCanvas=Canvas(mainframe, height=500, width=500, cursor='') #creates canvas area where images will be placed and displayed
displayCanvas.grid(column=1, row=4)
displayCanvas.create_text(250, 250, text=manager.text, font=("courier","9")) 
Write('Welcome to ImageGUI!')
root.title('ImageGUI Image Processor: Version 2.0')
root.mainloop() #starts Tkinter process

















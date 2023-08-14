from tkinter import Tk, filedialog, messagebox, simpledialog
from numpy import asarray, savetxt, arange
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
import scipy

class CPD:
    def __init__(self):
        self.run()
    def run(self):
        '''
        Main function of the digitizer
        '''

        # open the dialog box
        # first hide the root window
        root = Tk()
        root.withdraw()
        # open the dialog
        filein = filedialog.askopenfilename(
            title = "Select image to digitize",
            filetypes = (
                ("png files","*.png"),
                ("jpeg files","*.jpg"))
            )
        if len(filein) == 0:
            # nothing selected, return
            return

        # show the image    
        img = mpimg.imread(filein)
        _, ax = plt.subplots()
        ax.imshow(img)
        ax.axis('off')  # clear x-axis and y-axis

        # get origin (0,0) 
        origin,reforiginX,reforiginY = self.getOrigin()

        # get reference length in x direction
        xfactor = self.getReferenceLength(0)

        # get the reference length in y direction
        yfactor = self.getReferenceLength(1)

        # digitize curves until stopped by the user
        reply = True
        while reply:

            messagebox.showinfo("Digitize curve",
                "Please digitize the curve. The first point is the origin." +
                "Left click: select point; Right click: undo; Middle click: finish"
                )

            # get the curve points
            x = plt.ginput(
                -1,
                timeout=0,
                show_clicks=True
                )
            x = asarray(x)

            ax.plot(x[:,0],x[:,1],'g','linewidth',1.5)
            plt.draw()

            # convert the curve points from pixels to coordinates
            x[:,0] = (x[:,0]-origin[0][0]) * xfactor + reforiginX
            x[:,1] = (x[:,1]-origin[0][1]) * yfactor + reforiginY

            # write the data to a file
            # first get the filename
            validFile = False

            while not validFile:
                fileout = filedialog.asksaveasfilename(
                    title = "Select file to save the data",
                    filetypes = [ ("Simple text files (.txt)", "*.txt") ],
                    defaultextension = 'txt'
                )
                if len(fileout) == 0:
                    # nothing selected, pop up message to retry
                    messagebox.showinfo("Filename error", "Please select a filename to save the data.")
                else:
                    validFile = True

            # write the data to file
            savetxt(fileout, x, delimiter='\t')

            arr_x = x[:,0]
            arr_y = x[:,1]

            # interpolate by y
            y_init = simpledialog.askfloat("Enter initial y value for interpolate",
                "Enter initial y value for interpolate")
            bin_ = simpledialog.askfloat("Enter interpolation bin",
                "Enter interpolation bin")
            y_interp = arange(y_init,np.nanmax(arr_y)+1,bin_)
            x_interp = self.interpolate_wo_bin(arr_y,arr_x,y_interp)

            df = pd.DataFrame({
                'x':x[:,0],
                'y':x[:,1]
            })

            df_interp = pd.DataFrame({
                'x':x_interp,
                'y':y_interp
            })

            df.to_csv(fileout[:-4]+'.csv',index=False)
            df_interp.to_csv(fileout[:-4]+'_interp.csv',index=False)


            reply = messagebox.askyesno("Finished?",
                "Digitize another curve?"
                )

        # clear the figure
        plt.clf()
    def interpolate_wo_bin(self,x,y,x_interp):
        '''
        Interpolate
        '''
        interp = scipy.interpolate.interp1d(x,y) 
        y_interp = []
        for x_ in x_interp:
            try:
                y_interp.append(interp(x_))
            except Exception as e:
                y_interp.append(np.nan)
        return y_interp
    def getOrigin(self):
        '''
        Get the origin coordinates
        '''

        reply = False
        while not reply:
            messagebox.showinfo("Select origin",
                "Use the mouse to select the origin coordinates."
                )
            coord = plt.ginput(
                1,
                timeout=0,
                show_clicks=True
                ) # capture only one points

            # ask for a valid length
            validOrigin = False
            while not validOrigin:
                reforiginX = simpledialog.askfloat("Enter reference origin",
                    "Enter the reference origin in x direction")
                reforiginY = simpledialog.askfloat("Enter reference origin",
                    "Enter the reference origin in y direction")
                if isinstance(reforiginX, float) and isinstance(reforiginY, float):
                    validOrigin = True
                else:
                    messagebox.showerror("Error","Please provide a valid length.")

            reply = messagebox.askyesno("Length confirmation",
                "You selected {} as the origin coordinate. Is this correct?".format(coord)
                )

        return coord,reforiginX,reforiginY
    def getReferenceLength(self,index):
        '''
        Get the reference length in the requested direction

        USAGE: factor = getReferenceLength(index)
        index = 0 for x-direction or 1 for y-direction
        '''

        # define a 'direction' string
        direction = 'x' if index == 0 else 'y'

        # get the reference length
        reply = False
        while not reply:
            messagebox.showinfo("Select reference length",
                "Use the mouse to select the reference length in {:s} direction.".format(direction) +
                "Click the start and the end of the reference length."
                )
            coord = plt.ginput(
                2,
                timeout=0,
                show_clicks=True
                ) # capture only two points
            # ask for a valid length
            validLength = False
            while not validLength:
                reflength = simpledialog.askfloat("Enter reference length",
                    "Enter the reference length in {:s} direction".format(direction))
                if isinstance(reflength, float):
                    validLength = True
                else:
                    messagebox.showerror("Error","Please provide a valid length.")

            # calculate scaling factor
            deltaref=coord[1][index]-coord[0][index]
            factor=reflength/deltaref

            reply = messagebox.askyesno("Length confirmation",
                "You selected {:4.0f} pixels in {:s} direction corresponding to {:4.4f} units. Is this correct?".format(deltaref, direction, reflength)
                )

        return factor
    
CPD()    
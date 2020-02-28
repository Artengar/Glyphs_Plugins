#MenuTitle: Rhythm Conductor
# -*- coding: utf-8 -*-
__doc__="""
The Rhythm Conductor analyses the letterforms and determines the position of the typeface's rhythm based on the position of the largerst amount of the letters' black mass.
Consult the Glyphs manual for information about the installation of scripts. Contact Artengar on GitHub for changes to the code.
"""
#Programmed by Maarten Renckens and Thom Janssen. Version 2.1, dating 28 February 2020.
#CreativeCommons: Attribution-NonCommercial-NoDerivs (CC BY-NC-ND)
##That means: it is allowed to download this work and share them with others, with the restrictions that the work is correctly credited. The work cann't be changed in any way or use them commercially without permission first.
##Use the credits: RENCKENS, M.; & Janssen, T. (2020). Rhythm Conductor [Application].

#TODO: now it works with the open master. It should work for all selected masters or so.
#TODO: check if the input in EditTexts are decimals, and do not contain commas!


################################################# STRUCTURE #################################################
##### The general variables                                                                             #####
##### Subfunctions for this script                                                                      #####
#####     GetBlackMass()    #Analyse the letter for the black mass and output that                      #####
#####     CreateWorkingFile()    #Create a duplicate file                                               #####
#####     NewFile()   #Create a duplicate file                                                          #####
#####     DrawBlackMass()    #Draw the black mass of the letter                                         #####
#####     getStrokeThicknessLowercase()    #Get the stroke width of the letter 'i'                      #####
#####     getStrokeThicknessUppercase()    #Get the stroke width of the letter 'I'                      #####
##### Show the Windows                                                                                  #####
##### Activator                                                                                         #####
#############################################################################################################










############################################# General Variables #############################################
try:
    import GlyphsApp
    import vanilla
    from vanilla import *
    import math
except Exception:
    Message("Missing Modules", "There are python modulles missing. Go to the menu Glyphs -> Preferences -> latest tab and click on Modules -> Install Modules. Then, restart Glyphs.", OKButton=None)
#Default variables
debug = Glyphs.defaults["com.Artengar.RhythmConductor.debug"]
if debug==True: print "<<<The debug mode of the Rhythm Conductor is on.>>>\n"
Active_Font = Glyphs.fonts[0]
InvisibleWorkingFile = ""
FileForDistribution = ""
FileForRhythm = ""
thereAreAlreadyAnalysesOpenInDistribution = False
thereAreAlreadyAnalysesOpenInRhythm = False
iStrokeThickness = 0;
IStrokeThickness = 0;
Option_list = ["Use an automatically determined stroke thickness everywhere (default)", "Use a custom stroke thickness everywhere", "Use one custom threshold", "Use the threshold values found at the automatically determined stroke width in the 'i' and 'I'"];
fontAngle = Active_Font.masters[0].italicAngle












############################################### Subfunctions ###############################################
#--------------------------------------------
#Create a duplicate file
def CreateWorkingFile():
    InvisibleWorkingFile = Active_Font.copy()
    InvisibleWorkingFile.familyName = "Working draft of %s"%InvisibleWorkingFile.familyName
    InvisibleWorkingFile.gridSubDivisions = 100#for better details
    #Erase all glyphs in the copied font
    for thisGlyph in InvisibleWorkingFile.glyphs:
        for thisLayer in thisGlyph.layers:
            thisLayer.decomposeComponents()
            thisLayer.removeOverlap()
    return InvisibleWorkingFile


#--------------------------------------------
#Create a duplicate file
def CreateEmptyFile():
    Copied_Font = Active_Font.copy()
    Copied_Font.familyName = "The black mass of %s" %Copied_Font.familyName
    Copied_Font.gridSubDivisions = 100#for better details
    #Erase all glyphs in the copied font
    Copied_Font.disableUpdateInterface()
    for thisGlyph in Copied_Font.glyphs:
        for thisLayer in thisGlyph.layers:
            for x in range(len(thisLayer.components))[::-1]:
                del(thisLayer.components[0])
            for thisPath in range(len(thisLayer.paths))[::-1]:
                del thisLayer.paths[thisPath]
    Copied_Font.enableUpdateInterface()
    return Copied_Font


#--------------------------------------------
#Check if there are already analysis done on the active file, and if so, remember that.
def CheckForExistingAnalysesInDistribution():
    if debug==True:print "Starting search for existing analyses"
    for thisFont in Glyphs.fonts:
        if thisFont.familyName == ("The black mass of " + str(Active_Font.familyName)):
            if debug==True:print "An existing analysis is found"
            return True
        else:
            return False
def CheckForExistingAnalysesInRhythm():
    if debug==True:print "Starting search for existing analyses"
    for thisFont in Glyphs.fonts:
        if thisFont.familyName == ("The rhythm of " + str(Active_Font.familyName)):
            if debug==True:print "An existing analysis is found"
            return True
        else:
            return False


#--------------------------------------------
#Get the stroke width of the letter 'i'
def getStrokeThicknessLowercase():
    try:
        if debug==True:print "Starting the function getStrokeThicknessLowercase"
        #Take the metrics and take half the x-height
        halfLowercaseHeight = Active_Font.masters[0].xHeight/2
        if debug==True:print "Half of the x-height is: %s units" %halfLowercaseHeight
        
        #Cut the 'i' at half the x-height
        intersectionLowercase =     Active_Font.glyphs["i"].layers[0].intersectionsBetweenPoints((-1000,halfLowercaseHeight),(Active_Font.glyphs["i"].layers[0].width+1000,halfLowercaseHeight), True)
        if debug==True:print "Doing an intersection in the letter i: %s" %intersectionLowercase
        if len(intersectionLowercase) == 4:
            iStrokeThickness = intersectionLowercase[2].x - intersectionLowercase[1].x
            if debug==True:print "The thickness of the i is: %s units" %iStrokeThickness
        else:
            #skipped_glyphs.append(glyph.name)
            if debug==True:print "The stroke width could not be determined:"
        
        if debug==True:print "Leaving the function getStrokeThicknessLowercase\n"
        return iStrokeThickness
    
    #If the function is not working, throw in a warning
    except Exception, ex:
        print "The stroke width could not be determined: %s" %ex
        Message("The stroke width could not be determined for the lowercase. Please select the option to manually insert values. A reason could be that the letter 'i' is not drawn, or that the design is too complex.", "Warning", OKButton=None)
        return 1


#--------------------------------------------
#Get the stroke width of the letter 'i'
def getStrokeThicknessUppercase():
    try:
        if debug==True:print "Starting the function getStrokeThicknessUppercase"
        #Take the metrics and take half the Capital height
        halfCapitalHeight = Active_Font.masters[0].capHeight/2
        if debug==True:print "Half of the capital height is: %s units"%halfCapitalHeight
        
        #Cut the 'I' at half the Capital height
        intersectionUppercase = Active_Font.glyphs["I"].layers[0].intersectionsBetweenPoints((-1000,halfCapitalHeight),(Active_Font.glyphs["I"].layers[0].width+1000,halfCapitalHeight), True)
        if debug==True:print "Doing an intersection in the letter I: %s" %intersectionUppercase
        if len(intersectionUppercase) == 4:
            IStrokeThickness = intersectionUppercase[2].x - intersectionUppercase[1].x
            if debug==True:print "The thickness of the I is: %s units" %IStrokeThickness
        else:
            #skipped_glyphs.append(glyph.name)
            if debug==True:print "The stroke width could not be determined:"
            
        if debug==True:print "Leaving the function getStrokeThicknessUppercase\n"
        return IStrokeThickness
        
    #If the function is not working, throw in a warning
    except Exception, ex:
        print "The stroke width could not be determined: %s" %ex
        Message("The stroke width could not be determined for the uppercase. Please select the option to manually insert values. A reason could be that the letter 'I' is not drawn, or that the design is too complex.", "Warning", OKButton=None)
        return 1















################################################# Windows #################################################
class run_program(object):
    def __init__(self):
        #Determine the grid on which the window will be build
        Column1 = 20
        Column2 = Column1 + 130
        windowWidth = Column2 + 135
        MarginBox=5
        #Part1: the horizontal position
        #General introduction
        RowA01 = 15
        RowA01plus = 120
        #preciseness
        RowB01 = RowA01 + RowA01plus
        RowB01plus = 50
        RowB02 = RowB01 + RowB01plus#=EditText
        RowB02plus = 20
        RowB03 = RowB02 + RowB02plus#=button
        RowB03plus = 35
        RowB04 = RowB03 + RowB03plus
        RowB04plus = 10
        #All the options for the horizontal position of the rhythm
        RowC01 = RowB04 + RowB04plus
        RowC01plus = 80
        RowC02 = RowC01 + RowC01plus#PopUpButton
        RowC02plus = 30
        RowC03 = RowC02 + RowC02plus#Box
        RowC03plus = 140
        #the options
        Box01 = 5
        Box01plus = 110
        Box02 = Box01 + Box01plus-60#=EditText
        Box02plus = 20
        Box03 = Box02 + Box02plus#=EditText
        Box03plus = 20
        #Part 2: the vertical position
        RowD01 = RowC03 + RowC03plus
        RowD01plus = 10
        RowD02 = RowD01 + RowD01plus
        RowD02plus = 90
        RowD03 = RowD02 + RowD02plus
        RowD03plus = 45
        RowD04 = RowD03 + RowD03plus
        RowD04plus = 45
        RowD05 = RowD04 + RowD04plus
        RowD05plus = 30
        RowD06 = RowD05 + RowD05plus
        RowD06plus = 45
        #All the options for the vertical height of the rhythm
        #LATER
        #Part 3: the total height
        windowHeight = RowD06 + RowD06plus
        
        
        #Get the necessary stroke thickness
        iStrokeThickness = getStrokeThicknessLowercase()
        IStrokeThickness = getStrokeThicknessUppercase()
        global debug
        if debug == True: print "Loaded stroke thickness are", iStrokeThickness, IStrokeThickness
        
        
        #Create the first window
        self.window = vanilla.FloatingWindow(
            (windowWidth, windowHeight),
            "Rhythm Conductor", #Title Bar Title
            autosaveName = "com.Artengar.RhythmConductor.mainwindow"
            )
        #General introduction
        self.window.text_1 = vanilla.TextBox( (Column1, RowA01, -Column1, RowA01plus), "The Rhythm Conductor analyses the letterforms and determines the position of the typeface's rhythm based on the position of the largest amount of the letters' black mass. This plugin provides a step-by-step guide to determine the rhythm of the active font.", sizeStyle='small')#allowing for an objective comparison of different fonts.
        #preciseness
        self.window.text_2 = vanilla.TextBox( (Column1, RowB01, -Column1, RowB01plus), "First, fill in the preciseness for the analysis. This number relates to the Em units on the x-axis. ", sizeStyle='small')
        self.window.preciseness = vanilla.EditText( (Column1, RowB02, Column2, RowB02plus), 1.0, callback=self.SavePreferences, sizeStyle = 'small')
        #The button to draw the mass
        self.window.DrawBlackMass = vanilla.Button( (Column1, RowB03, -Column1, RowB03plus), "Draw the black mass of the selected glyphs", callback=self.DrawBlackMass, sizeStyle='small')
        self.window.text_4 = vanilla.TextBox( (Column1, RowB04, -Column1, RowB04plus), "", sizeStyle='small')
        #All the options for the horizontal position of the rhythm
        self.window.text_5 = vanilla.TextBox( (Column1, RowC01, -Column1, RowC01plus), "There are four ways to extract the horizontal position of the rhythm based on the black mass. Select the desired option. All options automatically rely on the Italic Angle if defined.", sizeStyle='small')
        self.window.Change_options = vanilla.PopUpButton( (Column1, RowC02, -Column1, RowC02plus), Option_list, sizeStyle='small', callback=self.Change_Options)
        
        
        ###Option1
        self.window.box1 = vanilla.Box( (Column1, RowC03, -Column1, RowC03plus) )
        self.window.box1.text_6 = vanilla.TextBox( (MarginBox, Box01, -MarginBox, Box01plus), "Use the automatically determined\nstroke widths of " + str(iStrokeThickness) + " units for\nthe lowercase and " + str(IStrokeThickness) + " units\nfor the uppercase to cut off the black mass.", sizeStyle='small')
        ###Option2
        self.window.box2 = vanilla.Box( (Column1, RowC03, -Column1, RowC03plus) )
        self.window.box2.show(False)
        self.window.box2.text_7 = vanilla.TextBox( (MarginBox, Box01, -MarginBox, Box01plus), "Fill in the custom stroke widths:", sizeStyle='small')
        self.window.box2.text_8 = vanilla.TextBox( (MarginBox, Box02, -MarginBox, Box02plus), "For the lowercase:", sizeStyle='small')
        self.window.box2.customLowercase = vanilla.EditText( (Column2, Box02, -Column1, Box02plus), 50.0, callback=self.SavePreferences, sizeStyle = 'small')
        self.window.box2.text_9 = vanilla.TextBox( (MarginBox, Box03, -MarginBox, Box03plus), "For the uppercase:", sizeStyle='small')
        self.window.box2.customUppercase = vanilla.EditText( (Column2, Box03, -Column1, Box03plus), 60.0, callback=self.SavePreferences, sizeStyle = 'small')
        ###Option3
        self.window.box3 = vanilla.Box( (Column1, RowC03, -Column1, RowC03plus) )
        self.window.box3.show(False)
        self.window.box3.text_10 = vanilla.TextBox( (MarginBox, Box01, -MarginBox, Box01plus), "Fill in the threshold on which the black mass will be cut off:", sizeStyle='small')
        self.window.box3.text_11 = vanilla.TextBox( (MarginBox, Box02, -MarginBox, Box02plus), "From the baseline:", sizeStyle='small')
        self.window.box3.customThreshold = vanilla.EditText( (Column2, Box02, -Column1, Box02plus), 50.0, callback=self.SavePreferences, sizeStyle = 'small')
        ###Option4
        self.window.box4 = vanilla.Box( (Column1, RowC03, -Column1, RowC03plus) )
        self.window.box4.show(False)
        self.window.box4.text_12 = vanilla.TextBox( (MarginBox, Box01, -MarginBox, Box01plus), "The automatically determined\nstroke widths of " + str(iStrokeThickness) + " units for\nthe lowercase and " + str(IStrokeThickness) + " units\nfor the uppercase will be used to determine thresholds. Two separate thresholds will be applied for lowercase and uppercase letters.", sizeStyle='small')
        
        
        self.window.text_13 = vanilla.TextBox( (Column1, RowD01, -Column1, RowD01plus), "", sizeStyle='small')
        self.window.text_14 = vanilla.TextBox( (Column1, RowD02, -Column1, RowD02plus), "Please note that if the custom values are too small or too large, the drawings will be incorrect, possibly not showing any rhythm at all. To update the automatically determined stroke thickness, restart the plugin.", sizeStyle='small')
        self.window.DrawRhythm = vanilla.Button( (Column1, RowD03, -Column1, RowD03plus), "Draw the rhythm of the selected glyphs", callback=self.DrawRhythm, sizeStyle='small')
        self.window.mergeFiles = vanilla.CheckBox( (Column1, RowD04, -Column1, RowD04plus), "Merge analyses in one file.\nSelect different letters to combine different analysis together", callback=self.SavePreferences, sizeStyle='small')
        self.window.closeWindowOnFinish = vanilla.CheckBox( (Column1, RowD05, -Column1, RowD05plus), "Close this window on finish", callback=self.SavePreferences, sizeStyle='small' )
        self.window.debug = vanilla.CheckBox( (Column1, RowD06, -Column1, RowD06plus), "Export a log to the console\n(Can require a restart of the plugin)", callback=self.SavePreferences, sizeStyle='small' )

        #All the options for the vertical height of the rhythm
        #RadioGroup
        
        #Render the window
        self.LoadPreferences()
        self.window.open()
        self.window.makeKey()
    
    #Save the prefs
    def SavePreferences(self, sender):
        try:
            Glyphs.defaults["com.Artengar.RhythmConductor.preciseness"] = self.window.preciseness.get()
            Glyphs.defaults["com.Artengar.RhythmConductor.Change_options"] = self.window.Change_options.get()
            Glyphs.defaults["com.Artengar.RhythmConductor.box2.customLowercase"] = self.window.box2.customLowercase.get()
            Glyphs.defaults["com.Artengar.RhythmConductor.box2.customUppercase"] = self.window.box2.customUppercase.get()
            Glyphs.defaults["com.Artengar.RhythmConductor.box3.customThreshold"] = self.window.box3.customThreshold.get()
            Glyphs.defaults["com.Artengar.RhythmConductor.mergeFiles"] = self.window.mergeFiles.get()
            Glyphs.defaults["com.Artengar.RhythmConductor.closeWindowOnFinish"] = self.window.closeWindowOnFinish.get()
            Glyphs.defaults["com.Artengar.RhythmConductor.debug"] = self.window.debug.get()
            if debug==True:print "Preferences saved"
            return True
        except Exception, ex:
            print "Could not save prefs: %s" %ex
            return False
    
    #Search for existing prefs:
    def LoadPreferences(self):
        try:
            NSUserDefaults.standardUserDefaults().registerDefaults_(
                {
                    "com.Artengar.RhythmConductor.preciseness": 1.0,
                    "com.Artengar.RhythmConductor.Change_options": 0,
                    "com.Artengar.RhythmConductor.box2.customLowercase": 20,
                    "com.Artengar.RhythmConductor.box2.customUppercase": 20,
                    "com.Artengar.RhythmConductor.box3.customThreshold": 0,
                    "com.Artengar.RhythmConductor.mergeFiles": True,
                    "com.Artengar.RhythmConductor.closeWindowOnFinish": True,
                    "com.Artengar.RhythmConductor.debug": False
                }
            )
            self.window.preciseness.set(Glyphs.defaults["com.Artengar.RhythmConductor.preciseness"])
            self.window.Change_options.set(Glyphs.defaults["com.Artengar.RhythmConductor.Change_options"])
            self.window.box2.customLowercase.set(Glyphs.defaults["com.Artengar.RhythmConductor.box2.customLowercase"])
            self.window.box2.customUppercase.set(Glyphs.defaults["com.Artengar.RhythmConductor.box2.customUppercase"])
            self.window.box3.customThreshold.set(Glyphs.defaults["com.Artengar.RhythmConductor.box3.customThreshold"])
            self.window.mergeFiles.set(Glyphs.defaults["com.Artengar.RhythmConductor.mergeFiles"])
            self.window.closeWindowOnFinish.set(Glyphs.defaults["com.Artengar.RhythmConductor.closeWindowOnFinish"])
            self.window.debug.set(Glyphs.defaults["com.Artengar.RhythmConductor.debug"])
            
            debug = Glyphs.defaults["com.Artengar.RhythmConductor.debug"]
            if debug==True:print "Preferences loaded"
            return True
        except Exception, ex:
            print "Could not load prefs: %s" %ex
            return False
    
    def Change_Options(self, sender):
        if debug==True:print "PopUpButton edit!", sender.get()
        try:
            option = self.window.Change_options.getItems()[self.window.Change_options.get()]
        except:
            print "Could not determine the option... Shape is:", shape
            return False
        try:
            #Determine which options should be visible (overwrites the previous instructions)
            if option == "Use an automatically determined stroke thickness everywhere (default)":
                self.window.box1.show(True)
                self.window.box2.show(False)
                self.window.box3.show(False)
                self.window.box4.show(False)
            elif option == "Use a custom stroke thickness everywhere":
                self.window.box1.show(False)
                self.window.box2.show(True)
                self.window.box3.show(False)
                self.window.box4.show(False)
            elif option == "Use one custom threshold":
                self.window.box1.show(False)
                self.window.box2.show(False)
                self.window.box3.show(True)
                self.window.box4.show(False)
            elif option == "Use the threshold values found at the automatically determined stroke width in the 'i' and 'I'":
                self.window.box1.show(False)
                self.window.box2.show(False)
                self.window.box3.show(False)
                self.window.box4.show(True)
        except Exception, ex:
            print "Error in determining the corresponding options: %s"%ex
            return False
        return

    def DrawBlackMass(self, sender):
        try:
            font.disableUpdateInterface()
            originalGridSubDivisions = Active_Font.gridSubDivisions#Backup for later
            Active_Font.gridSubDivisions = 100#for better details
            debug = self.window.debug.get()
            #############################
            Message("This function is not implemented yet.")
            #############################
            Active_Font.gridSubDivisions = originalGridSubDivisions#Back to the default
            font.enableUpdateInterface()
            if Glyphs.defaults["com.Artengar.RhythmConductor.closeWindowOnFinish"] == True:
                self.window.close()
            Message("Finished")
        except Exception, ex:
            print "Error while drawing the black mass: %s"%ex
            return False
        
    def DrawRhythm(self, sender):
        try:
            font.disableUpdateInterface()
            originalGridSubDivisions = Active_Font.gridSubDivisions#Backup for later
            Active_Font.gridSubDivisions = 100#for better details
            debug = self.window.debug.get()
            #############################
            Message("This function is not implemented yet.")
            #############################
            Active_Font.gridSubDivisions = originalGridSubDivisions#Back to the default
            font.enableUpdateInterface()
            if Glyphs.defaults["com.Artengar.RhythmConductor.closeWindowOnFinish"] == True:
                self.window.close()
        except Exception, ex:
            print "Error while drawing the rhythm: "%ex
            return False
















################################################# Activator #################################################
#Let the script do its work:
if len(Glyphs.fonts) <=0:
    Message("No open fonts", "There are no fonts open. The Rhythm Conductor can't do his work.", OKButton=None)
else:
    Glyphs.clearLog()
    if debug==True: Glyphs.showMacroWindow()
    run_program()
    font = Glyphs.font



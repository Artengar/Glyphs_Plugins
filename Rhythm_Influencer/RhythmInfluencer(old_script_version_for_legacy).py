#MenuTitle: Rhythm Influencer
# -*- coding: utf-8 -*-
__doc__="""
The Rhythm Influencer analyses the letterforms and determines the position of the typeface's rhythm based on the position of the largerst amount of the letters' black mass.
Consult the Glyphs manual for information about the installation of scripts. Contact Artengar on GitHub for changes to the code.
"""
#Programmed by Maarten Renckens. Version 2.3, dating 2020 May 19.
#CreativeCommons: Attribution-NonCommercial-NoDerivs (CC BY-NC-ND)
##That means: it is allowed to download this work and share it with others, with the restrictions that the work is correctly credited. The work cann't be changed in any way or use them commercially without permission first.
##Use the credits: RENCKENS, M. (2020). Rhythm Influencer 2 [Application] https://github.com/Artengar/Glyphs_Plugins/tree/master/Rhythm_Influencer_2.

#TODO: now it works with the open master. It should work for all selected masters or so.
#TODO: check if the input in EditTexts are decimals, and do not contain commas!
#TODO: add a message "Please wait while the Rhythm Influencer is analysing your font. Depending on the amount of selected letters, and due to possible complex letter shapes, this can take a couple of minutes. Meanwhile, we would like to notify you that even through this plugin went through a lot of quality tests, it is provided 'as-is.' Always check the output on quality."
#fontAngle = Active_Font.masters[0].italicAngle











############################################# General Variables #############################################
try:
    import GlyphsApp
    import vanilla
    from vanilla import *
    import math
except Exception:
    Message("Missing Modules", "There are python modules missing. Go to the menu Glyphs -> Preferences -> latest tab and click on Modules -> Install Modules. Then, restart Glyphs.", OKButton=None)
#Default variables
debug = Glyphs.defaults["com.Artengar.RhythmInfluencer.debug"]
if debug==True: print "<<<The debug mode of the Rhythm Influencer is on.>>>\n"
Active_Font = ""
InvisibleWorkingFile = ""
FileForDistribution = ""
FileForRhythm = ""
FileForScaling = ""
thereAreAlreadyAnalysesOpenInDistribution = False
thereAreAlreadyAnalysesOpenInRhythm = False
Option_list = ["Use an automatically determined stroke thickness everywhere (default)", "Use two custom stroke thicknesses"];#REMOVED: "Use one custom threshold", "Use the threshold values found at the automatically determined stroke width in the 'i' and 'I'"















############################################### File Handling ###############################################
#--------------------------------------------
#Create a duplicate file
def CreateWorkingFile(Active_Font):
    InvisibleWorkingFile = Active_Font.copy()
    InvisibleWorkingFile.familyName = "Working draft of %s"%InvisibleWorkingFile.familyName
    #Erase all glyphs in the copied font
    for thisGlyph in InvisibleWorkingFile.glyphs:
        for thisLayer in thisGlyph.layers:
            thisLayer.decomposeComponents()
            thisLayer.removeOverlap()
            for hint in reversed( range( len(thisLayer.hints) )):
                del thisLayer.hints[hint]
            
    return InvisibleWorkingFile


#--------------------------------------------
#Create a duplicate file
def CreateGraphFile(Active_Font):
    FileForDistribution = Active_Font.copy()
    FileForDistribution.familyName = "The horizontal black mass distribution of %s" %Active_Font.familyName
    #Erase all glyphs in the copied font
    FileForDistribution.disableUpdateInterface()
    for thisGlyph in FileForDistribution.glyphs:
        for thisLayer in thisGlyph.layers:
            for x in range(len(thisLayer.components))[::-1]:
                del(thisLayer.components[0])
            for thisPath in range(len(thisLayer.paths))[::-1]:
                del thisLayer.paths[thisPath]
            for hint in reversed( range( len(thisLayer.hints) )):
                del thisLayer.hints[hint]
    FileForDistribution.enableUpdateInterface()
    return FileForDistribution


#--------------------------------------------
#Create a duplicate file
def CreateRhythmFile(Active_Font):
    FileForRhythm = Active_Font.copy()
    FileForRhythm.familyName = "The rhythm of %s" %Active_Font.familyName
    #Erase all glyphs in the copied font
    FileForRhythm.disableUpdateInterface()
    for thisGlyph in FileForRhythm.glyphs:
        for thisLayer in thisGlyph.layers:
            for x in range(len(thisLayer.components))[::-1]:
                del(thisLayer.components[0])
            for thisPath in range(len(thisLayer.paths))[::-1]:
                del thisLayer.paths[thisPath]
            for hint in reversed( range( len(thisLayer.hints) )):
                del thisLayer.hints[hint]
    FileForRhythm.enableUpdateInterface()
    return FileForRhythm


#--------------------------------------------
#Create a duplicate file
def CreateScaledFile(Active_Font):
    #This function is based on Maarten Renckens' script 'Extract Master'
    FileForScaling = Active_Font.copy()
    FileForScaling.familyName = "Extracted master from %s" %Active_Font.familyName
    #Erase all other masters in the copied font
    FileForScaling.disableUpdateInterface()
    
    #Delete masters
    toKeep = FileForScaling.masters[0].id
    numberOfMasters = len(FileForScaling.masters)
    for i in range( numberOfMasters )[::-1]:
        if FileForScaling.masters[i].id != toKeep:
            del FileForScaling.masters[i]
    #Delete all Layers in the remaining Master (this is based on Mekkablue's script)
    searchTerms = [ "[]", "{}" ]
    for thisGlyph in FileForScaling.glyphs:
        numberOfLayers = len( thisGlyph.layers )
        thisGlyphName = thisGlyph.name

        if str(thisGlyphName)[:7] != "_smart.":
            thisGlyph.beginUndo()
            for i in range( numberOfLayers )[::-1]:
                thisLayer = thisGlyph.layers[i]
                if thisLayer.layerId != thisLayer.associatedMasterId: # not the master layer
                    thisLayerName = thisLayer.name
                    thisLayerShouldBeRemoved = True
                    if thisLayerName: # always delete unnamed layers
                        for parentheses in searchTerms:
                            opening = parentheses[0]
                            closing = parentheses[1]
                            
                            # check if ONE of them is at the END of the layer name, like:
                            # Bold [160], Bold [160[, Bold ]160], Regular {120}
                            if thisLayerName.endswith(opening) or thisLayerName.endswith(closing):
                                thisLayerShouldBeRemoved = False
                                
                    if thisLayerShouldBeRemoved:
                        del thisGlyph.layers[i]
            thisGlyph.endUndo()
        
    FileForScaling.enableUpdateInterface()
    return FileForScaling



















############################################### Subfunctions ###############################################

#--------------------------------------------
#Get the stroke width of the letter 'i'
def getStrokeThicknessLowercase(debug, Active_Font):
    try:
        if debug==True:print "Starting the function getStrokeThicknessLowercase"
        #Take the metrics and take half the x-height
        halfLowercaseHeight = Active_Font.masters[0].xHeight/2
        
        #Cut the 'i' at half the x-height
        intersectionLowercase =     Active_Font.glyphs["i"].layers[0].intersectionsBetweenPoints((-1000,halfLowercaseHeight),(Active_Font.glyphs["i"].layers[0].width+1000,halfLowercaseHeight), True)
        if len(intersectionLowercase) == 4:
            iStrokeThickness = intersectionLowercase[2].x - intersectionLowercase[1].x
            if debug==True:print "The thickness of the i is: %s units" %iStrokeThickness
        else:
            if debug==True:print "The stroke width could not be determined."
        return iStrokeThickness
    
    #If the function is not working, throw in a warning
    except Exception, ex:
        print "The stroke width could not be determined: %s" %ex
        Message("The stroke width could not be determined for the lowercase. Please check if the right font is active, or manually insert values. A reason could be that the letter 'i' is not drawn, or that the design is too complex.", "Warning", OKButton=None)
        return 50 #provide some value to work with


#--------------------------------------------
#Get the stroke width of the letter 'i'
def getStrokeThicknessUppercase(debug, Active_Font):
    try:
        if debug==True:print "Starting the function getStrokeThicknessUppercase"
        #Take the metrics and take half the Capital height
        halfCapitalHeight = Active_Font.masters[0].capHeight/2
        
        #Cut the 'I' at half the Capital height
        intersectionUppercase = Active_Font.glyphs["I"].layers[0].intersectionsBetweenPoints((-1000,halfCapitalHeight),(Active_Font.glyphs["I"].layers[0].width+1000,halfCapitalHeight), True)
        if len(intersectionUppercase) == 4:
            IStrokeThickness = intersectionUppercase[2].x - intersectionUppercase[1].x
            if debug==True:print "The thickness of the I is: %s units" %IStrokeThickness
        else:
            #skipped_glyphs.append(glyph.name)
            if debug==True:print "The stroke width could not be determined."
        return IStrokeThickness
        
    #If the function is not working, throw in a warning
    except Exception, ex:
        print "The stroke width could not be determined: %s" %ex
        Message("The stroke width could not be determined for the uppercase. Please check if the right font is active, or manually insert values. A reason could be that the letter 'I' is not drawn, or that the design is too complex.", "Warning", OKButton=None)
        return 50 #provide some value to work with






















############################################### Distribution ###############################################

#--------------------------------------------
#Analyse the letter for the black mass and enlist that
def DetermineBlackMass(debug, preciseness, thisLayer, InvisibleWorkingFile, FileForDistribution):
    try:
        if debug==True:print "Starting the function DetermineBlackMass on the glyph '%s'" %thisLayer.parent.name
        activeGlyphName = thisLayer.parent.name
        ActiveLayer = InvisibleWorkingFile.glyphs[activeGlyphName].layers[thisLayer.name]
        #Analyse the glyphs vertically per horizontally defined preciseness
        Xprogress = -1000#this value to start counting from before [0,0]
        #Prepare an empty path
        listOfIntersectionPointsXThisGlyph = []
        #remember in the analysis if a mass was detected, a glyphs can contain multiple shapes
        partOfEarlierDetectedMass = False

        ########Make a list of all intersections:
        while Xprogress <= ActiveLayer.width+1000:#count till way behind the glyphs width.
            #draw an intersection from bottom to top
            intersection = ActiveLayer.intersectionsBetweenPoints((Xprogress,-1500),(Xprogress,+2500), True)
            
            #only perform an action if a black mass was detected:
            if len(intersection) > 2:
                #If no previous mass was detected, create a starting point:
                if partOfEarlierDetectedMass == False:
                    listOfIntersectionPointsXThisGlyph += [[Xprogress, 0]]
                #from this point on, make sure that it connects to the earlier black mass:
                partOfEarlierDetectedMass = True
                #prepare variables for annotating the black mass:
                totalHeightBlackMass=0
                CurrentIntersectionPoint=2#Start with the third intersection
                #for each two intersections, count the length of the intersection in the black mass. ##############in a triangle, it provides an error!
                while CurrentIntersectionPoint <= len(intersection)-2:
                    #But only count if it effectively is a part of the letter: do not count counters,...
                    if InvisibleWorkingFile.glyphs[activeGlyphName].layers[thisLayer.name].completeBezierPath.containsPoint_((Xprogress, float(intersection[CurrentIntersectionPoint-1].y)+0.03)):
                        totalHeightBlackMass += intersection[CurrentIntersectionPoint].y - intersection[CurrentIntersectionPoint-1].y
                    CurrentIntersectionPoint+=1
                #add this value to the list, as part of the later graph:
                Node = [[Xprogress, totalHeightBlackMass]]
                listOfIntersectionPointsXThisGlyph += Node
            
            #if no intersection was found, it could mean that there are multiple shapes. Close the previous path.
            elif len(intersection) == 2:
                if partOfEarlierDetectedMass == True:
                    Node = [[Xprogress-preciseness, 0]]
                    listOfIntersectionPointsXThisGlyph += Node
                    listOfIntersectionPointsXThisGlyph += ["CLOSE PATH"]
                    partOfEarlierDetectedMass = False
            
            Xprogress += preciseness#till the width of the glyphs is analysed
        #if a log is requested, print the data
        if debug==True:
            print "for the glyph '%s' was the following data found:" %activeGlyphName
            for item in listOfIntersectionPointsXThisGlyph:
                print item
        return listOfIntersectionPointsXThisGlyph
    except Exception, ex:
        print "The black mass could not be determined: %s" %ex


#--------------------------------------------
#Draw the black mass of the letter
def DrawBlackMass(debug, mass, thisLayer, InvisibleWorkingFile, FileForDistribution):
    try:
        activeGlyphName = thisLayer.parent.name
        if debug==True:print "Starting the function DrawBlackMass for the glyph '%s'" %activeGlyphName
        Path = GSPath()
        heightPosition = ""#To remember the previous y-height, in order to possibly skip unnecessary nodes
        
        #Analyse the incoming data
        for Data in mass:
            #Detect when to close paths, possibly drawing separate paths
            if Data == "CLOSE PATH":
                Path.closed = True
                Path.reverse()#otherwise it contains a white fill
                FileForDistribution.glyphs[activeGlyphName].layers[0].paths.append(Path)
                #reset info
                Path = GSPath()
                heightPosition = ""
            else:
                NodeToAdd = GSNode()
                NodeToAdd.position = (Data[0], Data[1])
                heightPosition = Data[1]
                Path.nodes.append(NodeToAdd)
    except Exception, ex:
        print "The black mass could not be drawn: %s" %ex
















############################################### Rhythm ###############################################

#--------------------------------------------
#determine the position of the rhythm
def calculateRhythm(debug, FileForDistribution, FileForRhythm, thisLayer, preciseness):
    try:
        if debug==True:print "Starting the function calculateRhythm"
        activeGlyphName = thisLayer.parent.name
        ActiveLayer = FileForDistribution.glyphs[activeGlyphName].layers[thisLayer.name]
        buffermin = 0
        buffermax = 0
        desiredStrokeThickness = 0
        
        #provide a different desiredStrokeThickness for upper/lowercase
        if activeGlyphName[0].isupper():
            desiredStrokeThickness = Glyphs.defaults["com.Artengar.RhythmInfluencer.IStrokeThickness"]
        else:
            desiredStrokeThickness = Glyphs.defaults["com.Artengar.RhythmInfluencer.iStrokeThickness"]
        
        Xprogress = -1000#this value to start counting from before [0,0]
        currentlyAnalysingMass = False
        wasFalling = False
        FirstXvalueToFindMass = 0
        encounteredPeaks = []
        lastLowestPeak = 0
        LastHighestPeak = 0
        LastValue = 0
        #Analyse the glyphs vertically per horizontally defined preciseness
        Yprogess = 2000#this value to start counting from enough range
        #Prepare an empty path
        listOfRhythmPositions = []



        #Make a list of all intersections:
        #Memory hack!: first go through x-values and determine peak positions, as an analysis through y-values took too much memory
        
        #remember in the analysis if a mass was detected, a glyphs can contain multiple shapes
        partOfEarlierDetectedMass = False

        #Make a list of all intersections:
        while Xprogress <= ActiveLayer.width+1000:#count till way behind the glyphs width.
            #draw an intersection from bottom to top
            intersection = ActiveLayer.intersectionsBetweenPoints((Xprogress,-1500),(Xprogress,+2500), True)
            
            #only perform an action if a black mass was detected:
            if len(intersection) > 2:
                #Set the begin for the current range
                if currentlyAnalysingMass == False:
                    currentlyAnalysingMass = True
                    FirstXvalueToFindMass = Xprogress
                elif currentlyAnalysingMass == True:
                    #Case: raising graph
                    if intersection[len(intersection)-2].y >= LastValue and wasFalling == False:
                        if debug==True:print "case1, %s"%LastValue
                        LastValue = intersection[len(intersection)-2].y
                        LastHighestPeak = intersection[len(intersection)-2].y
                    #Case: falling graph
                    elif intersection[len(intersection)-2].y < LastValue:
                        if debug==True:print "case2, %s"%LastValue
                        LastValue = intersection[len(intersection)-2].y
                        wasFalling = True
                        lowestFalling = intersection[len(intersection)-2].y
                        latestFallingPoint = Xprogress
                    #Case: raising graph, setting breakpoint after falling BUT ONLY if raising more than 15! to catch irregularities.
                    elif intersection[len(intersection)-2].y >= LastValue and wasFalling == True:
                        if debug==True:print "case3, %s"%LastValue
                        LastValue = intersection[len(intersection)-2].y
                        #For going higher again with more than 15 units
                        if intersection[len(intersection)-2].y >= lowestFalling+15:
                            encounteredPeaks += [[FirstXvalueToFindMass, latestFallingPoint]]
                            FirstXvalueToFindMass = latestFallingPoint+preciseness
                            wasFalling = False
            elif len(intersection) == 2:
                if currentlyAnalysingMass == True:
                    encounteredPeaks += [[FirstXvalueToFindMass, Xprogress-preciseness]]
                currentlyAnalysingMass = False
                wasFalling = False
                LastValue = 0
            Xprogress += preciseness#till the width of the glyphs is analysed
        if debug==True:print "High peaks in the graphs are situated between: %s"%encounteredPeaks
        
        
        
        #Find the position of the rhythm
        found = False
        for nodes in encounteredPeaks:
            while Yprogess >= -2000 and found == False:#count till way behind the glyphs width. Start high, as there are the lowest points in the graphs
                #draw an intersection left to right
                intersection = ActiveLayer.intersectionsBetweenPoints((nodes[0],Yprogess),(nodes[1],Yprogess), True)
                #only perform an action if a black mass was detected:
                if len(intersection) > 2:
                    #Detect if there is a black mass wider than the stroke thickness:
                    item = 1
                    while item < len(intersection)-2:
                        if float(intersection[item+1].x) - float(intersection[item].x) >= desiredStrokeThickness:
                            #And check if this is also part of the letter (thus black)
                            if ActiveLayer.completeBezierPath.containsPoint_((float(intersection[item].x)+0.03, Yprogess)):
                                #add this value to the list, as part of the later graph:
                                Node = [[float(intersection[item].x), float(intersection[item+1].x)]]
                                listOfRhythmPositions += Node
                                found = True
                        item += 1
                Yprogess -= preciseness/2#Work more precise, to estimate the stroke width better. till the width of the glyphs is analysed
            found = False
        
            
        #if a log is requested, print the data
        if debug==True:
            print "for the glyph '%s' was the following data found:" %activeGlyphName
            for item in listOfRhythmPositions:
                print item
        return listOfRhythmPositions
    except Exception, ex:
        print "The rhythm could not be created: %s" %ex
        return 1


#--------------------------------------------
#Create the rhythm
def DrawTheRhythm(debug, FileForDistribution, FileForRhythm, thisLayer, listOfRhythmPositions):
    try:
        if debug==True:print "Starting the function DrawTheRhythm"
        activeGlyphName = thisLayer.parent.name
        ActiveLayer = FileForRhythm.glyphs[activeGlyphName].layers[thisLayer.name]
        
        for nodes in listOfRhythmPositions:
            StrokeOfRhythm = GSPath()
            StrokeCoordinates = [
                [ nodes[0], 0 ],
                [ nodes[1], 0 ],
                [ nodes[1], FileForRhythm.masters[0].xHeight ],
                [ nodes[0], FileForRhythm.masters[0].xHeight ]
            ]
            
            for thisPoint in StrokeCoordinates:
                newNode = GSNode()
                newNode.type = GSLINE
                newNode.position = ( thisPoint[0], thisPoint[1] )
                StrokeOfRhythm.nodes.append( newNode )
            StrokeOfRhythm.closed = True
            
            ActiveLayer.paths.append(StrokeOfRhythm)
            #The determined rectangle is placed in the previous function.
    except Exception, ex:
        print "The rhythm could not be created: %s" %ex
        return 1














############################################### Scale ###############################################
def scaling(debug, Active_Font, FileForScaling, listOfRhythmPositions, thisLayer):
    #!!!!!! to add: something for empty glyphs
    try:
        if debug==True:print "Starting the function scaling"
        activeGlyphName = thisLayer.parent.name
        ActiveLayer = FileForScaling.glyphs[activeGlyphName].layers[thisLayer.name]
        customScale = float(Glyphs.defaults["com.Artengar.RhythmInfluencer.customScale"])/100
        customStrokeScale = float(Glyphs.defaults["com.Artengar.RhythmInfluencer.customStrokeScale"])/100
        customSideBearingsScale = float(Glyphs.defaults["com.Artengar.RhythmInfluencer.SideBearingsScale"])/100
        #remember some data
        existingLSB = ActiveLayer.LSB
        existingRSB = ActiveLayer.RSB
        #Create the different zones within the letter #This will be a list [[X,Z]], in which X is the horizontal coordinate and Z the scale for the that distance
        zonesNegative = []
        zonesPositive = []
        currentList = []
        #handle negative sidebearings
        if existingLSB < 0:
            #if the rhythm does not immediately start while there is a negative SB
            if existingLSB != listOfRhythmPositions[0][0]:
                zonesNegative += [[existingLSB, customScale]]
            #add all other negative zones
            for RhythmBoundary in listOfRhythmPositions:
                if RhythmBoundary[0] < 0:
                    zonesNegative += [[RhythmBoundary[0], customStrokeScale]]
                if RhythmBoundary[1] < 0:
                    zonesNegative += [[RhythmBoundary[1], customScale]]
            print(zonesNegative)
        #handle positive sidebearings
        elif existingLSB > 0 and existingLSB != 0:
            zonesPositive += [[existingLSB, customSideBearingsScale]]
        #handle all other positive zones
        for RhythmBoundary in listOfRhythmPositions:
            if RhythmBoundary[0] > 0:
                #it could be that the LSB ends at the rhythm, so some extra tests are necessary
                if zonesNegative != []:
                    if RhythmBoundary[0] != (zonesNegative[len(zonesNegative)-1][0]):
                        zonesPositive += [[RhythmBoundary[0], customScale]]
                elif zonesPositive != []:
                    if RhythmBoundary[0] != (zonesPositive[len(zonesPositive)-1][0]):
                        zonesPositive += [[RhythmBoundary[0], customScale]]
            if RhythmBoundary[1] > 0:
                zonesPositive += [[RhythmBoundary[1], customStrokeScale]]
        #Add the zone between the latest stroke and the RSB
        if (zonesPositive[len(zonesPositive)-1][0]) < (ActiveLayer.width - existingRSB):
            zonesPositive += [[(ActiveLayer.width-existingRSB), customScale]]
        print(zonesPositive)
        zonesNegative.reverse() #reverse makes it easier to work with both lists in the same way later on
        #the RSB comes later, it does not need to be in the list.
        
        #re-position every x-value of nodes, anchors, and origins of components (scale)
        for thisPath in ActiveLayer.paths:
            currentList = [] #the zonesNegative or zonesPositive to work with
            for thisNode in thisPath.nodes:
                print("XXXXX")
                currentXValue = thisNode.x
                newXValue = 0
                lastPassedZone = 0
                newXValueFound = False
                #for negative nodes
                if currentXValue <0:
                    currentList = zonesNegative
                    for zone in currentList:
                        #block the iteration when the new newXValue is already found
                        if newXValueFound == False:
                            if zone[0] <= currentXValue:
                                if newXValue != 0:
                                    newXValue += (currentXValue + lastPassedZone) * zone[1]
                                    thisNode.x = newXValue
                                elif newXValue == 0: #if the node is close to zero and fits within one zone.
                                    newXValue += currentXValue * zone[1]
                                    thisNode.x = newXValue
                                newXValueFound = True
                                
                            elif zone[0] > currentXValue:
                                newXValue += (zone[0] - lastPassedZone) * zone[1]
                                lastPassedZone = zone[0]
                        print("newXValueFound: %s, currentXValue: %s, zone[0]: %s, zone[1]: %s, lastPassedZone: %s, newXValue: %s") %(newXValueFound, currentXValue, zone[0], zone[1], lastPassedZone, newXValue)
                    #anchors can go outside the SB. This catches those anchors.
                    if newXValueFound == False:
                        newXValue += (currentXValue + lastPassedZone) * customScale
                        print "too large"
                #for positive nodes
                elif currentXValue >0:
                    currentList = zonesPositive
                    for zone in currentList:
                        #block the iteration when the new newXValue is already found
                        if newXValueFound == False:
                            if zone[0] >= currentXValue:
                                if newXValue != 0:
                                    newXValue += (currentXValue - lastPassedZone) * zone[1]
                                    thisNode.x = newXValue
                                elif newXValue == 0: #if the node is close to zero and fits within one zone.
                                    newXValue += currentXValue * zone[1]
                                    thisNode.x = newXValue
                                newXValueFound = True
                                
                            elif zone[0] < currentXValue:
                                newXValue += (zone[0] - lastPassedZone) * zone[1]
                                lastPassedZone = zone[0]
                        print("newXValueFound: %s, currentXValue: %s, zone[0]: %s, zone[1]: %s, lastPassedZone: %s, newXValue: %s") %(newXValueFound, currentXValue, zone[0], zone[1], lastPassedZone, newXValue)
                    #anchors can go outside the SB. This catches those anchors.
                    if newXValueFound == False:
                        newXValue += (currentXValue + lastPassedZone) * customScale
                        print "too large"
        
        # + move the components/anchors
        #scale the strokes
        #scale the RSB. The LSB should already be ok by scaling the paths
        ActiveLayer.RSB = existingRSB * customSideBearingsScale
        ActiveLayer.parent.color = 5
    except Exception, ex:
        print "No new font with a different rhythm could be created: %s" %ex
        return 1

















################################################# Main function #################################################
def main_steps(makeDistribution, makeRhythm, makeScale):
    try:
        Glyphs.clearLog()
        debug = Glyphs.defaults["com.Artengar.RhythmInfluencer.debug"]
        Active_Font = resetCache()
        #############################
        if Active_Font == False:
            Message("No useful file detected. Make sure the names of the files do not start with 'Working draft of', 'The horizontal black mass distribution of', 'The rhythm of' or 'Scaled font for'.")
        elif Active_Font.selectedLayers == None:
            Message("Please, first select the glyphs which should be analysed.")
        else:
            #reset the data
            InvisibleWorkingFile = ""
            FileForDistribution = ""
            FileForRhythm = ""
            FileForScaling = ""
            #set a higer grid for better details
            originalGridSubDivisions = Active_Font.gridSubDivisions#Backup for later
            Active_Font.gridSubDivisions = 100
            preciseness = float(Glyphs.defaults["com.Artengar.RhythmInfluencer.preciseness"])
            
            ##################################
            ### Create the necessary files ###
            ##################################
            
            #create a working file that does not contain unnecessary details, nor overlap in paths
            InvisibleWorkingFile = CreateWorkingFile(Active_Font)
            #create a file for the distribution of the black mass
            FileForDistribution = CreateGraphFile(Active_Font)
            #create a file for the rhythm
            if makeRhythm:
                #but only create an empty file if the user does not want to merge files
                if Glyphs.defaults["com.Artengar.RhythmInfluencer.mergeRhythmFiles"] == 0:
                    FileForRhythm = ""
                    FileForRhythm = CreateRhythmFile(Active_Font)
                #if no previous file is open, still create one:
                else:
                    exists = False
                    for font in Glyphs.fonts:
                        if font.familyName.startswith("The rhythm of"):
                            FileForRhythm = font
                            exists = True
                    if exists == False:
                        FileForRhythm = CreateRhythmFile(Active_Font)
            if makeScale:
                FileForScaling = CreateScaledFile(Active_Font)
            
            ##################################
            ###      Analyse and draw      ###
            ##################################
            
            for thisLayer in Active_Font.selectedLayers:
                Glyphs.clearLog()
                #always analyze the black mass
                mass = DetermineBlackMass(debug, preciseness, thisLayer, InvisibleWorkingFile, FileForDistribution)
                DrawBlackMass(debug, mass, thisLayer, InvisibleWorkingFile, FileForDistribution)
                #Calculate where the rhythm is positioned
                if makeRhythm or makeScale:
                    listOfRhythmPositions = calculateRhythm(debug, FileForDistribution, FileForRhythm, thisLayer, preciseness)
                    DrawTheRhythm(debug, FileForDistribution, FileForRhythm, thisLayer, listOfRhythmPositions)
                if makeScale:
                    Glyphs.clearLog()
                    scaling(debug, Active_Font, FileForScaling, listOfRhythmPositions, thisLayer)
            
            ##################################
            ###      Show the results      ###
            ##################################
            
            if makeDistribution:
                Glyphs.fonts.append(FileForDistribution)
            if makeRhythm:
                Glyphs.fonts.append(FileForRhythm)
            if makeScale:
                Glyphs.fonts.append(FileForScaling)
                FileForScaling.gridSubDivisions = originalGridSubDivisions
            #set the grid back to the default
            Active_Font.gridSubDivisions = originalGridSubDivisions
    except Exception, ex:
        print "Error while running the function: %s"%ex
        return False



















################################################# Windows #################################################
class run_program(object):
    def __init__(self):
        #Determine the grid on which the window will be build
        Column1 = 20
        Column2 = Column1 + 280
        windowWidth = Column2 + 75
        MarginBox=5
        #Part1: the horizontal position
        #General introduction
        RowA01 = 15
        RowA01plus = 50
        #preciseness
        RowB01 = RowA01 + RowA01plus
        RowB01plus = 30
        RowB02 = RowB01 + RowB01plus#=EditText
        RowB02plus = 20
        RowB02B = RowB02 + RowB02plus+15#Added text
        RowB02Bplus = 30
        RowB03 = RowB02B + RowB02Bplus#=button
        RowB03plus = 30
        RowB04 = RowB03 + RowB03plus
        RowB04plus = 20
        #All the options for the horizontal position of the rhythm
        RowC01 = RowB04 + RowB04plus
        RowC01plus = 50
        RowC02 = RowC01 + RowC01plus#PopUpButton
        RowC02plus = 30
        RowC03 = RowC02 + RowC02plus#Box
        RowC03plus = 100
        #the options
        Box01 = 5
        Box01plus = 80#the box
        Box02 = Box01 + Box01plus-60#=EditText
        Box02plus = 20
        Box03 = Box02 + Box02plus#=EditText
        Box03plus = 20
        #Part 2: the vertical position
        RowD01 = RowC03 + RowC03plus
        RowD01plus = 10
        RowD02 = RowD01 + RowD01plus
        RowD02plus = 60
        RowD04 = RowD02 + RowD02plus
        RowD04plus = 55
        RowD03 = RowD04 + RowD04plus#button rhythm
        RowD03plus = 55
        #Part 3: the extra options
        RowE01 = RowD03 + RowD03plus
        RowE01plus = 35
        RowE01B = RowE01 + RowE01plus
        RowE01Bplus = 20
        RowE02 = RowE01B + RowE01Bplus
        RowE02plus = 20
        RowE03 = RowE02 + RowE02plus
        RowE03plus = 20
        RowE04 = RowE03 + RowE03plus#button
        RowE04plus = 20
        RowE05 = RowE04 + RowE04plus
        RowE05plus = 35
        RowE06 = RowE05 + RowE05plus#checkbox
        RowE06plus = 80
        RowE07 = RowE06 + RowE06plus+20
        RowE07plus = 90
        #Part 4: the extra options
        RowEX01 = RowE07 + RowE07plus
        RowEX01plus = 20
        RowEX02 = RowEX01 + RowEX01plus
        RowEX02plus = 30
        RowEX03 = RowEX02 + RowEX02plus
        RowEX03plus = 55
        #All the options for the vertical height of the rhythm
        #LATER
        #Part 3: the total height
        windowHeight = RowEX03 + RowEX03plus
        
        
        #Get the necessary stroke thickness
        Active_Font = resetCache()
        iStrokeThickness = 0;
        IStrokeThickness = 0;
        iStrokeThickness = getStrokeThicknessLowercase(debug, Active_Font)
        IStrokeThickness = getStrokeThicknessUppercase(debug, Active_Font)

        Glyphs.defaults["com.Artengar.RhythmInfluencer.iStrokeThickness"] = iStrokeThickness
        Glyphs.defaults["com.Artengar.RhythmInfluencer.IStrokeThickness"] = IStrokeThickness
        
        
        #Create the first window
        self.window = vanilla.FloatingWindow(
            (windowWidth, windowHeight),
            "Rhythm Influencer II", #Title Bar Title
            autosaveName = "com.Artengar.RhythmInfluencer.mainwindow"
            )
        #General introduction
        self.window.text_1 = vanilla.TextBox( (Column1, RowA01, -Column1, RowA01plus), "The Rhythm Influencer is a tool to analyze vertical letter strokes (the rhythm) and to create letter variations fast.", sizeStyle='small')
        #preciseness
        self.window.text_2 = vanilla.TextBox( (Column1, RowB01, -Column1, RowB01plus), "First, fill in the preciseness for the analysis. This number relates to the Em units on the x-axis. ", sizeStyle='small')
        self.window.preciseness = vanilla.EditText( (Column1, RowB02, Column2, RowB02plus), 1.0, callback=self.SavePreferences, sizeStyle = 'small')
        #The button to draw the mass
        self.window.text_3 = vanilla.TextBox( (Column1, RowB02B, -Column1, RowB02Bplus), "Second, have a look at the current distribution of the black mass.", sizeStyle='small')
        self.window.DrawBlackMass = vanilla.Button( (Column1, RowB03, -Column1, RowB03plus), "Draw the black mass of the selected glyphs", callback=self.DrawBlackMass, sizeStyle='small')
        self.window.text_4 = vanilla.TextBox( (Column1, RowB04, -Column1, RowB04plus), "", sizeStyle='small')
        #All the options for the horizontal position of the rhythm
        self.window.text_5 = vanilla.TextBox( (Column1, RowC01, -Column1, RowC01plus), "Third, there are four ways to extract the horizontal position of the rhythm based on the black mass. Select the desired option.", sizeStyle='small')
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
        self.window.text_14 = vanilla.TextBox( (Column1, RowD02, -Column1, RowD02plus), "To update the automatically determined stroke thickness, restart the plugin. Please note that if the custom values are too small or too large, the drawings will be incorrect, possibly not showing any rhythm at all.", sizeStyle='small')
        self.window.mergeRhythmFiles = vanilla.CheckBox( (Column1, RowD04, -Column1, RowD04plus), "Merge different rhythms in one file.\nSelect different letters to combine different analysis together", callback=self.SavePreferences, sizeStyle='small')
        self.window.DrawRhythm = vanilla.Button( (Column1, RowD03, -Column1, RowD03plus), "Draw the rhythm of the selected glyphs", callback=self.DrawRhythm, sizeStyle='small')
        
        
        
        #scaling options
        self.window.text_15A = vanilla.TextBox( (Column1, RowE01, -Column1, RowE01plus), "Fourth, with the rhythm in mind, it is possible to create letter variations fast.", sizeStyle='small')
        self.window.text_15B = vanilla.TextBox( (Column1, RowE01B, Column2, RowE01Bplus), "Scale the thickness of the vertical strokes by %:", sizeStyle='small')
        self.window.customStrokeScale = vanilla.EditText( (Column2, RowE01B, -Column1, RowE01Bplus), 60.0, callback=self.SavePreferences, sizeStyle = 'small')
        self.window.text_16 = vanilla.TextBox( (Column1, RowE02, Column2, RowE02plus), "Scale the rest of the glyph by %:", sizeStyle='small')
        self.window.customScale = vanilla.EditText( (Column2, RowE02, -Column1, RowE02plus), 50.0, callback=self.SavePreferences, sizeStyle = 'small')
        self.window.text_17 = vanilla.TextBox( (Column1, RowE03, Column2, RowE03plus), "Scale the side bearings by %:", sizeStyle='small')
        self.window.SideBearingsScale = vanilla.EditText( (Column2, RowE03, -Column1, RowE03plus), 60.0, callback=self.SavePreferences, sizeStyle = 'small')
        self.window.Scale = vanilla.Button( (Column1, RowE04, -Column1, RowE04plus), "Draw a variation on the current font", callback=self.scaleSelectedLetters, sizeStyle='small')
        self.window.text_18 = vanilla.TextBox( (Column1, RowE05, -Column1, RowE05plus), "Note: components are only changed in their original glyph. Select those as well. Edited glyphs are colored green.", sizeStyle='small')
        self.window.mergeScalingFiles = vanilla.CheckBox( (Column1, RowE06, -Column1, RowE06plus), "Merge different variations in one file.\nThis is advisable as uppercase and lowercase can be treated differently. Select different letters to combine different analysis together", callback=self.SavePreferences, sizeStyle='small')
        
        self.window.text_19 = vanilla.TextBox( (Column1, RowE07, -Column1, RowE07plus), "Fifth are the manual corrections. The Rhythm Influencer took away the repetitive work, now it is up to you as designer to make the refinements.", sizeStyle='small')
        
        self.window.closeWindowOnFinish = vanilla.CheckBox( (Column1, RowEX01, -Column1, RowEX01plus), "Close this window on finish", callback=self.SavePreferences, sizeStyle='small' )
        self.window.debug = vanilla.CheckBox( (Column1, RowEX02, -Column1, RowEX02plus), "Export a log to the console (requires a restart)", callback=self.SavePreferences, sizeStyle='small' )
        self.window.text_20 = vanilla.TextBox( (Column1, RowEX03, -Column1, RowEX03plus), "Copyright Maarten Renckens (Artengar) 2020. All rights reserved. For info, bug reports or gifts for further development: maarten.renckens@artengar.com", sizeStyle='small')

        #All the options for the vertical height of the rhythm
        #RadioGroup
        
        #Render the window
        self.LoadPreferences()
        self.window.open()
        self.window.makeKey()
    
    #Save the prefs
    def SavePreferences(self, sender):
        try:
            Glyphs.defaults["com.Artengar.RhythmInfluencer.preciseness"] = self.window.preciseness.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.Change_options"] = self.window.Change_options.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.box2.customLowercase"] = self.window.box2.customLowercase.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.box2.customUppercase"] = self.window.box2.customUppercase.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.box3.customThreshold"] = self.window.box3.customThreshold.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.mergeRhythmFiles"] = self.window.mergeRhythmFiles.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.customScale"] = self.window.customScale.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.customStrokeScale"] = self.window.customStrokeScale.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.SideBearingsScale"] = self.window.SideBearingsScale.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.mergeScalingFiles"] = self.window.mergeScalingFiles.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.closeWindowOnFinish"] = self.window.closeWindowOnFinish.get()
            Glyphs.defaults["com.Artengar.RhythmInfluencer.debug"] = self.window.debug.get()
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
                    "com.Artengar.RhythmInfluencer.preciseness": 1.0,
                    "com.Artengar.RhythmInfluencer.Change_options": 0,
                    "com.Artengar.RhythmInfluencer.box2.customLowercase": 20,
                    "com.Artengar.RhythmInfluencer.box2.customUppercase": 20,
                    "com.Artengar.RhythmInfluencer.box3.customThreshold": 0,
                    "com.Artengar.RhythmInfluencer.mergeRhythmFiles": True,
                    "com.Artengar.RhythmInfluencer.customScale": 100,
                    "com.Artengar.RhythmInfluencer.customStrokeScale": 100,
                    "com.Artengar.RhythmInfluencer.SideBearingsScale": 100,
                    "com.Artengar.RhythmInfluencer.mergeScalingFiles": True,
                    "com.Artengar.RhythmInfluencer.closeWindowOnFinish": True,
                    "com.Artengar.RhythmInfluencer.debug": False
                }
            )
            self.window.preciseness.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.preciseness"])
            self.window.Change_options.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.Change_options"])
            self.window.box2.customLowercase.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.box2.customLowercase"])
            self.window.box2.customUppercase.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.box2.customUppercase"])
            self.window.box3.customThreshold.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.box3.customThreshold"])
            self.window.mergeRhythmFiles.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.mergeRhythmFiles"])
            self.window.customScale.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.customScale"])
            self.window.customStrokeScale.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.customStrokeScale"])
            self.window.SideBearingsScale.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.SideBearingsScale"])
            self.window.mergeScalingFiles.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.mergeScalingFiles"])
            self.window.closeWindowOnFinish.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.closeWindowOnFinish"])
            self.window.debug.set(Glyphs.defaults["com.Artengar.RhythmInfluencer.debug"])
            
            debug = Glyphs.defaults["com.Artengar.RhythmInfluencer.debug"]
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
        main_steps(makeDistribution=True, makeRhythm=False, makeScale=False)
        if Glyphs.defaults["com.Artengar.RhythmInfluencer.closeWindowOnFinish"] == True:
            self.window.close()
        
    def DrawRhythm(self, sender):
        main_steps(makeDistribution=False, makeRhythm=True, makeScale=False)
        if Glyphs.defaults["com.Artengar.RhythmInfluencer.closeWindowOnFinish"] == True:
            self.window.close()
        
    def scaleSelectedLetters(self, sender):
        main_steps(makeDistribution=False, makeRhythm=False, makeScale=True)
        if Glyphs.defaults["com.Artengar.RhythmInfluencer.closeWindowOnFinish"] == True:
            self.window.close()

    




















################################################# Activator #################################################

#Empty the caches
def resetCache():
    for font in Glyphs.fonts:
        if not font.familyName.startswith("Working draft of"):
            if not font.familyName.startswith("The horizontal black mass distribution of"):
                if not font.familyName.startswith("The rhythm of"):
                    if not font.familyName.startswith("Scaled font for"):
                        if debug==True:print "Resetting cache: the active font will be: %s"%font
                        Active_Font = font
                        return Active_Font
    return False

#check if there are fonts open
if len(Glyphs.fonts) <=0:
    Message("No open fonts", "There are no fonts open. The Rhythm Influencer can't do his work.", OKButton=None)
#check if the open fonts are valid
elif resetCache() == False:
    Message("No useful file detected; the plugin cannot start. Make sure the names of the files do not start with 'Working draft of', 'The horizontal black mass distribution of', 'The rhythm of' or 'Scaled font for'.")
else:
    Glyphs.clearLog()
    if debug==True: Glyphs.showMacroWindow()
    run_program()





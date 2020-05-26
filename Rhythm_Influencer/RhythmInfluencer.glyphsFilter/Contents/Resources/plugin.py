# encoding: utf-8

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *

class RhythmInfluencer(FilterWithDialog):
	
	# Definitions of IBOutlets
	
	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()
	
	# Text field in dialog
	myTextField = objc.IBOutlet()
	
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({'en': u'My Filter', 'de': u'Mein Filter'})
		
		# Word on Run Button (default: Apply)
		self.actionButtonLabel = Glyphs.localize({'en': u'Apply', 'de': u'Anwenden'})
		
		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)
	
	# On dialog show
	@objc.python_method
	def start(self):
		
		# Set default value
		Glyphs.registerDefault('com.myname.myfilter.value', 15.0)
		
		# Set value of text field
		self.myTextField.setStringValue_(Glyphs.defaults['com.myname.myfilter.value'])
		
		# Set focus to text field
		self.myTextField.becomeFirstResponder()
		
	# Action triggered by UI
	@objc.IBAction
	def setValue_( self, sender ):
		
		# Store value coming in from dialog
		Glyphs.defaults['com.myname.myfilter.value'] = sender.floatValue()
		
		# Trigger redraw
		self.update()
	
	# Actual filter
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):
		
		# Called on font export, get value from customParameters
		if customParameters.has_key('shift'):
			value = customParameters['shift']
		
		# Called through UI, use stored value
		else:
			value = float(Glyphs.defaults['com.myname.myfilter.value'])
		
		# Shift all nodes in x and y direction by the value
		for path in layer.paths:
			for node in path.nodes:
				node.position = NSPoint(node.position.x + value, node.position.y + value)
	
	@objc.python_method
	def generateCustomParameter( self ):
		return "%s; shift:%s;" % (self.__class__.__name__, Glyphs.defaults['com.myname.myfilter.value'] )
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__

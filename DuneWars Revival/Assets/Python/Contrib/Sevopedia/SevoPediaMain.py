# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose, EmperorFool
# see ReadMe for details

# M danced and had some drinks here

from CvPythonExtensions import *
import string

import CvUtil
import ScreenInput
import SevoScreenEnums

import CvPediaScreen
import SevoPediaTech
import SevoPediaUnit
import SevoPediaBuilding
import SevoPediaPromotion
import SevoPediaUnitChart
import SevoPediaBonus
import SevoPediaTerrain
import SevoPediaFeature
import SevoPediaImprovement
import SevoPediaCivic
import SevoPediaCivilization
import SevoPediaLeader
import SevoPediaTrait
import SevoPediaSpecialist
import SevoPediaHistory
import SevoPediaProject
import SevoPediaReligion
import SevoPediaCorporation
import SevoPediaIndex

import UnitUpgradesGraph
import TraitUtil
import BugCore
import BugUtil

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

AdvisorOpt = BugCore.game.Advisors

g_TraitUtilInitDone = False

class SevoPediaMain(CvPediaScreen.CvPediaScreen):

	def __init__(self):
		self.PEDIA_MAIN_SCREEN	= "PediaMainScreen"
		self.INTERFACE_ART_INFO	= "SCREEN_BG_OPAQUE"
		
		self.TAB_TOC   = "Contents"
		self.TAB_INDEX = "Index"

		self.WIDGET_ID		= "PediaMainWidget"
		self.BACKGROUND_ID	= "PediaMainBackground"
		self.TOP_PANEL_ID	= "PediaMainTopPanel"
		self.BOT_PANEL_ID	= "PediaMainBottomPanel"
		self.HEAD_ID		= "PediaMainHeader"
		self.TOC_ID			= "PediaMainContents"
		self.INDEX_ID		= "PediaMainIndex"
		self.BACK_ID		= "PediaMainBack"
		self.NEXT_ID		= "PediaMainForward"
		self.EXIT_ID		= "PediaMainExit"
		self.CATEGORY_LIST_ID	= "PediaMainCategoryList"
		self.ITEM_LIST_ID	= "PediaMainItemList"
		self.UPGRADES_GRAPH_ID	= "PediaMainUpgradesGraph"

		self.X_SCREEN = 500
		self.Y_SCREEN = 396
		self.W_SCREEN = 1024
		self.H_SCREEN = 768

		self.H_PANEL = 55
		self.BUTTON_SIZE = 64
		self.BUTTON_COLUMNS = 9
		self.ITEMS_MARGIN = 18
		self.ITEMS_SEPARATION = 2

		self.X_TOP_PANEL = 0
		self.Y_TOP_PANEL = 0
		self.W_TOP_PANEL = self.W_SCREEN
		self.H_TOP_PANEL = self.H_PANEL

		self.X_BOT_PANEL = 0
		self.Y_BOT_PANEL = self.H_SCREEN - self.H_PANEL
		self.W_BOT_PANEL = self.W_SCREEN
		self.H_BOT_PANEL = self.H_PANEL

		self.X_CATEGORIES = 0
		self.Y_CATEGORIES = (self.Y_TOP_PANEL + self.H_TOP_PANEL) - 4
		self.W_CATEGORIES = 175
		self.H_CATEGORIES = (self.Y_BOT_PANEL + 3) - self.Y_CATEGORIES

		self.X_ITEMS = self.X_CATEGORIES + self.W_CATEGORIES + 2
		self.Y_ITEMS = self.Y_CATEGORIES
		self.W_ITEMS = 210
		self.H_ITEMS = self.H_CATEGORIES

		self.X_PEDIA_PAGE = self.X_ITEMS + self.W_ITEMS + 18
		self.Y_PEDIA_PAGE = self.Y_ITEMS + 13
		self.R_PEDIA_PAGE = self.W_SCREEN - 20
		self.B_PEDIA_PAGE = self.Y_ITEMS + self.H_ITEMS - 16
		self.W_PEDIA_PAGE = self.R_PEDIA_PAGE - self.X_PEDIA_PAGE
		self.H_PEDIA_PAGE = self.B_PEDIA_PAGE - self.Y_PEDIA_PAGE

		self.X_TITLE = self.X_SCREEN
		self.Y_TITLE = 8
		self.X_TOC = 75
		self.Y_TOC = 730
		self.X_INDEX = 210
		self.Y_INDEX = 730
		self.X_BACK = 510
		self.Y_BACK = 730
		self.X_NEXT = 645
		self.Y_NEXT = 730
		self.X_EXIT = 994
		self.Y_EXIT = 730

		self.tab = None
		self.iActivePlayer = -1
		self.nWidgetCount = 0

		self.categoryList = []
		self.categoryGraphics = []
		self.iCategory = -1
		self.iItem = -1
		self.iItemIndex = -1
		self.pediaHistory = []
		self.pediaFuture = []

		self.mapListGenerators = {
			SevoScreenEnums.PEDIA_TECHS		: self.placeTechs,
			SevoScreenEnums.PEDIA_UNITS		: self.placeUnits,
			SevoScreenEnums.PEDIA_UNIT_UPGRADES	: self.placeUnitUpgrades,
			SevoScreenEnums.PEDIA_UNIT_CATEGORIES	: self.placeUnitCategories,
			SevoScreenEnums.PEDIA_PROMOTIONS		: self.placePromotions,
			SevoScreenEnums.PEDIA_PROMOTION_TREE	: self.placePromotionTree,
			SevoScreenEnums.PEDIA_BUILDINGS		: self.placeBuildings,
			SevoScreenEnums.PEDIA_NATIONAL_WONDERS	: self.placeNationalWonders,
			SevoScreenEnums.PEDIA_GREAT_WONDERS	: self.placeGreatWonders,
			SevoScreenEnums.PEDIA_PROJECTS		: self.placeProjects,
			SevoScreenEnums.PEDIA_SPECIALISTS		: self.placeSpecialists,
			SevoScreenEnums.PEDIA_TERRAINS		: self.placeTerrains,
			SevoScreenEnums.PEDIA_FEATURES		: self.placeFeatures,
			SevoScreenEnums.PEDIA_BONUSES		: self.placeBonuses,
			SevoScreenEnums.PEDIA_IMPROVEMENTS	: self.placeImprovements,
			SevoScreenEnums.PEDIA_CIVS		: self.placeCivs,
			SevoScreenEnums.PEDIA_LEADERS		: self.placeLeaders,
			SevoScreenEnums.PEDIA_TRAITS		: self.placeTraits,
			SevoScreenEnums.PEDIA_CIVICS		: self.placeCivics,
			SevoScreenEnums.PEDIA_RELIGIONS		: self.placeReligions,
			SevoScreenEnums.PEDIA_CORPORATIONS	: self.placeEspionage,
			SevoScreenEnums.PEDIA_CONCEPTS		: self.placeConcepts,
			SevoScreenEnums.PEDIA_BTS_CONCEPTS	: self.placeBTSConcepts,
			SevoScreenEnums.PEDIA_HINTS		: self.placeHints,
			SevoScreenEnums.PEDIA_SHORTCUTS  	: self.placeShortcuts,
			SevoScreenEnums.PEDIA_STRATEGY  	: self.placeStrategy,
			}

		self.pediaBuilding	= SevoPediaBuilding.SevoPediaBuilding(self)
		self.pediaLeader	= SevoPediaLeader.SevoPediaLeader(self)
		self.pediaIndex     = SevoPediaIndex.SevoPediaIndex(self)

		self.mapScreenFunctions = {
			SevoScreenEnums.PEDIA_TECHS		: SevoPediaTech.SevoPediaTech(self),
			SevoScreenEnums.PEDIA_UNITS		: SevoPediaUnit.SevoPediaUnit(self),
			SevoScreenEnums.PEDIA_UNIT_CATEGORIES	: SevoPediaUnitChart.SevoPediaUnitChart(self),
			SevoScreenEnums.PEDIA_PROMOTIONS		: SevoPediaPromotion.SevoPediaPromotion(self),
			SevoScreenEnums.PEDIA_BUILDINGS		: self.pediaBuilding,
			SevoScreenEnums.PEDIA_NATIONAL_WONDERS	: SevoPediaBuilding.SevoPediaBuilding(self),
			SevoScreenEnums.PEDIA_GREAT_WONDERS	: SevoPediaBuilding.SevoPediaBuilding(self),
			SevoScreenEnums.PEDIA_PROJECTS		: SevoPediaProject.SevoPediaProject(self),
			SevoScreenEnums.PEDIA_SPECIALISTS		: SevoPediaSpecialist.SevoPediaSpecialist(self),
			SevoScreenEnums.PEDIA_TERRAINS		: SevoPediaTerrain.SevoPediaTerrain(self),
			SevoScreenEnums.PEDIA_FEATURES		: SevoPediaFeature.SevoPediaFeature(self),
			SevoScreenEnums.PEDIA_BONUSES		: SevoPediaBonus.SevoPediaBonus(self),
			SevoScreenEnums.PEDIA_IMPROVEMENTS	: SevoPediaImprovement.SevoPediaImprovement(self),
			SevoScreenEnums.PEDIA_CIVS		: SevoPediaCivilization.SevoPediaCivilization(self),
			SevoScreenEnums.PEDIA_LEADERS		: self.pediaLeader,
			SevoScreenEnums.PEDIA_TRAITS		: SevoPediaTrait.SevoPediaTrait(self),
			SevoScreenEnums.PEDIA_CIVICS		: SevoPediaCivic.SevoPediaCivic(self),
			SevoScreenEnums.PEDIA_RELIGIONS		: SevoPediaReligion.SevoPediaReligion(self),
			SevoScreenEnums.PEDIA_CORPORATIONS	: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_CONCEPTS		: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_BTS_CONCEPTS	: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_SHORTCUTS  	: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_STRATEGY  	: SevoPediaHistory.SevoPediaHistory(self),
			}



	def getScreen(self):
		return CyGInterfaceScreen(self.PEDIA_MAIN_SCREEN, SevoScreenEnums.PEDIA_MAIN)

	def createScreen(self, screen):
		if screen.isActive(): return
		BugUtil.debug("Creating screen")
		self.iCategory = -1
		self.tab = None
		self.setPediaCommonWidgets()

	def pediaShow(self):
		global g_TraitUtilInitDone
		if not g_TraitUtilInitDone:
			TraitUtil.init()
			g_TraitUtilInitDone = True
		self.iActivePlayer = gc.getGame().getActivePlayer()
		self.iCategory = -1
		if (not self.pediaHistory):
			self.pediaHistory.append((SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_BTS_CONCEPTS))
		current = self.pediaHistory.pop()
		self.pediaFuture = []
		self.pediaHistory = []
		self.pediaJump(current[0], current[1], False, True)



	def pediaJump(self, iCategory, iItem, bRemoveFwdList, bIsLink):
		bAddToHistory = False
		if (not self.pediaHistory):
			bAddToHistory = True
		elif (iCategory != SevoScreenEnums.PEDIA_MAIN or iItem == SevoScreenEnums.PEDIA_UNIT_UPGRADES or iItem == SevoScreenEnums.PEDIA_PROMOTION_TREE or iItem == SevoScreenEnums.PEDIA_HINTS):
			prev = self.pediaHistory[0]
			if (prev[0] != iCategory or prev[1] != iItem):
				bAddToHistory = True
		if (bAddToHistory):
			self.pediaHistory.append((iCategory, iItem))
		if (bRemoveFwdList):
			self.pediaFuture = []

		screen = self.getScreen()
		if not screen.isActive():
			self.createScreen(screen)

		if (iCategory == SevoScreenEnums.PEDIA_MAIN):
			BugUtil.debug("Main link %d" % iItem)
			self.showContents(bIsLink, iItem)
			screen.setSelectedListBoxStringGFC(self.CATEGORY_LIST_ID, iItem - (SevoScreenEnums.PEDIA_MAIN + 1))
			#self.iCategory = iItem
			return

		if (iCategory == SevoScreenEnums.PEDIA_BUILDINGS):
			iCategory += self.pediaBuilding.getBuildingType(iItem)
		elif (iCategory == SevoScreenEnums.PEDIA_BTS_CONCEPTS):
			iCategory = self.determineNewConceptSubCategory(iItem)
			BugUtil.debug("Switching to category %d" % iCategory)
		self.showContents(bIsLink, iCategory)
		screen.setSelectedListBoxStringGFC(self.CATEGORY_LIST_ID, iCategory - (SevoScreenEnums.PEDIA_MAIN + 1))
		if (iCategory not in (SevoScreenEnums.PEDIA_UNIT_UPGRADES, SevoScreenEnums.PEDIA_PROMOTION_TREE, SevoScreenEnums.PEDIA_HINTS)):
			screen.enableSelect(self.ITEM_LIST_ID, True)
			if (self.iItemIndex != -1):
				BugUtil.debug("Deselecting item %d" % self.iItemIndex)
				screen.selectRow(self.ITEM_LIST_ID, self.iItemIndex, False)
			BugUtil.debug("Selecting item %d" % iItem)
			self.iItem = iItem
			for i, item in enumerate(self.list):
				if (item[1] == iItem):
					BugUtil.debug("Selecting %dth item %d" % (i, iItem))
					#screen.setSelectedListBoxStringGFC(self.ITEM_LIST_ID, i)
					screen.selectRow(self.ITEM_LIST_ID, i, True)
					self.iItemIndex = i
					#break

		#self.iCategory = iCategory
		BugUtil.debug("Drawing screen %d item %d" % (iCategory, iItem))
		self.deleteAllWidgets()
		func = self.mapScreenFunctions.get(iCategory)
		func.interfaceScreen(iItem)

	def determineNewConceptSubCategory(self, iItem):
		info = gc.getNewConceptInfo(iItem)
		BugUtil.debug("NewConcept itme %d is %s" % (iItem, info.getDescription()))
		if (self.isTraitInfo(info)):
			return SevoScreenEnums.PEDIA_TRAITS
		if (self.isStrategyInfo(info)):
			return SevoScreenEnums.PEDIA_STRATEGY
		if (self.isShortcutInfo(info)):
			return SevoScreenEnums.PEDIA_SHORTCUTS
		if (self.isEspionageInfo(info)):
			return SevoScreenEnums.PEDIA_CORPORATIONS
		return SevoScreenEnums.PEDIA_BTS_CONCEPTS

	def isContentsShowing(self):
		return self.tab == self.TAB_TOC
	
	def showContents(self, bForce=False, iCategory=SevoScreenEnums.PEDIA_TECHS):
		self.deleteAllWidgets()
		if not self.isContentsShowing():
			BugUtil.debug("Drawing category list")
			self.placeCategories(iCategory)
			screen = self.getScreen()
			screen.setText(self.TOC_ID, "Background", self.TOC_ACTIVE_TEXT,   CvUtil.FONT_LEFT_JUSTIFY,   self.X_TOC,   self.Y_TOC,   0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
			screen.setText(self.INDEX_ID, "Background", self.INDEX_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.X_INDEX, self.Y_INDEX, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
			screen.show(self.BACK_ID)
			screen.show(self.NEXT_ID)
		if not self.isContentsShowing() or self.iCategory != iCategory or bForce:
			BugUtil.debug("Drawing item list %d" % iCategory)
			self.mapListGenerators.get(iCategory)()
			self.iCategory = iCategory
			self.iItem = -1
			self.iItemIndex = -1
		self.tab = self.TAB_TOC

	def isIndexShowing(self):
		return self.tab == self.TAB_INDEX
	
	def showIndex(self):
		if self.isIndexShowing(): return
		self.deleteAllWidgets()
		self.deleteListWidgets()
		screen = self.getScreen()
		screen.setText(self.TOC_ID, "Background", self.TOC_TEXT,   CvUtil.FONT_LEFT_JUSTIFY,   self.X_TOC,   self.Y_TOC,   0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.setText(self.INDEX_ID, "Background", self.INDEX_ACTIVE_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.X_INDEX, self.Y_INDEX, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.hide(self.BACK_ID)
		screen.hide(self.NEXT_ID)
		self.pediaIndex.interfaceScreen()
		self.tab = self.TAB_INDEX
	
	def setPediaCommonWidgets(self):
		self.HEAD_TEXT = u"<font=4b>" + localText.getText("TXT_KEY_SEVOPEDIA_TITLE",      ())         + u"</font>"
		self.BACK_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_BACK",    ()).upper() + u"</font>"
		self.NEXT_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_FORWARD", ()).upper() + u"</font>"
		self.EXIT_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT",    ()).upper() + u"</font>"
		
		self.TOC_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_CONTENTS", ()).upper() + u"</font>"
		self.INDEX_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_INDEX",  ()).upper() + u"</font>"
		eYellow = gc.getInfoTypeForString("COLOR_YELLOW")
		self.TOC_ACTIVE_TEXT = u"<font=4>"  + localText.getColorText("TXT_KEY_PEDIA_SCREEN_CONTENTS", (), eYellow).upper() + u"</font>"
		self.INDEX_ACTIVE_TEXT = u"<font=4>"  + localText.getColorText("TXT_KEY_PEDIA_SCREEN_INDEX",  (), eYellow).upper() + u"</font>"

		self.szCategoryTechs		= localText.getText("TXT_KEY_PEDIA_CATEGORY_TECH", ())
		self.szCategoryUnits		= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ())
		self.szCategoryUnitUpgrades	= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT_UPGRADES", ())
		self.szCategoryUnitCategories	= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT_COMBAT", ())
		self.szCategoryPromotions	= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ())
		self.szCategoryPromotionTree	= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION_TREE", ())
		self.szCategoryBuildings	= localText.getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ())
		self.szCategoryNationalWonders	= localText.getText("TXT_KEY_PEDIA_CATEGORY_NATIONAL_WONDERS", ())
		self.szCategoryGreatWonders	= localText.getText("TXT_KEY_PEDIA_CATEGORY_GREAT_WONDERS", ())
		self.szCategoryProjects		= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ())
		self.szCategorySpecialists	= localText.getText("TXT_KEY_PEDIA_CATEGORY_SPECIALIST", ())
		self.szCategoryTerrains		= localText.getText("TXT_KEY_PEDIA_CATEGORY_TERRAIN", ())
		self.szCategoryFeatures		= localText.getText("TXT_KEY_PEDIA_CATEGORY_FEATURE", ())
		self.szCategoryBonuses		= localText.getText("TXT_KEY_PEDIA_CATEGORY_BONUS", ())
		self.szCategoryImprovements	= localText.getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT", ())
		self.szCategoryCivs		= localText.getText("TXT_KEY_PEDIA_CATEGORY_CIV", ())
		self.szCategoryLeaders		= localText.getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ())
		self.szCategoryTraits		= localText.getText("TXT_KEY_PEDIA_TRAITS", ())
		self.szCategoryCivics		= localText.getText("TXT_KEY_PEDIA_CATEGORY_CIVIC", ())
		self.szCategoryReligions	= localText.getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ())
		self.szCategoryCorporations	= "Espionage"
		self.szCategoryConcepts		= "General Game Concepts"
		self.szCategoryConceptsNew	= localText.getText("TXT_KEY_PEDIA_CATEGORY_CONCEPT_NEW", ())
		self.szCategoryHints		= localText.getText("TXT_KEY_PEDIA_CATEGORY_HINTS", ())
		self.szCategoryShortcuts	= localText.getText("TXT_KEY_PEDIA_CATEGORY_SHORTCUTS", ())
		self.szCategoryStrategy   	= "General Strategy Guides"
		
		self.categoryList = [
			["HINTS",	self.szCategoryConceptsNew],
			["TECHS",	self.szCategoryTechs],
			["UNITS",	self.szCategoryUnits],
			["UNITS",	self.szCategoryUnitUpgrades],
			["UNITS",	self.szCategoryUnitCategories],
			["PROMOTIONS",	self.szCategoryPromotions],
			["PROMOTIONS",	self.szCategoryPromotionTree],
			["BUILDINGS",	self.szCategoryBuildings],
			["BUILDINGS",	self.szCategoryNationalWonders],
			["BUILDINGS",	self.szCategoryGreatWonders],
			["BUILDINGS",	self.szCategoryProjects],
			["SPECIALISTS",	self.szCategorySpecialists],
			["CIVS",	self.szCategoryCivs],
			["CIVS",	self.szCategoryLeaders],
			["TRAITS",	self.szCategoryTraits],
			["CIVICS",	self.szCategoryCivics],
			["RELIGION",	self.szCategoryReligions],
			["ESPIONAGE",	self.szCategoryCorporations],
			["TERRAINS",	self.szCategoryTerrains],
			["TERRAINS",	self.szCategoryFeatures],
			["TERRAINS",	self.szCategoryBonuses],
			["TERRAINS",	self.szCategoryImprovements],
			["HINTS",	self.szCategoryConcepts],
			["HINTS",	self.szCategoryHints],
			["HINTS",	self.szCategoryShortcuts],
			["HINTS",	self.szCategoryStrategy],
			]

		self.categoryGraphics = {
			"TECHS"		: u"%c  " %(gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar()),
			"UNITS"		: u"%c  " %(CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR)),
			"PROMOTIONS"	: u"%c  " %(CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR)),
			"BUILDINGS"	: u"%c  " %(gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()),
			"SPECIALISTS"	: u"%c  " %(CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR)),
			"TERRAINS"	: u"%c  " %(gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar()),
			"CIVS"		: u"%c  " %(CyGame().getSymbolID(FontSymbols.MAP_CHAR)),
			"CIVICS"	: u"%c  " %(CyGame().getSymbolID(FontSymbols.GOLDEN_AGE_CHAR)),
			"HINTS"		: u"%c  " %(CyGame().getSymbolID(FontSymbols.DEFENSIVE_PACT_CHAR)),
                        "ESPIONAGE"     : u"%c  " %(gc.getCommerceInfo(CommerceTypes.COMMERCE_ESPIONAGE).getChar()),
                        "RELIGION"	: u"%c  " %(CyGame().getSymbolID(FontSymbols.RELIGION_CHAR)),
                        "TRAITS"        : u"%c  " %(CyGame().getSymbolID(FontSymbols.STAR_CHAR)),
			}

		screen = self.getScreen()
		screen.setRenderInterfaceOnly(True)
		screen.setScreenGroup(1)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel(self.TOP_PANEL_ID, u"", u"", True, False, self.X_TOP_PANEL, self.Y_TOP_PANEL, self.W_TOP_PANEL, self.H_TOP_PANEL, PanelStyles.PANEL_STYLE_TOPBAR)
		screen.addPanel(self.BOT_PANEL_ID, u"", u"", True, False, self.X_BOT_PANEL, self.Y_BOT_PANEL, self.W_BOT_PANEL, self.H_BOT_PANEL, PanelStyles.PANEL_STYLE_BOTTOMBAR)
		screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)

		screen.setText(self.HEAD_ID, "Background", self.HEAD_TEXT, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.setText(self.BACK_ID, "Background", self.BACK_TEXT, CvUtil.FONT_LEFT_JUSTIFY,   self.X_BACK,  self.Y_BACK,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_BACK,    1, -1)
		screen.setText(self.NEXT_ID, "Background", self.NEXT_TEXT, CvUtil.FONT_LEFT_JUSTIFY,   self.X_NEXT,  self.Y_NEXT,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_FORWARD, 1, -1)
		screen.setText(self.EXIT_ID, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY,  self.X_EXIT,  self.Y_EXIT,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)



	def placeCategories(self, iCategory=None):
		screen = self.getScreen()
		screen.addListBoxGFC(self.CATEGORY_LIST_ID, "", self.X_CATEGORIES, self.Y_CATEGORIES, self.W_CATEGORIES, self.H_CATEGORIES, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.CATEGORY_LIST_ID, True)
		screen.setStyle(self.CATEGORY_LIST_ID, "Table_StandardCiv_Style")
		screen.clearListBoxGFC(self.CATEGORY_LIST_ID)
		for i, category in enumerate(self.categoryList):
			graphic = self.categoryGraphics[category[0]]
			screen.appendListBoxStringNoUpdate(self.CATEGORY_LIST_ID, graphic + category[1], WidgetTypes.WIDGET_PEDIA_MAIN, SevoScreenEnums.PEDIA_MAIN + i + 1, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(self.CATEGORY_LIST_ID)



	def placeTechs(self):
		l0 = []; h0 = "Ayat - Seeds"
		l1 = []; h1 = 'Wali - Youth'
		l2 = []; h2 = 'Mihna - Testing'
		l3 = []; h3 = 'Hajra - Seeking'
		l4 = []; h4 = 'Tahaddi - Strength'
		l5 = []; h5 = 'Ijaz - Prophecy'
		l6 = []; h6 = 'Jannah - Paradise'
		
                for iTech in xrange(gc.getNumTechInfos()):
                        if gc.getTechInfo(iTech).getType().find('_TLEILAXU') > -1: continue
                        if gc.getTechInfo(iTech).getType().find('_PRESCIENCE2') > -1: continue
                        Era = gc.getTechInfo(iTech).getEra()
                        if Era == 0:
                                l0.append((gc.getTechInfo(iTech).getDescription(), iTech))
                        elif Era == 1:
                                l1.append((gc.getTechInfo(iTech).getDescription(), iTech))
                        elif Era == 2:
                                l2.append((gc.getTechInfo(iTech).getDescription(), iTech))
                        elif Era == 3:
                                l3.append((gc.getTechInfo(iTech).getDescription(), iTech))
                        elif Era == 4:
                                l4.append((gc.getTechInfo(iTech).getDescription(), iTech))
                        elif Era == 5:
                                l5.append((gc.getTechInfo(iTech).getDescription(), iTech))
                        elif Era == 6:
                                l6.append((gc.getTechInfo(iTech).getDescription(), iTech))

                l0.sort(); l1.sort(); l2.sort(); l3.sort(); l4.sort(); l5.sort(); l6.sort()
		
		l0.insert(0, (h0, -1))
		l1.insert(0, (h1, -1)); l1.insert(0, ("", -1))
		l2.insert(0, (h2, -1)); l2.insert(0, ("", -1))
		l3.insert(0, (h3, -1)); l3.insert(0, ("", -1))
		l4.insert(0, (h4, -1)); l4.insert(0, ("", -1))
		l5.insert(0, (h5, -1)); l5.insert(0, ("", -1))
		l6.insert(0, (h6, -1)); l6.insert(0, ("", -1))
                
		self.list = l0 + l1 + l2 + l3 + l4 + l5 + l6
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, gc.getTechInfo)
	
	def getTechList(self):
		return self.getSortedList(gc.getNumTechInfos(), gc.getTechInfo)


	def placeUnits(self):
		lMelee = []; hMelee = localText.getText("TXT_KEY_UNITCOMBAT_MELEE", ())
		lGuard = []; hGuard = localText.getText("TXT_KEY_UNITCOMBAT_GUARDSMAN", ())
		lVehi = []; hVehi = localText.getText("TXT_KEY_UNITCOMBAT_VEHICLE", ())
		lSiege = []; hSiege = localText.getText("TXT_KEY_UNITCOMBAT_SIEGE", ())
		lTrans = []; hTrans = localText.getText("TXT_KEY_UNITCOMBAT_TRANSPORT", ())
		lSusp = []; hSusp = localText.getText("TXT_KEY_UNITCOMBAT_SUSPENSOR", ())
		lThop = []; hThop = localText.getText("TXT_KEY_UNITCOMBAT_THOPTER", ())
		lHorn = []; hHorn = localText.getText("TXT_KEY_UNITCOMBAT_HORNET", ())
		lMech = []; hMech = localText.getText("TXT_KEY_UNITCOMBAT_MECH", ())
		lSpy = []; hSpy = localText.getText("TXT_KEY_UNITCOMBAT_SPY", ())
		lWork = []; hWork = localText.getText("TXT_KEY_UNITCOMBAT_WORKER", ())
		lNone = []; hNone = "No Unit Category"

		for iUnit in xrange(gc.getNumUnitInfos()):
			Combat = gc.getUnitInfo(iUnit).getUnitCombatType()
			if Combat == gc.getInfoTypeForString('UNITCOMBAT_MELEE'):
				lMelee.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_GUARDSMAN'):
				lGuard.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_VEHICLE'):
				lVehi.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_SIEGE'):
				lSiege.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_TRANSPORT'):
				lTrans.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_SUSPENSOR'):
				lSusp.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_THOPTER'):
				lThop.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_HORNET'):
				lHorn.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_MECH'):
				lMech.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_SPY'):
				lSpy.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('UNITCOMBAT_WORKER'):
				lWork.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))
			elif Combat == gc.getInfoTypeForString('NONE'):
                                if gc.getUnitInfo(iUnit).getType().find('_HOMEWORLD') > -1: continue
				lNone.append((gc.getUnitInfo(iUnit).getDescription(), iUnit))

		lMelee.sort(); lGuard.sort(); lVehi.sort(); lSiege.sort(); lTrans.sort(); lSusp.sort()
		lThop.sort(); lHorn.sort(); lMech.sort(); lSpy.sort(); lWork.sort(); lNone.sort()
		
		lMelee.insert(0, (hMelee, -1))
                lGuard.insert(0, (hGuard, -1)); lGuard.insert(0, ("", -1))
		lVehi.insert(0, (hVehi, -1)); lVehi.insert(0, ("", -1))
		lSiege.insert(0, (hSiege, -1)); lSiege.insert(0, ("", -1))
		lTrans.insert(0, (hTrans, -1)); lTrans.insert(0, ("", -1))
		lSusp.insert(0, (hSusp, -1)); lSusp.insert(0, ("", -1))
		lThop.insert(0, (hThop, -1)); lThop.insert(0, ("", -1))
		lHorn.insert(0, (hHorn, -1)); lHorn.insert(0, ("", -1))
		lMech.insert(0, (hMech, -1)); lMech.insert(0, ("", -1))
		lSpy.insert(0, (hSpy, -1)); lSpy.insert(0, ("", -1))
		lWork.insert(0, (hWork, -1)); lWork.insert(0, ("", -1))
		lNone.insert(0, (hNone, -1)); lNone.insert(0, ("", -1))
		
		self.list = lMelee + lGuard + lVehi + lSiege + lTrans + lSusp + lThop + lHorn + lMech + lSpy + lWork + lNone
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, gc.getUnitInfo)
	
	def getUnitList(self):
		#homeworld planet fix - koma13 - START
		List = self.getSortedList(gc.getNumUnitInfos(), gc.getUnitInfo)
		for item in List:
			if "Homeworld Planet" in item:
				List.remove(item)
				break
		return List
		#homeworld planet fix - koma13 - END

	def placeUnitUpgrades(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		self.UPGRADES_GRAPH_ID = self.getNextWidgetName()
		screen.addScrollPanel(self.UPGRADES_GRAPH_ID, u"", self.X_ITEMS, self.Y_PEDIA_PAGE - 13, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 2, PanelStyles.PANEL_STYLE_STANDARD)
		screen.setActivation(self.UPGRADES_GRAPH_ID, ActivationTypes.ACTIVATE_NORMAL)
		upgradesGraph = UnitUpgradesGraph.UnitUpgradesGraph(self)
		upgradesGraph.getGraph()
		upgradesGraph.drawGraph()


	def placeUnitCategories(self):
		lCombat = []
		for iCombat in xrange(gc.getNumUnitCombatInfos()):
			CombatInfo = gc.getUnitCombatInfo(iCombat)
			if CombatInfo.getType().find("_WORM") > -1: continue
			lCombat.append([CombatInfo.getDescription(), iCombat])
		lCombat.sort()
		
		self.list = lCombat
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, gc.getUnitCombatInfo)
	
	def getUnitCategoryList(self):
		return self.getSortedList(gc.getNumUnitCombatInfos(), gc.getUnitCombatInfo)


	def placePromotions(self):
                lComb = []; hComb = "Combat Promotions"
                lDrill = []; hDrill = "Drill Promotions"
                lCity = []; hCity = "City Promotions"
                lDesert = []; hDesert = "Desert Promotions"
                lWarLord = []; hWarLord = "Bashar Promotions"
                lSpy = []; hSpy = "Spy Promotions"
		lCiv = []; hCiv = "Civilization Specific"
                lAdvanced = []; hAdvanced = "Advanced Promotions"
		lMentat = []; hMentat = "Mentat Promotions"
		lSpe = []; hSpe = "Specializing Promotions"
		lMisc = []; hMisc = "Miscellaneous Promotions"

		lTech = []
		for i in xrange(gc.getNumTechInfos()):
                        if gc.getTechInfo(i).getEra() > 4:
                               lTech.append(i)
                                
		for iPromo in xrange(gc.getNumPromotionInfos()):
                        Pinfo = gc.getPromotionInfo(iPromo)
			if Pinfo.getType().find('_COMBAT') > -1 and not Pinfo.getType().find('6') > -1:
                                lComb.append((Pinfo.getDescription(), iPromo))
			elif Pinfo.getType().find('_DRILL') > -1:
                                lDrill.append((Pinfo.getDescription(), iPromo))
                        elif Pinfo.getType().find('_CITY') > -1:
                                lCity.append((Pinfo.getDescription(), iPromo))
                        elif (Pinfo.isCanMoveAllTerrain() \
                              or Pinfo.getDesertAttack() \
                              or Pinfo.getBonusPrereq() == gc.getInfoTypeForString('BONUS_WATER_DEBT') \
                              or Pinfo.getType().find('SAND') > -1 \
							  or Pinfo.getType().find('SPOTTER') > -1):
                                lDesert.append((Pinfo.getDescription(), iPromo))
                        elif (Pinfo.isLeader() \
                              or Pinfo.getPrereqPromotion() == gc.getInfoTypeForString('PROMOTION_LEADER') \
                              or Pinfo.getPrereqOrPromotion1() == gc.getInfoTypeForString('PROMOTION_LEADER')):
                                lWarLord.append((Pinfo.getDescription(), iPromo))
                        elif Pinfo.getUnitCombat(gc.getInfoTypeForString('UNITCOMBAT_SPY')):
				lSpy.append((Pinfo.getDescription(), iPromo))
			elif Pinfo.getNumPrereqCivilizations() \
                              or Pinfo.getPrereqPromotion() == gc.getInfoTypeForString('PROMOTION_IXIAN'):
                                lCiv.append((Pinfo.getDescription(), iPromo))
                        elif Pinfo.getTechPrereq() in lTech:
                                lAdvanced.append((Pinfo.getDescription(), iPromo))
                        elif Pinfo.getType().find('_MENTAT') > -1:
                                lMentat.append((Pinfo.getDescription(), iPromo))
                        elif (Pinfo.getType().find('1') > -1 \
                              or Pinfo.getType().find('2') > -1 \
                              or Pinfo.getType().find('3') > -1) \
                              and not Pinfo.getType().find('HOME') > -1:
                                lSpe.append((Pinfo.getDescription(), iPromo))
                        else:
                                lMisc.append((Pinfo.getDescription(), iPromo))
                                
                lComb.sort()   
                lDrill.sort()
                lCity.sort() 
                lDesert.sort()
                lWarLord.sort()
		lSpy.sort()
		lCiv.sort()
                lAdvanced.sort()
		lMentat.sort()
		lSpe.sort()
		lMisc.sort()
		
		lComb.insert(0, (hComb, -1))
		lDrill.insert(0, (hDrill, -1)); lDrill.insert(0, ("", -1))
		lCity.insert(0, (hCity, -1)); lCity.insert(0, ("", -1))
		lDesert.insert(0, (hDesert, -1)); lDesert.insert(0, ("", -1))
		lWarLord.insert(0, (hWarLord, -1)); lWarLord.insert(0, ("", -1))
		lSpy.insert(0, (hSpy, -1)); lSpy.insert(0, ("", -1))
                lCiv.insert(0, (hCiv, -1)); lCiv.insert(0, ("", -1))
		lAdvanced.insert(0, (hAdvanced, -1)); lAdvanced.insert(0, ("", -1))
                lMentat.insert(0, (hMentat, -1)); lMentat.insert(0, ("", -1))
                lSpe.insert(0, (hSpe, -1)); lSpe.insert(0, ("", -1))
                lMisc.insert(0, (hMisc, -1)); lMisc.insert(0, ("", -1))
				
		self.list = lComb + lDrill + lSpe + lCity + lDesert + lCiv + lAdvanced + lWarLord + lMisc + lSpy + lMentat
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, gc.getPromotionInfo)
	
	def getPromotionList(self):
		return self.getSortedList(gc.getNumPromotionInfos(), gc.getPromotionInfo)


	def placePromotionTree(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		self.UPGRADES_GRAPH_ID = self.getNextWidgetName()
		screen.addScrollPanel(self.UPGRADES_GRAPH_ID, u"", self.X_ITEMS, self.Y_PEDIA_PAGE - 13, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 2, PanelStyles.PANEL_STYLE_STANDARD)
		screen.setActivation(self.UPGRADES_GRAPH_ID, ActivationTypes.ACTIVATE_NORMAL)
		upgradesGraph = UnitUpgradesGraph.PromotionsGraph(self)
		upgradesGraph.getGraph()
		upgradesGraph.drawGraph()


	def placeBuildings(self):
                lGrow = []; hGrow = "Growth"
                lEco = []; hEco = "Economy"
		lResearch = []; hResearch = "Science"
                lMil = []; hMil = "Military"
                lProd = []; hProd = "Production"
                lEspionage = []; hEspionage = "Espionage"
                lCul = []; hCul = "Culture"
                lReligion = []; hReligion = "Religion"
                lContracts = []; hContracts = "Contracts"
                
		for iBuild in xrange(gc.getNumBuildingInfos()):
                        Binfo = gc.getBuildingInfo(iBuild)
                        Des = Binfo.getDescription()
                        if isWorldWonderClass(Binfo.getBuildingClassType()): continue
                        if isTeamWonderClass(Binfo.getBuildingClassType()): continue
                        if isNationalWonderClass(Binfo.getBuildingClassType()): continue
                        
                        if Binfo.getReligionType() > -1:
                                lReligion.append((Des, iBuild))
                        elif Binfo.getAdvisorType() == gc.getInfoTypeForString('ADVISOR_GROWTH'):
                                lGrow.append((Des, iBuild))
                        elif Binfo.getAdvisorType() == gc.getInfoTypeForString('ADVISOR_SCIENCE'):
                                lResearch.append((Des, iBuild))
                        elif Binfo.getAdvisorType() == gc.getInfoTypeForString('ADVISOR_CULTURE'):
                                lCul.append((Des, iBuild))
                        elif Binfo.getAdvisorType() == gc.getInfoTypeForString('ADVISOR_MILITARY'):
                                if Binfo.getArtDefineTag() == 'ART_DEF_BUILDING_ESPIONAGE': continue
                                if Binfo.getType().find("_TLEILAXU") > -1: continue
                                if Binfo.getType().find("_MENTAT") > -1: continue
                                if Binfo.getType().find("_DEN") > -1: continue
                                
                                if (Binfo.getCommerceChange(gc.getInfoTypeForString('COMMERCE_ESPIONAGE')) \
                                    or Binfo.getCommerceModifier(gc.getInfoTypeForString('COMMERCE_ESPIONAGE'))) \
                                    and not Binfo.getDefenseModifier():
                                        lEspionage.append((Des, iBuild))
                                else:
                                        lMil.append((Des, iBuild))
                        elif Binfo.getAdvisorType() == gc.getInfoTypeForString('ADVISOR_ECONOMY'):
                                if Binfo.getType().find("_INSPIRATION") > -1: continue
                                if Binfo.getType().find("_LOCAL_GOLDENAGE") > -1: continue
                                
                                if (Binfo.getMaintenanceModifier() \
                                    or Binfo.getTradeRouteModifier() or Binfo.getTradeRoutes() \
                                    or Binfo.getCommerceChange(gc.getInfoTypeForString('COMMERCE_GOLD')) \
                                    or Binfo.getCommerceModifier(gc.getInfoTypeForString('COMMERCE_GOLD')) \
                                    or Binfo.getBonusConsumed() == gc.getInfoTypeForString('BONUS_SPICE') \
                                    or Binfo.getFreeBonus() == gc.getInfoTypeForString('BONUS_SPICE')):
                                        lEco.append((Des, iBuild))
                                        
                                elif (Binfo.getYieldModifier(gc.getInfoTypeForString('YIELD_PRODUCTION')) \
                                      or Binfo.getYieldChange(gc.getInfoTypeForString('YIELD_PRODUCTION')) \
                                      or Binfo.getType().find("_SPOTTER") > -1):
                                        lProd.append((Des, iBuild))
                                        
                                elif (Binfo.getCommerceChange(gc.getInfoTypeForString('COMMERCE_ESPIONAGE')) \
                                      or Binfo.getCommerceModifier(gc.getInfoTypeForString('COMMERCE_ESPIONAGE'))):
                                        lEspionage.append((Des, iBuild))
                                else:
                                        lContracts.append((Des, iBuild))
                        else:#just a last check
                                lContracts.append((Des, iBuild))
                                
		lGrow.sort()  
		lEco.sort()        
                lResearch.sort()
		lMil.sort()
		lProd.sort()
		lEspionage.sort()
		lCul.sort()
		lReligion.sort()
		lContracts.sort()
		
		lGrow.insert(0, (hGrow, -1)); lGrow.insert(0, ("", -1))
		lEco.insert(0, (hEco, -1)); 
		lResearch.insert(0, (hResearch, -1)); lResearch.insert(0, ("", -1))
		lMil.insert(0, (hMil, -1)); lMil.insert(0, ("", -1))
		lProd.insert(0, (hProd, -1)); lProd.insert(0, ("", -1))
		lEspionage.insert(0, (hEspionage, -1)); lEspionage.insert(0, ("", -1))
		lCul.insert(0, (hCul, -1));  lCul.insert(0, ("", -1))
		lReligion.insert(0, (hReligion, -1)); lReligion.insert(0, ("", -1))
		lContracts.insert(0, (hContracts, -1)); lContracts.insert(0, ("", -1))
                
		self.list = lEco + lResearch + lGrow + lProd + lMil + lEspionage + lCul + lReligion + lContracts
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)
	
	def getBuildingList(self):
		# davidlallen: skip invisible buildings start
		List = self.pediaBuilding.getBuildingSortedList(0)
		newList = []
		for item in List:
			iPosn = item[0].find("Mentat")
			if (iPosn == -1) and (not "Tleilaxu Plague" in item):
				newList.append(item)
		return newList
		# davidlallen: skip invisible buildings end

	def placeNationalWonders(self):
		self.list = self.getNationalWonderList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)
	
	def getNationalWonderList(self):
		# davidlallen: skip base spice corp building start
		List = self.pediaBuilding.getBuildingSortedList(1)
		for item in List:
			if "House Spice Corporation" in item:
				List.remove(item)
				break
		return List
		# davidlallen: skip base spice corp building end

	def placeGreatWonders(self):
		self.list = self.getGreatWonderList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)
	
	def getGreatWonderList(self):
		return self.pediaBuilding.getBuildingSortedList(2)


	def placeProjects(self):
		self.list = self.getProjectList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, gc.getProjectInfo)
	
	def getProjectList(self):
		return self.getSortedList(gc.getNumProjectInfos(), gc.getProjectInfo)


	def placeSpecialists(self):
		lSpecialists = []
		hSpecialists = localText.getText("TXT_KEY_PEDIA_HEADER_SPECIALIST", ())
		lGreatSpecialists = []
		hGreatSpecialists = localText.getText("TXT_KEY_PEDIA_HEADER_GREAT_SPECIALIST", ())
		lSpecialSpecialists = []
		hSpecialSpecialists = localText.getText("TXT_KEY_PEDIA_HEADER_SPECIAL_SPECIALIST", ())

		for iSpecialist in xrange(gc.getNumSpecialistInfos()):
			SpecialistInfo = gc.getSpecialistInfo(iSpecialist)
			if iSpecialist < 7:
				lSpecialists.append((SpecialistInfo.getDescription(), iSpecialist))
			elif SpecialistInfo.getType().find("GREAT_") > -1:
				lGreatSpecialists.append((SpecialistInfo.getDescription(), iSpecialist))
			else:
                                lSpecialSpecialists.append((SpecialistInfo.getDescription(), iSpecialist))

		lSpecialists.sort()
		lGreatSpecialists.sort()
		lSpecialSpecialists.sort()
		
		lSpecialists.insert(0, (hSpecialists, -1))
		lGreatSpecialists.insert(0, (hGreatSpecialists, -1))
		lGreatSpecialists.insert(0, ("", -1))
                lSpecialSpecialists.insert(0, (hSpecialSpecialists, -1))
                lSpecialSpecialists.insert(0, ("", -1))
                        
		self.list = lSpecialists + lGreatSpecialists + lSpecialSpecialists
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST, gc.getSpecialistInfo)
	
	def getSpecialistList(self):
		return self.getSortedList(gc.getNumSpecialistInfos(), gc.getSpecialistInfo)


	def placeTerrains(self):
		self.list = self.getTerrainList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, gc.getTerrainInfo)
	
	def getTerrainList(self):
		return self.getSortedList(gc.getNumTerrainInfos(), gc.getTerrainInfo)


	def placeFeatures(self):
                lFeatures = []
                for iFeature in xrange(gc.getNumFeatureInfos()):
                        bAppend = True
                        for s, i in lFeatures:
                                if gc.getFeatureInfo(iFeature).getDescription() == s:
                                        bAppend = False
                        if bAppend:
                                lFeatures.append((gc.getFeatureInfo(iFeature).getDescription(), iFeature))
                        
                lFeatures.sort()
                
		self.list = lFeatures
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, gc.getFeatureInfo)
	
	def getFeatureList(self):
		return self.getSortedList(gc.getNumFeatureInfos(), gc.getFeatureInfo)


	def placeBonuses(self):
		self.list = self.getBonusList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, gc.getBonusInfo)
	
	def getBonusList(self):
		return self.getSortedList(gc.getNumBonusInfos(), gc.getBonusInfo)


	def placeImprovements(self):
		self.list = self.getImprovementList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, gc.getImprovementInfo)
	
	def getImprovementList(self):
		return self.getSortedList(gc.getNumImprovementInfos(), gc.getImprovementInfo)


	def placeCivs(self):
		self.list = self.getCivilizationList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, gc.getCivilizationInfo)
	
	def getCivilizationList(self):
		return self.getSortedList(gc.getNumCivilizationInfos(), gc.getCivilizationInfo)


	def placeLeaders(self):
		self.list = self.getLeaderList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, gc.getLeaderHeadInfo)
	
	def getLeaderList(self):
		return self.getSortedList(gc.getNumLeaderHeadInfos(), gc.getLeaderHeadInfo)


	def placeTraits(self):
		self.list = self.getTraitList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getTraitInfo)
	
	def getTraitList(self):
		return self.getSortedList(gc.getNumNewConceptInfos(), self.getTraitInfo, True)

	def getTraitInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isTraitInfo(info):
			
			class TraitInfo:
				def __init__(self, conceptInfo):
					self.conceptInfo = conceptInfo
					sKey = conceptInfo.getType()
					sKey = sKey[sKey.find("TRAIT_"):]
					self.eTrait = gc.getInfoTypeForString(sKey)
					self.traitInfo = gc.getTraitInfo(self.eTrait)
				def getDescription(self):
					return u"%c %s" % (TraitUtil.getIcon(self.eTrait), self.traitInfo.getDescription())
				def getButton(self):
					return self.traitInfo.getButton()
			
			return TraitInfo(info)
		return None
	
	def isTraitInfo(self, info):
		return info.getType().find("_TRAIT_") != -1


	def placeCivics(self):
		lCivics = []
		iPrevCategory = -1
		for iCivic in xrange(gc.getNumCivicInfos()):
			CivicInfo = gc.getCivicInfo(iCivic)
			iCategory = CivicInfo.getCivicOptionType()
			if iCategory > -1 and iCategory != iPrevCategory:
				if lCivics != []:
					lCivics.append(("", -1))
				lCivics.append((gc.getCivicOptionInfo(iCategory).getDescription(), -1))
			lCivics.append((CivicInfo.getDescription(), iCivic))
			iPrevCategory = iCategory
			
		self.list = lCivics
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, gc.getCivicInfo)
	
	def getCivicList(self):
		return self.getSortedList(gc.getNumCivicInfos(), gc.getCivicInfo)


	def placeReligions(self):
		self.list = self.getReligionList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, gc.getReligionInfo)
	
	def getReligionList(self):
		return self.getSortedList(gc.getNumReligionInfos(), gc.getReligionInfo)

        #!M!
	def placeEspionage(self):
                self.list = self.getSortedList(gc.getNumNewConceptInfos(), self.getEspionageInfo)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getEspionageInfo)
	
	def getEspionageInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isEspionageInfo(info):
			return info
		return None
                
        def isEspionageInfo(self, info):
		return info.getType().find("_ESPIONAGE_") != -1

	def getEspionageList(self):
		return self.getSortedList(gc.getNumNewConceptInfos(), self.getEspionageInfo)

	def placeConcepts(self):
		self.list = self.getConceptList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, gc.getConceptInfo)
	
	def getConceptList(self):
		return self.getSortedList(gc.getNumConceptInfos(), gc.getConceptInfo)


	def placeBTSConcepts(self):
		self.list = self.getNewConceptList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getNewConceptInfo)
	
	def getNewConceptList(self):
		return self.getSortedList(gc.getNumNewConceptInfos(), self.getNewConceptInfo)

	def getNewConceptInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if not self.isShortcutInfo(info) and not self.isStrategyInfo(info) and not self.isTraitInfo(info) \
                   and not self.isEspionageInfo(info):
			return info
		return None


	def placeHints(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		szHintBox = self.getNextWidgetName()
		screen.addListBoxGFC(szHintBox, "", self.X_ITEMS, self.Y_PEDIA_PAGE - 10, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 23, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(szHintBox, False)
		szHintsText = CyGameTextMgr().buildHintsList()
		hintText = string.split(szHintsText, "\n")
		for hint in hintText:
			if len(hint) != 0:
				screen.appendListBoxStringNoUpdate(szHintBox, hint, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(szHintBox)


	def placeShortcuts(self):
		self.list = self.getSortedList(gc.getNumNewConceptInfos(), self.getShortcutInfo)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getShortcutInfo)

	def getShortcutInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isShortcutInfo(info):
			return info
		return None
	
	def isShortcutInfo(self, info):
		return info.getType().find("SHORTCUTS") != -1


	def placeStrategy(self):
		self.list = self.getSortedList(gc.getNumNewConceptInfos(), self.getStrategyInfo)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getStrategyInfo)

	def getStrategyInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isStrategyInfo(info):
			return info
		return None
	
	def isStrategyInfo(self, info):
		return info.getType().find("STRATEGY") != -1
	
	
	
	def placeItems(self, widget, info):
		screen = self.getScreen()
		screen.clearListBoxGFC(self.ITEM_LIST_ID)

		screen.addTableControlGFC(self.ITEM_LIST_ID, 1, self.X_ITEMS, self.Y_ITEMS, self.W_ITEMS, self.H_ITEMS, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.ITEM_LIST_ID, False)
		screen.setStyle(self.ITEM_LIST_ID, "Table_StandardCiv_Style")
		screen.setTableColumnHeader(self.ITEM_LIST_ID, 0, "", self.W_ITEMS)

		i = 0
		for item in self.list:
			if (info == gc.getConceptInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT
				data2 = item[1]
			elif (info == self.getNewConceptInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			elif (info == self.getShortcutInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			elif (info == self.getStrategyInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			elif (info == self.getTraitInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			elif (info == self.getEspionageInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			else:
				data1 = item[1]
				data2 = 1
				
			if item[1] == -1:
				sTitle = localText.changeTextColor(item[0], gc.getInfoTypeForString('COLOR_HIGHLIGHT_TEXT'))
				button = ""
			else:
				sTitle = item[0]
				button = info(item[1]).getButton()
			screen.appendTableRow(self.ITEM_LIST_ID)
			screen.setTableText(self.ITEM_LIST_ID, 0, i, u"<font=3>" + sTitle + u"</font>", button, widget, data1, data2, CvUtil.FONT_LEFT_JUSTIFY)
			i += 1
		#screen.updateListBox(self.ITEM_LIST_ID)



	def back(self):
		if (len(self.pediaHistory) > 1):
			self.pediaFuture.append(self.pediaHistory.pop())
			current = self.pediaHistory.pop()
			self.pediaJump(current[0], current[1], False, True)
		return 1



	def forward(self):
		if (self.pediaFuture):
			current = self.pediaFuture.pop()
			self.pediaJump(current[0], current[1], False, True)
		return 1



	def link(self, szLink):
		if (szLink == "PEDIA_MAIN_TECH"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TECHS, True, True)
		elif (szLink == "PEDIA_MAIN_UNIT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_UNITS, True, True)
		elif (szLink == "PEDIA_MAIN_UNIT_GROUP"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_UNIT_CATEGORIES, True, True)
		elif (szLink == "PEDIA_MAIN_PROMOTION"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_PROMOTIONS, True, True)
		elif (szLink == "PEDIA_MAIN_BUILDING"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_BUILDINGS, True, True)
		elif (szLink == "PEDIA_MAIN_PROJECT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_PROJECTS, True, True)
		elif (szLink == "PEDIA_MAIN_SPECIALIST"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_SPECIALISTS, True, True)
		elif (szLink == "PEDIA_MAIN_TERRAIN"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TERRAINS, True, True)
		elif (szLink == "PEDIA_MAIN_FEATURE"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_FEATURES, True, True)
		elif (szLink == "PEDIA_MAIN_BONUS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_BONUSES, True, True)
		elif (szLink == "PEDIA_MAIN_IMPROVEMENT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_IMPROVEMENTS, True, True)
		elif (szLink == "PEDIA_MAIN_CIV"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CIVS, True, True)
		elif (szLink == "PEDIA_MAIN_LEADER"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_LEADERS, True, True)
		elif (szLink == "PEDIA_MAIN_TRAIT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TRAITS, True, True)
		elif (szLink == "PEDIA_MAIN_CIVIC"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CIVICS, True, True)
		elif (szLink == "PEDIA_MAIN_RELIGION"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_RELIGIONS, True, True)
		elif (szLink == "PEDIA_MAIN_CONCEPT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CONCEPTS, True, True)
		elif (szLink == "PEDIA_MAIN_HINTS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_HINTS, True, True)
		elif (szLink == "PEDIA_MAIN_SHORTCUTS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_SHORTCUTS, True, True)
		elif (szLink == "PEDIA_MAIN_STRATEGY"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_STRATEGY, True, True)

		for i in range(gc.getNumTechInfos()):
			if (gc.getTechInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_TECHS, i, True, True)
		for i in range(gc.getNumUnitInfos()):
			if (gc.getUnitInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_UNITS, i, True, True)
		for i in range(gc.getNumUnitCombatInfos()):
			if (gc.getUnitCombatInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_UNIT_CATEGORIES, i, True, True)
		for i in range(gc.getNumPromotionInfos()):
			if (gc.getPromotionInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_PROMOTIONS, i, True, True)
		for i in range(gc.getNumBuildingInfos()):
			if (gc.getBuildingInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BUILDINGS, i, True, True)
		for i in range(gc.getNumProjectInfos()):
			if (gc.getProjectInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_PROJECTS, i, True, True)
		for i in range(gc.getNumSpecialistInfos()):
			if (gc.getSpecialistInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_SPECIALISTS, i, True, True)
		for i in range(gc.getNumTerrainInfos()):
			if (gc.getTerrainInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_TERRAINS, i, True, True)
		for i in range(gc.getNumFeatureInfos()):
			if (gc.getFeatureInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_FEATURES, i, True, True)
		for i in range(gc.getNumBonusInfos()):
			if (gc.getBonusInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BONUSES, i, True, True)
		for i in range(gc.getNumImprovementInfos()):
			if (gc.getImprovementInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_IMPROVEMENTS, i, True, True)
		for i in range(gc.getNumCivilizationInfos()):
			if (gc.getCivilizationInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CIVS, i, True, True)
		for i in range(gc.getNumLeaderHeadInfos()):
			if (gc.getLeaderHeadInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_LEADERS, i, True, True)
		for i in range(gc.getNumCivicInfos()):
			if (gc.getCivicInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CIVICS, i, True, True)
		for i in range(gc.getNumReligionInfos()):
			if (gc.getReligionInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_RELIGIONS, i, True, True)
		for i in range(gc.getNumCorporationInfos()):
			if (gc.getCorporationInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CORPORATIONS, i, True, True)
		for i in range(gc.getNumConceptInfos()):
			if (gc.getConceptInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CONCEPTS, i, True, True)
		for i in range(gc.getNumNewConceptInfos()):
			if (gc.getNewConceptInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BTS_CONCEPTS, i, True, True)



	def handleInput (self, inputClass):
		if (inputClass.getPythonFile() == SevoScreenEnums.PEDIA_LEADERS):
			return self.pediaLeader.handleInput(inputClass)
		elif (inputClass.getFunctionName() == self.TOC_ID):
			self.showContents()
			return 1
		elif (inputClass.getFunctionName() == self.INDEX_ID):
			self.showIndex()
			return 1
		elif (self.isIndexShowing()):
			return self.pediaIndex.handleInput(inputClass)
		
		return 0



	def deleteAllWidgets(self):
		screen = self.getScreen()
		iNumWidgets = self.nWidgetCount
		self.nWidgetCount = 0
		for i in range(iNumWidgets):
			screen.deleteWidget(self.getNextWidgetName())
		self.nWidgetCount = 0

	def deleteListWidgets(self):
		screen = self.getScreen()
		screen.deleteWidget("PediaMainCategoryList")
		screen.deleteWidget("PediaMainItemList")

	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName


	def isSortLists(self):
		return AdvisorOpt.SevopediaSortItemList()

	def getSortedList(self, numInfos, getInfo, noSort=False):
		list = []
		for i in range(numInfos):
			item = getInfo(i)
			if item:
				list.append((item.getDescription(), i))
		if self.isSortLists() and not noSort:
			list.sort()
		return list

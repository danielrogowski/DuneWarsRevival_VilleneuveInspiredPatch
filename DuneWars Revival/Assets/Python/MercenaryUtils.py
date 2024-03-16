#
# Homeworld - Dune Wars
# koma13
#
# Thanks to:
# Mercenaries Mod
# By: The Lopez
# MercenaryUtils

# !M! -> With specific modifications for DW Revival

from CvPythonExtensions import *
import CvUtil
import PyHelpers
import cPickle as pickle
import BugUtil
import BugData

# globals
###################################################
gc = CyGlobalContext()	
PyPlayer = PyHelpers.PyPlayer
PyGame = PyHelpers.PyGame()
PyInfo = PyHelpers.PyInfo

SD_MOD_ID = "MercenaryData"
AVAILABLE_MERCENARIES = "AvailableMercenaries"
UNIQUE_ID = "UniqueID"
SEQUENCE = "Sequence"

#Requirements for homeworld access
OFFWORLD_TECH = "TECH_OFFWORLD_TRADE"
#NEEDED_BUILDING = "NO_BUILDING"

dictHomeworld = {'CIVILIZATION_ATREIDES' : 'Caladan', 'CIVILIZATION_ORDOS' : 'Sigma Draconis', 'CIVILIZATION_TLEILAX' : 'Tleilax', 'CIVILIZATION_CORRINO' : 'Kaitain', 'CIVILIZATION_HARKONNEN' : 'Geidi Prime', 'CIVILIZATION_GESSERIT' : 'Wallach IX', 'CIVILIZATION_IX' : 'Ix', 'CIVILIZATION_ECAZ' : 'Ecaz', 'CIVILIZATION_FREMEN' : 'the Southern Sietches', 'CIVILIZATION_RICHESE' : 'Richese'}
		
#Base chance of spawning a unit in a player's unit pool
g_iSpawningChance = 50

#Change price - default: 100%
g_iHireCostModifier = 100

#Chance for elite unit - default: 20%
g_iChanceForElite = 25

#number of units added to pool at initialization
g_iStartingUnits = 5

# the maximum number of units that can be in the unit pool
g_iMaxUnitsInPool = 18

# throttles the spawning chance based on the current pool size, lower means more extreme slowdown as the list fills up
g_iUnitPoolSizeSpawningDivisor = 3.0

#print out mercenary placements
g_bMercenaryDebug = false

class MercenaryUtils:
		
	def __init__(self):
		# Setup the mercenary data structure if it hasn't been setup yet.
		if (not BugData.getGameData().getTable(SD_MOD_ID).hasTable(AVAILABLE_MERCENARIES)):
			self.setupMercenaryData()
		
		global g_iSpawningChance
		global g_dHireCostModifier
		global g_iChanceForElite
		global g_iStartingUnits
		global g_bMercenaryDebug
		
	def doHomeworld(self):		
		if (not BugData.getGameData().getTable(SD_MOD_ID).hasTable(AVAILABLE_MERCENARIES)):
			self.setupMercenaryData()		
			
		for iPlayer in xrange(gc.getMAX_CIV_PLAYERS()):
			player = gc.getPlayer(iPlayer)
			if not player.isAlive():
				continue
			
			team = gc.getTeam(player.getTeam())
			if not team.isHasTech(gc.getInfoTypeForString(OFFWORLD_TECH)):
				continue
			
			mercenaries, nextidarray, sequencearray = self.loadMercenaryData(iPlayer)
			
			iRand = gc.getGame().getMapRand().get(100, "get a random number")
			iChance = self.getSpawningChance(len(mercenaries[iPlayer]), player)
			
			id = nextidarray[iPlayer]
			
			if  (iRand < iChance and len(mercenaries[iPlayer]) < g_iMaxUnitsInPool):
				mercenary = self.getMercenaryUnit(iPlayer)
				
				mercenaries[iPlayer][id] = mercenary
				id += 1
				
				if iPlayer == gc.getGame().getActivePlayer():
					szCiv = gc.getCivilizationInfo(player.getCivilizationType()).getType()
					
					# Message to report that a new unit is avaialble
					iUnit = int(mercenary['UnitType'])
					iCost = int(mercenary['Cost'])
					UnitInfo = gc.getUnitInfo(iUnit)
					bElite = mercenary['Elite']
					
					szColor = u"<color=255,255,255>"
					if bElite:
						szColor = u"<color=240,190,0>"
						
					szUnitText = szColor + CyTranslator().getText("%s1", (UnitInfo.getDescription(),())) 
					if bElite:
						szUnitText = szUnitText + CyTranslator().getText(" [ICON_STAR]", ())
					szUnitText = szUnitText + u"</color>"
					szUnitText = szUnitText + CyTranslator().getText(" for %d1 [ICON_GOLD]", (iCost,())) 
					
					szMessage = CyTranslator().getText("New Unit from %s1 available: ", (dictHomeworld[szCiv],())  )
					szMessage = szMessage + szUnitText 
					CyInterface().addImmediateMessage(szMessage, "")
					# Message - End
					
			nextidarray[iPlayer] = id	
			mercenaries = self.updateMercenaries(mercenaries, iPlayer)
			self.saveMercenaryData(mercenaries, nextidarray, sequencearray)
		
			self.computerPlayerThink(iPlayer, mercenaries)
		
	def setupMercenaryData(self):
		#BugUtil.debug("Mercenary Utils - Calling setupMercenaryData")
		mercData = BugData.getGameData().getTable(SD_MOD_ID)
		mercData[AVAILABLE_MERCENARIES] = {}
		mercData[UNIQUE_ID] = {}
		mercData[SEQUENCE] = {}
		
	def loadMercenaryData(self, iPlayer):
		#BugUtil.debug("Mercenary Utils - Calling loadMercenaryData")
		mercData = BugData.getGameData().getTable(SD_MOD_ID)
		mercenaries = mercData[AVAILABLE_MERCENARIES]
		nextIDArray = mercData[UNIQUE_ID]
		sequenceArray = mercData[SEQUENCE]

		nextid = 0
		try:
			if not iPlayer in mercenaries:
				#BugUtil.debug("Mercenary Utils - refresh data - try")
				mercenaries[iPlayer] = {}
				for i in xrange(g_iStartingUnits):
					mercenaries[iPlayer][nextid] = self.getMercenaryUnit(iPlayer)
					nextid += 1
				nextIDArray[iPlayer] = nextid
				sequenceArray[iPlayer] = "on"
		except:
			#BugUtil.debug("Mercenary Utils - refresh data - except")
			mercenaries[iPlayer] = {}
			for i in xrange(g_iStartingUnits):
				mercenaries[iPlayer][nextid] = self.getMercenaryUnit(iPlayer)
				nextid += 1
			nextIDArray[iPlayer] = nextid
			sequenceArray[iPlayer] = "on"
		
		return mercenaries, nextIDArray, sequenceArray
		
	def saveMercenaryData(self, mercenaries, nextIDArray, sequenceArray):
		#BugUtil.debug("Mercenary Utils - saveMercenaryData")
		mercData = {
			AVAILABLE_MERCENARIES: mercenaries,
			UNIQUE_ID: nextIDArray,
			SEQUENCE: sequenceArray
		}
		BugData.getTable(SD_MOD_ID).setData(mercData)
	
	
	def getMercenaryUnit(self, iPlayer):
		#BugUtil.debug("Mercenary Utils - getMercenaryUnit")
		player = gc.getPlayer(iPlayer)
		
		iUnit = self.getRandomUnitType(player)
		Promotions, bElite = self.getPromotions(player, iUnit)
		iCost = self.getUnitCost(player, iUnit, bElite)		
				
		return { "UnitType" : iUnit, "Promotions" : Promotions, "Elite" : bElite, "Cost" : iCost }
		
		
	def getRandomUnitType(self, player):
		unitList = []		
		for iUnitClass in xrange(gc.getNumUnitClassInfos()):
			iUnit = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(iUnitClass)
			
			if iUnit == -1:
				continue	
			if player.isUnitClassMaxedOut(iUnitClass, 1):
				continue

			UnitInfo = gc.getUnitInfo(iUnit)
##			if UnitInfo.isAnimal():
##				continue
			if UnitInfo.getProductionCost() <= 0:
				continue
			if UnitInfo.getUnitCombatType() < 0:
				continue
			if self.isInvalidEra(player, iUnit):
				continue
			if self.isNotApproved(player, iUnit):
				continue
			
			unitList.append(iUnit)
		
		iRnd = gc.getGame().getMapRand().get(len(unitList), "Random Unit")
		
		return unitList[iRnd]
		
	#automatically upgrades units in the pool
	def updateMercenaries(self, mercenaries, iPlayer):
		UpdateDictionary = {}
		player = gc.getPlayer(iPlayer)
		
		for id in mercenaries[iPlayer]:
			iUnit = mercenaries[iPlayer][id]['UnitType']
			
			if self.isInvalidEra(player, iUnit):
				for k in xrange(gc.getNumUnitClassInfos()):
					eLoopUnit = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(k)
					
					if eLoopUnit == -1:
						continue
					if gc.getUnitInfo(eLoopUnit).getProductionCost() <= 0:
						continue
					if self.isInvalidEra(player, eLoopUnit):
						continue
					if self.isNotApproved(player, eLoopUnit):
						continue
					
					if (eLoopUnit >= 0 and gc.getUnitInfo(iUnit).getUpgradeUnitClass(k)):
						UpdateDictionary[id] = eLoopUnit
					
		for id in UpdateDictionary.keys():
			mercenaries[iPlayer][id]['UnitType'] = UpdateDictionary[id]
			mercenaries[iPlayer][id]['Cost'] = self.getUnitCost(gc.getPlayer(iPlayer), UpdateDictionary[id], mercenaries[iPlayer][id]['Elite'])
			
		return mercenaries
		
	def isInvalidEra(self, player, iUnit):
		UnitInfo = gc.getUnitInfo(iUnit)
		PrereqTechList = []
		iEra = player.getCurrentEra()
		bInvalidEra = true
		
		if UnitInfo.getPrereqAndTech() != -1:
			PrereqTechList.append(UnitInfo.getPrereqAndTech())
				
		for i in range(3):
			if UnitInfo.getPrereqAndTechs(i) != -1:
				PrereqTechList.append(UnitInfo.getPrereqAndTechs(i))
			
		for iTech in PrereqTechList:
			iTechEra = gc.getTechInfo(iTech).getEra()
			
			if iTech == -1:
				continue
			if iTechEra + 1 < iEra:
				continue
			if iTechEra > iEra:
				break
				
			bInvalidEra = false
			break
	
		return bInvalidEra
	
	# !M! -> With changes and additions:
	def isNotApproved(self, player, iUnit):
		if not hasattr(self, "lApprovedUnits"):
			self.lApprovedUnits = [
                                        UnitTypes.UNIT_ROCKET_TROOPER,
                                        UnitTypes.UNIT_MASTER_GUARDSMAN,
                                        UnitTypes.UNIT_GRENADE_TROOPER,
                                        UnitTypes.UNIT_MISSILE_TROOPER,
                                        UnitTypes.UNIT_HEAVY_TROOPER,
                                        UnitTypes.UNIT_LASGUN_SOLDIER,
                                        UnitTypes.UNIT_MONGOOSE_TROOPER,
                                        UnitTypes.UNIT_LASGUN_TROOPER,
                                        UnitTypes.UNIT_WASP,
                                        UnitTypes.UNIT_DRAGONFLY,
                                        UnitTypes.UNIT_CIELAGO,
                                        UnitTypes.UNIT_FIREFLY,
                                        UnitTypes.UNIT_LOCUST,
                                        UnitTypes.UNIT_BLADESMAN,
                                        UnitTypes.UNIT_HARDENED_BLADESMAN,
                                        UnitTypes.UNIT_SHIELD_FIGHTER,
                                        UnitTypes.UNIT_KINDJAL_SOLDIER,
                                        UnitTypes.UNIT_MAULA_MORTAR,
                                        UnitTypes.UNIT_ROCKET_ARTILLERY,
                                        UnitTypes.UNIT_MISSILE_LAUNCHER,
                                        UnitTypes.UNIT_ASSAULT_CANNON,
                                        UnitTypes.UNIT_SUSPENSOR_GUNSHIP,
                                        UnitTypes.UNIT_SUSPENSOR_FRIGATE,
					UnitTypes.UNIT_SUSPENSOR_DESTROYER,
                                        UnitTypes.UNIT_SUSPENSOR_CRUISER,
                                        UnitTypes.UNIT_VULTURE_THOPTER,
                                        UnitTypes.UNIT_EAGLE_THOPTER,
                                        UnitTypes.UNIT_BUZZARD_THOPTER,
                                        UnitTypes.UNIT_FALCON_THOPTER,
                                        UnitTypes.UNIT_QUAD,
                                        UnitTypes.UNIT_ROLLER,
                                        UnitTypes.UNIT_LIGHT_SCORPION,
                                        UnitTypes.UNIT_MEDIUM_SCORPION,
                                        UnitTypes.UNIT_HEAVY_SCORPION
				]
				
			self.lFremenUnits = [
                                        UnitTypes.UNIT_CRYSKNIFE_FIGHTER,
                                        UnitTypes.UNIT_FREMEN_RAIDER,
                                        UnitTypes.UNIT_NAIBS_CHOSEN,
                                        UnitTypes.UNIT_FEDAYKIN
				]
				
			self.lCorrinoUnits = [
                                        UnitTypes.UNIT_SARDAUKAR_LEGIONARY,
                                        UnitTypes.UNIT_SARDAUKAR_NOUKKER
				]
				
			self.lHarkonnenUnits = [
                                        UnitTypes.UNIT_DEVASTATOR,
                                        UnitTypes.UNIT_HOWITZER
				]				
			
			self.lAtreidesUnits = [
                                        UnitTypes.UNIT_HAWK_THOPTER,
                                        UnitTypes.UNIT_BEESTING,
                                        UnitTypes.UNIT_SONIC_TANK
				]

			self.lIxianUnits = [
                                        UnitTypes.UNIT_CRAWLER,
                                        UnitTypes.UNIT_WALKER,
                                        UnitTypes.UNIT_SPIDER,
                                        UnitTypes.UNIT_TARANTULA
				]

                        self.lOrdosUnits1 = [
                                        UnitTypes.UNIT_ROCKET_TROOPER,
                                        UnitTypes.UNIT_MASTER_GUARDSMAN,
                                        UnitTypes.UNIT_MISSILE_TROOPER,
                                        UnitTypes.UNIT_HEAVY_TROOPER,
                                        UnitTypes.UNIT_LASGUN_SOLDIER,
                                        UnitTypes.UNIT_MONGOOSE_TROOPER,
                                        UnitTypes.UNIT_LASGUN_TROOPER,
                                        UnitTypes.UNIT_WASP,
                                        UnitTypes.UNIT_DRAGONFLY,
                                        UnitTypes.UNIT_CIELAGO,
                                        UnitTypes.UNIT_FIREFLY,
                                        UnitTypes.UNIT_LOCUST,
                                        UnitTypes.UNIT_BLADESMAN,
                                        UnitTypes.UNIT_HARDENED_BLADESMAN,
                                        UnitTypes.UNIT_SHIELD_FIGHTER,
                                        UnitTypes.UNIT_KINDJAL_SOLDIER,
                                        UnitTypes.UNIT_MAULA_MORTAR,
                                        UnitTypes.UNIT_ROCKET_ARTILLERY,
                                        UnitTypes.UNIT_ASSAULT_CANNON,
                                        UnitTypes.UNIT_SUSPENSOR_GUNSHIP,
                                        UnitTypes.UNIT_SUSPENSOR_FRIGATE,
					UnitTypes.UNIT_SUSPENSOR_DESTROYER,
                                        UnitTypes.UNIT_SUSPENSOR_CRUISER,
                                        UnitTypes.UNIT_VULTURE_THOPTER,
                                        UnitTypes.UNIT_EAGLE_THOPTER,
                                        UnitTypes.UNIT_BUZZARD_THOPTER,
                                        UnitTypes.UNIT_FALCON_THOPTER,
                                        UnitTypes.UNIT_CRAWLER,
                                        UnitTypes.UNIT_WALKER,
                                        UnitTypes.UNIT_SPIDER,
                                        UnitTypes.UNIT_SARDAUKAR_LEGIONARY,
                                        UnitTypes.UNIT_SARDAUKAR_NOUKKER,
                                        UnitTypes.UNIT_DEVASTATOR,
                                        UnitTypes.UNIT_HOWITZER,
                                        UnitTypes.UNIT_HAWK_THOPTER,
                                        UnitTypes.UNIT_BEESTING,
                                        UnitTypes.UNIT_SONIC_TANK
				]

			self.lOrdosUnits2 = [
                                        UnitTypes.UNIT_CHEMICAL_TROOPER,
                                        UnitTypes.DEVIATOR,
                                        UnitTypes.UNIT_TRIKE,
                                        UnitTypes.UNIT_ORDOS_RAIDER,
                                        UnitTypes.UNIT_LIGHT_SCORPION,
                                        UnitTypes.UNIT_MEDIUM_SCORPION,
                                        UnitTypes.UNIT_HEAVY_SCORPION
                                ]

			self.lEcazUnits = [
                                        UnitTypes.UNIT_MASTER_GUARDSMAN,
                                        UnitTypes.UNIT_GRENADE_TROOPER,
                                        UnitTypes.UNIT_MISSILE_TROOPER,
                                        UnitTypes.UNIT_MONGOOSE_TROOPER,
                                        UnitTypes.UNIT_LASGUN_TROOPER,
                                        UnitTypes.UNIT_WASP,
                                        UnitTypes.UNIT_DRAGONFLY,
                                        UnitTypes.UNIT_CIELAGO,
                                        UnitTypes.UNIT_FIREFLY,
                                        UnitTypes.UNIT_LOCUST,
                                        UnitTypes.UNIT_SHIELD_FIGHTER,
                                        UnitTypes.UNIT_KINDJAL_SOLDIER,
                                        UnitTypes.UNIT_ROCKET_ARTILLERY,
                                        UnitTypes.UNIT_MISSILE_LAUNCHER,
                                        UnitTypes.UNIT_ASSAULT_CANNON,
                                        UnitTypes.UNIT_SUSPENSOR_GUNSHIP,
                                        UnitTypes.UNIT_SUSPENSOR_FRIGATE,
                                        UnitTypes.UNIT_VULTURE_THOPTER,
                                        UnitTypes.UNIT_EAGLE_THOPTER,
                                        UnitTypes.UNIT_BUZZARD_THOPTER,
                                        UnitTypes.UNIT_FALCON_THOPTER,
                                        UnitTypes.UNIT_ROLLER,
                                        UnitTypes.UNIT_LIGHT_SCORPION,
                                        UnitTypes.UNIT_MEDIUM_SCORPION,
                                        UnitTypes.UNIT_HEAVY_SCORPION,
                                        UnitTypes.UNIT_LASGUN_SOLDIER2,
                                        UnitTypes.UNIT_SUSPENSOR_CRUISER2,
                                        UnitTypes.UNIT_GLADIATOR
                                ]

			self.lRicheseUnits = [
                                        UnitTypes.UNIT_CHASER,
                                        UnitTypes.UNIT_SENTINEL,
                                        UnitTypes.UNIT_NO_CRUISER
                                ]

                iCivType = player.getCivilizationType()
                if not (iCivType == CivilizationTypes.ECAZ_CIV \
                        or iCivType == CivilizationTypes.ORDOS_CIV):
		        for i in self.lApprovedUnits:
			        if (i == iUnit):
				        return false

		if (iCivType == CivilizationTypes.FREMEN_CIV):
			for i in self.lFremenUnits:
				if (i == iUnit):
					return false
				
		elif (iCivType == CivilizationTypes.RICHESE_CIV):
			for i in self.lRicheseUnits:
				if (i == iUnit):
					return false
		
		elif (iCivType == CivilizationTypes.CORRINO_CIV):
			for i in self.lCorrinoUnits:
				if (i == iUnit):
					return false
		
		elif (iCivType == CivilizationTypes.HARK_CIV):
			for i in self.lHarkonnenUnits:
				if (i == iUnit):
					return false
		
		elif (iCivType == CivilizationTypes.ATREIDES_CIV):
			for i in self.lAtreidesUnits:
				if (i == iUnit):
					return false
		
		elif (iCivType == CivilizationTypes.IX_CIV):
			for i in self.lIxianUnits:
				if (i == iUnit):
					return false

		elif (iCivType == CivilizationTypes.ORDOS_CIV):
                        if CyGame().getSorenRandNum(100, "") < 58:
                                for i in self.lOrdosUnits1:
                                        if (i == iUnit):
                                                return false
                        else:
                                for i in self.lOrdosUnits2:
                                        if (i == iUnit):
                                                return false

		elif (iCivType == CivilizationTypes.ECAZ_CIV):
			for i in self.lEcazUnits:
				if (i == iUnit):
					return false
		
		return true

	def getPromotions(self, player, iUnit):
		UnitInfo = gc.getUnitInfo(iUnit)
		bElite = false
		PromotionList = ["PROMOTION_MERCENARY"]
		
		for i in xrange(gc.getNumTraitInfos()):
			if player.hasTrait(i):
				for k in xrange(gc.getNumPromotionInfos()):
					if gc.getTraitInfo(i).isFreePromotion(k):
						PromotionInfo = gc.getPromotionInfo(k)
						if PromotionInfo.getUnitCombat(UnitInfo.getUnitCombatType()):
							PromotionList.append(PromotionInfo.getType())
			
		iChance = g_iChanceForElite
		iRnd1 = gc.getGame().getMapRand().get(100, "Promotion Chance")

                # !M! -> Ordos better chance:
		if player.getCivilizationType() == CivilizationTypes.ORDOS_CIV:
                        iChance = 35
                        
		if iRnd1 <= iChance:
			bElite = true
			
		return PromotionList, bElite
		
	
	def getUnitCost(self, player, iUnit, bElite):
		UnitInfo = gc.getUnitInfo(iUnit)
		iHireCost = UnitInfo.getProductionCost()
				
		iHireCost *= g_iHireCostModifier
		iHireCost /= 100
		
		if bElite:
			iHireCost += iHireCost / 2
	
		return int(iHireCost)

	# !M! -> modified -> higher spawning rate for Ecaz and Ordos
	def getSpawningChance(self, iLen, player):
                iSpeed = CyGame().getGameSpeedType()
                iTrainPercent = gc.getGameSpeedInfo(iSpeed).getTrainPercent()
                iCivType = player.getCivilizationType()
                
                if iCivType == CivilizationTypes.ECAZ_CIV or iCivType == CivilizationTypes.ORDOS_CIV:
                        revisedSpawnChance = 2 * g_iSpawningChance / ( (iLen + 1.0) / g_iUnitPoolSizeSpawningDivisor)
                else:
                        # The next line makes spawning increasingly unlikely as the unit pool list grows long
                        revisedSpawnChance = g_iSpawningChance / ( (iLen + 1.0) / g_iUnitPoolSizeSpawningDivisor)
                        
                return int( revisedSpawnChance * (100.0 / iTrainPercent))
                
	def placeMercenaries(self, argsList):
		iData1, iData2, iData3, iData4, iData5 = argsList
		iPlayer = iData2
		iCity = iData3
		id = iData4
		player = gc.getPlayer(iPlayer)
			
		if (not BugData.getGameData().getTable(SD_MOD_ID).hasTable(AVAILABLE_MERCENARIES)):
			return
		if -1 in [iCity, id]:
			return
		
		mercenaries, nextIdArray, sequenceArray = self.loadMercenaryData(iPlayer)
		mercenary = mercenaries[iPlayer][id]
		iCost = mercenary['Cost']
		
		if iCost < 1:
			return
		if player.getGold() < iCost:
			return
		pCity = player.getCity(iCity)
		pUnit = player.initUnit(mercenary['UnitType'], pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_EAST)
                pUnit.finishMoves()
		player.changeGold(-iCost)
			
		for promotion in mercenary['Promotions']:
			iPromotion = gc.getInfoTypeForString(promotion)
			if iPromotion != -1: 
				pUnit.setHasPromotion(iPromotion, true)

                # !M! -> Unique Ecaz, Ordos, Richese mercs; promo settings
                iCivType = player.getCivilizationType()
		if iCivType == CivilizationTypes.ORDOS_CIV:
                        iMercCombatType = pUnit.getUnitCombatType()
                        if iMercCombatType == UnitCombatTypes.VEHICLE_COMBAT:
                                pUnit.setHasPromotion(PromotionTypes.PROMOTION_ORDOS_VEHICLE, True)
                                pUnit.setHasPromotion(PromotionTypes.PROMOTION_MERCENARY, False)
                        elif iMercCombatType == UnitCombatTypes.MECH_COMBAT:
                                pUnit.setHasPromotion(PromotionTypes.PROMOTION_IXIAN, True)
                elif iCivType == CivilizationTypes.ECAZ_CIV:
                        if pUnit.getUnitType() == UnitTypes.UNIT_GLADIATOR:
                                pUnit.setHasPromotion(PromotionTypes.PROMOTION_MERCENARY, False)
                elif iCivType == CivilizationTypes.RICHESE_CIV:
                        iMercCombatType = pUnit.getUnitCombatType()
                        if iMercCombatType == UnitCombatTypes.VEHICLE_COMBAT or \
                           iMercCombatType == UnitCombatTypes.THOPTER_COMBAT or \
                           iMercCombatType == UnitCombatTypes.SUSPENSOR_COMBAT or \
                           iMercCombatType == UnitCombatTypes.MECH_COMBAT:
                                pUnit.setHasPromotion(PromotionTypes.PROMOTION_NANOTECH, True);

		if mercenary['Elite']:
			pUnit.changeExperience(8, 99, false, false, false)
	
##		if g_bMercenaryDebug:
##			self.mercenaryLog(iPlayer, mercenary, pCity)
				
		szCiv = gc.getCivilizationInfo(iCivType).getType()
		szMessage = CyTranslator().getText("Reinforcements from %s1 have arrived at %s2.", (dictHomeworld[szCiv], pCity.getName()))
		CyInterface().addImmediateMessage(szMessage, "")
		
		del mercenaries[iPlayer][id]
		self.saveMercenaryData(mercenaries, nextIdArray, sequenceArray)
		
		if player != gc.getPlayer(gc.getGame().getActivePlayer()):
			CyEngine().triggerEffect(gc.getInfoTypeForString("EFFECT_STASIS"), pCity.plot().getPoint())
		
		return pCity, pUnit
		
	def mercenaryLog(self, iPlayer, mercenary, pCity):
		iUnit = int(mercenary['UnitType'])
		iCost = int(mercenary['Cost'])
		Promotions = mercenary['Promotions']
		UnitInfo = gc.getUnitInfo(iUnit)
		player = gc.getPlayer(iPlayer)
		bElite = mercenary['Elite']
		
		BugUtil.debug("***HOMEWORLD_START***************************")
		BugUtil.debug("Dune Wars Homeworld placing a unit!")
		BugUtil.debug("Turn: %d" , CyGame().getGameTurn())
		BugUtil.debug("Player name: %s" , player.getName())
		BugUtil.debug("Player gold: %d" , player.getGold())
		BugUtil.debug("Unit name: %s" , UnitInfo.getDescription())
		BugUtil.debug("Unit cost: %d" , iCost)
		BugUtil.debug("Elite: %s" , str(bElite))
		BugUtil.debug("Promotions: %s" , str(Promotions))
		BugUtil.debug("Destination: %s" , pCity.getName())
		BugUtil.debug("*****************************HOMEWORLD_END***")
		
	#!M! -> Modified
	def computerPlayerThink(self, iPlayer, mercenaries):
                if len(mercenaries[iPlayer]) < 1: return
		player = gc.getPlayer(iPlayer)
		if player.isHuman(): return
		if player.getNumCities() <= 0: return
		
		iTeam = player.getTeam()
		pTeam = gc.getTeam(iTeam)
		atWarCount = pTeam.getAtWarCount(True)
		currentGold = player.getGold()
		
		if atWarCount <= 0:
                        if currentGold < 125: return
                elif currentGold < 95: return
		
		baseMercenaryCount = (pTeam.getAnyWarPlanCount(True) * max(1, atWarCount)) + self.getMorePowerfulPlayerCount(iPlayer)
		randomMercCount = gc.getGame().getMapRand().get(baseMercenaryCount, "")
		
                if atWarCount < 1 and randomMercCount < 1: return
                
                pBestCityForLaunch = player.getCapitalCity()

                if atWarCount > 0:
                        pSight = player.firstUnit(false)[0]
                        if pSight == None: return
                        
                        iBestValue = 0     
                        (pCity, iter) = player.firstCity(false)
                        while (pCity):
                                iValue = 0
                                if pCity.plot().getNumDefenders(iPlayer) < 3 or pCity.isOccupation():
                                        iValue += 3
                                iAreaAIType = pCity.area().getAreaAIType(iTeam)
                                if iAreaAIType > -1 and iAreaAIType != 6:
                                        if iAreaAIType == 0:
                                                iValue += 4
                                        elif iAreaAIType == 1:
                                                iValue += 6
                                        else:
                                                iValue += 3
                                iX = pCity.getX(); iY = pCity.getY()
                                pClosestEnemyCity = CyMap().findCity(iX, iY, -1, -1, False, False, iTeam, -1, CyCity())
                                if not pClosestEnemyCity.isNone():
                                        iDistance = plotDistance(iX, iY, pClosestEnemyCity.getX(), pClosestEnemyCity.getY())
                                        if iDistance <= 10:
                                                iValue += (10 - iDistance)
                                for i in xrange(21):
                                        pLoopPlot = pCity.getCityIndexPlot(i)
                                        if not pLoopPlot.isNone():
                                                iValue += pLoopPlot.getNumVisibleEnemyDefenders(pSight)
                                                
                                if iValue > iBestValue:
                                        iBestValue = iValue
                                        pBestCityForLaunch = pCity
                                (pCity, iter) = player.nextCity(iter, false)

                        if iBestValue >= 12: randomMercCount += 1
                        if iBestValue >= 24: randomMercCount += 1
                                             
		for i in xrange(randomMercCount):
                        id, iCost = self.getBestAvailableMercenary(iPlayer, mercenaries, player.getGold())
			if -1 in [id, iCost]:
				continue			
                        self.placeMercenaries([-1, iPlayer, pBestCityForLaunch.getID(), id, -1])
		
	def getMorePowerfulPlayerCount(self, iPlayer):
		playerCount = 0
		player = gc.getPlayer(iPlayer)
		if(gc.getPlayer(iPlayer) == None):
			return 0
		
		for iPlay in xrange(gc.getMAX_CIV_PLAYERS()):
                        pPlay = gc.getPlayer(iPlay)
			if not pPlay.isAlive(): continue
			if pPlay.getPower() > (player.getPower() - 50):
				playerCount += 1
		
		return playerCount
		
	def getBestAvailableMercenary(self, iPlayer, mercenaries, iGold):
		hireCost = -1
		bestId = -1
				
		for id in mercenaries[iPlayer]:
			iCost = mercenaries[iPlayer][id]['Cost']
						
			if iCost > hireCost and iGold > iCost:
				hireCost = iCost
				bestId = id
				
		return bestId, hireCost

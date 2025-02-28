from kikit import panelize_ui_impl as ki
from kikit.units import mm, deg
from kikit.panelize import Panel, BasicGridPosition, Origin
from pcbnewTransition.pcbnew import LoadBoard, VECTOR2I
from pcbnewTransition import pcbnew
from itertools import chain



############### Custom config

board_list = ["../BIDIR_5V/BIDIR-5V.kicad_pcb", "../IN_24V/IN-24V.kicad_pcb", "../IN_ANA/IN-ANA.kicad_pcb", "../OUT_TORM/OUT_TORM.kicad_pcb"]
output_path = "./panneau.kicad_pcb"

# These numbers correspond to the index of the choosen board in board_list
panel_layout = [
	[0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2],
	[0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2]
]

board_spacing_h = 0
board_spacing_v = 5 * mm

################ KiKit Panel Config (Only deviations from default)

framing={
		"type": "frame", #only rail on top and bottom
		"vspace" : "0mm", # space between board and rail
		"hspace" : "0mm",
		"width": "8mm" # Width of the rail
	}
	
cuts =  {
		"type": "vcuts"
	}
tabs = { #Add tabs between board and board as well as board and rail
		"type":"spacing", #Place them with constant width and spacing 
		"vwidth": "5mm",
		"spacing" : "5mm"
	}
tooling = {
        "type": "none",
    }

fiducials = {
		"type": "4fid",
		"hoffset": "4mm",
		"voffset": "4mm",
		"coppersize": "1mm",
		"opening": "2mm"
	}

# Obtain full config by combining above with default
preset = ki.obtainPreset([], tabs=tabs, cuts=cuts, framing=framing, tooling=tooling, fiducials=fiducials)



################ Adjusted `panelize_ui#doPanelization`

# Prepare			
#board1 = LoadBoard(board1_path)
#board2 = LoadBoard(board2_path)
boards = []
for board_path in board_list:
	boards.append(LoadBoard(board_path))

panel = Panel(output_path)

panel.inheritDesignSettings(boards[0])
panel.inheritProperties(boards[0])
panel.inheritTitleBlock(boards[0])

###### Manually build layout. Inspired by `panelize_ui_impl#buildLayout`
#sourceArea1 = ki.readSourceArea(preset["source"], board1)
#sourceArea2 = ki.readSourceArea(preset["source"], board2)

sourceAreas = []
for b in boards:
	sourceAreas.append(ki.readSourceArea(preset["source"], b))

substrateCount = len(panel.substrates) # Store number of previous boards (probably 0)
# Prepare renaming nets and references
netRenamer = lambda x, y: "Board_{n}-{orig}".format(n=x, orig=y)
refRenamer = lambda x, y: "Board_{n}-{orig}".format(n=x, orig=y)

# Actually place the individual boards
# Use existing grid positioner
# Place two boards above each other
panelOrigin = VECTOR2I(0,0)
placer = BasicGridPosition(board_spacing_h, board_spacing_v) #HorSpace, VerSpace

last_area = None
inh_drc = True
#for i in range(len(boards)):
#	last_area = panel.appendBoard(board_list[i], panelOrigin + placer.position(i, 0, last_area), origin=Origin.Center, sourceArea=sourceAreas[i], netRenamer=netRenamer, refRenamer=refRenamer, inheritDrc=inh_drc)
#	inh_drc = False # Will be True once and then false for every other boards

for y in range(len(panel_layout)):
	for x in range(len(panel_layout[y])):
		board_index = panel_layout[y][x]
		board_pos = panelOrigin + placer.position(y, x, last_area)

		last_area = panel.appendBoard(board_list[board_index], board_pos, origin=Origin.Center, sourceArea=sourceAreas[board_index], netRenamer=netRenamer, refRenamer=refRenamer, inheritDrc=inh_drc)
		inh_drc = False # Will be True once and then false for every other boards


substrates = panel.substrates[substrateCount:] # Collect set of newly added boards

# Prepare frame and partition
framingSubstrates = ki.dummyFramingSubstrate(substrates, preset)
panel.buildPartitionLineFromBB(framingSubstrates)
backboneCuts = ki.buildBackBone(preset["layout"], panel, substrates, preset)


######## --------------------- Continue doPanelization

tabCuts = ki.buildTabs(preset, panel, substrates, framingSubstrates)

frameCuts = ki.buildFraming(preset, panel)


ki.buildTooling(preset, panel)
ki.buildFiducials(preset, panel)
for textSection in ["text", "text2", "text3", "text4"]:
	ki.buildText(preset[textSection], panel)
ki.buildPostprocessing(preset["post"], panel)

ki.makeTabCuts(preset, panel, tabCuts)
ki.makeOtherCuts(preset, panel, chain(backboneCuts, frameCuts))


ki.buildCopperfill(preset["copperfill"], panel)

ki.setStackup(preset["source"], panel)
ki.setPageSize(preset["page"], panel, boards[0])
ki.positionPanel(preset["page"], panel)

ki.runUserScript(preset["post"], panel)

ki.buildDebugAnnotation(preset["debug"], panel)

panel.save(reconstructArcs=preset["post"]["reconstructarcs"],
		   refillAllZones=preset["post"]["refillzones"])

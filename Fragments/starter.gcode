;STARTER
; EXECUTABLE_BLOCK_START
M73 P0 R37
M201 X500 Y500 Z100 E5000
M203 X500 Y500 Z10 E60
M204 P500 R1000 T500
M205 X8.00 Y8.00 Z0.40 E5.00 ; sets the jerk limits, mm/sec
;TYPE:Custom
G90 ; use absolute coordinates
M83 ; extruder relative mode
M140 S80 ; set final bed temp
M104 S150 ; set temporary nozzle temp to prevent oozing during homing
G4 S10 ; allow partial nozzle warmup
G28 ; home all axis
G1 Z50 F240
G1 X2 Y10 F3000
M104 S210 ; set final nozzle temp
M190 S80 ; wait for bed temp to stabilize
M109 S210 ; wait for nozzle temp to stabilize
G1 Z0.28 F240
G92 E0
G1 Y140 E10 F1500 ; prime the nozzle
M73 P1 R37
G1 X2.3 F5000
G92 E0
G1 Y10 E10 F1200 ; prime the nozzle
G92 E0
G90
G21
M83 ; use relative distances for extrusion
; filament start gcode
M106 S0
;LAYER_CHANGE
;Z:0.2
;HEIGHT:0.2
;BEFORE_LAYER_CHANGE
;0.2
G92 E0

G1 E-4 F3600
;_SET_FAN_SPEED_CHANGING_LAYER
G1 Z.6 F9000
G1 X101.071 Y100.932
G1 Z.6
G1 Z.2
G1 E4 F2400
;STARTER_END

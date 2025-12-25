;FINISHER
G1 E-2.8 F3600
;WIPE_START
G1 F2400
G1 X106.079 Y106.959 E-.7038
G1 X106.35 Y106.647 E-.4962
;WIPE_END
M106 S0
;TYPE:Custom
; filament end gcode 
G1 Z38.6 F600 ; Move print head up
G1 X5 Y176 F9000 ; present print
G1 Z106.6 F600 ; Move print head further up
G1 Z150 F600 ; Move print head further up
M140 S0 ; turn off heatbed
M104 S0 ; turn off temperature
M107 ; turn off fan
M84 X Y E ; disable motors
M73 P100 R0
;FINISHER_END

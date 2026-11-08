// memento_assembly.scad
// MEMENTO Exploded & Fitted Mechanical Assembly

use <01_front_housing.scad>
use <02_rear_clip_housing.scad>
use <03_button_actuators.scad>

$fn = 40;

// Exploded View Parameter: 0 = fully assembled, 1 = exploded
exploded = 0; 
offset = exploded ? 30 : 0;

// 1. Front Bezel Housing (Translucent / Matte Black PETG)
color([0.2, 0.2, 0.25, 0.85])
    translate([0, 0, offset * 2])
        front_housing();

// 2. 0.96" OLED Display Panel (Deep Blue / Glass)
color([0.1, 0.3, 0.6, 0.9])
    translate([46/2 - 14, 25 + 2 - 7.5, offset * 1.5 + 2])
        cube([28, 15, 1.2]);

// 3. MEMENTO 2-Layer FR4 PCB (Matte Black with ENIG Gold Contacts)
color([0.1, 0.1, 0.1, 1.0])
    translate([2, 2, offset * 1 + 3.0])
        difference() {
            cube([42, 75, 1.6]);
            // Mic acoustic hole
            translate([21, 62, -1]) cylinder(d=1.5, h=3.6);
        }

// 4. 1200mAh LiPo Battery (Silver Foil with Gold Kapton Tape)
color([0.8, 0.8, 0.85, 0.95])
    translate([46/2 - 17, 14, -offset * 0.5 - 4.5])
        cube([34, 50, 5.5]);

// 5. Rear Clip Housing (Matte Black PETG)
color([0.15, 0.15, 0.18, 0.9])
    translate([0, 0, -offset * 1.5 - 7.0])
        rear_housing();


// 01_front_housing.scad
// MEMENTO Front Bezel & Acoustic Port Housing
// Dimensions: 79mm x 46mm x 8mm (fits 75x42mm PCB with 2mm wall)

$fn = 60;

board_w = 42.0;
board_h = 75.0;
wall = 2.0;
corner_r = 5.0;
total_w = board_w + 2*wall;  // 46mm
total_h = board_h + 2*wall;  // 79mm
depth = 8.0;

module rounded_rect(w, h, r, d) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=d);
        translate([w-r, r, 0]) cylinder(r=r, h=d);
        translate([r, h-r, 0]) cylinder(r=r, h=d);
        translate([w-r, h-r, 0]) cylinder(r=r, h=d);
    }
}

module front_housing() {
    difference() {
        // Outer Shell
        rounded_rect(total_w, total_h, corner_r, depth);

        // Internal Cavity for PCB
        translate([wall, wall, wall])
            cube([board_w, board_h, depth]);

        // 0.96" OLED Window (28mm x 15mm)
        translate([total_w/2 - 14, 25 + wall - 7.5, -1])
            cube([28, 15, wall + 2]);

        // Front Chamfered Acoustic Mic Port (1.5mm hole with 45° funnel)
        translate([total_w/2, 62 + wall, -1]) {
            cylinder(d=1.5, h=wall + 2);
            translate([0, 0, 0]) cylinder(d1=4.0, d2=1.5, h=1.2);
        }

        // Side Mute Switch Cutout (Left Wall)
        translate([-1, 38 + wall - 3.5, 3])
            cube([wall + 2, 7, 3.5]);

        // Side Tactile Button Cutouts (Right Wall)
        // Record Button
        translate([total_w - wall - 1, 33 + wall - 2.5, 3])
            cube([wall + 2, 5, 3]);
        // Bookmark Button
        translate([total_w - wall - 1, 45 + wall - 2.5, 3])
            cube([wall + 2, 5, 3]);

        // Bottom USB-C and MicroSD Cutouts
        translate([10 + wall - 5, total_h - wall - 1, 2])
            cube([10, wall + 2, 4]); // USB-C
        translate([32 + wall - 6, total_h - wall - 1, 2])
            cube([12, wall + 2, 3]); // MicroSD
    }

    // Screw Bosses (M2.5) at 4 corners
    boss_coords = [
        [wall + 3.5, wall + 4.0],
        [total_w - wall - 3.5, wall + 4.0],
        [wall + 3.5, total_h - wall - 4.0],
        [total_w - wall - 3.5, total_h - wall - 4.0]
    ];
    for (pos = boss_coords) {
        translate([pos[0], pos[1], wall]) {
            difference() {
                cylinder(d=5.5, h=depth - wall);
                translate([0, 0, -1]) cylinder(d=2.0, h=depth - wall + 2); // Pilot hole for M2.5 screw
            }
        }
    }
}

front_housing();

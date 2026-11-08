// 02_rear_clip_housing.scad
// MEMENTO Rear Shell, 1200mAh LiPo Battery Cavity & Integrated Spring Lapel Clip

$fn = 60;

board_w = 42.0;
board_h = 75.0;
wall = 2.0;
corner_r = 5.0;
total_w = board_w + 2*wall;  // 46mm
total_h = board_h + 2*wall;  // 79mm
depth = 7.0;

module rounded_rect(w, h, r, d) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=d);
        translate([w-r, r, 0]) cylinder(r=r, h=d);
        translate([r, h-r, 0]) cylinder(r=r, h=d);
        translate([w-r, h-r, 0]) cylinder(r=r, h=d);
    }
}

module rear_housing() {
    difference() {
        // Outer Shell
        rounded_rect(total_w, total_h, corner_r, depth);

        // Battery Bay Cavity (fits 1200mAh 603450 LiPo: 50mm x 34mm x 6mm)
        translate([total_w/2 - 17, 12, wall])
            cube([34, 52, depth]);

        // M2.5 Counterbored Screw Holes
        boss_coords = [
            [wall + 3.5, wall + 4.0],
            [total_w - wall - 3.5, wall + 4.0],
            [wall + 3.5, total_h - wall - 4.0],
            [total_w - wall - 3.5, total_h - wall - 4.0]
        ];
        for (pos = boss_coords) {
            translate([pos[0], pos[1], -1]) {
                cylinder(d=2.8, h=depth + 2); // Thru hole
                cylinder(d=5.0, h=2.5);       // Counterbore for screw head
            }
        }

        // Top Lanyard Loop Cutout
        translate([total_w/2 - 4, 3, -1])
            cube([8, 3.5, depth + 2]);
    }

    // Integrated Spring-Steel / PETG Lapel Clip (on exterior back)
    translate([total_w/2 - 9, 20, -6.5]) {
        difference() {
            cube([18, 48, 6.5]);
            // Undercut for clothes/pocket fabric
            translate([0, 0, 1.8]) cube([18, 42, 3.2]);
            // Entry ramp angle
            translate([0, 42, 0]) rotate([15, 0, 0]) cube([18, 10, 8]);
        }
    }
}

rear_housing();


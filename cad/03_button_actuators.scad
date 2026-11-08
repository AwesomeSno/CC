// 03_button_actuators.scad
// MEMENTO Tactile Pushbutton Caps & Slide Mute Switch Knob

$fn = 40;

module tactile_button_cap() {
    difference() {
        cylinder(d=4.2, h=5.5);
        // Tactile switch plunger recess
        translate([0, 0, -0.5]) cylinder(d=2.4, h=2.0);
    }
    // Retention brim
    cylinder(d=6.0, h=0.8);
}

module mute_switch_knob() {
    difference() {
        cube([6.0, 4.0, 5.0], center=true);
        // Switch lever slot (1.5mm x 1.5mm)
        translate([0, 0, -1.0]) cube([1.8, 1.8, 4.0], center=true);
    }
    // Grippy texture ridges on top
    translate([-2, -1.5, 2.5]) cube([4, 0.6, 0.5]);
    translate([-2, 0.0, 2.5]) cube([4, 0.6, 0.5]);
    translate([-2, 1.5, 2.5]) cube([4, 0.6, 0.5]);
}

// Layout for printing
translate([0, 0, 0]) tactile_button_cap(); // REC button
translate([10, 0, 0]) tactile_button_cap(); // MARK button
translate([22, 0, 2.5]) mute_switch_knob(); // MUTE knob


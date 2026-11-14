$fn = 64;

/* [Size] */
// Outer box width (X)
width = 200;
// Outer box depth (Y)
depth = 100;
// Lid height
height_top = 10;
// Bottom part height up to the rim (lip not included)
height_bottom = 60;
// Wall thickness
wall = 2;

/* [Fit] */
// Mechanical clearance between moving parts
clearance = 0.3;
// Height of the stepped lip that locks the lid sideways
lip_height = 3;
// Gap between the lid recess and the lip
lip_gap = 0.2;

/* [Hinges] */
// Distance from box side to the hinges
hinge_from_wall = 10;
// Width of the hinges
hinge_width = 10;

/* [Latch] */
// Latch size
latch_width = 5;

/* [Output] */
// bottom: body, lid: lid in print orientation, lid_closed: lid in closed position, all: preview
part = "all"; // [bottom, lid, lid_closed, all]

hinge_distance = width / 2 - hinge_from_wall - hinge_width / 2;

// Latch ridge profile on the bottom part: x = outward from the wall, y = down from the top
ridge_depth = 1.5;
ridge_base = 3.5;
ridge_tip = 2;
ridge_drop = 1.3; // distance from the rim to the top of the ridge
ridge_points = [
        [-0.5, 0], // extends into the wall so the ridge fuses with it
        [0, 0],
        [ridge_depth, (ridge_base - ridge_tip) / 2],
        [ridge_depth, (ridge_base - ridge_tip) / 2 + ridge_tip],
        [0, ridge_base],
        [-0.5, ridge_base]
    ];

latch_thickness = 3;
latch_height = 5.68;
latch_arm_width = latch_width + 10;

// Hinge pin (bottom part) and socket (lid) cones
pin_radius = 2.4;
pin_height = 1.0;
socket_radius = 2.8;
socket_height = 1.25;

module box_with_cutout(width, depth, height, wall) {
    difference() {
        translate([-width / 2, -depth / 2, 0])
            cube([width, depth, height]);

        translate([-width / 2 + wall, -depth / 2 + wall, wall])
            // +1 keeps the cut-out open at the top
            cube([width - wall * 2, depth - wall * 2, height - wall + 1]);
    }
}

// Inner half of the bottom wall rising above the rim
module lip() {
    translate([0, 0, height_bottom - 0.01])
        linear_extrude(height = lip_height + 0.01)
            difference() {
                square([width - wall, depth - wall], center = true);
                square([width - wall * 2, depth - wall * 2], center = true);
            }
}

// Pocket in the lid rim that receives the lip
module lip_recess() {
    inset = wall / 2 - lip_gap;
    translate([-width / 2 + inset, -depth / 2 + inset, height_top - lip_height - lip_gap])
        cube([width - inset * 2, depth - inset * 2, lip_height + lip_gap + 1]);
}

module bottom_latch() {
    translate([-latch_width / 2, -depth / 2, height_bottom - ridge_drop])
        rotate([90, 180, 90])
            linear_extrude(height = latch_width)
                polygon(points = ridge_points);
}

module bottom_hinge() {
    w = hinge_width + 2.5; // outer width of the two arms
    dist = 2.8; // distance from the wall
    d = 5; // diameter of circle
    t = 2.5; // thickness
    ft = 2.5; // from top

    module arm() {
        translate([-t / 2, depth / 2 + dist, height_bottom - ft])
            rotate([90, 180, 90])
                linear_extrude(height = t)
                    difference() {
                        union() {
                            circle(d = d);
                            translate([0, -d / 2, 0])
                                square([dist, d + d / 2]);
                        }

                        translate([0, (dist + d / 2), 0])
                            circle(d = dist * 2);
                    }

        // anchor inside the wall
        translate([-t / 2, depth / 2 - 1, height_bottom - ft - 4])
            cube([t, 1.3, 6]);
    }

    module pin() {
        rotate([0, 90, 0])
            rotate_extrude()
                polygon(points = [[0, 0], [pin_radius, 0], [0, pin_height]]);
    }

    translate([hinge_distance, 0, 0]) {
        translate([w / 2, 0, 0]) arm();
        translate([-w / 2, 0, 0]) arm();

        translate([-w / 2 + t / 2, depth / 2 + dist, height_bottom - ft])
            pin();

        translate([w / 2 - t / 2, depth / 2 + dist, height_bottom - ft])
            rotate([0, 180, 0])
                pin();
    }
}

module lid_latch() {
    some_radius = 2;

    translate([-latch_arm_width / 2, depth / 2 + latch_thickness / 2, height_top + latch_height / 2])
        rotate([90, 0, 90])
            difference() {
                linear_extrude(height = latch_arm_width) {
                    union() {
                        square([latch_thickness, latch_height], center = true);

                        translate([0, latch_height / 2, 0])
                            circle(d = latch_thickness);

                        intersection() {
                            translate([-some_radius + latch_thickness / 2, -latch_height / 2, 0])
                                circle(r = some_radius);

                            translate([0, -latch_height / 2, 0])
                                square([latch_thickness, latch_height], center = true);
                        }

                        translate([-latch_thickness / 2, -6.6, 0])
                            difference() {
                                square([some_radius, some_radius]);

                                translate([some_radius, 0, 0])
                                    circle(r = some_radius);
                            }
                    }
                }

                // window for the bottom ridge, enlarged by the clearance
                translate([-latch_thickness / 2 - 0.01, ridge_drop - latch_height / 2, latch_arm_width / 2])
                    linear_extrude(height = latch_width + 2 * clearance, center = true)
                        offset(delta = clearance)
                            polygon(points = ridge_points);
            }

    // anchor inside the lid wall
    translate([-latch_arm_width / 2, depth / 2 - 0.5, height_top - 3])
        cube([latch_arm_width, 1.1, 3.8]);
}

module lid_hinge() {
    a = 8.817;
    b = 3.714;
    c = 5.6;
    e = 5.214;
    knuckle_width = hinge_width - 2 * clearance;
    offset_from_top = -1.1;

    socket_points = [[0, 0], [socket_radius, 0], [0, socket_height]];

    module knuckle() {
        translate([-knuckle_width / 2, -depth / 2 - c / 2, a / 2 + height_top - e])
            rotate([90, -180, 90])
                difference() {
                    linear_extrude(height = knuckle_width)
                        union() {
                            translate([0, -(a - b) / 2, 0])
                                square([c, b], center = true);

                            translate([0, -a / 2, 0])
                                circle(d = c);

                            intersection() {
                                translate([-c / 2, -(c * 2 - a) / 2, 0])
                                    circle(r = c);

                                square([c, a], center = true);
                            }
                        }

                    translate([0, -a / 2, -0.01])
                        rotate_extrude()
                            polygon(points = socket_points);

                    translate([0, -a / 2, knuckle_width + 0.01])
                        rotate([180, 0, 0])
                            rotate_extrude()
                                polygon(points = socket_points);
                }

        // anchor inside the lid wall
        translate([-knuckle_width / 2, -depth / 2 - 0.6, height_top - 5 - offset_from_top])
            cube([knuckle_width, 1.1, 5]);
    }

    for (x = [hinge_distance, -hinge_distance])
        translate([x, 0, offset_from_top])
            knuckle();
}

module bottom_part() {
    box_with_cutout(width, depth, height_bottom, wall);
    lip();
    bottom_latch();
    bottom_hinge();
}

// Print orientation: outer top face on the bed, hinge on -Y, latch on +Y
module lid_part() {
    difference() {
        box_with_cutout(width, depth, height_top, wall);
        lip_recess();
    }
    lid_latch();
    lid_hinge();
}

// Flipped around X so the hinge ends up on +Y, matching the bottom part
module lid_closed() {
    translate([0, 0, height_bottom + height_top])
        rotate([180, 0, 0])
            lid_part();
}

if (part == "bottom") {
    bottom_part();
} else if (part == "lid") {
    lid_part();
} else if (part == "lid_closed") {
    lid_closed();
} else {
    color([0, 1, 1])
        bottom_part();
    color([1, 1, 0])
        translate([0, depth + 15, 0])
            lid_part();
}

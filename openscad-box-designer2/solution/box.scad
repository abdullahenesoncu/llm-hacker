include <BOSL2/std.scad>

$fn = 64;

/* [Size] */
// Box width
width = 200; // [30:1:256]
// Box depth
depth = 100; // [30:1:256]
// Lid height
height_top = 10; // [10:1:256]
// Bottom part height
height_bottom = 60; // [10:1:256]
// Wall thickness
wall = 2;

/* [Hinges] */
// Distance from box side to the hinges
hinge_from_wall = 10; // [7:1:120]
// Width of the hinges
hinge_width = 10; // [4:1:50]


/* [Other] */
// Show as two separate pieces
exploded = false;
// Which part to render: all, bottom, top, hinge_bottom or hinge_top
show = "all"; // [all:bottom:top:hinge_bottom:hinge_top]

// Simple parser
function parse_string(input_str) =
let(
    // Split the input string into blocks (separated by spaces)
    blocks = [for (s = str_split(input_str, " ")) s],

    // Process each block into its own array
    result = [for (block = blocks)
        let(
            // First character is the type (v or h)
            type = substr(block, 0, 1),
            // Rest is numbers separated by commas
            numbers_str = substr(block, 1),
            // Split numbers by comma and convert to numbers
            numbers = [for (n = str_split(numbers_str, ",")) is_letter(n) ? n : parse_float(n)]
        )
        concat([type], numbers)
        ]
)
result;

// Actual code
module box() {
    hinge_distance = width / 2 - hinge_from_wall - hinge_width / 2;

    module box_with_cutout(width, depth, height, wall) {
        difference() {
            translate([-width / 2, -depth / 2, 0])
                cube([width, depth, height]);

            translate([-width / 2 + wall, -depth / 2 + wall, wall])
                // +1 is for fixing geometry in openscad
                cube([width - wall * 2, depth - wall * 2, height - wall + 1]);
        }
    }

    module top_part(body = true, hinge = true) {

        module hinge_2() {
            a = 8.817;
            b = 3.714;
            c = 5.6;
            e = 5.214;
            hinge_depth = hinge_width - 0.3; // depth
            offset_from_top = -1.1; // from top

            points = [
                    [0, 0],
                    [2.5, 0],
                    [0, 0.9]
                ];

            module hinge_2_1() {
                translate([-hinge_depth / 2, -depth / 2 - c / 2, a / 2 + height_top - e])
                    rotate([90, -180, 90])
                        difference() {
                            linear_extrude(height = hinge_depth)
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

                            translate([0, -a / 2, 0])
                                rotate_extrude()
                                    polygon(points = points);

                            translate([0.15, -a / 2, hinge_depth + 0.01])
                                rotate([180, 0, 0])
                                    rotate_extrude()
                                        polygon(points = points);

                        }
            }

            translate([hinge_distance, 0, offset_from_top])
                hinge_2_1();

            translate([-hinge_distance, 0, offset_from_top])
                hinge_2_1();

        }

        if (body)
            box_with_cutout(width, depth, height_top, wall);

        if (hinge)
            hinge_2();
    }

    module bottom_part(body = true, hinge = true) {

        module hinge_1() {
            w = hinge_width + 2.5; // width
            dist = 2.8; // distance from the wall
            d = 5; // diameter of circle
            t = 2.5; // thickness
            ft = 2.5; // from top
            h = 1.0; // height of cone
            r = 2.4; // radius of cone

            module hinge_1_1(dist, d, t, ft) {
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
            }

            module hinge_1_2(h) {
                points = [
                        [0, 0],
                        [r, 0],
                        [0, h]
                    ];

                rotate([0, 90, 0])
                    rotate_extrude()
                        polygon(points = points);
            }


            translate([hinge_distance, 0, 0])
                union() {
                    translate([w / 2, 0, 0])
                        hinge_1_1(dist = dist, d = d, t = t, ft = ft);
                    translate([-w / 2, 0, 0])
                        hinge_1_1(dist = dist, d = d, t = t, ft = ft);

                    translate([-w / 2 + t / 2, depth / 2 + dist, height_bottom - ft])
                        hinge_1_2(h = h);

                    translate([w / 2 - t / 2, depth / 2 + dist, height_bottom - ft])
                        rotate([0, 180, 0])
                            hinge_1_2(h = h);
                }

            translate([-hinge_distance, 0, 0])
                union() {
                    translate([w / 2, 0, 0])
                        hinge_1_1(dist = dist, d = d, t = t, ft = ft);
                    translate([-w / 2, 0, 0])
                        hinge_1_1(dist = dist, d = d, t = t, ft = ft);

                    translate([-w / 2 + t / 2, depth / 2 + dist, height_bottom - ft])
                        hinge_1_2(h = h);

                    translate([w / 2 - t / 2, depth / 2 + dist, height_bottom - ft])
                        rotate([0, 180, 0])
                            hinge_1_2(h = h);
                }
        }

        if (hinge)
            hinge_1();

        if (body)
            box_with_cutout(width, depth, height_bottom, wall);
    }

    module placed_top(body, hinge) {
        if (exploded)
            translate([0, depth + 15, 0])
                top_part(body, hinge);
        else
            translate([0, 0, height_bottom + height_top])
                rotate([180, 0, 0])
                    top_part(body, hinge);
    }

    if (show == "all" || show == "top")
        color([1, 1, 0, 0.5]) placed_top(true, false);

    if (show == "all" || show == "hinge_top")
        color([1, 0.5, 0, 0.5]) placed_top(false, true);

    if (show == "all" || show == "bottom")
        color([0, 1, 1, 0.2]) bottom_part(true, false);

    if (show == "all" || show == "hinge_bottom")
        color([0, 0.5, 1, 0.2]) bottom_part(false, true);
}

box();

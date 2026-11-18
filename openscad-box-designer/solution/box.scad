/* Parametric captive-hinge storage box. Units: mm.
 * Coordinates: X width, Y front-to-back, Z up. Closed configuration.
 * Export: openscad --export-format binstl -o bottom.stl -D 'show="bottom"' box.scad
 * Opening is -180 degrees about the journal axis; closing reverses that path.
 * Separate +180 degrees from closed is NOT a permissible motion.
 * The four files are intended for printing together in their native coordinates.
 * Body/hinge keyed interfaces have zero clearance (rigid, contacting interfaces).
 * Journal cavities have 0.4 mm diametral clearance; captive flanges have
 * 0.25 mm axial clearance on either side. Journals rest against cavity floors.
 */
show = "all";
width=200;
depth=100;
body_height=60;
lid_height=10;
wall=2;
hinge_count=2;
station_inset=30;
fit=0.25;
rim_height=2;
rim_inset=wall+fit;
lid_z=body_height-rim_height+fit;
axis_y=depth+14;
axis_z=lid_z;
stations=[station_inset,width-station_inset];
$fn=128;
shaft_r=2.5;
radial_gap=0.2;
flange_r=3.8;
cup_r=6;
key_width=12;
body_key_z=44;
lid_key_z=lid_z+2;
assert(hinge_count==2,"This layout uses exactly two stations.");
assert(width>2*station_inset+30 && wall>0 && fit>0);
assert(show=="all" || show=="bottom" || show=="top" ||
       show=="hinge_bottom" || show=="hinge_top","Unknown show selector");

module block(x0,x1,y0,y1,z0,z1) {
    translate([x0,y0,z0]) cube([x1-x0,y1-y0,z1-z0]);
}
module xcylinder(x0,x1,y,z,r,phase=0) {
    translate([x0,y,z]) rotate([0,90,0]) rotate([0,0,phase])
        cylinder(h=x1-x0,r=r);
}
module frame(inset,z0,z1) {
    difference() {
        block(inset,width-inset,inset,depth-inset,z0,z1);
        block(inset+wall,width-inset-wall,inset+wall,depth-inset-wall,z0-1,z1+1);
    }
}
// T-heads cannot leave their enclosing sockets by straight translation.
module mounting_key(x,z) {
    union() {
        block(x-4,x+4,depth,depth+4,z+1,z+5);
        block(x-key_width/2,x+key_width/2,depth+3,depth+6,z,z+6);
    }
}
module bottom() {
    union() {
        difference() {
            block(0,width,0,depth,0,body_height-rim_height);
            block(wall,width-wall,wall,depth-wall,wall,body_height-2*rim_height);
            block(rim_inset+wall,width-rim_inset-wall,
                  rim_inset+wall,depth-rim_inset-wall,wall,body_height+1);
        }
        frame(rim_inset,body_height-rim_height,body_height);
        for(x=stations) mounting_key(x,body_key_z);
    }
}
module top() {
    union() {
        difference() {
            block(0,width,0,depth,lid_z,lid_z+lid_height);
            block(wall,width-wall,wall,depth-wall,lid_z-1,lid_z+lid_height-wall);
        }
        for(x=stations) mounting_key(x,lid_key_z);
    }
}
module stationary_blank(x) {
    block(x-9,x+9,depth,depth+8,body_key_z-2,body_key_z+8);
    block(x-9,x+9,depth+2,axis_y+6,body_key_z,body_key_z+4);
    for(side=[-1,1]) {
        a=side<0 ? x-14 : x+6.25;
        b=side<0 ? x-6.25 : x+14;
        xcylinder(a,b,axis_y,axis_z,cup_r);
        block(a,b,axis_y,axis_y+cup_r,body_key_z+2,axis_z);
    }
}
module bearing_cavities(x) {
    // Circumscribed bore polygons contain the true circular shaft envelope.
    // Their bottom facets touch the shaft's bottom vertex along X at rest.
    for(side=[-1,1]) {
        a=side<0 ? x-11.75 : x+6;
        b=side<0 ? x-6 : x+11.75;
        xcylinder(a,b,axis_y,axis_z+radial_gap,
                  (shaft_r+radial_gap)/cos(180/$fn),180/$fn);
        fa=side<0 ? x-11.25 : x+8.75;
        fb=side<0 ? x-8.75 : x+11.25;
        xcylinder(fa,fb,axis_y,axis_z,
                  (flange_r+radial_gap)/cos(180/$fn),180/$fn);
    }
}
module hinge_bottom() {
    difference() {
        union() {
            for(x=stations) stationary_blank(x);
            // Connect both stations into one printable, connected mesh.
            block(stations[0],stations[1],axis_y+2,axis_y+6,body_key_z,body_key_z+3);
        }
        for(x=stations) {
            mounting_key(x,body_key_z);
            bearing_cavities(x);
        }
    }
}
module rotating_blank(x) {
    block(x-8,x+8,depth,depth+7,lid_z+1,lid_z+9);
    hull() {
        xcylinder(x-4,x+4,depth+6,lid_z+5,2);
        xcylinder(x-4,x+4,axis_y,axis_z,2);
    }
    xcylinder(x-11.5,x+11.5,axis_y,axis_z,shaft_r);
    xcylinder(x-11,x-9,axis_y,axis_z,flange_r);
    xcylinder(x+9,x+11,axis_y,axis_z,flange_r);
}
module hinge_top() {
    difference() {
        union() {
            for(x=stations) rotating_blank(x);
            block(stations[0],stations[1],depth,depth+3,lid_z+4,lid_z+6);
        }
        for(x=stations) mounting_key(x,lid_key_z);
    }
}
if(show=="bottom") bottom();
if(show=="top") top();
if(show=="hinge_bottom") hinge_bottom();
if(show=="hinge_top") hinge_top();
if(show=="all") {
    color("lightgray") bottom();
    color([0.3,0.6,0.9,0.6]) top();
    color("orange") hinge_bottom();
    color("gold") hinge_top();
}

# FreeCAD Python Script - Heating Control Faceplate V6
# Run this script inside FreeCAD: Macro > Macros > Run
# 
# This creates a faceplate for a UK 2-gang dry lining box with:
# - 3x BILRESA mounting plate pockets (accessible from back) - VERTICAL
# - 3x LED holes (10.75mm)
# - 3x Shelly 1PM Mini Gen4 housings on the back (tighter fit)
# - 2x screw holes (120mm centres, vertically centred)
# - Designed to fit Appleby 2-gang 35mm dry lining box
# 
# V6 changes:
# - BILRESA plates now in pockets accessible from back of faceplate
#   -> Slide plates in after printing, no pause needed
#   -> Thin front wall lets magnet work through
# - Removed embedded pocket approach (slicer bridging issues)

import FreeCAD
import Part
from FreeCAD import Vector
import math

# ============================================================
# PARAMETERS - Adjust these as needed
# ============================================================

# UK 2-gang faceplate dimensions (mm)
FACEPLATE_WIDTH = 146.0
FACEPLATE_HEIGHT = 86.0
FACEPLATE_THICKNESS = 4.0  # Total thickness of faceplate

# Screw holes
SCREW_SPACING = 120.0  # Centre to centre (UK 2-gang standard)
SCREW_DIAMETER = 4.0   # M3.5/M4 screws typical
SCREW_COUNTERSINK_DIAMETER = 8.0
SCREW_COUNTERSINK_DEPTH = 2.0

# BILRESA mounting plate (stadium/pill shape)
# Physical dimensions: 47mm long x 16.6mm wide
# Will be mounted VERTICALLY (47mm in Y direction)
# SURFACE MOUNT: plates sit in shallow 0.5mm recess on front
BILRESA_LENGTH = 47.0
BILRESA_WIDTH = 16.6
BILRESA_THICKNESS = 0.5
BILRESA_CORNER_RADIUS = 8.3  # Half of width for stadium ends

# Number of BILRESA plates
NUM_BILRESA = 3

# BILRESA spacing
BILRESA_SPACING = 40.0  # Centre to centre between plates

# LED holes
LED_HOLE_DIAMETER = 10.75
LED_HEAD_DIAMETER = 11.6  # For countersink/recess
LED_COUNTERSINK_DEPTH = 1.0

# LED position (above BILRESA)

# BILRESA back pocket parameters
BILRESA_FRONT_WALL = 1.0        # Thin wall between plate and front surface (magnet works through)
BILRESA_POCKET_DEPTH = 0.7      # Depth of pocket (plates are 0.5mm, +0.2mm Z clearance)
BILRESA_CLEARANCE = 0.2         # XY clearance around plates for easy slide-in

# Shelly 1PM Mini Gen4 dimensions (mm)
SHELLY_WIDTH = 35.0   # X dimension (side to side)
SHELLY_HEIGHT = 29.0  # Y dimension (top to bottom in housing)
SHELLY_DEPTH = 16.0   # Z dimension (how far it sticks out)

# Shelly housing parameters
SHELLY_WALL_THICKNESS = 2.0    # Thickness of cradle walls
SHELLY_LIP_HEIGHT = 2.0        # Height of retention lips
SHELLY_LIP_DEPTH = 1.5         # How far lips protrude inward
SHELLY_CLEARANCE = -0.75       # Tighter fit (was -0.25, now 0.5mm tighter)
SHELLY_SHELF_THICKNESS = 2.0   # Thickness of bottom shelf


# ============================================================
# MAIN MODEL CREATION
# ============================================================

def create_faceplate():
    """Create the complete faceplate model"""
    
    # Create new document
    doc = FreeCAD.newDocument("HeatingFaceplate")
    
    # ------------------------------------------------------------
    # Base faceplate
    # ------------------------------------------------------------
    base_box = Part.makeBox(
        FACEPLATE_WIDTH, 
        FACEPLATE_HEIGHT, 
        FACEPLATE_THICKNESS,
        Vector(-FACEPLATE_WIDTH/2, -FACEPLATE_HEIGHT/2, 0)
    )
    
    faceplate = base_box
    
    # ------------------------------------------------------------
    # Screw holes (120mm apart, centred vertically)
    # ------------------------------------------------------------
    screw_positions = [
        Vector(-SCREW_SPACING/2, 0, 0),
        Vector(SCREW_SPACING/2, 0, 0)
    ]
    
    for pos in screw_positions:
        # Through hole
        screw_hole = Part.makeCylinder(
            SCREW_DIAMETER/2,
            FACEPLATE_THICKNESS + 1,
            pos + Vector(0, 0, -0.5),
            Vector(0, 0, 1)
        )
        faceplate = faceplate.cut(screw_hole)
        
        # Countersink on front (wide at surface, narrow inside)
        # Cone goes from small radius to large radius along Z direction
        # So we start at the inner point and go outward to the front surface
        countersink = Part.makeCone(
            SCREW_DIAMETER/2,              # Small radius (inner, at depth)
            SCREW_COUNTERSINK_DIAMETER/2,  # Large radius (outer, at front surface)
            SCREW_COUNTERSINK_DEPTH,
            pos + Vector(0, 0, FACEPLATE_THICKNESS - SCREW_COUNTERSINK_DEPTH),
            Vector(0, 0, 1)
        )
        faceplate = faceplate.cut(countersink)
    
    # ------------------------------------------------------------
    # BILRESA mounting plate pockets (VERTICAL orientation)
    # Back-accessible pocket: plates slide in from behind after printing
    # Thin front wall lets magnet work through
    # Using rounded rectangle (box with fillet) for stadium shape
    # ------------------------------------------------------------
    bilresa_y_pos = -12.0  # Dropped lower for more LED clearance
    
    bilresa_positions = []
    total_span = BILRESA_SPACING * (NUM_BILRESA - 1)
    start_x = -total_span / 2
    
    for i in range(NUM_BILRESA):
        x = start_x + (i * BILRESA_SPACING)
        bilresa_positions.append(Vector(x, bilresa_y_pos, 0))
    
    # Pocket dimensions (slightly oversized for easy slide-in)
    pocket_width = BILRESA_WIDTH + BILRESA_CLEARANCE
    pocket_length = BILRESA_LENGTH + BILRESA_CLEARANCE
    pocket_corner_radius = BILRESA_CORNER_RADIUS + BILRESA_CLEARANCE/2
    
    # Pocket Z position: accessible from back (Z=0), with thin front wall
    # Front surface is at Z = FACEPLATE_THICKNESS (4mm)
    # Front wall thickness = BILRESA_FRONT_WALL (1mm)
    # So pocket starts at Z = 0 (back) and goes to Z = FACEPLATE_THICKNESS - BILRESA_FRONT_WALL
    pocket_z_depth = FACEPLATE_THICKNESS - BILRESA_FRONT_WALL  # How deep the pocket goes from the back
    
    for pos in bilresa_positions:
        # Create box for pocket - VERTICAL: width along X, length along Y
        # Starts at Z=0 (back surface) and extends inward
        pocket_box = Part.makeBox(
            pocket_width,
            pocket_length,
            pocket_z_depth,
            Vector(pos.x - pocket_width/2, pos.y - pocket_length/2, 0)
        )
        
        # Round the vertical edges to make stadium shape
        # Select edges parallel to Z axis (the 4 vertical corners)
        edges_to_fillet = []
        for edge in pocket_box.Edges:
            # Check if edge is parallel to Z axis
            if edge.Vertexes[0].X == edge.Vertexes[1].X and \
               edge.Vertexes[0].Y == edge.Vertexes[1].Y:
                edges_to_fillet.append(edge)
        
        if edges_to_fillet:
            try:
                pocket = pocket_box.makeFillet(pocket_corner_radius - 0.1, edges_to_fillet)
            except:
                pocket = pocket_box  # Fall back to square if fillet fails
        else:
            pocket = pocket_box
            
        faceplate = faceplate.cut(pocket)
    
    # ------------------------------------------------------------
    # LED holes (fixed Y position, not relative to BILRESA)
    # ------------------------------------------------------------
    led_y_pos = 30.0  # Absolute Y position for LEDs
    
    for i, pos in enumerate(bilresa_positions):
        led_pos = Vector(pos.x, led_y_pos, 0)  # Same X as BILRESA, fixed Y
        
        # Through hole for LED body
        led_hole = Part.makeCylinder(
            LED_HOLE_DIAMETER/2,
            FACEPLATE_THICKNESS + 1,
            led_pos + Vector(0, 0, -0.5),
            Vector(0, 0, 1)
        )
        faceplate = faceplate.cut(led_hole)
        
        # Countersink/recess for LED head on front surface
        led_recess = Part.makeCylinder(
            LED_HEAD_DIAMETER/2,
            LED_COUNTERSINK_DEPTH + 0.1,
            led_pos + Vector(0, 0, FACEPLATE_THICKNESS - LED_COUNTERSINK_DEPTH),
            Vector(0, 0, 1)
        )
        faceplate = faceplate.cut(led_recess)
    
    # ------------------------------------------------------------
    # Shelly 1PM Mini Gen4 housings on back
    # Three cradles with shelf, lips, and side guides
    # Positioned at bottom of faceplate, aligned with BILRESA switches
    # ------------------------------------------------------------
    
    # Internal dimensions of cradle (with clearance)
    cradle_internal_width = SHELLY_WIDTH + SHELLY_CLEARANCE
    cradle_internal_height = SHELLY_HEIGHT + SHELLY_CLEARANCE
    
    # External dimensions of cradle
    cradle_external_width = cradle_internal_width + (2 * SHELLY_WALL_THICKNESS)
    cradle_external_height = cradle_internal_height + SHELLY_SHELF_THICKNESS
    
    # How far the cradle extends from back of faceplate
    cradle_depth = SHELLY_DEPTH + SHELLY_SHELF_THICKNESS
    
    # Y position - towards bottom of faceplate but within inner box dimensions
    # Faceplate Y range: -43 to +43 (half of 86mm)
    # Inner box height: 69.5mm, so inner Y range: -34.75 to +34.75
    shelly_y_pos = -FACEPLATE_HEIGHT/2 + cradle_external_height/2 + 6.0  # Raised 4mm total (was 2mm from bottom)
    
    shelly_housings = Part.Shape()  # Empty shape to collect all housing parts
    
    for i, bilresa_pos in enumerate(bilresa_positions):
        # Centre each Shelly housing under its BILRESA switch (same X position)
        shelly_x = bilresa_pos.x
        
        # Z positions: faceplate is 0 to THICKNESS, cradles extend backwards from 0 into negative Z
        z_back = -cradle_depth  # Back of cradle
        z_front = 0             # Front of cradle (touching faceplate back)
        
        # --- Bottom shelf ---
        shelf = Part.makeBox(
            cradle_external_width,
            SHELLY_SHELF_THICKNESS,
            cradle_depth,
            Vector(
                shelly_x - cradle_external_width/2,
                shelly_y_pos - cradle_external_height/2,
                z_back
            )
        )
        
        # --- Shelf lip (at back edge, stops Shelly sliding out) ---
        shelf_lip = Part.makeBox(
            cradle_internal_width,
            SHELLY_LIP_DEPTH,
            SHELLY_LIP_HEIGHT,
            Vector(
                shelly_x - cradle_internal_width/2,
                shelly_y_pos - cradle_external_height/2 + SHELLY_SHELF_THICKNESS,
                z_back
            )
        )
        
        # --- Left side guide ---
        left_guide = Part.makeBox(
            SHELLY_WALL_THICKNESS,
            cradle_internal_height,
            cradle_depth,
            Vector(
                shelly_x - cradle_external_width/2,
                shelly_y_pos - cradle_external_height/2 + SHELLY_SHELF_THICKNESS,
                z_back
            )
        )
        
        # --- Left side lip (inward at back) ---
        left_lip = Part.makeBox(
            SHELLY_LIP_DEPTH,
            cradle_internal_height,
            SHELLY_LIP_HEIGHT,
            Vector(
                shelly_x - cradle_external_width/2 + SHELLY_WALL_THICKNESS,
                shelly_y_pos - cradle_external_height/2 + SHELLY_SHELF_THICKNESS,
                z_back
            )
        )
        
        # --- Right side guide ---
        right_guide = Part.makeBox(
            SHELLY_WALL_THICKNESS,
            cradle_internal_height,
            cradle_depth,
            Vector(
                shelly_x + cradle_external_width/2 - SHELLY_WALL_THICKNESS,
                shelly_y_pos - cradle_external_height/2 + SHELLY_SHELF_THICKNESS,
                z_back
            )
        )
        
        # --- Right side lip (inward at back) ---
        right_lip = Part.makeBox(
            SHELLY_LIP_DEPTH,
            cradle_internal_height,
            SHELLY_LIP_HEIGHT,
            Vector(
                shelly_x + cradle_external_width/2 - SHELLY_WALL_THICKNESS - SHELLY_LIP_DEPTH,
                shelly_y_pos - cradle_external_height/2 + SHELLY_SHELF_THICKNESS,
                z_back
            )
        )
        
        # Fuse all parts of this cradle together
        cradle = shelf.fuse(shelf_lip)
        cradle = cradle.fuse(left_guide)
        cradle = cradle.fuse(left_lip)
        cradle = cradle.fuse(right_guide)
        cradle = cradle.fuse(right_lip)
        
        # Add to housings collection
        if shelly_housings.isNull():
            shelly_housings = cradle
        else:
            shelly_housings = shelly_housings.fuse(cradle)
    
    # Fuse housings onto the back of the faceplate
    faceplate = faceplate.fuse(shelly_housings)
    
    # ------------------------------------------------------------
    # Add faceplate to document
    # ------------------------------------------------------------
    faceplate_obj = doc.addObject("Part::Feature", "HeatingFaceplate")
    faceplate_obj.Shape = faceplate
    
    # ------------------------------------------------------------
    # Create separate BILRESA plate objects for reference (visual only)
    # These show where the plates will sit IN the shallow recesses on front
    # ------------------------------------------------------------
    for i, pos in enumerate(bilresa_positions):
        # Plate sits against the front wall of the pocket (pushed in from back)
        plate_z = pocket_z_depth - BILRESA_THICKNESS  # Against front wall
        
        plate_box = Part.makeBox(
            BILRESA_WIDTH,
            BILRESA_LENGTH,
            BILRESA_THICKNESS,
            Vector(
                pos.x - BILRESA_WIDTH/2, 
                pos.y - BILRESA_LENGTH/2, 
                plate_z
            )
        )
        
        # Try to round the corners
        edges_to_fillet = []
        for edge in plate_box.Edges:
            if edge.Vertexes[0].X == edge.Vertexes[1].X and \
               edge.Vertexes[0].Y == edge.Vertexes[1].Y:
                edges_to_fillet.append(edge)
        
        if edges_to_fillet:
            try:
                plate = plate_box.makeFillet(BILRESA_CORNER_RADIUS - 0.1, edges_to_fillet)
            except:
                plate = plate_box
        else:
            plate = plate_box
            
        plate_obj = doc.addObject("Part::Feature", f"BILRESA_Plate_{i+1}")
        plate_obj.Shape = plate
        plate_obj.ViewObject.Transparency = 50
    
    # ------------------------------------------------------------
    # Create reference Shelly objects for visualization
    # ------------------------------------------------------------
    for i, bilresa_pos in enumerate(bilresa_positions):
        shelly_x = bilresa_pos.x
        
        shelly_box = Part.makeBox(
            SHELLY_WIDTH,
            SHELLY_HEIGHT,
            SHELLY_DEPTH,
            Vector(
                shelly_x - SHELLY_WIDTH/2,
                shelly_y_pos - cradle_external_height/2 + SHELLY_SHELF_THICKNESS + SHELLY_CLEARANCE/2,
                -cradle_depth + SHELLY_SHELF_THICKNESS  # Sits on shelf at back
            )
        )
        
        shelly_obj = doc.addObject("Part::Feature", f"Shelly_{i+1}")
        shelly_obj.Shape = shelly_box
        shelly_obj.ViewObject.Transparency = 70
        shelly_obj.ViewObject.ShapeColor = (0.2, 0.4, 0.8)  # Blue tint
    
    # Recompute
    doc.recompute()
    
    # Set view
    try:
        FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
        FreeCADGui.ActiveDocument.ActiveView.fitAll()
    except:
        pass
    
    print("=" * 60)
    print("Heating Control Faceplate V6 created!")
    print("=" * 60)
    print(f"Faceplate size: {FACEPLATE_WIDTH} x {FACEPLATE_HEIGHT} x {FACEPLATE_THICKNESS} mm")
    print(f"Screw spacing: {SCREW_SPACING} mm (centred)")
    print(f"BILRESA pockets: {NUM_BILRESA}x VERTICAL ({BILRESA_LENGTH}mm x {BILRESA_WIDTH}mm)")
    print(f"  -> Back-accessible: {pocket_z_depth}mm deep, {BILRESA_FRONT_WALL}mm front wall")
    print(f"  -> Slide plates in from back after printing")
    print(f"  -> Position: Y={bilresa_y_pos}mm")
    print(f"LED holes: {NUM_BILRESA}x ({LED_HOLE_DIAMETER}mm)")
    print(f"Shelly housings: {NUM_BILRESA}x cradles on back (tighter fit)")
    print(f"  -> Shelly size: {SHELLY_WIDTH} x {SHELLY_HEIGHT} x {SHELLY_DEPTH} mm")
    print(f"  -> Cradle depth: {cradle_depth} mm from back surface")
    print("=" * 60)
    
    return doc


# Run if executed as macro
if __name__ == "__main__":
    try:
        import FreeCADGui
        create_faceplate()
    except:
        print("Run this script from within FreeCAD")
        print("Macro > Macros > select this file > Run")
import ezdxf
import os
import time

class CADGenerator:
    """
    Generates automated architectural 2D DXF files for floorplans.
    """
    def __init__(self):
        self.output_dir = "assets/engineering"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_room(self, length_ft, width_ft, wall_thickness_in=6, window_size_ft=5):
        """
        Parametrically generates a standard architectural room layout.
        Outputs a .dxf file saved to disk.
        """
        # Create a new DXF R2010 document
        doc = ezdxf.new('R2010')
        doc.header['$INSUNITS'] = 1  # 1 = Inches
        
        msp = doc.modelspace()
        
        # Convert all to inches for precise AutoCAD scale
        l_in = length_ft * 12
        w_in = width_ft * 12
        t = wall_thickness_in
        
        # Define Layers
        doc.layers.add("WALLS", color=7) # White/Black
        doc.layers.add("WINDOWS", color=5) # Blue
        doc.layers.add("DIMENSIONS", color=3) # Green
        
        # Draw Outer Wall Rectangle
        outer_points = [(0, 0), (l_in, 0), (l_in, w_in), (0, w_in)]
        msp.add_lwpolyline(outer_points, close=True, dxfattribs={'layer': 'WALLS'})
        
        # Draw Inner Wall Rectangle
        inner_points = [(t, t), (l_in - t, t), (l_in - t, w_in - t), (t, w_in - t)]
        msp.add_lwpolyline(inner_points, close=True, dxfattribs={'layer': 'WALLS'})
        
        # --- Add a basic Window on the South (Bottom) wall ---
        win_size_in = window_size_ft * 12
        # Center the window
        win_start = (l_in / 2) - (win_size_in / 2)
        win_end = (l_in / 2) + (win_size_in / 2)
        
        # Cut the wall line visually by drawing the window block
        # Outer window sill
        msp.add_line((win_start, 0), (win_end, 0), dxfattribs={'layer': 'WINDOWS'})
        # Inner window sill
        msp.add_line((win_start, t), (win_end, t), dxfattribs={'layer': 'WINDOWS'})
        # Glass pane (middle)
        msp.add_line((win_start, t/2), (win_end, t/2), dxfattribs={'layer': 'WINDOWS'})
        
        # Generating filename
        filename = f"room_{length_ft}x{width_ft}_{int(time.time())}.dxf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc.saveas(filepath)
        
        return filepath

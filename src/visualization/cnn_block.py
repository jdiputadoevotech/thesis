import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from _style import apply_style, save_figure, COLORS

def draw_tilted_plate(ax, cx, cy, w, h, color, alpha=0.5, edgecolor=None, linewidth=1.0):
    """Draws a 3D-like tilted rectangle (isometric projection) centered at (cx, cy)."""
    tilt_x = 0.15
    tilt_y = 0.25
    
    # Vertices of the parallelogram
    dx = w / 2.0
    dy = h / 2.0
    
    # Coordinates of 4 corners
    x = [
        cx - dx + dy * tilt_x,
        cx + dx + dy * tilt_x,
        cx + dx - dy * tilt_x,
        cx - dx - dy * tilt_x
    ]
    y = [
        cy + dy + dx * tilt_y,
        cy + dy - dx * tilt_y,
        cy - dy - dx * tilt_y,
        cy - dy + dx * tilt_y
    ]
    
    if edgecolor is None:
        edgecolor = COLORS['primary']
        
    poly = patches.Polygon(
        list(zip(x, y)), 
        facecolor=color, 
        edgecolor=edgecolor, 
        alpha=alpha, 
        linewidth=linewidth,
        zorder=3
    )
    ax.add_patch(poly)
    return x, y

def create_cnn_block_figure():
    apply_style()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-3.2, 3.2)
    ax.axis('off')
    
    # --- Input Layer (Single channel) ---
    in_cx, in_cy = 0.8, 0.0
    in_w, in_h = 1.6, 1.6
    # Draw background box
    draw_tilted_plate(ax, in_cx, in_cy, in_w, in_h, COLORS['bg_box'], alpha=0.9, linewidth=1.2)
    # Put a letter 'a' inside it to show it's a glyph crop
    ax.text(in_cx, in_cy, "a", fontname='Times New Roman', fontsize=45, 
            ha='center', va='center', color=COLORS['primary'], alpha=0.85, zorder=4)
    # Kernel on Input
    k_size = 0.3
    k_x, k_y = in_cx + 0.2, in_cy + 0.3
    draw_tilted_plate(ax, k_x, k_y, k_size, k_size, COLORS['accent_rose'], alpha=0.8, edgecolor=COLORS['accent_rose'])
    
    # --- Conv 1 Layer (6 channels stacked) ---
    c1_cx, c1_cy = 2.8, 0.0
    c1_w, c1_h = 1.3, 1.3
    c1_channels = 6
    c1_offset = 0.08
    
    # Draw stack
    for i in range(c1_channels):
        draw_tilted_plate(ax, c1_cx + i * c1_offset, c1_cy + i * c1_offset, 
                          c1_w, c1_h, COLORS['accent_teal'], alpha=0.35, linewidth=0.8)
    
    # Add kernel mapping lines from input to conv1
    # Connect corners of kernel in Input to first layer of Conv 1
    # First layer of Conv 1 center is c1_cx, c1_cy. Target feature point:
    tp1_x, tp1_y = c1_cx + 0.1, c1_cy + 0.25
    ax.plot([k_x + k_size/2, tp1_x], [k_y + k_size/2, tp1_y], color=COLORS['accent_rose'], linestyle=':', linewidth=0.8, zorder=5)
    ax.plot([k_x - k_size/2, tp1_x], [k_y - k_size/2, tp1_y], color=COLORS['accent_rose'], linestyle=':', linewidth=0.8, zorder=5)
    # Highlight the target point
    ax.scatter(tp1_x, tp1_y, color=COLORS['accent_rose'], s=8, zorder=6)
    
    # Kernel on Conv 1
    k1_size = 0.25
    k1_x, k1_y = c1_cx + (c1_channels-1)*c1_offset + 0.15, c1_cy + (c1_channels-1)*c1_offset + 0.2
    draw_tilted_plate(ax, k1_x, k1_y, k1_size, k1_size, COLORS['accent_orange'], alpha=0.9, edgecolor=COLORS['accent_orange'])
    
    # --- Pool 1 Layer (6 channels stacked, smaller size) ---
    p1_cx, p1_cy = 4.6, 0.0
    p1_w, p1_h = 0.8, 0.8
    p1_channels = 6
    p1_offset = 0.06
    
    for i in range(p1_channels):
        draw_tilted_plate(ax, p1_cx + i * p1_offset, p1_cy + i * p1_offset, 
                          p1_w, p1_h, COLORS['accent_teal'], alpha=0.25, linewidth=0.6)
        
    # Mapping from Conv 1 kernel to Pool 1
    tp2_x, tp2_y = p1_cx + 0.08, p1_cy + 0.15
    ax.plot([k1_x + k1_size/2, tp2_x], [k1_y + k1_size/2, tp2_y], color=COLORS['accent_orange'], linestyle=':', linewidth=0.8, zorder=5)
    ax.plot([k1_x - k1_size/2, tp2_x], [k1_y - k1_size/2, tp2_y], color=COLORS['accent_orange'], linestyle=':', linewidth=0.8, zorder=5)
    ax.scatter(tp2_x, tp2_y, color=COLORS['accent_orange'], s=6, zorder=6)
    
    # --- Conv 2 Layer (10 channels stacked, even smaller) ---
    c2_cx, c2_cy = 6.2, 0.0
    c2_w, c2_h = 0.6, 0.6
    c2_channels = 10
    c2_offset = 0.04
    
    for i in range(c2_channels):
        draw_tilted_plate(ax, c2_cx + i * c2_offset, c2_cy + i * c2_offset, 
                          c2_w, c2_h, COLORS['accent_blue'], alpha=0.3, linewidth=0.5)
        
    # --- Pool 2 Layer (10 channels stacked, smallest) ---
    p2_cx, p2_cy = 7.6, 0.0
    p2_w, p2_h = 0.35, 0.35
    p2_channels = 10
    p2_offset = 0.03
    
    for i in range(p2_channels):
        draw_tilted_plate(ax, p2_cx + i * p2_offset, p2_cy + i * p2_offset, 
                          p2_w, p2_h, COLORS['accent_blue'], alpha=0.2, linewidth=0.4)
        
    # --- Fully Connected / Flatten Block ---
    # Draw vertical vector representation
    fc_x = 9.0
    fc_ys = np.linspace(-1.8, 1.8, 12)
    # Backing box
    ax.add_patch(patches.Rectangle((fc_x - 0.15, -2.0), 0.3, 4.0, 
                                   facecolor=COLORS['bg_box'], edgecolor=COLORS['muted'], 
                                   alpha=0.8, zorder=2))
    ax.scatter([fc_x]*len(fc_ys), fc_ys, color=COLORS['accent_rose'], s=25, edgecolor=COLORS['primary'], zorder=4)
    ax.text(fc_x, 2.2, "Flattened\nVector", fontsize=8, ha='center', weight='bold')
    
    # Draw lines connecting Pool 2 to Flatten vector
    p2_last_x = p2_cx + (p2_channels-1)*p2_offset
    p2_last_y = p2_cy + (p2_channels-1)*p2_offset
    for y_dest in fc_ys[::2]: # Draw a few connection lines to avoid clutter
        ax.plot([p2_last_x, fc_x - 0.15], [p2_last_y, y_dest], color=COLORS['muted'], alpha=0.25, linewidth=0.6, zorder=1)
        
    # --- Output / Embedding Layer ---
    out_x = 10.2
    out_ys = np.linspace(-1.0, 1.0, 6)
    ax.add_patch(patches.Rectangle((out_x - 0.15, -1.2), 0.3, 2.4, 
                                   facecolor=COLORS['bg_box'], edgecolor=COLORS['accent_teal'], 
                                   linewidth=1.2, alpha=0.9, zorder=2))
    ax.scatter([out_x]*len(out_ys), out_ys, color=COLORS['accent_teal'], s=35, edgecolor=COLORS['primary'], zorder=4)
    ax.text(out_x, 1.4, "Font Style\nEmbedding", fontsize=8, ha='center', weight='bold', color=COLORS['accent_teal'])
    
    # Connect FC to Output
    for y_src in fc_ys:
        for y_dest in out_ys:
            ax.plot([fc_x, out_x - 0.15], [y_src, y_dest], color=COLORS['accent_teal'], alpha=0.08, linewidth=0.4, zorder=1)
            
    # --- Structural/Layer Labels at the bottom ---
    y_label_pos = -2.6
    ax.text(in_cx, y_label_pos, "Input Glyph Crop\n(64 × 64 × 1)", ha='center', va='top', fontsize=8.5, weight='bold')
    ax.text(c1_cx + 0.2, y_label_pos, "Convolution\n(60 × 60 × 8)\n5×5 Kernel", ha='center', va='top', fontsize=8.5)
    ax.text(p1_cx + 0.2, y_label_pos, "Max-Pool\n(30 × 30 × 8)\n2×2 Stride 2", ha='center', va='top', fontsize=8.5)
    ax.text(c2_cx + 0.2, y_label_pos, "Convolution\n(26 × 26 × 16)\n5×5 Kernel", ha='center', va='top', fontsize=8.5)
    ax.text(p2_cx + 0.15, y_label_pos, "Max-Pool\n(13 × 13 × 16)\n2×2 Stride 2", ha='center', va='top', fontsize=8.5)
    ax.text(fc_x, y_label_pos - 0.1, "Fully\nConnected", ha='center', va='top', fontsize=8.5)
    ax.text(out_x, y_label_pos - 0.1, "Output\nMetric\nEmbedding", ha='center', va='top', fontsize=8.5, color=COLORS['accent_teal'], weight='bold')
    
    # Draw flow arrows between blocks
    arrow_style = dict(arrowstyle="->", color=COLORS['primary'], lw=1.5)
    ax.annotate("", xy=(c1_cx - 0.4, 0), xytext=(in_cx + 0.9, 0), arrowprops=arrow_style)
    ax.annotate("", xy=(p1_cx - 0.2, 0), xytext=(c1_cx + 0.8, 0), arrowprops=arrow_style)
    ax.annotate("", xy=(c2_cx - 0.2, 0), xytext=(p1_cx + 0.6, 0), arrowprops=arrow_style)
    ax.annotate("", xy=(p2_cx - 0.2, 0), xytext=(c2_cx + 0.6, 0), arrowprops=arrow_style)
    
    plt.tight_layout()
    save_figure(fig, "cnn_block")
    plt.close()

if __name__ == '__main__':
    create_cnn_block_figure()

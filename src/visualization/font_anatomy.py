import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from _style import apply_style, save_figure, COLORS

def create_font_anatomy_figure():
    apply_style()
    
    # Create figure with 2 subplots (Top: x-Height & Metrics; Bottom: Four Font Families Panel)
    fig = plt.figure(figsize=(10, 6.5))
    
    # ----------------------------------------------------
    # Top Panel: Font Metrics and x-Height Demonstration
    # ----------------------------------------------------
    ax_top = plt.subplot2grid((3, 4), (0, 0), colspan=4, rowspan=1)
    ax_top.set_xlim(-0.5, 4.5)
    ax_top.set_ylim(-1.2, 1.8)
    ax_top.axis('off')
    
    # Draw guides
    ax_top.axhline(1.4, color=COLORS['muted'], linestyle='--', linewidth=0.8)  # Cap height
    ax_top.axhline(0.8, color=COLORS['accent_teal'], linestyle='--', linewidth=1.0) # Mean line / x-height
    ax_top.axhline(0.0, color=COLORS['primary'], linestyle='-', linewidth=1.2)   # Baseline
    ax_top.axhline(-0.7, color=COLORS['muted'], linestyle='--', linewidth=0.8) # Descender line
    
    # Add text labels for guide lines
    ax_top.text(-0.4, 1.45, "Cap Height", color=COLORS['muted'], fontsize=8, va='bottom', weight='bold')
    ax_top.text(-0.4, 0.85, "Mean Line (x-Height)", color=COLORS['accent_teal'], fontsize=8, va='bottom', weight='bold')
    ax_top.text(-0.4, 0.05, "Baseline", color=COLORS['primary'], fontsize=8, va='bottom', weight='bold')
    ax_top.text(-0.4, -0.65, "Descender Line", color=COLORS['muted'], fontsize=8, va='top', weight='bold')
    
    # Render letters demonstrating metrics: "h", "x", "p"
    # Using Georgia (Serif) for clear metrics
    font_props = {'fontname': 'Georgia', 'fontsize': 70, 'color': COLORS['text']}
    
    # Render letters side-by-side
    ax_top.text(1.0, 0, "h", ha='center', va='baseline', **font_props)
    ax_top.text(2.0, 0, "x", ha='center', va='baseline', **font_props)
    ax_top.text(3.0, 0, "p", ha='center', va='baseline', **font_props)
    
    # Draw dimension annotations
    # x-height dimension arrow
    ax_top.annotate('', xy=(2.0, 0.8), xytext=(2.0, 0),
                    arrowprops=dict(arrowstyle='<->', color=COLORS['accent_teal'], linewidth=1.5))
    ax_top.text(2.1, 0.4, "x-Height", color=COLORS['accent_teal'], fontsize=9, va='center', weight='bold')
    
    # Ascender height arrow
    ax_top.annotate('', xy=(1.0, 1.4), xytext=(1.0, 0.8),
                    arrowprops=dict(arrowstyle='<->', color=COLORS['accent_blue'], linewidth=1.2))
    ax_top.text(1.1, 1.1, "Ascender", color=COLORS['accent_blue'], fontsize=8, va='center')
    
    # Descender depth arrow
    ax_top.annotate('', xy=(3.0, -0.7), xytext=(3.0, 0),
                    arrowprops=dict(arrowstyle='<->', color=COLORS['accent_rose'], linewidth=1.2))
    ax_top.text(3.1, -0.35, "Descender", color=COLORS['accent_rose'], fontsize=8, va='center')
    
    ax_top.set_title("Standard Typographic Dimensions & Font Metrics", weight='bold', pad=15)
    
    # ----------------------------------------------------
    # Bottom Panel: Four Font Families and Structural Traits
    # ----------------------------------------------------
    families = [
        {'name': 'Serif', 'font': 'Times New Roman', 'letter': 'e', 'desc': 'Terminal serifs & high stroke contrast'},
        {'name': 'Sans-Serif', 'font': 'Arial', 'letter': 'e', 'desc': 'Clean terminals & uniform stroke width'},
        {'name': 'Display', 'font': 'Impact', 'letter': 'e', 'desc': 'Heavy weight & stylized counters'},
        {'name': 'Monospace', 'font': 'Courier New', 'letter': 'e', 'desc': 'Fixed width & constant spacing'}
    ]
    
    for idx, fam in enumerate(families):
        ax = plt.subplot2grid((3, 4), (1, idx), colspan=1, rowspan=2)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Draw a bounding box for monospace or for clean framing
        box_color = COLORS['bg_box'] if fam['name'] != 'Monospace' else '#E2E8F0'
        rect = patches.FancyBboxPatch((-0.9, -0.9), 1.8, 1.8, boxstyle="round,pad=0.05",
                                     edgecolor=COLORS['muted'], facecolor=box_color, 
                                     linestyle='--' if fam['name'] == 'Monospace' else '-', linewidth=0.8)
        ax.add_patch(rect)
        
        # Render glyph
        ax.text(0, -0.3, fam['letter'], fontname=fam['font'], fontsize=90, 
                ha='center', va='center', color=COLORS['primary'], weight='normal')
        
        # Label family name
        ax.text(0, 0.7, fam['name'], fontsize=11, weight='bold', ha='center', color=COLORS['text'])
        
        # Short description below
        ax.text(0, -0.7, fam['desc'], fontsize=7.5, ha='center', va='center', 
                color=COLORS['muted'], wrap=True)
        
        # Add family-specific callouts
        if fam['name'] == 'Serif':
            # Terminal/Serif callout
            ax.annotate('Serif\nTerminal', xy=(0.35, -0.22), xytext=(0.6, -0.5),
                        arrowprops=dict(arrowstyle='->', color=COLORS['accent_rose'], linewidth=1),
                        fontsize=7, color=COLORS['accent_rose'], weight='bold', ha='center')
            # Stroke contrast callout
            ax.annotate('Thin\nStroke', xy=(0.0, 0.1), xytext=(-0.5, 0.35),
                        arrowprops=dict(arrowstyle='->', color=COLORS['accent_teal'], linewidth=1),
                        fontsize=7, color=COLORS['accent_teal'], weight='bold', ha='center')
            # Counter callout
            ax.annotate('Enclosed\nCounter', xy=(-0.1, -0.1), xytext=(-0.6, -0.5),
                        arrowprops=dict(arrowstyle='->', color=COLORS['accent_blue'], linewidth=1),
                        fontsize=7, color=COLORS['accent_blue'], weight='bold', ha='center')
            
        elif fam['name'] == 'Sans-Serif':
            # Clean terminal callout
            ax.annotate('Clean\nTerminal', xy=(0.38, -0.18), xytext=(0.6, -0.5),
                        arrowprops=dict(arrowstyle='->', color=COLORS['accent_teal'], linewidth=1),
                        fontsize=7, color=COLORS['accent_teal'], weight='bold', ha='center')
            # Uniform stroke width callout
            ax.annotate('Uniform\nStroke', xy=(-0.4, -0.05), xytext=(-0.65, 0.3),
                        arrowprops=dict(arrowstyle='->', color=COLORS['muted'], linewidth=1),
                        fontsize=7, color=COLORS['muted'], weight='bold', ha='center')
            
        elif fam['name'] == 'Display':
            # Extreme contrast callout
            ax.annotate('Heavy\nWeight', xy=(-0.35, -0.1), xytext=(-0.6, 0.35),
                        arrowprops=dict(arrowstyle='->', color=COLORS['accent_orange'], linewidth=1),
                        fontsize=7, color=COLORS['accent_orange'], weight='bold', ha='center')
            # Tiny/compressed counter callout
            ax.annotate('Compressed\nCounter', xy=(-0.05, 0.22), xytext=(0.55, 0.4),
                        arrowprops=dict(arrowstyle='->', color=COLORS['accent_rose'], linewidth=1),
                        fontsize=7, color=COLORS['accent_rose'], weight='bold', ha='center')
            
        elif fam['name'] == 'Monospace':
            # Show equal width boundaries
            ax.axvline(-0.6, color=COLORS['accent_teal'], linestyle=':', linewidth=1.0)
            ax.axvline(0.6, color=COLORS['accent_teal'], linestyle=':', linewidth=1.0)
            ax.text(0, 0.5, "Fixed Width Box", color=COLORS['accent_teal'], fontsize=7, ha='center')
            
    plt.tight_layout()
    save_figure(fig, "font_anatomy")
    plt.close()

if __name__ == '__main__':
    create_font_anatomy_figure()

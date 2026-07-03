import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from _style import apply_style, save_figure, COLORS

def draw_matplotlib_flowchart(filepath):
    """Fallback function to draw a high-quality flowchart using Matplotlib 
    if the system Graphviz binary is not available.
    """
    apply_style()
    
    fig, ax = plt.subplots(figsize=(8.5, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    # Helper to draw rounded boxes
    def draw_box(cx, cy, w, h, text, title=None, facecolor='#F1F5F9', edgecolor=COLORS['primary'], textcolor=COLORS['text'], shape='box'):
        dx = w / 2
        dy = h / 2
        
        if shape == 'box':
            rect = patches.FancyBboxPatch((cx - dx, cy - dy), w, h, boxstyle="round,pad=0.03",
                                         edgecolor=edgecolor, facecolor=facecolor, linewidth=1.2, zorder=3)
            ax.add_patch(rect)
        elif shape == 'diamond':
            # Drawing a diamond polygon
            pts = [[cx - dx, cy], [cx, cy + dy], [cx + dx, cy], [cx, cy - dy]]
            poly = patches.Polygon(pts, facecolor=facecolor, edgecolor=edgecolor, linewidth=1.2, zorder=3)
            ax.add_patch(poly)
        elif shape == 'document':
            # Document shape (rect with cut bottom corner)
            rect = patches.Rectangle((cx - dx, cy - dy), w, h, facecolor=facecolor, edgecolor=edgecolor, linewidth=1.2, zorder=3)
            ax.add_patch(rect)
            
        # Draw Text
        if title:
            ax.text(cx, cy + 0.1, title, fontsize=9.5, weight='bold', ha='center', va='bottom', color=textcolor, zorder=4)
            ax.text(cx, cy - 0.05, text, fontsize=8.5, ha='center', va='top', color=COLORS['muted'], zorder=4)
        else:
            ax.text(cx, cy, text, fontsize=9.5, weight='bold', ha='center', va='center', color=textcolor, zorder=4)

    # Helper to draw arrows
    def draw_arrow(src_x, src_y, dest_x, dest_y, label=None, label_pos=None):
        arrow_style = dict(arrowstyle="->", color=COLORS['primary'], lw=1.2, mutation_scale=15)
        ax.annotate("", xy=(dest_x, dest_y), xytext=(src_x, src_y), arrowprops=arrow_style, zorder=2)
        if label and label_pos:
            ax.text(label_pos[0], label_pos[1], label, fontsize=8.5, weight='bold', ha='center', color=COLORS['text'])

    # --- Draw Nodes ---
    # 1. Input Document Node
    draw_box(cx=5.0, cy=10.0, w=4.5, h=0.8, 
             title="Input Generative AI Image", text="Containing Probabilistically Deformed Text", 
             facecolor=COLORS['bg_box'], edgecolor=COLORS['primary'], shape='box')
    
    # 2. Crop Isolation
    draw_box(cx=5.0, cy=8.7, w=4.5, h=0.8, 
             title="Attention-Based Crop Isolation", text="Isolates text bbox from background context",
             facecolor='#E0F2FE', edgecolor=COLORS['accent_blue'])
             
    # 3. Isolated Crop (Intermediate Data)
    draw_box(cx=5.0, cy=7.4, w=4.5, h=0.8, 
             title="Isolated Text Crop", text="Hallucinated glyphs & deformed kerning", 
             facecolor=COLORS['bg_box'], edgecolor=COLORS['primary'])
             
    # 4. Vision Transformer
    draw_box(cx=5.0, cy=6.0, w=5.2, h=0.9, 
             title="Frozen Vision Transformer (ViT)", text="DINOv2 Feature Extractor + Register Tokens", 
             facecolor='#E0F7FA', edgecolor=COLORS['accent_teal'])
             
    # 5. Metric Embedding
    draw_box(cx=5.0, cy=4.6, w=5.2, h=0.9, 
             title="Metric Embedding Projection Head", text="Contrastive Triplet Space Mapping (f_θ)", 
             facecolor='#E0F2FE', edgecolor=COLORS['accent_blue'])
             
    # 6. Decision Diamond
    draw_box(cx=5.0, cy=2.9, w=3.4, h=1.4, 
             text="Open-Set\nDecision Engine\n(Distance / Energy)", 
             facecolor='#FEF3C7', edgecolor=COLORS['accent_orange'], shape='diamond')
             
    # 7a. Reject Outcome (Left)
    draw_box(cx=2.2, cy=1.1, w=3.2, h=0.8, 
             title="Rejected as Unknown", text="Out-of-Palette / Hallucinated Font", 
             facecolor='#FEE2E2', edgecolor=COLORS['accent_rose'], textcolor=COLORS['accent_rose'])
             
    # 7b. Accept/Shortlist Outcome (Right)
    draw_box(cx=7.8, cy=1.1, w=3.2, h=0.8, 
             title="Calibrated Top-K Shortlist", text="Matching In-Palette Google Fonts", 
             facecolor='#ECFDF5', edgecolor=COLORS['accent_teal'], textcolor=COLORS['accent_teal'])

    # --- Draw Connecting Arrows ---
    draw_arrow(5.0, 9.6, 5.0, 9.1)  # 1 -> 2
    draw_arrow(5.0, 8.3, 5.0, 7.8)  # 2 -> 3
    draw_arrow(5.0, 7.0, 5.0, 6.45) # 3 -> 4
    draw_arrow(5.0, 5.55, 5.0, 5.05) # 4 -> 5
    draw_arrow(5.0, 4.15, 5.0, 3.6) # 5 -> 6
    
    # 6 -> 7a (Left Branch)
    # Draw an angled path for branch
    ax.plot([5.0, 2.2, 2.2], [2.2, 2.2, 1.5], color=COLORS['primary'], lw=1.2, zorder=1)
    draw_arrow(2.2, 1.6, 2.2, 1.5, label="d > θ\n(High Risk)", label_pos=(3.4, 2.35))
    
    # 6 -> 7b (Right Branch)
    ax.plot([5.0, 7.8, 7.8], [2.2, 2.2, 1.5], color=COLORS['primary'], lw=1.2, zorder=1)
    draw_arrow(7.8, 1.6, 7.8, 1.5, label="d ≤ θ\n(Low Risk)", label_pos=(6.6, 2.35))

    # Title of Flowchart
    ax.text(5.0, 10.7, "End-to-End System Pipeline Flowchart", fontsize=13, weight='bold', ha='center', color=COLORS['primary'])

    fig.patch.set_facecolor('white')
    plt.savefig(filepath, dpi=300, bbox_inches='tight', pad_inches=0.1)
    print(f"Saved fallback Matplotlib flowchart: {filepath}")
    plt.close()

def create_system_pipeline_figure():
    # Target path
    fig_name = "system_pipeline"
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "figures"))
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{fig_name}.png")
    
    # Try using Graphviz first
    try:
        import graphviz
        from _style import COLORS
        
        dot = graphviz.Digraph('system_pipeline', format='png')
        dot.attr(dpi='300', rankdir='TB', size='8.5,11')
        
        # Consistent styling matching _style.py colors
        dot.attr('node', fontname='Arial', fontsize='10', shape='box', style='filled,rounded', 
                 color=COLORS['primary'], fillcolor=COLORS['bg_box'], fontcolor=COLORS['text'])
        dot.attr('edge', fontname='Arial', fontsize='8.5', color=COLORS['primary'], fontcolor=COLORS['text'])
        
        # Nodes definition
        dot.node('input', 'Input Generative AI Image\n(Containing deformed text crops)', shape='box', fillcolor=COLORS['bg_box'])
        dot.node('crop_iso', 'Attention-Based Crop Isolation\n(Isolates text bounding box)', fillcolor='#E0F2FE')
        dot.node('crop', 'Isolated Text Crop\n(Hallucinated glyph geometries)', shape='box', fillcolor=COLORS['bg_box'])
        dot.node('vit', 'Frozen Vision Transformer Encoder\n(DINOv2 + Register Tokens)', fillcolor='#E0F7FA')
        dot.node('embedding', 'Metric Embedding Projection Head\n(Triplet space mapping f_θ)', fillcolor='#E0F2FE')
        dot.node('decision', 'Open-Set Decision Engine\n(Distance / Energy score)', shape='diamond', style='filled', fillcolor='#FEF3C7')
        dot.node('reject', 'Rejected as Unknown\n(Out-of-Palette)', fillcolor='#FEE2E2', fontcolor=COLORS['accent_rose'], color=COLORS['accent_rose'])
        dot.node('accept', 'Calibrated Top-K Shortlist\n(Ranked Google Fonts)', fillcolor='#ECFDF5', fontcolor=COLORS['accent_teal'], color=COLORS['accent_teal'])
        
        # Edges
        dot.edge('input', 'crop_iso')
        dot.edge('crop_iso', 'crop')
        dot.edge('crop', 'vit')
        dot.edge('vit', 'embedding')
        dot.edge('embedding', 'decision')
        dot.edge('decision', 'reject', label='d > θ\n(Out-of-Palette)')
        dot.edge('decision', 'accept', label='d ≤ θ\n(In-Palette)')
        
        # Render
        dot.render(outfile=filepath, cleanup=True)
        print(f"Saved Graphviz flowchart: {filepath}")
        
    except Exception as e:
        print(f"Graphviz rendering failed or binary not found. Error: {e}")
        print("Falling back to Matplotlib flowchart rendering...")
        draw_matplotlib_flowchart(filepath)

if __name__ == '__main__':
    create_system_pipeline_figure()

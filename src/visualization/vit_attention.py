import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from _style import apply_style, save_figure, COLORS

def draw_patch_grid(ax, x0, y0, size, n_patches=3):
    """Draws a grid of patches representing the input glyph crop."""
    # Draw main image box
    ax.add_patch(patches.Rectangle((x0, y0), size, size, 
                                   facecolor='#FFFFFF', edgecolor=COLORS['primary'], linewidth=1.5, zorder=2))
    
    # Draw a stylized letter "f" on the grid
    # We will use simple bezier curves or polygons to make it look like a serif 'f'
    ax.text(x0 + size/2.0, y0 + size/2.0, "f", fontname='Times New Roman', fontsize=120,
            ha='center', va='center', color=COLORS['primary'], alpha=0.15, zorder=3)
    
    # Draw grid lines
    step = size / n_patches
    for i in range(1, n_patches):
        ax.plot([x0 + i*step, x0 + i*step], [y0, y0 + size], color=COLORS['muted'], linestyle=':', linewidth=0.8, zorder=4)
        ax.plot([x0, x0 + size], [y0 + i*step, y0 + i*step], color=COLORS['muted'], linestyle=':', linewidth=0.8, zorder=4)
        
    # Label patches 1 to 9
    patch_id = 1
    for row in reversed(range(n_patches)):
        for col in range(n_patches):
            px = x0 + col*step + step/2
            py = y0 + row*step + step/2
            ax.text(px, py, f"P{patch_id}", fontsize=8, color=COLORS['muted'], 
                    ha='center', va='center', weight='bold', zorder=5)
            patch_id += 1

def create_vit_attention_figure():
    apply_style()
    
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-3.5, 3.5)
    ax.axis('off')
    
    # 1. Input Image Panel (3x3 grid)
    img_x, img_y = 0.2, -1.0
    img_size = 2.0
    draw_patch_grid(ax, img_x, img_y, img_size)
    ax.text(img_x + img_size/2, img_y - 0.4, "Input Glyph Crop\nSplit into 3×3 Patches", 
            ha='center', va='top', fontsize=9, weight='bold')

    # 2. Linear Projection & Position Embedding
    proj_x = 3.2
    n_tokens = 9
    token_ys = np.linspace(1.8, -1.8, n_tokens)
    
    # Draw connections from image patches to token embeddings
    for i, y_pos in enumerate(token_ys):
        # Center of each patch in 3x3 grid:
        patch_col = i % 3
        patch_row = 2 - (i // 3)
        src_x = img_x + patch_col*(img_size/3.0) + (img_size/6.0)
        src_y = img_y + patch_row*(img_size/3.0) + (img_size/6.0)
        
        # Connect to token vector
        ax.plot([src_x, proj_x], [src_y, y_pos], color=COLORS['muted'], alpha=0.15, linewidth=0.8)
        
        # Draw the token vector (a small horizontal bar)
        ax.add_patch(patches.Rectangle((proj_x, y_pos - 0.1), 0.6, 0.2, 
                                       facecolor=COLORS['bg_box'], edgecolor=COLORS['primary'], linewidth=0.8, zorder=3))
        
        # Position embedding addition (+)
        pos_emb_x = proj_x + 0.9
        ax.scatter(pos_emb_x, y_pos, color=COLORS['accent_orange'], s=45, edgecolor=COLORS['primary'], zorder=4)
        ax.text(pos_emb_x, y_pos, "+", fontsize=8, ha='center', va='center', color='white', weight='bold', zorder=5)
        
    ax.text(proj_x + 0.3, -2.4, "Linear Projection\n& Flattening", ha='center', va='top', fontsize=8)
    ax.text(proj_x + 0.9, -2.4, "Position\nEmbeddings", ha='center', va='top', fontsize=8, color=COLORS['accent_orange'])

    # 3. Multi-Head Self-Attention Block (We pick Patch P5 to illustrate)
    sa_x = 5.2
    # Select P5 (index 4)
    p5_y = token_ys[4]
    
    # Highlight P5 projection
    ax.annotate("", xy=(sa_x, p5_y), xytext=(proj_x + 1.1, p5_y),
                arrowprops=dict(arrowstyle="->", color=COLORS['primary'], lw=1.2))
    
    # Self-Attention Header/Box
    ax.add_patch(patches.Rectangle((sa_x, -2.2), 3.4, 4.4, 
                                   facecolor='#F8FAFC', edgecolor=COLORS['accent_teal'], linestyle='-', linewidth=1.5, zorder=1))
    ax.text(sa_x + 1.7, 2.45, "Transformer Encoder Block\n(Multi-Head Self-Attention)", 
            ha='center', va='center', fontsize=9, weight='bold', color=COLORS['accent_teal'])
    
    # Draw Q, K, V projections inside the box
    qkv_x = sa_x + 0.3
    # Q vector from P5
    ax.add_patch(patches.Rectangle((qkv_x, p5_y + 0.3), 0.4, 0.15, facecolor='#FEE2E2', edgecolor='#EF4444', linewidth=0.8, zorder=3))
    ax.text(qkv_x + 0.2, p5_y + 0.37, "Q5", fontsize=7, ha='center', va='center', weight='bold', color='#B91C1C')
    
    # K, V vectors (showing a stack representing all patches)
    for j, y_pos in enumerate(token_ys):
        if j % 2 == 0:  # Draw just a few to keep it clean
            # K stack
            ax.add_patch(patches.Rectangle((qkv_x + 0.6, y_pos - 0.15), 0.3, 0.1, facecolor='#E0F2FE', edgecolor='#0284C7', linewidth=0.6, zorder=3))
            # V stack
            ax.add_patch(patches.Rectangle((qkv_x + 1.1, y_pos - 0.15), 0.3, 0.1, facecolor='#ECFDF5', edgecolor='#059669', linewidth=0.6, zorder=3))
            
    ax.text(qkv_x + 0.2, -1.9, "Queries\n(Q)", fontsize=7, ha='center', va='top')
    ax.text(qkv_x + 0.75, -1.9, "Keys\n(K)", fontsize=7, ha='center', va='top')
    ax.text(qkv_x + 1.25, -1.9, "Values\n(V)", fontsize=7, ha='center', va='top')

    # Draw Attention Weights Matrix (QK^T)
    attn_matrix_x = sa_x + 1.9
    attn_matrix_y = -0.6
    attn_size = 1.1
    ax.add_patch(patches.Rectangle((attn_matrix_x, attn_matrix_y), attn_size, attn_size, 
                                   facecolor='#FFFFFF', edgecolor=COLORS['primary'], linewidth=0.8, zorder=3))
    
    # Add matrix cells (9x9 simplified to 3x3 visually)
    n_cells = 3
    c_size = attn_size / n_cells
    # Draw some shaded cells indicating attention weights
    np.random.seed(12)
    weights = np.random.rand(n_cells, n_cells)
    weights[1, 0] = 0.95  # Strong attention from P5 to P1 (stroke)
    weights[1, 2] = 0.75  # Attention to P9 (bottom stroke)
    
    for r in range(n_cells):
        for c in range(n_cells):
            alpha = weights[r, c] * 0.8
            ax.add_patch(patches.Rectangle((attn_matrix_x + c*c_size, attn_matrix_y + r*c_size), c_size, c_size, 
                                           facecolor=COLORS['accent_rose'], alpha=alpha, edgecolor='none', zorder=4))
    
    # Label matrix
    ax.text(attn_matrix_x + attn_size/2, attn_matrix_y - 0.25, "Attention Matrix\nsoftmax(QKᵀ / √d)", 
            fontsize=7, ha='center', va='top', weight='bold')
    
    # Connect Q5 and Keys to Attention Matrix
    ax.plot([qkv_x + 0.4, attn_matrix_x], [p5_y + 0.37, attn_matrix_y + attn_size/2], color='#B91C1C', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.plot([qkv_x + 0.9, attn_matrix_x], [0, attn_matrix_y + attn_size/2], color='#0284C7', linestyle='-', linewidth=0.8, alpha=0.5)
    
    # Connect Matrix + Values to Output updated P5
    out_vector_x = sa_x + 3.0
    ax.plot([attn_matrix_x + attn_size, out_vector_x], [attn_matrix_y + attn_size/2, p5_y], color='#059669', linestyle='-', linewidth=0.8, alpha=0.5)

    # 4. Outputs Section
    out_x = 9.8
    for i, y_pos in enumerate(token_ys):
        is_p5 = (i == 4)
        box_color = COLORS['accent_teal'] if is_p5 else COLORS['bg_box']
        edge_color = COLORS['primary']
        line_w = 1.2 if is_p5 else 0.8
        
        # Updated output vector
        ax.add_patch(patches.Rectangle((out_x, y_pos - 0.1), 0.6, 0.2, 
                                       facecolor=box_color, edgecolor=edge_color, linewidth=line_w, zorder=3))
        
        # Connect encoder to outputs
        ax.plot([sa_x + 3.4, out_x], [y_pos, y_pos], color=COLORS['muted'], alpha=0.2, linewidth=0.8)
        
    ax.text(out_x + 0.3, -2.4, "Contextualized\nOutput Embeddings", ha='center', va='top', fontsize=8, weight='bold', color=COLORS['accent_teal'])
    
    # Callout for updated P5
    ax.annotate("P5 attends to strokes\nin P1 and P9", 
                xy=(out_x + 0.6, p5_y), xytext=(out_x + 1.2, p5_y + 0.6),
                arrowprops=dict(arrowstyle="->", color=COLORS['accent_teal'], lw=1.0),
                fontsize=8, color=COLORS['accent_teal'], weight='bold')

    plt.tight_layout()
    save_figure(fig, "vit_attention")
    plt.close()

if __name__ == '__main__':
    create_vit_attention_figure()

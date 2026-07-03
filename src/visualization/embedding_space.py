import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from _style import apply_style, save_figure, COLORS

def create_embedding_space_figure():
    apply_style()
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    fig, ax = plt.subplots(figsize=(7.5, 6))
    
    # 1. Define Known Centroids & Generate Points
    centroids = {
        'Roboto (Sans)': np.array([1.5, 2.2]),
        'Garamond (Serif)': np.array([4.0, 1.2]),
        'Consolas (Mono)': np.array([2.2, -1.2])
    }
    
    cluster_colors = {
        'Roboto (Sans)': COLORS['accent_teal'],
        'Garamond (Serif)': COLORS['accent_blue'],
        'Consolas (Mono)': COLORS['accent_orange']
    }
    
    cluster_markers = {
        'Roboto (Sans)': 'o',
        'Garamond (Serif)': 's',
        'Consolas (Mono)': '^'
    }
    
    # Generate points around each centroid
    n_points = 25
    std_dev = 0.22
    
    for name, center in centroids.items():
        x = np.random.normal(center[0], std_dev, n_points)
        y = np.random.normal(center[1], std_dev, n_points)
        
        # Plot cluster points
        ax.scatter(x, y, color=cluster_colors[name], marker=cluster_markers[name], 
                   s=40, alpha=0.8, edgecolors='black', linewidth=0.5, label=name)
        
        # Draw the rejection boundary (threshold circle around centroid)
        # Radius of the boundary represents the threshold d_thresh
        threshold_radius = 0.65
        circle = patches.Circle(center, threshold_radius, fill=True, 
                               facecolor=cluster_colors[name], alpha=0.08,
                               edgecolor=cluster_colors[name], linestyle='--', linewidth=1.2, zorder=1)
        ax.add_patch(circle)
        
        # Add label next to boundary
        ax.text(center[0], center[1] + threshold_radius + 0.08, f"d < θ", 
                color=cluster_colors[name], fontsize=8, ha='center', weight='bold')

    # 2. Add Out-of-Palette (OOD) Hallucinated Crop
    ood_point = np.array([4.2, -0.8])
    ax.scatter(ood_point[0], ood_point[1], color=COLORS['accent_rose'], marker='X', 
               s=100, edgecolors='black', linewidth=0.8, label='Out-of-Palette Crop', zorder=5)
    
    # Add In-Palette Query Point (Warped Roboto glyph)
    in_palette_query = np.array([1.68, 1.95])
    ax.scatter(in_palette_query[0], in_palette_query[1], color='#10B981', marker='*',
               s=140, edgecolors='black', linewidth=0.8, label='In-Palette Warped Query', zorder=5)

    # 3. Visual Annotations and Explanations
    # Annotate OOD crop
    ax.annotate("Hallucinated Crop\n(Rejected as Unknown)", 
                xy=(ood_point[0] - 0.05, ood_point[1] + 0.05), 
                xytext=(4.8, -0.2),
                arrowprops=dict(arrowstyle="->", color=COLORS['accent_rose'], lw=1.2),
                fontsize=9, color=COLORS['accent_rose'], weight='bold', ha='center')
    
    # Annotate In-Palette query
    ax.annotate("Warped Input Crop\n(Classified as Roboto)", 
                xy=(in_palette_query[0], in_palette_query[1] - 0.08), 
                xytext=(0.5, 0.9),
                arrowprops=dict(arrowstyle="->", color='#059669', lw=1.2),
                fontsize=9, color='#059669', weight='bold', ha='center')

    # Highlight Open Space
    ax.text(3.4, -1.8, "Open Space Risk\n(Rejected Region)", 
            color=COLORS['muted'], fontsize=10, style='italic', ha='center', weight='semibold')
    
    # Draw open space background hatch
    # Let's draw a few subtle hatching lines or just label it clearly
    
    # Axis configuration
    ax.set_xlabel("Metric Embedding Dimension 1", fontsize=10, labelpad=8)
    ax.set_ylabel("Metric Embedding Dimension 2", fontsize=10, labelpad=8)
    ax.set_title("Open-Set Metric Space & Rejection Boundaries", fontsize=12, weight='bold', pad=15)
    
    ax.set_xlim(-0.2, 5.8)
    ax.set_ylim(-2.2, 3.8)
    ax.grid(True, linestyle=':', alpha=0.5)
    
    # Place legend
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor=COLORS['muted'], framealpha=0.9)
    
    plt.tight_layout()
    save_figure(fig, "embedding_space")
    plt.close()

if __name__ == '__main__':
    create_embedding_space_figure()

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from _style import apply_style, save_figure, COLORS

def render_char(char, fontname='Georgia', fontsize=100, shape=(180, 180)):
    """Renders a single character to a grayscale image array."""
    fig = plt.figure(figsize=(2, 2), dpi=100, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.text(0.5, 0.5, char, fontname=fontname, fontsize=fontsize,
            ha='center', va='center', color='black')
    fig.canvas.draw()
    rgba = fig.canvas.buffer_rgba()
    img = np.asarray(rgba)[:, :, 0]
    plt.close(fig)
    return 1.0 - (img.astype(float) / 255.0)

def warp_char(image, alpha=15, sigma=4, seed=42):
    """Applies elastic warp to simulate hallucination."""
    random_state = np.random.RandomState(seed)
    shape = image.shape
    dx = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
    dy = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
    warped = map_coordinates(image, indices, order=1).reshape(shape)
    return np.clip(warped, 0, 1)

def create_ssim_pipeline_figure():
    apply_style()
    
    char = "a"
    
    # 1. Render pristine template
    pristine = render_char(char)
    
    # 2. Render and warp input crop
    deformed = warp_char(pristine)
    # Add slight noise and blur
    deformed = gaussian_filter(deformed, sigma=0.8)
    np.random.seed(42)
    deformed = np.clip(deformed + np.random.normal(0, 0.03, deformed.shape), 0, 1)
    
    # 3. Compute difference map (SSIM error map proxy)
    # Highlight differences in a custom colorway (blue/red representing mismatch)
    diff = np.abs(pristine - deformed)
    
    # Create 4 horizontal subplots with extra space for flowchart connections
    fig = plt.figure(figsize=(11.5, 4.5))
    
    # Define axes positions manually to allow flow arrows
    # Layout: [Left Margin, Bottom Margin, Width, Height]
    ax1 = fig.add_axes([0.05, 0.2, 0.18, 0.5]) # Deformed Input
    ax2 = fig.add_axes([0.31, 0.2, 0.18, 0.5]) # Pristine Template
    ax3 = fig.add_axes([0.57, 0.2, 0.18, 0.5]) # Difference Map
    ax4 = fig.add_axes([0.80, 0.2, 0.16, 0.5]) # Textual / Math block
    
    # Panel 1: Deformed Input Crop
    ax1.imshow(1.0 - deformed, cmap='gray', vmin=0, vmax=1)
    ax1.set_title("Input Crop ($\mathbf{\tilde{x}}$)\n(GenAI Hallucinated)", fontsize=9.5, weight='bold', pad=8)
    ax1.set_xticks([])
    ax1.set_yticks([])
    for spine in ax1.spines.values():
        spine.set_color(COLORS['accent_rose'])
        spine.set_linewidth(1.5)
        
    # Panel 2: Pristine Template
    ax2.imshow(1.0 - pristine, cmap='gray', vmin=0, vmax=1)
    ax2.set_title("Template ($\mathbf{x}$)\n(Re-rendered Prediction)", fontsize=9.5, weight='bold', pad=8)
    ax2.set_xticks([])
    ax2.set_yticks([])
    for spine in ax2.spines.values():
        spine.set_color(COLORS['accent_teal'])
        spine.set_linewidth(1.5)
        
    # Panel 3: Structural Difference Map
    # Use a custom colormap where 0 (match) is white, and mismatch is teal/rose
    # Standard hot or seismic can look nice, let's use red hot map
    ax3.imshow(diff, cmap='Reds', vmin=0, vmax=1.0)
    ax3.set_title("Structural Mismatch\nError Map", fontsize=9.5, weight='bold', pad=8)
    ax3.set_xticks([])
    ax3.set_yticks([])
    for spine in ax3.spines.values():
        spine.set_color(COLORS['muted'])
        spine.set_linewidth(0.8)
        
    # Panel 4: Metric Summary
    ax4.axis('off')
    # Draw a backing box
    box = patches.FancyBboxPatch((0.02, 0.05), 0.96, 0.9, boxstyle="round,pad=0.02",
                                 edgecolor=COLORS['accent_teal'], facecolor=COLORS['bg_box'], linewidth=1.2)
    ax4.add_patch(box)
    
    # Formula & Score Text
    ax4.text(0.5, 0.78, "SSIM Score", fontsize=11, weight='bold', ha='center', color=COLORS['text'])
    ax4.text(0.5, 0.50, "0.742", fontsize=28, weight='bold', ha='center', color=COLORS['accent_teal'])
    
    # Breakdown labels
    ax4.text(0.5, 0.32, "Luminance: 0.981\nContrast: 0.912\nStructure: 0.828", 
             fontsize=8.5, ha='center', va='top', color=COLORS['muted'], linespacing=1.5)
    
    # --- Draw Flowchart Arrows on the Figure Canvas ---
    # We will use fig.text or annotate with fig.transFigure
    
    # Arrow 1: From Input Crop to Classifier (represented textually)
    fig.text(0.245, 0.55, "Predict", fontsize=8.5, weight='bold', color=COLORS['primary'], ha='center')
    ax_arr1 = fig.add_axes([0.23, 0.45, 0.08, 0.01])
    ax_arr1.axis('off')
    ax_arr1.annotate("", xy=(1, 0.5), xytext=(0, 0.5), arrowprops=dict(arrowstyle="->", color=COLORS['primary'], lw=1.2))
    
    # Label prediction above the arrow
    fig.text(0.245, 0.38, "Roboto\n(Predicted)", fontsize=7.5, color=COLORS['accent_teal'], ha='center', weight='bold')
    
    # Arrow 2: Connect inputs to comparison
    # Draw arrows from ax1 and ax2 pointing towards ax3
    # Arrow from ax1 (Input) to difference calculation (ax3)
    ax_arr2 = fig.add_axes([0.15, 0.05, 0.47, 0.15])
    ax_arr2.axis('off')
    # Draw path showing alignment comparison
    ax_arr2.plot([0, 0], [0.8, 0], color=COLORS['muted'], linestyle='-', linewidth=1)
    ax_arr2.plot([0, 0.95], [0, 0], color=COLORS['muted'], linestyle='-', linewidth=1)
    ax_arr2.annotate("", xy=(0.95, 0.8), xytext=(0.95, 0), arrowprops=dict(arrowstyle="->", color=COLORS['muted'], lw=1.0))
    
    # Arrow from ax2 (Template) to difference calculation (ax3)
    ax_arr3 = fig.add_axes([0.41, 0.05, 0.21, 0.15])
    ax_arr3.axis('off')
    ax_arr3.plot([0, 0], [0.8, 0], color=COLORS['muted'], linestyle='-', linewidth=1)
    ax_arr3.plot([0, 0.95], [0, 0], color=COLORS['muted'], linestyle='-', linewidth=1)
    ax_arr3.annotate("", xy=(0.95, 0.8), xytext=(0.95, 0), arrowprops=dict(arrowstyle="->", color=COLORS['muted'], lw=1.0))
    
    # Label comparison
    fig.text(0.38, 0.07, "Compute Perceptual Structural Match", fontsize=8, color=COLORS['primary'], weight='bold', ha='center')
    
    # Arrow from Difference Map (ax3) to Score (ax4)
    ax_arr4 = fig.add_axes([0.755, 0.45, 0.045, 0.01])
    ax_arr4.axis('off')
    ax_arr4.annotate("", xy=(1, 0.5), xytext=(0, 0.5), arrowprops=dict(arrowstyle="->", color=COLORS['primary'], lw=1.2))
    
    # General title
    fig.suptitle("Perceptual Re-Render-and-Compare Evaluation Model", fontsize=12, weight='bold', y=0.92)
    
    save_figure(fig, "ssim_pipeline")
    plt.close()

if __name__ == '__main__':
    create_ssim_pipeline_figure()

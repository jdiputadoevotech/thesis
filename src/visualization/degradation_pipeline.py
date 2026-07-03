import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from _style import apply_style, save_figure, COLORS

def render_word_to_array(text, offsets=None, fontname='Georgia', fontsize=48):
    """Renders a word to a 2D numpy array, optionally with horizontal offsets per char."""
    fig = plt.figure(figsize=(4, 1.2), dpi=100, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    
    n_chars = len(text)
    if offsets is None:
        offsets = [0.0] * n_chars
        
    # Standard character positions (normalized coordinates 0 to 1)
    base_xs = np.linspace(0.12, 0.88, n_chars)
    
    for i, char in enumerate(text):
        x_pos = base_xs[i] + offsets[i]
        # Draw each letter
        ax.text(x_pos, 0.5, char, fontname=fontname, fontsize=fontsize,
                ha='center', va='center', color='black', weight='normal')
                
    fig.canvas.draw()
    rgba = fig.canvas.buffer_rgba()
    img = np.asarray(rgba)[:, :, 0] # Red channel as grayscale
    plt.close(fig)
    
    # Normalise: 1.0 = text (black), 0.0 = background (white)
    img_norm = 1.0 - (img.astype(float) / 255.0)
    return img_norm

def elastic_warp(image, alpha=14, sigma=3, seed=42):
    """Applies a 2D elastic transformation (distortion) to the image array."""
    random_state = np.random.RandomState(seed)
    shape = image.shape
    
    # Generate random displacement fields
    dx = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
    dy = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
    
    # Map coordinates using the displacement fields
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
    
    warped = map_coordinates(image, indices, order=1).reshape(shape)
    return np.clip(warped, 0, 1)

def add_blur_and_noise(image, sigma=1.2, noise_std=0.08, seed=42):
    """Applies Gaussian blur and adds random Gaussian noise."""
    random_state = np.random.RandomState(seed)
    blurred = gaussian_filter(image, sigma=sigma)
    noise = random_state.normal(0, noise_std, image.shape)
    noisy = blurred + noise
    return np.clip(noisy, 0, 1)

def create_degradation_pipeline_figure():
    apply_style()
    
    # Words to render
    word = "Style"
    
    # 1. Clean
    img_clean = render_word_to_array(word)
    
    # 2. Elastic Warp
    img_warped = elastic_warp(img_clean)
    
    # 3. Blur & Noise
    img_blur_noise = add_blur_and_noise(img_warped)
    
    # 4. Kerning Jitter (render with offset spacing) + Warp + Blur/Noise
    # For "Style", let's push 'S' and 't' closer, and 'y', 'l', 'e' further apart
    jitter_offsets = [-0.03, -0.05, 0.04, -0.01, 0.05]
    img_kerned = render_word_to_array(word, offsets=jitter_offsets)
    img_fully_degraded = add_blur_and_noise(elastic_warp(img_kerned))
    
    # Create horizontal subplots layout (1 row, 4 cols)
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.2))
    
    stages = [
        ("1. Clean Glyph", img_clean, "Original pristine vector text"),
        ("2. Elastic Warp", img_warped, "Probabilistic glyph distortion"),
        ("3. Blur & Noise", img_blur_noise, "Gaussian blur & sensor noise"),
        ("4. Kerning Jitter", img_fully_degraded, "Combined jitter + warping + noise")
    ]
    
    for idx, (title, img, desc) in enumerate(stages):
        ax = axes[idx]
        
        # Display image (invert color for publication: black text on white background)
        # 1 - img will make text dark on white background
        ax.imshow(1.0 - img, cmap='gray', vmin=0, vmax=1)
        ax.set_title(title, fontsize=10, weight='bold', pad=8)
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Draw custom box border
        for spine in ax.spines.values():
            spine.set_color(COLORS['muted'])
            spine.set_linewidth(0.8)
            
        # Description text below the plot
        ax.text(0.5, -0.15, desc, transform=ax.transAxes, fontsize=8, 
                ha='center', va='top', color=COLORS['text'], wrap=True)
        
    plt.tight_layout()
    # Add layout margin for bottom descriptions
    plt.subplots_adjust(bottom=0.22)
    save_figure(fig, "degradation_pipeline")
    plt.close()

if __name__ == '__main__':
    create_degradation_pipeline_figure()

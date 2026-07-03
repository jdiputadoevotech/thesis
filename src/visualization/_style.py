import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Output settings
DPI = 300
FIGURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "figures"))

# Color Palette (Harmonious, professional Slate/Teal/Rose palette)
COLORS = {
    'primary': '#1E293B',       # Dark Slate (main text, structural lines)
    'accent_teal': '#0D9488',   # Teal (known classes, positive flows)
    'accent_rose': '#E11D48',   # Crimson/Rose (out-of-palette, boundaries, negative flows)
    'accent_orange': '#D97706', # Amber (intermediate stages, warp operations)
    'accent_blue': '#2563EB',   # Blue (extra highlights)
    'text': '#0F172A',          # Dark Slate/Almost Black for readability
    'muted': '#64748B',         # Muted gray for gridlines/secondary labels
    'bg_light': '#F8FAFC',      # Soft off-white background
    'bg_box': '#F1F5F9'         # Soft gray for box backgrounds
}

def apply_style():
    """Applies a clean, professional thesis plotting style."""
    plt.rcParams.update({
        'figure.dpi': DPI,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans', 'Liberation Sans'],
        'font.size': 10,
        'axes.labelsize': 10,
        'axes.titlesize': 12,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.titlesize': 14,
        'text.usetex': False,
        'svg.fonttype': 'none',
        'axes.edgecolor': COLORS['muted'],
        'axes.linewidth': 0.8,
        'grid.color': '#E2E8F0',
        'grid.linewidth': 0.5,
        'xtick.color': COLORS['muted'],
        'ytick.color': COLORS['muted'],
        'text.color': COLORS['text'],
        'axes.labelcolor': COLORS['text'],
        'axes.titlecolor': COLORS['text'],
    })

def save_figure(fig, name):
    """Saves the figure to assets/figures/<name>.png at 300 DPI."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    filename = f"{name}.png"
    filepath = os.path.join(FIGURES_DIR, filename)
    fig.patch.set_facecolor('white')
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight', pad_inches=0.1)
    print(f"Saved figure: {filepath}")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.ticker as ticker

# Constant a
a = 1

# Graph area
x = np.linspace(-6, 6, 800)
y = np.linspace(-6, 6, 800)
X, Y = np.meshgrid(x, y)

# Define functions
g1 = (X - a)**2 - Y**2 + 1
g2 = (X + a)**2 - Y**2 + 1
g_sum = g1 + g2

fig, ax = plt.subplots(figsize=(8, 8))

# SEt aspect
ax.set_aspect('equal')

# Set ticker
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

# Plot graph
ax.contour(X, Y, g1, levels=[0], colors='red', linestyles='solid')
ax.contour(X, Y, g2, levels=[0], colors='red', linestyles='solid')
ax.contour(X, Y, g_sum, levels=[0], colors='red', linewidths=4, linestyles='-.')

# Dummy
# line1 = mlines.Line2D([], [], color='red', label=r'$(x-a)^2 - y^2 = -1$')
# line2 = mlines.Line2D([], [], color='red', label=r'$(x+a)^2 - y^2 = -1$')
# line3 = mlines.Line2D([], [], color='red', linestyle='dashed', linewidth=2, label=r'Sum: $x^2 - y^2 = -(a^2+1)$')

# ax.legend(handles=[line1, line2, line3], loc='upper right')


ax.axhline(0, color='black', linewidth=0.8)
ax.axvline(0, color='black', linewidth=0.8)
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title(f'Sum of Hyperbolas (a={a})')
ax.set_xlabel('x')
ax.set_ylabel('y')

plt.show()
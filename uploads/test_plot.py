import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2, label='Sine Wave')

# Add labels and title
plt.title('Sample Sine Wave Plot')
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.legend()

# Add grid
plt.grid(True, alpha=0.3)

# Show plot
plt.tight_layout()
plt.show()
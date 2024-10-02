from dataclasses import dataclass
from typing import List

import numpy as np
from matplotlib import pyplot as plt


def bring_to_interval(x, around):
    while x < around - np.pi:
        x += 2 * np.pi

    while x > around + np.pi:
        x -= 2 * np.pi

    return x


NOT_SEEN_COLOR = "whitesmoke"


@dataclass
class Camera:
    x: float
    y: float
    orientation: float
    fov: float
    range: float
    resolution_horizontal: float
    color: str

    def has_point_in_fov(self, px, py):
        orientation = np.deg2rad(self.orientation)
        camera_to_point_angle = bring_to_interval(
            np.arctan2(py - self.y, px - self.x), orientation
        )

        half_fov = np.deg2rad(self.fov / 2)

        return (
            bring_to_interval(orientation - half_fov, orientation)
            <= camera_to_point_angle
            and bring_to_interval(orientation + half_fov, orientation)
            >= camera_to_point_angle
        )

    def has_within_range(self, px, py):
        distance = np.linalg.norm(np.array([self.x, self.y]) - np.array([px, py]))
        return distance < self.range

    def compute_information(self, px, py):
        pass

    def get_color(self, px, py):

        if not self.has_point_in_fov(px, py):
            return None

        if not self.has_within_range(px, py):
            return None

        return self.color


def combine_rgba_list(colors):
    # Start with the first color as the base
    r, g, b, a = colors[0]

    # Iterate through the rest of the colors and blend them
    for color in colors[1:]:
        r2, g2, b2, a2 = color

        # Calculate the new alpha
        a_new = a + a2 * (1 - a)

        if a_new == 0:
            r_new, g_new, b_new = 0, 0, 0  # If fully transparent
        else:
            # Blend the RGB channels
            r_new = (r * a + r2 * a2 * (1 - a)) / a_new
            g_new = (g * a + g2 * a2 * (1 - a)) / a_new
            b_new = (b * a + b2 * a2 * (1 - a)) / a_new

        # Update the current color to the new blended color
        r, g, b, a = r_new, g_new, b_new, a_new

    return (r, g, b, a)


def main():
    cameras = [
        Camera(0, 0.5, 90, 30, 30, 1200, (0, 0, 1, 0.1)),
        Camera(0, 0.5, 115, 30, 20, 1200, (1, 0.3, 0.2, 0.1)),
        Camera(0, 0.5, 65, 30, 20, 1200, (1, 0.3, 0.2, 0.1)),
        Camera(0, -2, -90, 120, 10, 1200, (0, 1, 0, 0.1)),
        Camera(1, 0, 0, 190, 7, 1200, (0, 1, 1, 0.1)),
        Camera(-1, 0, 180, 190, 7, 1200, (1, 1, 0.5, 0.1)),
    ]

    resolution = 0.3
    size = 40

    plt.axis("equal")

    r = np.arange(-size, size, resolution)

    colors_to_plot = []
    xs = []
    ys = []

    for x in r:
        for y in r:
            colors = [c.get_color(x, y) for c in cameras]
            non_empty_colors = [c for c in colors if c is not None]
            color = (
                combine_rgba_list(non_empty_colors)
                if non_empty_colors
                else NOT_SEEN_COLOR
            )
            colors_to_plot.append(color)
            xs.append(x)
            ys.append(y)

    plt.scatter(xs, ys, color=colors_to_plot)
    plt.show()


if __name__ == "__main__":
    main()

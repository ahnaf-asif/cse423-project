from core.component import Component


class Collider(Component):
    """Component to handle AABB collision detection."""

    def __init__(self, width, depth, offset_x=0, offset_y=0):
        self.width = width
        self.depth = depth
        self.offset_x = offset_x
        self.offset_y = offset_y

    def get_bounds(self, transform):
        """Returns (min_x, max_x, min_y, max_y) in world space."""
        abs_yaw = abs(transform.yaw % 360)
        if 45 < abs_yaw < 135 or 225 < abs_yaw < 315:
            effective_width = self.depth
            effective_depth = self.width
        else:
            effective_width = self.width
            effective_depth = self.depth

        half_w = effective_width / 2
        half_d = effective_depth / 2

        ox, oy = self.offset_x, self.offset_y
        if 45 < abs_yaw < 135:  # 90
            ox, oy = -self.offset_y, self.offset_x
        elif 135 <= abs_yaw < 225:  # 180
            ox, oy = -self.offset_x, -self.offset_y
        elif 225 <= abs_yaw < 315:  # 270
            ox, oy = self.offset_y, -self.offset_x

        return (
            transform.x + ox - half_w,
            transform.x + ox + half_w,
            transform.y + oy - half_d,
            transform.y + oy + half_d,
        )

    def intersects(self, transform, other_x, other_y, other_radius=0):
        """Checks if a point (or circle) intersects this collider."""
        min_x, max_x, min_y, max_y = self.get_bounds(transform)

        closest_x = max(min_x, min(other_x, max_x))
        closest_y = max(min_y, min(other_y, max_y))

        distance_sq = (closest_x - other_x) ** 2 + (closest_y - other_y) ** 2
        return distance_sq < (other_radius**2)

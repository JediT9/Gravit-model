# Why did I decide to do this lol
# Tait Keller
# 27/5/2024
# Programme to simulate a gravitational system, based on sfs

# imports
import dataclasses
from dataclasses import dataclass
import matplotlib
import matplotlib.pyplot as plt
import math
from typing import Self
import time


# Create main object class
@dataclass
class Body:
    """The main class that carries all the functions and methods """

    name: str
    mass: float
    velocity_x: float
    velocity_y: float
    position_x: float
    position_y: float
    past_positions: list[tuple[float, float]] = dataclasses.field(default_factory=list)
    forces: list[tuple[float, float]] = dataclasses.field(default_factory=list)

    def move(self, time_change: float, iterations: int):
        """Update the position values using the velocities"""
        self.position_x += self.velocity_x * time_change
        self.position_y += self.velocity_y * time_change
        if iterations % 30 == 0:
            self.past_positions.append((self.position_x, self.position_y))

    def accelerate(self, time_change: float):
        """Update the velocity of the body"""
        x_forces = []
        y_forces = []
        for force_tuple in self.forces:
            x_forces.append(force_tuple[0])
            y_forces.append(force_tuple[1])
        x_acceleration: float = sum(x_forces) / self.mass
        y_acceleration: float = sum(y_forces) / self.mass
        self.velocity_x += x_acceleration * time_change
        self.velocity_y += y_acceleration * time_change
        self.forces = []

    def calculate_force(self, acting_body: Self) -> tuple[float, float]:
        """Calculate the force acting on a body from the central object"""
        gravitational_constant = 6.674 * 10 ** (-11)
        force = -gravitational_constant * self.mass * acting_body.mass / (
                ((acting_body.position_x - self.position_x) ** 2) +
                ((acting_body.position_y - self.position_y) ** 2))
        angle: float = math.atan2(self.position_y - acting_body.position_y, self.position_x - acting_body.position_x)
        force_x: float = force * math.cos(angle)
        force_y: float = force * math.sin(angle)
        return force_x, force_y


def update_forces(pairs_to_calc: list[tuple[Body, Body]]) -> None:
    """Sum the forces acting on a body"""
    for pair in pairs_to_calc:
        add_force: tuple[float, float] = pair[0].calculate_force(pair[1])
        total_x = add_force[0]
        total_y = add_force[1]
        pair[0].forces.append((total_x, total_y))
        pair[1].forces.append((-1 * total_x, -1 * total_y))


def plot_positions_initial(bodies_to_plot: list[Body]) -> None:
    """Plot the positions of the bodies"""
    plt.cla()
    for body_to_plot in bodies_to_plot:
        plt.plot(body_to_plot.position_x, body_to_plot.position_y, marker="o")
        plt.plot([position[0] for position in list(body_to_plot.past_positions)],
                 [position[1] for position in list(body_to_plot.past_positions)])
    plt.draw()
    plt.pause(0.000001)


def read_input_bodies() -> tuple[list[tuple[Body, Body]], list[Body]]:
    """Get the body info from the file"""
    current_bodies: list[Body] = []
    force_pairs: list[tuple[Body, Body]] = []
    file_contents = open("input_bodies.csv")
    for line in file_contents:
        separated_body: list[str] = line[:-1].split(",")
        if separated_body[0] != "name" and separated_body != [""]:
            new_body = Body(separated_body[0], eval(separated_body[1]), eval(separated_body[2]),
                            eval(separated_body[3]), eval(separated_body[4]), eval(separated_body[5]))
            for pair in current_bodies:
                force_pairs.append((new_body, pair))
            current_bodies.append(new_body)
    return force_pairs, current_bodies


programme_start = time.time()

repeats: int = 10000000
bodies_tuple: tuple[list[tuple[Body, Body]], list[Body]] = read_input_bodies()
body_pairs: list[tuple[Body, Body]] = bodies_tuple[0]
bodies: list[Body] = bodies_tuple[1]

matplotlib.use('TkAgg')
plt.axes()
plt.ion()
plt.show()

times: list[tuple[float, float]] = []

for iteration in range(repeats):
    start = time.time()
    update_forces(body_pairs)
    for body_to_move_index in range(len(bodies)):
        bodies[body_to_move_index].accelerate(8640)
        bodies[body_to_move_index].move(8640, iteration)
        if iteration % 30000 == 0:
            plot_positions_initial(bodies)
    finish = time.time()
    times.append((iteration, finish - start))

programme_finish = time.time()
print(programme_finish - programme_start)

plt.cla()
plt.plot([position[0] for position in times],
         [position[1] for position in times])
plt.draw()
plt.pause(0.00001)

# plot_positions_initial(bodies)
print([len(body.past_positions) for body in bodies])

end = input()

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
    resolution: float
    past_positions: list[tuple[float, float]] = dataclasses.field(default_factory=list)
    forces: dict[str, tuple[float, float]] = dataclasses.field(default_factory=dict)

    def total_force(self) -> float:
        """Calculate the force magnitude on an object"""
        x_forces = []
        y_forces = []
        for force_tuple in self.forces.values():
            x_forces.append(force_tuple[0])
            y_forces.append(force_tuple[1])
        return math.sqrt((sum(x_forces)**2 + sum(y_forces)**2))

    def move(self, time_change: float, iterations: int):
        """Update the position values using the velocities"""
        self.position_x += self.velocity_x * time_change
        self.position_y += self.velocity_y * time_change
        if iterations % 1 == 0:
            self.past_positions.append((self.position_x, self.position_y))

    def accelerate(self, time_change: float):
        """Update the velocity of the body"""
        x_forces = []
        y_forces = []
        for force_tuple in self.forces.values():
            x_forces.append(force_tuple[0])
            y_forces.append(force_tuple[1])
        x_acceleration: float = sum(x_forces) / self.mass
        y_acceleration: float = sum(y_forces) / self.mass
        self.velocity_x += x_acceleration * time_change
        self.velocity_y += y_acceleration * time_change

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


@dataclass
class BodyPair:
    """Class to store the information of each pair of bodies"""

    body_1: Body
    body_2: Body
    priority = 1

    def calculate_forces(self, iteration):
        """Calculate the forces on the bodies"""
        if iteration % self.priority == 0:
            add_force: tuple[float, float] = self.body_1.calculate_force(self.body_2)
            total_x = add_force[0]
            total_y = add_force[1]
            self.body_1.forces[self.body_2.name] = (total_x, total_y)
            self.body_2.forces[self.body_1.name] = (-1 * total_x, -1 * total_y)

        if iteration % 100 == 0:
            self.evaluate_priority()

    def evaluate_priority(self) -> None:
        """Update the priority level"""
        current_force: tuple[float, float] = self.body_1.calculate_force(self.body_2)
        force_magnitude: float = math.sqrt(current_force[0] ** 2 + current_force[1] ** 2)
        body_1_condition: bool = force_magnitude / self.body_1.total_force() < 10 ** -4
        body_2_condition: bool = force_magnitude / self.body_2.total_force() < 10 ** -4
        if body_1_condition and body_2_condition:
            self.priority = 50


def update_forces(pairs_to_calc: list[BodyPair], iteration_number: int) -> None:
    """Sum the forces acting on a body"""
    for pair in pairs_to_calc:
        pair.calculate_forces(iteration_number)


def plot_positions_initial(bodies_to_plot: list[Body]) -> None:
    """Plot the positions of the bodies"""
    plt.cla()
    for body_to_plot in bodies_to_plot:
        plt.plot(body_to_plot.position_x, body_to_plot.position_y, marker="o", label=body_to_plot.name)
        plt.plot([position[0] for position in list(body_to_plot.past_positions)],
                 [position[1] for position in list(body_to_plot.past_positions)])
    plt.legend(loc="upper left")
    plt.draw()
    plt.pause(0.000001)


def read_input_bodies() -> tuple[list[BodyPair], list[Body]]:
    """Get the body info from the file"""
    current_bodies: list[Body] = []
    force_pairs: list[BodyPair] = []
    file_contents = open("input_bodies.csv")
    for line in file_contents:
        separated_body: list[str] = line[:-1].split(",")
        if separated_body[0] != "name" and separated_body != [""]:
            new_body = Body(separated_body[0], eval(separated_body[1]), eval(separated_body[2]),
                            eval(separated_body[3]), eval(separated_body[4]), eval(separated_body[5]), 1)
            for pair in current_bodies:
                force_pairs.append(BodyPair(new_body, pair))
            current_bodies.append(new_body)
    return force_pairs, current_bodies


def main_loop(iterations: int, time_per_iteration: float, force_pairs: list[BodyPair],
              simulation_bodies: list[Body]) -> None:
    """Run the main loop of the simulation."""
    for iteration in range(iterations):
        update_forces(force_pairs, iteration)
        for body_to_move_index in range(len(simulation_bodies)):
            simulation_bodies[body_to_move_index].accelerate(time_per_iteration)
            simulation_bodies[body_to_move_index].move(time_per_iteration, iteration)
            if iteration % 500000000000000 == 0:
                plot_positions_initial(bodies)


programme_start = time.time()

simulated_time: int = 100000
bodies_tuple: tuple[[BodyPair], list[Body]] = read_input_bodies()
body_pairs: list[BodyPair] = bodies_tuple[0]
bodies: list[Body] = bodies_tuple[1]

matplotlib.use('TkAgg')
plt.axes()
plt.ion()
plt.show()

main_loop(simulated_time, 1000, body_pairs, bodies)

programme_finish = time.time()
print(programme_finish - programme_start)
plot_positions_initial(bodies)
print(bodies[-1].position_x, bodies[-1].position_y)
plt.pause(1)

end = input()
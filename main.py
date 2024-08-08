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


def round_to_time(iteration_size, number_to_round) -> float:
    """Return the rounded value"""
    base_number = number_to_round // iteration_size
    if number_to_round % iteration_size >= iteration_size / 2:
        base_number += 1
    if base_number == 0:
        base_number = 1
    return base_number * iteration_size


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
    forces: dict[str, tuple[float, float]] = dataclasses.field(default_factory=dict)
    last_moved: int = 0

    def total_force(self) -> float:
        """Calculate the force magnitude on an object"""
        x_forces = []
        y_forces = []
        for force_tuple in self.forces.values():
            x_forces.append(force_tuple[0])
            y_forces.append(force_tuple[1])
        return math.sqrt((sum(x_forces)**2 + sum(y_forces)**2))

    def move(self, current_iteration: float, time_change_per_iteration: float, add_pos_frequency: int):
        """Update the position values using the velocities"""
        time_past = (current_iteration - self.last_moved) * time_change_per_iteration
        self.last_moved = int(current_iteration)
        self.position_x += self.velocity_x * time_past
        self.position_y += self.velocity_y * time_past
        if current_iteration % add_pos_frequency == 0:
            self.past_positions.append((self.position_x, self.position_y))

    def accelerate(self, time_change_per_iteration: float, current_iteration):
        """Update the velocity of the body"""
        time_past = (current_iteration - self.last_moved) * time_change_per_iteration
        x_forces = []
        y_forces = []
        for force_tuple in self.forces.values():
            x_forces.append(force_tuple[0])
            y_forces.append(force_tuple[1])
        x_acceleration: float = sum(x_forces) / self.mass
        y_acceleration: float = sum(y_forces) / self.mass
        self.velocity_x += x_acceleration * time_past
        self.velocity_y += y_acceleration * time_past

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
    priority: float = 1

    def calculate_forces(self, time_past: float, iteration_size: float, eval_prior_frequency: int) -> bool:
        """Calculate the forces on the bodies"""
        if time_past % self.priority == 0:
            add_force: tuple[float, float] = self.body_1.calculate_force(self.body_2)
            total_x = add_force[0]
            total_y = add_force[1]
            self.body_1.forces[self.body_2.name] = (total_x, total_y)
            self.body_2.forces[self.body_1.name] = (-1 * total_x, -1 * total_y)
            if time_past % eval_prior_frequency == 0:
                self.evaluate_priority(iteration_size)
            return True
        else:
            return False

    def evaluate_priority(self, min_time: float) -> None:
        """Update the priority level"""
        current_force: tuple[float, float] = self.body_1.calculate_force(self.body_2)
        force_magnitude: float = math.sqrt(current_force[0] ** 2 + current_force[1] ** 2)
        body_1_acceleration: float = force_magnitude / self.body_1.mass
        body_2_acceleration: float = force_magnitude / self.body_2.mass
        # if body_1_acceleration < 10**-30 and body_2_acceleration < 10**-30:
        self.priority = int(100 * (1000 * max([body_1_acceleration, body_2_acceleration])) ** (-1/2) + 1)
        if self.priority == 0:
            self.priority = 1
        print(self.priority)


def update_forces(pairs_to_calc: list[BodyPair], iteration_number: float, iteration_size: float,
                  eval_prior_frequency: int) -> list[Body]:
    """Sum the forces acting on a body"""
    bodies_updated: list[Body] = []
    for pair in pairs_to_calc:
        occurred = pair.calculate_forces(iteration_number, iteration_size, eval_prior_frequency)
        if occurred:
            if pair.body_1 not in bodies_updated:
                bodies_updated.append(pair.body_1)
            if pair.body_2 not in bodies_updated:
                bodies_updated.append(pair.body_2)
    return bodies_updated


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
                            eval(separated_body[3]), eval(separated_body[4]), eval(separated_body[5]))
            for pair in current_bodies:
                force_pairs.append(BodyPair(new_body, pair))
            current_bodies.append(new_body)
    file_contents.close()
    return force_pairs, current_bodies


def main_loop(time_to_sim: float, time_per_iteration: float, force_pairs: list[BodyPair], bodies: list[Body],
              graph_update_frequency: int, eval_prior_frequency: int, add_pos_frequency: int) -> None:
    """Run the main loop of the simulation."""
    iteration_numbers = (x for x in range(0, int(time_to_sim / time_per_iteration)))
    for iteration in iteration_numbers:
        iteration_bodies_to_move = update_forces(force_pairs, iteration, time_per_iteration, eval_prior_frequency)
        for body_to_move in iteration_bodies_to_move:
            body_to_move.accelerate(time_per_iteration, iteration)
            body_to_move.move(iteration, time_per_iteration, add_pos_frequency)
            if iteration % graph_update_frequency == 0:
                plot_positions_initial(bodies)


def read_file_settings() -> list[int]:
    """Read the run settings off the txt file"""
    file_contents = open("programme settings")
    settings: dict[str, int] = {}
    for line in file_contents:
        settings[line.split(":")[0]] = int(line.split(":")[1])
    return [settings["Simulated time"], settings["Time per iteration"], settings["Iterations per graph update"],
            settings["Evaluate priority frequency"], settings["Add to past positions"]]


def main() -> None:
    """Start and run the main programme"""
    settings = read_file_settings()
    programme_start = time.time()
    simulated_time: int = settings[0]
    bodies_tuple: tuple[[BodyPair], list[Body]] = read_input_bodies()
    body_pairs: list[BodyPair] = bodies_tuple[0]
    bodies: list[Body] = bodies_tuple[1]
    matplotlib.use('TkAgg')
    plt.axes()
    plt.ion()
    plt.show()

    main_loop(simulated_time, settings[1], body_pairs, bodies, settings[2], settings[3], settings[4])

    programme_finish = time.time()
    print(programme_finish - programme_start)
    plot_positions_initial(bodies)
    plt.pause(1)


main()

end = input()

# 1000 repeats at 10,000 sec: 54498692038.55139  4514626615668.019
# 10000 repeats at 1,000 sec: 54498692037.376564 4514626909139.937
# 100000 repeats at 100, sec: 54498692037.37566  4514626938487.132
# 1000,000 repeats at 10 sec: 54498692037.378586 4514626941421.877

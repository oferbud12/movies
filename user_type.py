from movie_order import MovieOrder
import math


class UserType(MovieOrder):

    TYPE_ENDS = {1: {"vertical":
                         {"start": 0.00000000001, "end": 0.5},
                     "horizontal":
                         {"start": 0.00000000001, "end": float(1/3)}
                     },
                 2: {"vertical":
                         {"start": 0.00000000001, "end": 0.5},
                     "horizontal":
                         {"start": float(1/3), "end": float(2/3)}
                     },
                 3: {"vertical":
                         {"start": 0.00000000001, "end": 0.5},
                     "horizontal":
                         {"start": float(2/3), "end": 1}
                     },
                 4: {"vertical":
                         {"start": 0.5, "end": float(3/4)},
                     "horizontal":
                         {"start": 0.00000000001, "end": float(1/3)}
                     },
                 5: {"vertical":
                         {"start": 0.5, "end": float(3 / 4)},
                     "horizontal":
                         {"start": float(1/3), "end": float(2/3)}
                     },
                 6: {"vertical":
                         {"start": 0.5, "end": float(3 / 4)},
                     "horizontal":
                         {"start": float(2/3), "end": 1}
                     },
                 7: {"vertical":
                         {"start": float(3/4), "end": 1},
                     "horizontal":
                         {"start": 0.00000000001, "end": float(1/3)}
                     },
                 8: {"vertical":
                         {"start": float(3 / 4), "end": 1},
                     "horizontal":
                         {"start": float(1 / 3), "end": float(2 / 3)}
                     },
                 9: {"vertical":
                         {"start": float(3 / 4), "end": 1},
                     "horizontal":
                         {"start": float(2/3), "end": 1}
                     }
                 }

    def __init__(self, user_type, *args, **kwargs):
        super(UserType, self).__init__(*args, **kwargs)
        self.type = user_type
        self.gush_ends = self.get_gush_ends()
        self.validate_tickets_number_for_gush_ends()
        self.type_height_ratio = self.get_type_height_ratio()
        self.type_horizontal_ratio = self.get_type_horizontal_ratio()
        self.max_movement_between_lines = self.get_max_movement_between_lines()

        self.max_movement_for_ideal_best_line = 2

    @staticmethod
    def compute_for_type(ratio, num):
        return math.ceil(ratio * num)

    def get_gush_ends(self):
        vertical_type_start = self.compute_for_type(self.TYPE_ENDS[self.type]["vertical"]["start"], self.theater_measures[1])
        vertical_type_end = self.compute_for_type(self.TYPE_ENDS[self.type]["vertical"]["end"], self.theater_measures[1])
        horizontal_type_start = self.compute_for_type(self.TYPE_ENDS[self.type]["horizontal"]["start"], self.theater_measures[0])
        horizontal_type_end = self.compute_for_type(self.TYPE_ENDS[self.type]["horizontal"]["end"], self.theater_measures[0])
        return (horizontal_type_start, horizontal_type_end), (vertical_type_start, vertical_type_end)

    def validate_tickets_number_for_gush_ends(self):
        seats_in_gush = self.gush_ends[0][1] - self.gush_ends[0][0] + 1
        if self.tickets > seats_in_gush:
            raise Exception("Not enough seats in this part to accommodate all %s participants" % self.tickets)

    def get_type_height_ratio(self):
        height_start = self.TYPE_ENDS[self.type]["vertical"]["start"]
        height_end = self.TYPE_ENDS[self.type]["vertical"]["end"]
        middle_difference = (height_end - height_start) / 2
        ratio = height_start + middle_difference
        return ratio

    def get_type_horizontal_ratio(self):
        horizon_start = self.TYPE_ENDS[self.type]["horizontal"]["start"]
        horizon_end = self.TYPE_ENDS[self.type]["horizontal"]["end"]
        middle_difference = (horizon_end - horizon_start) / 2
        ratio = horizon_start + middle_difference
        return ratio

    def get_max_movement_between_lines(self):
        max_movement_between_lines = self.gush_ends[1][1] - self.gush_ends[1][0]
        return max_movement_between_lines

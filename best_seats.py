import math


class MovieOrder:

    def __init__(self, seats_db, tickets):
        self.real_seats_db = seats_db
        self.horizon_length = self.theater_measures()
        self.seats_db = self.keep_free_seats_only()
        self.tickets = tickets
        self.optional_lines = self.get_optional_lines()
        self.fake_optional_lines = self.fake_the_optional_lines()

    def theater_measures(self):
        last_seat_in_line = lambda line: list(self.real_seats_db[line]["seats"].keys())[-1]
        real_lines_length = [(last_seat_in_line(line) + self.real_seats_db[line]["seats"][last_seat_in_line(line)]["offset"]) for line in self.real_seats_db.keys()]
        horizon_length_reference = max(real_lines_length)
        return horizon_length_reference

    def keep_free_seats_only(self):
        # Filter the seats_db and keep only the free seats
        seats_db = self.real_seats_db
        for line, seats_dict in self.real_seats_db.items():
            free_seats_dict = {seat: seats_dict["seats"][seat]["offset"] for seat in seats_dict["seats"].keys() if seats_dict["seats"][seat]["state"] == "0"}
            seats_db[line]["seats"] = free_seats_dict
        return seats_db

    def get_line_chunks(self, line):
        # Function used to divide a line's seats into chunks -
        # according to both 'jump' in the seats' offset and a break in the sequence (non-free seats in the line)
        # Returns the line as a list of chunks -
        # each chunk is a dict, the seats are the keys and their offset is their value --> [ {1: 0, 2: 0}, {3: 1} ]
        seats_in_line = self.seats_db[line]["seats"]
        new_chunks_seats = []
        chunks = []

        for seat in list(seats_in_line.keys())[1:]:
            try:
                if seats_in_line[seat] != seats_in_line[seat - 1]:
                    # This seat is from a new chunk
                    new_chunks_seats.append(seat)
            except KeyError:
                # Sequence break - there's no (free) self.seats_db[line][seat - 1], this counts as a new chunk as well
                new_chunks_seats.append(seat)
        for new_chunk_seat in new_chunks_seats:
            chunk = {seat: seats_in_line[seat] for seat in seats_in_line.keys() if seat < new_chunk_seat}
            chunks.append(chunk)
            seats_in_line = {seat: seats_in_line[seat] for seat in seats_in_line.keys() if seat >= new_chunk_seat}
        chunks.append(seats_in_line)
        return chunks

    def get_optional_lines(self):
        # Returns a dict of lines and chunks of seats in each line, which are optional -
        # each chunk has enough (free) seats and can accommodate all participants --> { 1: [ {1: 0, 2: 0} ] }
        optional_lines = {}
        lines = list(self.seats_db.keys())
        for line in lines:
            valid = None
            valid_chunks = []

            chunks = self.get_line_chunks(line)
            for chunk in chunks:
                if len(chunk) >= self.tickets:
                    valid = True
                    optional_lines[line] = {"line_offset": None, "seats": []}
                    valid_chunks.append(chunk)
                else:
                    continue
            if valid is True:
                optional_lines[line]["line_offset"] = self.seats_db[line]["line_offset"]
                optional_lines[line]["seats"] = valid_chunks
            else:
                continue
        if len(optional_lines) == 0:
            raise Exception("No chunk is big enough to accommodate all participants.")
        else:
            print(optional_lines)
            return optional_lines

    def fake_the_optional_lines(self):
        # Function used to "fake" the optional lines dict -
        # it changes each chunk's seat to its real location in the theater space, by re-initializing it with its offset

        fake_the_chunk = lambda chunk: {seat + chunk[seat]: chunk[seat] for seat in chunk.keys()}
        fake_the_line = lambda line, line_offset: line + line_offset

        fake_optional_lines = {fake_the_line(line, self.optional_lines[line]["line_offset"]): {"line_offset": self.optional_lines[line]["line_offset"], "seats": [fake_the_chunk(chunk) for chunk in self.optional_lines[line]["seats"]]} for line in self.optional_lines.keys()}

        # fake_optional_lines = {fake_the_line(line, self.optional_lines[line]["line_offset"]): {"line_offset": self.optional_lines[line]["line_offset"], "seats":
        #     [fake_the_chunk(chunk) for chunk in self.optional_lines[line]["seats"]] for line in self.optional_lines.keys()}
        print(fake_optional_lines)
        return fake_optional_lines


class BestSeats(MovieOrder):

    def __init__(self, *args, **kwargs):
        self.steps_away_from_ideal = 0
        super(BestSeats, self).__init__(*args, **kwargs)
        self.best_seats = self.find_best_seats()

    def get_best_line_for_theater_measures(self, type_height_ratio=0.75):
        # Find the best line candidate in the real seats_db -
        # if no conditions were involved, according to the type_height_ratio and the theater's measures
        real_last_line = list(self.real_seats_db.keys())[-1]
        max_fake_line = real_last_line + self.optional_lines[real_last_line]["line_offset"]
        best_line = int(math.ceil(type_height_ratio * int(max_fake_line)))
        return best_line

    def validate_best_line_for_theater_measures(self, best_line, max_movement_between_lines=3):
        # Rotate as less as possible to find the closest best_line_for_theater_measures in our optional lines
        if best_line not in self.fake_optional_lines.keys():
            for i in range(1, (max_movement_between_lines * 2) + 1):
                if i % 2 != 0:
                    best_line += i
                elif i % 2 == 0:
                    best_line -= i
                self.steps_away_from_ideal += 1
                if best_line in self.optional_lines.keys():
                    return best_line
                else:
                    continue
            raise Exception("Moved too much from the best_line_for_theater_measures, you shouldn't order.")
        else:
            return best_line

    def get_best_seats_for_theater_measures(self, type_horizontal_ratio=2):
        # Find the best seats candidates in our horizontal_length_reference -
        # if no conditions were involved, according to our tickets number and the type_horizon_ratio
        seats_in_horizontal_length_reference = list(range(1, self.horizon_length + 1))
        best_seat_in_line = int(math.ceil(seats_in_horizontal_length_reference[-1] / type_horizontal_ratio))
        places_to_add = self.tickets - 1
        on_the_left = int(math.ceil(places_to_add / 2.0))
        on_the_right = places_to_add - on_the_left
        start_seat = best_seat_in_line - on_the_left
        end_seat = best_seat_in_line + on_the_right
        return list(range(start_seat, end_seat + 1))

    def validate_best_seats_in_best_line_chunks(self, optional_best_seats, optional_best_line):
        # Function used to validate that our optional_best_seats are contained in one of the optional best line's chunks
        optional_best_seats_are_found_in_chunk = None
        for chunk in self.fake_optional_lines[optional_best_line]["seats"]:
            if set(optional_best_seats).intersection(set(chunk.keys())) == set(optional_best_seats):
                optional_best_seats_are_found_in_chunk = True
                break
            else:
                continue
        return optional_best_seats_are_found_in_chunk

    @staticmethod
    def move_optional_best_seats_horizontally(places_to_move, optional_best_seats):
        # Function used to move a seats list
        new_optional_best_seats = list(range(optional_best_seats[0] + places_to_move, optional_best_seats[-1] + 1 + places_to_move))
        return new_optional_best_seats

    def unfake_best_seats(self, best_seats, best_line):
        # Function used after we've found our best_seats in the best_line -
        # converts the fake seats to the actual seat number in the movie theater
        interesting_chunk = None
        for chunk in self.fake_optional_lines[best_line]["seats"]:
            if set(best_seats).intersection(set(chunk.keys())) == set(best_seats):
                interesting_chunk = chunk
                break
            else:
                continue
        interesting_chunk_only_best_seats = {seat: interesting_chunk[seat] for seat in interesting_chunk.keys() if seat in best_seats}
        real_interesting_chunk_only_best_seats = {seat - interesting_chunk_only_best_seats[seat]: interesting_chunk_only_best_seats[seat] for seat in interesting_chunk_only_best_seats.keys()}
        real_best_line = best_line - self.fake_optional_lines[best_line]["line_offset"]
        return real_interesting_chunk_only_best_seats, real_best_line

    def validate_optional_best_seats(self, optional_best_seats, optional_best_line, max_movement_in_line=2):
        # Rotate the optional best seats as less as possible,
        # until fitting inside one of the optional best line's fake chunks - as if there was no offset
        optional_best_seats_are_valid = self.validate_best_seats_in_best_line_chunks(optional_best_seats, optional_best_line)
        if optional_best_seats_are_valid is not True:
            for i in range(1, (max_movement_in_line * 2) + 1):
                if i % 2 != 0:
                    optional_best_seats = self.move_optional_best_seats_horizontally(i, optional_best_seats)
                elif i % 2 == 0:
                    optional_best_seats = self.move_optional_best_seats_horizontally(-i, optional_best_seats)
                self.steps_away_from_ideal += 1
                optional_best_seats_are_valid = self.validate_best_seats_in_best_line_chunks(optional_best_seats, optional_best_line)
                if optional_best_seats_are_valid is True:
                    return self.unfake_best_seats(optional_best_seats, optional_best_line)
                else:
                    continue
            return False, False
        else:
            return self.unfake_best_seats(optional_best_seats, optional_best_line)

    def find_best_seats(self, max_movement_between_lines=2):
        best_line_for_theater_measures = self.validate_best_line_for_theater_measures(self.get_best_line_for_theater_measures())
        best_seats_for_theater_measures = self.get_best_seats_for_theater_measures()
        validation_of_ideal_best_seats = self.validate_optional_best_seats(best_seats_for_theater_measures, best_line_for_theater_measures)
        if validation_of_ideal_best_seats[0] is False:
            validation_of_optional_best_seats = None
            for i in range(1, (max_movement_between_lines * 2) + 1):
                self.steps_away_from_ideal += 1
                if i % 2 != 0:
                    validation_of_optional_best_seats = self.validate_optional_best_seats(best_seats_for_theater_measures, best_line_for_theater_measures + i, 2)
                elif i % 2 == 0:
                    validation_of_optional_best_seats = self.validate_optional_best_seats(best_seats_for_theater_measures, best_line_for_theater_measures - i, 2)
                if validation_of_optional_best_seats[0] is not False:
                    return validation_of_optional_best_seats
                else:
                    continue
            return "too much movement, shouldn't buy tickets at all"
        else:
            return validation_of_ideal_best_seats


if __name__ == "__main__":

    movie_seats = {1: {'line_offset': 0, 'seats': {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 2: {'line_offset': 0, 'seats': {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 3: {'line_offset': 0, 'seats': {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 4: {'line_offset': 0, 'seats': {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 5: {'line_offset': 0, 'seats': {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 6: {'line_offset': 0, 'seats': {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 7: {'line_offset': 0, 'seats': {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 8: {'line_offset': 1, 'seats': {1: {'state': '0', 'offset': 10}, 2: {'state': '0', 'offset': 10}, 3: {'state': '0', 'offset': 10}, 4: {'state': '0', 'offset': 10}, 5: {'state': '0', 'offset': 10}, 6: {'state': '0', 'offset': 10}, 7: {'state': '0', 'offset': 10}, 8: {'state': '0', 'offset': 10}, 9: {'state': '0', 'offset': 10}, 10: {'state': '0', 'offset': 10}, 11: {'state': '0', 'offset': 10}, 12: {'state': '0', 'offset': 10}, 13: {'state': '0', 'offset': 10}, 14: {'state': '0', 'offset': 10}, 15: {'state': '0', 'offset': 10}}}, 9: {'line_offset': 1, 'seats': {1: {'state': '0', 'offset': 8}, 2: {'state': '0', 'offset': 8}, 3: {'state': '0', 'offset': 8}, 4: {'state': '0', 'offset': 8}, 5: {'state': '0', 'offset': 8}, 6: {'state': '0', 'offset': 8}, 7: {'state': '0', 'offset': 8}, 8: {'state': '0', 'offset': 8}, 9: {'state': '0', 'offset': 8}, 10: {'state': '0', 'offset': 8}, 11: {'state': '0', 'offset': 8}, 12: {'state': '0', 'offset': 8}, 13: {'state': '0', 'offset': 8}, 14: {'state': '0', 'offset': 8}, 15: {'state': '0', 'offset': 8}, 16: {'state': '0', 'offset': 8}, 17: {'state': '0', 'offset': 8}, 18: {'state': '0', 'offset': 8}, 19: {'state': '0', 'offset': 8}, 20: {'state': '0', 'offset': 8}}}, 10: {'line_offset': 1, 'seats': {1: {'state': '0', 'offset': 8}, 2: {'state': '0', 'offset': 8}, 3: {'state': '0', 'offset': 8}, 4: {'state': '0', 'offset': 8}, 5: {'state': '0', 'offset': 8}, 6: {'state': '0', 'offset': 8}, 7: {'state': '0', 'offset': 8}, 8: {'state': '0', 'offset': 8}, 9: {'state': '0', 'offset': 8}, 10: {'state': '0', 'offset': 8}, 11: {'state': '0', 'offset': 8}, 12: {'state': '0', 'offset': 8}, 13: {'state': '0', 'offset': 8}, 14: {'state': '0', 'offset': 8}, 15: {'state': '0', 'offset': 8}, 16: {'state': '0', 'offset': 8}, 17: {'state': '0', 'offset': 8}, 18: {'state': '0', 'offset': 8}, 19: {'state': '0', 'offset': 8}, 20: {'state': '0', 'offset': 8}}}, 11: {'line_offset': 1, 'seats': {1: {'state': '0', 'offset': 8}, 2: {'state': '0', 'offset': 8}, 3: {'state': '0', 'offset': 8}, 4: {'state': '0', 'offset': 8}, 5: {'state': '0', 'offset': 8}, 6: {'state': '0', 'offset': 8}, 7: {'state': '0', 'offset': 8}, 8: {'state': '0', 'offset': 8}, 9: {'state': '0', 'offset': 8}, 10: {'state': '0', 'offset': 8}, 11: {'state': '0', 'offset': 8}, 12: {'state': '0', 'offset': 8}, 13: {'state': '0', 'offset': 8}, 14: {'state': '0', 'offset': 8}, 15: {'state': '0', 'offset': 8}, 16: {'state': '0', 'offset': 8}, 17: {'state': '0', 'offset': 8}, 18: {'state': '0', 'offset': 8}, 19: {'state': '0', 'offset': 8}, 20: {'state': '0', 'offset': 8}}}, 12: {'line_offset': 1, 'seats': {1: {'state': '-', 'offset': 0}, 2: {'state': '-', 'offset': 0}, 3: {'state': '-', 'offset': 0}, 4: {'state': '-', 'offset': 0}, 5: {'state': '0', 'offset': 4}, 6: {'state': '0', 'offset': 4}, 7: {'state': '0', 'offset': 4}, 8: {'state': '0', 'offset': 4}, 9: {'state': '0', 'offset': 4}, 10: {'state': '0', 'offset': 4}, 11: {'state': '0', 'offset': 4}, 12: {'state': '0', 'offset': 4}, 13: {'state': '0', 'offset': 4}, 14: {'state': '0', 'offset': 4}, 15: {'state': '0', 'offset': 4}, 16: {'state': '0', 'offset': 4}, 17: {'state': '0', 'offset': 4}, 18: {'state': '0', 'offset': 4}, 19: {'state': '0', 'offset': 4}, 20: {'state': '0', 'offset': 4}, 21: {'state': '0', 'offset': 4}, 22: {'state': '0', 'offset': 4}, 23: {'state': '0', 'offset': 4}, 24: {'state': '0', 'offset': 4}}}, 13: {'line_offset': 1, 'seats': {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 14: {'line_offset': 1, 'seats': {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 15: {'line_offset': 1, 'seats': {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}}, 16: {'line_offset': 1, 'seats': {1: {'state': '0', 'offset': 2}, 2: {'state': '0', 'offset': 2}, 3: {'state': '0', 'offset': 2}, 4: {'state': '0', 'offset': 2}, 5: {'state': '0', 'offset': 2}, 6: {'state': '0', 'offset': 2}, 7: {'state': '0', 'offset': 2}, 8: {'state': '0', 'offset': 2}, 9: {'state': '0', 'offset': 2}, 10: {'state': '0', 'offset': 2}, 11: {'state': '0', 'offset': 2}, 12: {'state': '0', 'offset': 2}, 13: {'state': '0', 'offset': 2}, 14: {'state': '0', 'offset': 2}, 15: {'state': '0', 'offset': 2}, 16: {'state': '0', 'offset': 2}, 17: {'state': '0', 'offset': 2}, 18: {'state': '0', 'offset': 2}, 19: {'state': '0', 'offset': 2}, 20: {'state': '0', 'offset': 2}, 21: {'state': '0', 'offset': 2}, 22: {'state': '0', 'offset': 2}, 23: {'state': '0', 'offset': 2}, 24: {'state': '0', 'offset': 2}, 25: {'state': '0', 'offset': 2}, 26: {'state': '0', 'offset': 2}, 27: {'state': '0', 'offset': 2}, 28: {'state': '0', 'offset': 2}}}}
    movie_tickets = 9
    check = BestSeats(movie_seats, movie_tickets)
    print(check.best_seats)
    print(check.steps_away_from_ideal)

    # documentation
    # return also best line
    # real line in theater space support
    # add 'gushim' support in get_best_line_candidate and get_optional_best_seats
    # reverse for user

import math


class OrderBestSeats:

    def __init__(self, seats_db, tickets):
        self.real_seats_db = seats_db
        self.seats_db = self.keep_free_seats_only(self.real_seats_db)
        self.tickets = tickets
        self.optional_lines = self.get_optional_lines()
        self.best_line = self.validate_best_line(self.get_best_line_candidate())
        self.best_seats_in_best_line = self.validate_best_seats(self.get_optional_best_seats())

    # Phase 1 - choose best line:
    # check if there's enough seat in the line's chunks (filter to optional lines)
    # find the best line candidate according to the type_ratio and seats_db
    # compare this candidate to the optional lines and fix accordingly (find the nearest)

    @classmethod
    def keep_free_seats_only(cls, seats_db):
        # Filter the seats_db and keep only the free seats
        for line, seats_dict in seats_db.items():
            free_seats_dict = {seat: seats_dict[seat] for seat in seats_dict.keys() if seats_dict[seat]["state"] == "0"}
            seats_db[line] = free_seats_dict
        return seats_db

    def get_line_chunks(self, line):
        # Function used to divide a line's seats into chunks -
        # according to both 'jump' in the seats' offset and a break in the sequence (non-free seats in the line)
        seats_in_line = list(self.seats_db[line].keys())
        new_chunks_seats = []
        chunks = []
        for seat in seats_in_line[1:]:
            try:
                if self.seats_db[line][seat]["offset"] != self.seats_db[line][seat - 1]["offset"]:
                    # This seat is from a new chunk
                    new_chunks_seats.append(seat)
            except KeyError:
                # Sequence break - there's no (free) self.seats_db[line][seat - 1], this counts as a new chunk as well
                new_chunks_seats.append(seat)
        for new_chunk_seat in new_chunks_seats:
            chunk = [seat for seat in seats_in_line if seat < new_chunk_seat]
            chunks.append(chunk)
            seats_in_line = seats_in_line[len(chunk):]
        line_divided_by_offsets_and_non_free_seats = chunks + [seats_in_line]
        return line_divided_by_offsets_and_non_free_seats

    def get_optional_lines(self):
        # Returns a dict of lines and chunks of seats in each line, which are optional -
        # the seats in each chunk are free and can accommodate all participants.
        optional_lines = {}
        lines = list(self.seats_db.keys())
        for line in lines:
            valid = None
            valid_chunks = []

            chunks = self.get_line_chunks(line)
            for chunk in chunks:
                if len(chunk) >= self.tickets:
                    valid = True
                    valid_chunks.append(chunk)
                else:
                    continue
            if valid is True:
                optional_lines[line] = valid_chunks
            else:
                continue
        return optional_lines

    # Notice to type ratio!

    def get_best_line_candidate(self, type_ratio=0.75):
        # Finds the best line candidate in the real seats_db, if no conditions were involved
        max_line = list(self.real_seats_db.keys())[-1]
        best_line = int(math.ceil(type_ratio * int(max_line)))
        return best_line

    def validate_best_line(self, best_line):
        # Rotates as short as possible to find the best line in our optional lines
        max_movement = list(self.optional_lines.keys())[-1] - best_line
        if best_line not in self.optional_lines.keys():
            for i in range(1, (max_movement * 2) + 1):
                if i % 2 != 0:
                    best_line += i
                elif i % 2 == 0:
                    best_line -= i
                if best_line in self.optional_lines.keys():
                    break
        return best_line

    # Phase 2 - choose best seats:
    # find the best candidate seats in your chosen best line
    # compare to the real seats (and chunks) in this line and fix properly:
    #  set a limit to maximum horizontal movements and start skipping the lines
    # check if seats are free and skip smartly again

    def get_optional_best_seats(self):
        seats_in_best_line = list(self.seats_db[self.best_line].keys())
        best_seat_in_line = int(math.ceil(seats_in_best_line[-1] / 2))
        places_to_add = self.tickets - 1
        on_the_left = int(math.ceil(places_to_add / 2.0))
        on_the_right = places_to_add - on_the_left
        start_seat = best_seat_in_line - on_the_left
        end_seat = best_seat_in_line + on_the_right
        return list(range(start_seat, end_seat + 1))

    def validate_best_seats_in_best_line_chunks(self, optional_best_seats):
        optional_best_seats_are_found_in_chunk = None
        for chunk in self.optional_lines[self.best_line]:
            if set(optional_best_seats).intersection(set(chunk)) == set(optional_best_seats):
                optional_best_seats_are_found_in_chunk = True
                break
            else:
                continue
        return optional_best_seats_are_found_in_chunk

    def validate_best_seats(self, optional_best_seats):
        # Move the optional best seats until fitting in to one of the best line's chunks
        optional_best_seats_are_valid = self.validate_best_seats_in_best_line_chunks(optional_best_seats)
        if optional_best_seats_are_valid is not True:
            # Rotate when maximum movement is the difference between the last seat in the last chunk to the last seat in the optional best seats
            max_movement = self.optional_lines[self.best_line][-1][-1] - optional_best_seats[-1]
            for i in range(1, (max_movement * 2) + 1):
                if i % 2 != 0:
                    optional_best_seats = self.move_optional_best_seats_horizontally(i, optional_best_seats)
                elif i % 2 == 0:
                    optional_best_seats = self.move_optional_best_seats_horizontally(-i, optional_best_seats)
                optional_best_seats_are_valid = self.validate_best_seats_in_best_line_chunks(optional_best_seats)
                if optional_best_seats_are_valid is True:
                    break
        return optional_best_seats

    @staticmethod
    def move_optional_best_seats_horizontally(places_to_move, optional_best_seats):
        new_optional_best_seats = list(range(optional_best_seats[0] + places_to_move, optional_best_seats[-1] + 1 + places_to_move))
        return new_optional_best_seats


if __name__ == "main":

    movie_seats = {1: {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 2: {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 3: {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 4: {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 5: {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 6: {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 7: {1: {'state': '0', 'offset': 5}, 2: {'state': '0', 'offset': 5}, 3: {'state': '0', 'offset': 5}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 8: {}, 9: {1: {'state': '0', 'offset': 10}, 2: {'state': '0', 'offset': 10}, 3: {'state': '0', 'offset': 10}, 4: {'state': '0', 'offset': 10}, 5: {'state': '0', 'offset': 10}, 6: {'state': '0', 'offset': 10}, 7: {'state': '0', 'offset': 10}, 8: {'state': '-', 'offset': 10}, 9: {'state': '-', 'offset': 10}, 10: {'state': '0', 'offset': 10}, 11: {'state': '0', 'offset': 10}, 12: {'state': '0', 'offset': 10}, 13: {'state': '0', 'offset': 10}, 14: {'state': '0', 'offset': 10}, 15: {'state': '0', 'offset': 10}}, 10: {1: {'state': '0', 'offset': 8}, 2: {'state': '0', 'offset': 8}, 3: {'state': '0', 'offset': 8}, 4: {'state': '0', 'offset': 8}, 5: {'state': '0', 'offset': 8}, 6: {'state': '0', 'offset': 8}, 7: {'state': '0', 'offset': 8}, 8: {'state': '0', 'offset': 8}, 9: {'state': '0', 'offset': 8}, 10: {'state': '0', 'offset': 8}, 11: {'state': '0', 'offset': 8}, 12: {'state': '0', 'offset': 8}, 13: {'state': '0', 'offset': 8}, 14: {'state': '0', 'offset': 8}, 15: {'state': '0', 'offset': 8}, 16: {'state': '0', 'offset': 8}, 17: {'state': '0', 'offset': 8}, 18: {'state': '0', 'offset': 8}, 19: {'state': '0', 'offset': 8}, 20: {'state': '0', 'offset': 8}}, 11: {1: {'state': '0', 'offset': 8}, 2: {'state': '0', 'offset': 8}, 3: {'state': '0', 'offset': 8}, 4: {'state': '0', 'offset': 8}, 5: {'state': '0', 'offset': 8}, 6: {'state': '0', 'offset': 8}, 7: {'state': '0', 'offset': 8}, 8: {'state': '0', 'offset': 8}, 9: {'state': '0', 'offset': 8}, 10: {'state': '0', 'offset': 8}, 11: {'state': '0', 'offset': 8}, 12: {'state': '0', 'offset': 8}, 13: {'state': '0', 'offset': 8}, 14: {'state': '0', 'offset': 8}, 15: {'state': '0', 'offset': 8}, 16: {'state': '0', 'offset': 8}, 17: {'state': '0', 'offset': 8}, 18: {'state': '0', 'offset': 8}, 19: {'state': '0', 'offset': 8}, 20: {'state': '0', 'offset': 8}}, 12: {1: {'state': '0', 'offset': 8}, 2: {'state': '0', 'offset': 8}, 3: {'state': '0', 'offset': 8}, 4: {'state': '0', 'offset': 8}, 5: {'state': '0', 'offset': 8}, 6: {'state': '0', 'offset': 8}, 7: {'state': '0', 'offset': 8}, 8: {'state': '0', 'offset': 8}, 9: {'state': '0', 'offset': 8}, 10: {'state': '0', 'offset': 8}, 11: {'state': '0', 'offset': 8}, 12: {'state': '0', 'offset': 8}, 13: {'state': '0', 'offset': 8}, 14: {'state': '0', 'offset': 8}, 15: {'state': '0', 'offset': 8}, 16: {'state': '0', 'offset': 8}, 17: {'state': '0', 'offset': 8}, 18: {'state': '0', 'offset': 8}, 19: {'state': '0', 'offset': 8}, 20: {'state': '0', 'offset': 8}}, 13: {1: {'state': '-', 'offset': 0}, 2: {'state': '-', 'offset': 0}, 3: {'state': '-', 'offset': 0}, 4: {'state': '-', 'offset': 0}, 5: {'state': '0', 'offset': 4}, 6: {'state': '0', 'offset': 4}, 7: {'state': '0', 'offset': 4}, 8: {'state': '0', 'offset': 4}, 9: {'state': '0', 'offset': 4}, 10: {'state': '0', 'offset': 4}, 11: {'state': '0', 'offset': 4}, 12: {'state': '0', 'offset': 4}, 13: {'state': '0', 'offset': 4}, 14: {'state': '0', 'offset': 4}, 15: {'state': '0', 'offset': 4}, 16: {'state': '0', 'offset': 4}, 17: {'state': '0', 'offset': 4}, 18: {'state': '0', 'offset': 4}, 19: {'state': '0', 'offset': 4}, 20: {'state': '0', 'offset': 4}, 21: {'state': '0', 'offset': 4}, 22: {'state': '0', 'offset': 4}, 23: {'state': '0', 'offset': 4}, 24: {'state': '0', 'offset': 4}}, 14: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 15: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 16: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 5}, 5: {'state': '0', 'offset': 5}, 6: {'state': '0', 'offset': 5}, 7: {'state': '0', 'offset': 5}, 8: {'state': '0', 'offset': 5}, 9: {'state': '0', 'offset': 5}, 10: {'state': '0', 'offset': 5}, 11: {'state': '0', 'offset': 5}, 12: {'state': '0', 'offset': 5}, 13: {'state': '0', 'offset': 5}, 14: {'state': '0', 'offset': 5}, 15: {'state': '0', 'offset': 5}, 16: {'state': '0', 'offset': 5}, 17: {'state': '0', 'offset': 5}, 18: {'state': '0', 'offset': 5}, 19: {'state': '0', 'offset': 5}, 20: {'state': '0', 'offset': 5}, 21: {'state': '0', 'offset': 5}, 22: {'state': '0', 'offset': 5}, 23: {'state': '0', 'offset': 5}}, 17: {1: {'state': '0', 'offset': 2}, 2: {'state': '0', 'offset': 2}, 3: {'state': '0', 'offset': 2}, 4: {'state': '0', 'offset': 2}, 5: {'state': '0', 'offset': 2}, 6: {'state': '0', 'offset': 2}, 7: {'state': '0', 'offset': 2}, 8: {'state': '0', 'offset': 2}, 9: {'state': '0', 'offset': 2}, 10: {'state': '0', 'offset': 2}, 11: {'state': '0', 'offset': 2}, 12: {'state': '0', 'offset': 2}, 13: {'state': '0', 'offset': 2}, 14: {'state': '0', 'offset': 2}, 15: {'state': '0', 'offset': 2}, 16: {'state': '0', 'offset': 2}, 17: {'state': '0', 'offset': 2}, 18: {'state': '0', 'offset': 2}, 19: {'state': '0', 'offset': 2}, 20: {'state': '0', 'offset': 2}, 21: {'state': '0', 'offset': 2}, 22: {'state': '0', 'offset': 2}, 23: {'state': '0', 'offset': 2}, 24: {'state': '0', 'offset': 2}, 25: {'state': '0', 'offset': 2}, 26: {'state': '0', 'offset': 2}, 27: {'state': '0', 'offset': 2}, 28: {'state': '0', 'offset': 2}}}
    movie_tickets = 21
    check = OrderBestSeats(movie_seats, movie_tickets)

    # add 'gushim' support in get_best_line_candidate and get_optional_best_seats

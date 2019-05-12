import math


class OrderBestSeats:

    def __init__(self, seats_db, tickets):
        self.real_seats_db = seats_db
        self.horizon_length = self.theater_measures()
        self.seats_db = self.keep_free_seats_only(self.real_seats_db)
        self.tickets = tickets
        self.optional_lines = self.get_optional_lines()
        self.fake_optional_lines = self.fake_the_optional_lines()
        # self.best_line = self.validate_best_line(self.get_best_line_candidate())
        # last_play = self.validate_best_seats(self.get_optional_best_seats())
        # self.best_seats_in_best_line = last_play[0]
        # self.away_from_ideal = last_play[1]
        self.best_seats = self.find_best_seats(2)

    def theater_measures(self):
        last_seat_in_line = lambda line: list(self.real_seats_db[line].keys())[-1]
        real_lines_length = [(last_seat_in_line(line) + self.real_seats_db[line][last_seat_in_line(line)]["offset"]) for line in self.real_seats_db.keys()]
        horizon_length_reference = max(real_lines_length)
        return horizon_length_reference

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
        # Returns the line as a list of chunks (each chunk is also a list) --> [ {1: 0, 2: 0} ]

        seats_in_line = self.seats_db[line]
        seats_in_line = {seat: seats_in_line[seat]["offset"] for seat in seats_in_line.keys()}
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
        # each chunk has enough (free) seats and can accommodate all participants --> { 1: [ [3,4,5,6], [7,8,9] ] }
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
        if len(optional_lines) == 0:
            raise Exception("no chunk big enough to accomodate all")
        else:
            return optional_lines

    def get_best_line_candidate(self, type_height_ratio=0.75):
        # Find the best line candidate in the real seats_db -
        # if no conditions were involved, according to the type_height_ratio
        max_line = list(self.real_seats_db.keys())[-1]
        best_line = int(math.ceil(type_height_ratio * int(max_line)))
        return best_line

    def validate_best_line(self, best_line):
        # Rotate as less as possible to find the best line in our optional lines
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

    def get_optional_best_seats(self, type_horizontal_ratio=2):
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

    def fake_the_optional_lines(self):
        fake_the_chunk = lambda chunk: {seat + chunk[seat]: chunk[seat] for seat in chunk.keys()}
        fake_optional_lines = {line: [fake_the_chunk(chunk) for chunk in self.optional_lines[line]] for line in self.optional_lines.keys()}
        return fake_optional_lines

    def validate_best_seats_in_best_line_chunks(self, optional_best_seats, optional_best_line):
        # Function used to validate that our optional_best_seats are contained in one of the best line's chunks
        optional_best_seats_are_found_in_chunk = None
        for chunk in self.fake_optional_lines[optional_best_line]:
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

    def unfake_best_seats(self, optional_best_seats, best_line):
        interesting_chunk = None
        for chunk in self.fake_optional_lines[best_line]:
            if set(optional_best_seats).intersection(set(chunk.keys())) == set(optional_best_seats):
                interesting_chunk = chunk
                break
            else:
                continue
        interesting_chunk_only_best_seats = {seat: interesting_chunk[seat] for seat in interesting_chunk.keys() if seat in optional_best_seats}
        unfake_interesting_chunk_only_best_seats = {seat - interesting_chunk_only_best_seats[seat]: interesting_chunk_only_best_seats[seat] for seat in interesting_chunk_only_best_seats.keys()}
        return unfake_interesting_chunk_only_best_seats

    def validate_best_seats(self, optional_best_seats, optional_best_line, max_movement_in_line):
        # Rotate the optional best seats as less as possible,
        # until fitting in to one of the best line's fake chunks - as if there was no offset
        movements_away_from_ideal_seats = 0
        optional_best_seats_are_valid = self.validate_best_seats_in_best_line_chunks(optional_best_seats, optional_best_line)
        if optional_best_seats_are_valid is not True:
            # Maximum movement is the difference between the last seat in the last chunk,
            # to the last seat in the optional best seats
            #max_movement = list(self.fake_optional_lines[self.best_line][-1].keys())[-1] - optional_best_seats[-1]
            for i in range(1, (max_movement_in_line * 2) + 1):
                if i % 2 != 0:
                    optional_best_seats = self.move_optional_best_seats_horizontally(i, optional_best_seats)
                elif i % 2 == 0:
                    optional_best_seats = self.move_optional_best_seats_horizontally(-i, optional_best_seats)
                movements_away_from_ideal_seats += 1
                optional_best_seats_are_valid = self.validate_best_seats_in_best_line_chunks(optional_best_seats, optional_best_line)
                if optional_best_seats_are_valid is True:
                    return self.unfake_best_seats(optional_best_seats, optional_best_line), movements_away_from_ideal_seats
                else:
                    continue
            return False, movements_away_from_ideal_seats
        else:
            return self.unfake_best_seats(optional_best_seats, optional_best_line), movements_away_from_ideal_seats

    def find_best_seats(self, max_movement_between_lines):
        best_line_for_theater_measures = self.validate_best_line(self.get_best_line_candidate())
        best_seats_for_theater_measures = self.get_optional_best_seats()
        validation_of_best_seats = self.validate_best_seats(best_seats_for_theater_measures, best_line_for_theater_measures, 2)
        if validation_of_best_seats[0] is False:
            steps_away_from_ideal = validation_of_best_seats[1]
            # max_movement = list(self.fake_optional_lines[self.best_line][-1].keys())[-1] - optional_best_seats[-1]
            for i in range(1, (max_movement_between_lines * 2) + 1):
                steps_away_from_ideal += 1
                if i % 2 != 0:
                    validation_of_best_seats = self.validate_best_seats(best_seats_for_theater_measures, best_line_for_theater_measures + i, 2)
                elif i % 2 == 0:
                    validation_of_best_seats = self.validate_best_seats(best_seats_for_theater_measures, best_line_for_theater_measures - i, 2)
                steps_away_from_ideal += validation_of_best_seats[1]
                if validation_of_best_seats[0] is not False:
                    return validation_of_best_seats
                else:
                    continue
            return "too much movement, shouldn't buy tickets at all"
        else:
            return validation_of_best_seats


if __name__ == "__main__":

    movie_seats = {1: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 2: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 3: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 4: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 5: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 6: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 7: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 8: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 9: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 1}, 8: {'state': '0', 'offset': 1}, 9: {'state': '0', 'offset': 1}, 10: {'state': '0', 'offset': 1}, 11: {'state': '0', 'offset': 1}, 12: {'state': '0', 'offset': 1}, 13: {'state': '0', 'offset': 1}, 14: {'state': '0', 'offset': 1}, 15: {'state': '0', 'offset': 1}, 16: {'state': '0', 'offset': 1}, 17: {'state': '0', 'offset': 1}, 18: {'state': '0', 'offset': 1}, 19: {'state': '0', 'offset': 1}, 20: {'state': '0', 'offset': 1}, 21: {'state': '0', 'offset': 1}}, 10: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 0}, 7: {'state': '0', 'offset': 6}, 8: {'state': '0', 'offset': 6}, 9: {'state': '0', 'offset': 6}, 10: {'state': '0', 'offset': 6}, 11: {'state': '0', 'offset': 6}, 12: {'state': '0', 'offset': 6}, 13: {'state': '0', 'offset': 6}, 14: {'state': '0', 'offset': 6}, 15: {'state': '0', 'offset': 6}, 16: {'state': '0', 'offset': 6}}, 11: {1: {'state': '0', 'offset': 0}, 2: {'state': '0', 'offset': 0}, 3: {'state': '0', 'offset': 0}, 4: {'state': '0', 'offset': 0}, 5: {'state': '0', 'offset': 0}, 6: {'state': '0', 'offset': 8}, 7: {'state': '0', 'offset': 8}, 8: {'state': '0', 'offset': 8}, 9: {'state': '0', 'offset': 8}, 10: {'state': '0', 'offset': 8}, 11: {'state': '0', 'offset': 8}, 12: {'state': '0', 'offset': 8}, 13: {'state': '0', 'offset': 8}, 14: {'state': '0', 'offset': 8}}}
    movie_tickets = 9
    check = OrderBestSeats(movie_seats, movie_tickets)
    print(check.best_seats)

    # add 'gushim' support in get_best_line_candidate and get_optional_best_seats

class MovieOrder:

    def __init__(self, seats_db, tickets):
        self.real_seats_db = seats_db
        self.theater_measures = self.get_theater_measures()
        self.seats_db = self.keep_free_seats_only()
        self.tickets = tickets
        self.optional_lines = self.get_optional_lines()
        self.fake_optional_lines = self.fake_the_optional_lines()

    def get_theater_measures(self):
        # Function used to get the theater's measures -
        # returns a tuple: (max_fake seat = horizontal length, max_fake_line = vertical length)
        last_seat_in_line = lambda line: list(self.real_seats_db[line]["seats"].keys())[-1]
        max_fake_seat = max([(last_seat_in_line(line) + self.real_seats_db[line]["seats"][last_seat_in_line(line)]["offset"]) for line in self.real_seats_db.keys()])
        last_line = list(self.real_seats_db.keys())[-1]
        max_fake_line = last_line + self.real_seats_db[last_line]["line_offset"]
        return max_fake_seat, max_fake_line

    def keep_free_seats_only(self):
        # Filter the given seats_db (stored as 'real_seats_db'), and keep only the free seats
        seats_db = self.real_seats_db
        for line, seats_dict in self.real_seats_db.items():
            free_seats_dict = {seat: seats_dict["seats"][seat]["offset"] for seat in seats_dict["seats"].keys() if seats_dict["seats"][seat]["state"] == "0"}
            seats_db[line]["seats"] = free_seats_dict
        return seats_db

    def get_line_chunks(self, line):
        # Function used to divide a line's seats into chunks -
        # according to both 'jump' in the seats' offset and a break in the seats' sequence (non-free seats in the line).
        # This function returns the line as a list of chunks -
        # each chunk is a dict: the seats are the keys and their offset is their value --> [ {1: 0, 2: 0}, {3: 1} ]
        seats_in_line = self.seats_db[line]["seats"]
        new_chunks_seats = []
        chunks = []

        for seat in list(seats_in_line.keys())[1:]:
            try:
                if seats_in_line[seat] != seats_in_line[seat - 1]:
                    # Offset changed, This seat is from a new chunk
                    new_chunks_seats.append(seat)
            except KeyError:
                # Sequence break - there's no (free) self.seats_db[line][seat - 1], this counts as a new chunk as well
                new_chunks_seats.append(seat)
        for new_chunk_seat in new_chunks_seats:
            # Build the chunk according to the new_chunks_seats list:
            chunk = {seat: seats_in_line[seat] for seat in seats_in_line.keys() if seat < new_chunk_seat}
            chunks.append(chunk)
            seats_in_line = {seat: seats_in_line[seat] for seat in seats_in_line.keys() if seat >= new_chunk_seat}
        chunks.append(seats_in_line)
        return chunks

    def get_optional_lines(self):
        # Returns a dict of lines and lists consisting chunks of seats in each line, which are optional -
        # each chunk has enough (free) seats and can accommodate all participants.
        optional_lines = {}
        lines = list(self.seats_db.keys())

        for line in lines:
            valid = None
            valid_chunks = []
            chunks = self.get_line_chunks(line)
            for chunk in chunks:
                if len(chunk) >= self.tickets:
                    valid = True
                    # Construct the line key and proper dict value in the optional_lines_dict -
                    # no problem with re-doing this here for more valid chunks -
                    # since no actual values are set at this point.
                    optional_lines[line] = {"line_offset": None, "seats": []}
                    valid_chunks.append(chunk)
                else:
                    continue
            if valid is True:
                # This line has optional chunks to accommodate all participants -
                # adding only the valid chunks, and keeping the line_offset as well for later use.
                optional_lines[line]["line_offset"] = self.seats_db[line]["line_offset"]
                optional_lines[line]["seats"] = valid_chunks
            else:
                # This line isn't valid and can't accommodate all participants
                continue

        if len(optional_lines) == 0:
            # There are no optional lines
            raise Exception("No chunk is big enough to accommodate all participants.")
        else:
            return optional_lines

    def fake_the_optional_lines(self):
        # Function used to "fake" the optional lines dict -
        # it changes each chunk's seat to its real location in the theater space, by re-initializing it with its offset.
        # It does the same with the lines value - re-initializing it with its offset.
        # The offsets are still stored as values inside the dicts, for later use (unfake).
        # The returned dict represents the real location of each seat and line in the theater's space.
        fake_the_chunk = lambda chunk: {seat + chunk[seat]: chunk[seat] for seat in chunk.keys()}
        fake_the_line = lambda line, line_offset: line + line_offset
        fake_optional_lines = {fake_the_line(line, self.optional_lines[line]["line_offset"]): {"line_offset": self.optional_lines[line]["line_offset"],
                                                                                               "seats": [fake_the_chunk(chunk) for chunk in self.optional_lines[line]["seats"]]
                                                                                               } for line in self.optional_lines.keys()}
        return fake_optional_lines







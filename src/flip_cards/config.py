class Config:
    QUESTION_START_INDEX = 0  # Inclusive
    QUESTION_END_INDEX = 3  # Exclusive

    N_RANDOM_QUESTIONS = 2  # Indicates the number of unique questions during overhoring
    ANSWER_SUGGESTIONS = False  # If True, will present species options in the current overhoring
    RANDOM_SELECTION = False  # If True, will select questions randomly, else in order

    # If True, will multiply the species list by a large number (so not really infinite)
    INFINITE_PRACTICE = False

    SELECTED_QUESTIONS = []
    INCLUDED_TAGS = []
    EXCLUDED_TAGS = []

    def dict(self):
        """Turns config into dict and lowers the keys"""
        return {
            key.lower(): value
            for key, value in vars(self.__class__).items()
            if not (key.startswith("__") or key == "dict")
        }

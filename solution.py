import logging
logging.basicConfig(level=logging.ERROR)

assignments = []


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]


rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

# This is builds the diagonal unit A1,B2,C3...,I9
diag_unit1 = [rows[i] + cols[i] for i in range(len(rows))]
# This is builds the diagonal unit I1,H2,G3...,A9. Note the reversed order of the rows-string
diag_unit2 = [rows[::-1][i] + cols[i] for i in range(len(rows))]
# Create a list of diagonal units
diag_unit = [diag_unit1, diag_unit2]
# Update the unitlits to include the diagonal units list
unitlist = row_units + column_units + square_units + diag_unit
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def find_twins(values, unit, box):
    """Find naked twin values for a given box in a givin unit.
    :param values: the values dictionary
    :param unit: the unit to look at
    :param box: the box to look at
    :return: True if a naked twin is found for this box. False otherwise.
    """
    box_value = values[box]
    # Naked twins only works for 'twins', so we skip boxes with possible values that are not a pair
    if len(box_value) != 2:
        return False

    # 3. See if any other box in the same unit shares the same set of possible values
    # The bool above is used to store if we have seen such a box in the unit
    for b in unit:
        # Skip the box for which we're looking for twins
        if box == b:
            continue

        # Compare the list of possible values for box 'b', with the list of possible values for the current
        # 'box' we're looking at
        # If the values match, we have a naked twin, and so we set the bool, and break out of the for-loop
        if values[b] == box_value:
            return True

    return False


def eliminate_twins(values,unit,box):
    """ Prune naked twin values from possible values of other boxes in the same unit

    :param values: the values dictionary
    :param unit: the unit to look at
    :param box: the box containing a naked twin pair to be pruned from all other boxes in the same unit
    :return: the values dictionary with the naked twins eliminated from peers.
    """
    # Remove each possible value of the naked twin pair from the list of possible values of all other
    # boxes in the same unit
    for b in unit:
        box_value = values[box]
        val = values[b]
        # Only prune values, for a box that is not a naked twins
        if val != box_value:
            for v in box_value:
                if v in val:
                    val = val.replace(v, "")
            assign_value(values, b, val)

    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # 1. Iterate over all units
    for unit in unitlist:
        # 2. For each box in a unit
        for box in unit:
            if find_twins(values, unit, box):
                # 4. If two boxes in the same unit share the same set of possible values =>
                values = eliminate_twins(values,unit,box)

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
            #values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                #values[dplaces[0]] = digit
                assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)

        # Propagate constraint about naked twins
        values = naked_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

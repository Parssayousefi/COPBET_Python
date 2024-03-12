# LZ complexity code DMT EEG paper


def cpr(string):
    # Initialize an empty dictionary
    dict = {}
    complexity = 1
    # Initialize an empty string to keep track of the window of characters
    w = ""
    # Initialize b outside the loop
    b = 1
    # Iterate over each character in the input string
    for index, c in enumerate(string):
        # Debugging: Print the current iteration number
        print("current iteration:", b)
        # Debugging: Print the current character
        print(f"current character: {c}, at position: {index+1}")
        # Add the current character to the window
        wc = w + c
        # Debugging: Print the current window of characters
        print("window + current character:", wc)
        # Check if the window is already in the dictionary
        if wc in dict:
            w = wc
            # Debugging: Print the current window
            print("window:", w)
            # If it is, just update the window to include the current character
            print(f"wc ({wc}) is in dict, so {wc} wont be added to dict")

        else:
            # If it's not, add it to the dictionary and reset the window
            print(f"wc ({wc}) is not in dict, so {wc} will be added to dict:")
            dict[wc] = wc
            w = c
            complexity +=1
            # Debugging: Print the updated window
            print("window reset & moves forward 1 chr) to:", w)
        # Increment the iteration counter
        b += 1
        print("current state of the dict",dict)

    # Return the dictionary containing unique subsequences
        
    return len(dict),complexity, dict


# To test this function, we need an input string, typically this would be a binarized
# EEG signal but we can use any binary string for demonstration purposes.

# Example 
binary_string = '010011'
#'110000001110001110000000001'

cpr_result = cpr(binary_string)

cpr_result



# calculate complexity, relative to length of string

import random

def lz_complexity(string):
    """Calculate the Lempel-Ziv complexity of a binary string."""
    # Initialize an empty list to keep track of unique patterns
    patterns = []
    # Initialize an empty string for the current pattern
    pattern = ""
    # Iterate over each character in the string
    for c in string:
        # Attempt to extend the current pattern with the next character
        new_pattern = pattern + c
        # If the new pattern has not been seen before
        if new_pattern not in patterns:
            # Add it to the list of unique patterns
            patterns.append(new_pattern)
            # Start a new pattern from the current character
            pattern = c
        else:
            # Otherwise, extend the current pattern
            pattern = new_pattern
    # The complexity is the number of unique patterns
    return len(patterns)

def normalize_lz(binary_string):
    """Normalize the LZ complexity by comparing it with that of a shuffled version."""
    # Calculate the LZ complexity of the original string
    original_complexity = lz_complexity(binary_string[:25])  # Limit to the first 25 characters
    
    # Shuffle the string to get a random sequence
    shuffled_string = list(binary_string[:25])  # Limit to the first 25 characters
    random.shuffle(shuffled_string)
    shuffled_string = ''.join(shuffled_string)
    
    # Calculate the LZ complexity of the shuffled string
    shuffled_complexity = lz_complexity(shuffled_string)
    
    # Normalize the complexity by dividing the original by the shuffled
    normalized_complexity = original_complexity / shuffled_complexity if shuffled_complexity else 0
    
    return normalized_complexity

# Example binary string
binary_string = '101010101000111'

# Normalize the Lempel-Ziv complexity
normalized_lz = normalize_lz(binary_string)

normalized_lz
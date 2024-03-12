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
        #  Print the current iteration number
        print("current iteration:", b)
        #  Print the current character
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


# Example 
binary_string = '010011'
#'110000001110001110000000001'

cpr_result = cpr(binary_string)

cpr_result

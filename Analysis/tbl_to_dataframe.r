# Install and load required packages
if (!requireNamespace("R.matlab", quietly = TRUE)) {
  install.packages("R.matlab")
}
library(R.matlab)
library(dplyr)
library(purrr)

setwd("C:/Users/prsyu/OneDrive/Bidlung/University/M.S. Leiden University/M.S. Neuroscience (Research)/Thesis/Analysis")
# Set the file path
mat_file <- "C:/Users/prsyu/OneDrive/Bidlung/University/M.S. Leiden University/M.S. Neuroscience (Research)/Thesis/Analysis/tbl_struct.mat"

# Read the .mat file
mat_data <- readMat(mat_file)

# Extract the tbl.struct
tbl_struct <- mat_data$tbl.struct[,,1]

# Function to extract data from nested lists
extract_data <- function(x) {
  if (is.list(x) && length(x) == 1066) {
    return(sapply(x, function(y) y[[1]]))
  } else if (is.array(x) && length(dim(x)) == 2 && dim(x)[2] == 1) {
    return(x[,1])
  } else {
    return(x)
  }
}

# Convert the struct to a list and extract data
tbl_list <- map(tbl_struct, extract_data)

# Examine each element of tbl_list
for (name in names(tbl_list)) {
  cat("Element:", name, "\n")
  cat("Class:", class(tbl_list[[name]]), "\n")
  cat("Length:", length(tbl_list[[name]]), "\n")
  cat("First few values:", head(tbl_list[[name]]), "\n\n")
}

# Try to create separate data frames for elements with 1066 rows
df_list <- list()
for (name in names(tbl_list)) {
  if (length(tbl_list[[name]]) == 1066) {
    df_list[[name]] <- data.frame(tbl_list[[name]])
  }
}

# Check which data frames were created
names(df_list)

# If any data frames were created, examine the first one
if (length(df_list) > 0) {
  first_df_name <- names(df_list)[1]
  cat("Structure of", first_df_name, ":\n")
  str(df_list[[first_df_name]])
  cat("\nFirst few rows of", first_df_name, ":\n")
  print(head(df_list[[first_df_name]]))
}

# Combine all the data frames in df_list
combined_df <- do.call(cbind, df_list)

# Rename the columns to remove the "tbl_list..name.." prefix
colnames(combined_df) <- names(df_list)

# Display the structure of the combined data frame
str(combined_df)

# Display the first few rows of the combined data frame
head(combined_df)

# Save the combined data frame to a CSV file
write.csv(combined_df, file = "combined_data.csv", row.names = FALSE)


library(dplyr)
library(tidyr)

# Function to convert matrix to data frame
matrix_to_df <- function(matrix_data, prefix) {
  if(is.null(dim(matrix_data))) {
    # If it's a vector, convert to a single-column matrix
    matrix_data <- matrix(matrix_data, ncol=1)
  }
  df <- as.data.frame(matrix_data)
  colnames(df) <- paste0(prefix, "_", 1:ncol(df))
  return(df)
}

# Convert matrix elements to data frames
df_dcc_var <- matrix_to_df(tbl_list$dcc.var, "dcc_var")
df_dcc_entropy <- matrix_to_df(tbl_list$dcc.entropy, "dcc_entropy")
df_entropy_pl <- matrix_to_df(tbl_list$entropy.pl, "entropy_pl")

# Combine all data frames
combined_df <- bind_cols(
  df_list,
  df_dcc_var,
  df_dcc_entropy,
  df_entropy_pl
)

# Display the structure of the combined data frame
str(combined_df)

# Display the first few rows of the combined data frame
head(combined_df)

# Save the combined data frame to a CSV file
write.csv(combined_df, file = "combined_data_with_matrices.csv", row.names = FALSE)
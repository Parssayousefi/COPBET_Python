%% Script to convert table to structure (matlab struct)

% Assuming 'tbl' is your table in MATLAB
tbl_struct = table2struct(tbl, 'ToScalar', true);

% Save the struct as a .mat file
save('tbl_struct.mat', 'tbl_struct');
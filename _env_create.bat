call _env_set.bat
call conda env create -f environment.yml
call conda activate %env%
call python -m ipykernel install --user --name %env% --display-name %env%
pause

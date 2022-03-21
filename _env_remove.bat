call set_env.bat
call conda env remove -n %env%
call jupyter kernelspec uninstall %env%
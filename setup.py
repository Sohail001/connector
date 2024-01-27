from cx_Freeze import setup, Executable

setup(
    name="YourAppName",
    version="1.0",
    description="Connector",
    executables=[Executable("app.py")],
) 
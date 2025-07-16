@echo off
echo Building executable...

REM Activate virtual environment
call venv\Scripts\activate

REM Clean up old build files
echo Cleaning up old build files...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "control_panel.spec" del "control_panel.spec"

REM Create spec file
echo Creating spec file...
pyi-makespec ^
    --onefile ^
    --add-data "src\utils\config.json;utils" ^
    --add-data "src\Doc\Doc_config.json;Doc" ^
    --hidden-import=tkinter ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageTk ^
    --hidden-import=PIL.ImageFont ^
    --hidden-import=PIL.ImageDraw ^
    --hidden-import=PIL.ImageGrab ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --hidden-import=pynput ^
    --hidden-import=pynput.mouse ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=docx ^
    --hidden-import=docx.shared ^
    --hidden-import=docx.oxml ^
    --hidden-import=docx.oxml.ns ^
    --hidden-import=psutil ^
    --hidden-import=pyautogui ^
    --hidden-import=webbrowser ^
    --hidden-import=selenium ^
    --hidden-import=requests ^
    --hidden-import=tempfile ^
    --hidden-import=shutil ^
    --hidden-import=atexit ^
    --hidden-import=threading ^
    --hidden-import=queue ^
    --hidden-import=base64 ^
    --hidden-import=io ^
    --hidden-import=math ^
    --hidden-import=datetime ^
    --hidden-import=json ^
    --hidden-import=os ^
    --hidden-import=sys ^
    --hidden-import=time ^
    --hidden-import=random ^
    --hidden-import=string ^
    --hidden-import=subprocess ^
    --hidden-import=typing ^
    --hidden-import=typing.Dict ^
    --hidden-import=typing.Any ^
    --hidden-import=typing.List ^
    src\gui\control_panel.py

REM Build using spec file
echo Building executable...
pyinstaller --noconfirm ^
    --clean ^
    --log-level DEBUG ^
    control_panel.spec

echo Build complete!
echo The executable is in the dist folder.
echo.
echo To debug the executable:
echo 1. Open Command Prompt
echo 2. Navigate to the dist folder
echo 3. Run: control_panel.exe
echo 4. Check for any error messages
pause 
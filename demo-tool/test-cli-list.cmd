@echo off
REM Test CLI --list command

cd /d C:\TestRepo\demo-tool

echo Testing CLI --list command...
echo.

call "%USERPROFILE%\tools\apache-maven-3.9.9\bin\mvn.cmd" exec:java -Dexec.mainClass="com.tts.demo.CliApp" -Dexec.args="--list" -Dexec.cleanupDaemonThreads=false

echo.
echo Exit code: %ERRORLEVEL%

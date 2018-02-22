# For non-IDE usage.
OUT = ./target
MAIN = main.Main

all: compile run

compile:
	@#https://stackoverflow.com/a/2096298
	javac -classpath src -d $(OUT) `find src -name *.java`

run:
	cd target && java $(MAIN) -Xdock:name=AdvancesSettingsMacOS
